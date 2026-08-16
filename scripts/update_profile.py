from collections import defaultdict
from datetime import datetime, timedelta, timezone
from html import escape
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

from profile_renderers import (
    load_snapshot_mode,
    render_snapshot_readme,
    write_native_table_hybrid_assets,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

PROFILE_ASSETS_DIR = REPO_ROOT / "assets" / "profile"
README_PATH = REPO_ROOT / "README.md"

USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER", "Yusseter")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

EXCLUDED_REPOSITORIES = {
    USERNAME,
    "Placeholder",
}

BUILDING_NOW_LIMIT = 4
ACTIVITY_WINDOW_DAYS = 30

RECENT_RELEASE_VISIBLE = 3
RECENT_RELEASE_LIMIT = 8
RECENT_REPOSITORY_LIMIT = 5

GRAPHQL_URL = "https://api.github.com/graphql"

REPOSITORIES_QUERY = """
query($login: String!, $after: String, $activitySince: GitTimestamp!) {
    user(login: $login) {

        repositories(
            first: 100
            after: $after
            ownerAffiliations: OWNER
            privacy: PUBLIC
            isFork: false
            orderBy: {field: PUSHED_AT, direction: DESC}
        ) {
            pageInfo {
                hasNextPage
                endCursor
            }
            nodes {
                name
                url
                description
                isArchived
                stargazerCount
                pushedAt
                createdAt
                defaultBranchRef {
                    target {
                        ... on Commit {
                            history(first: 50, since: $activitySince) {
                                nodes {
                                    committedDate
                                    author {
                                        user {
                                            login
                                        }
                                    }
                                    committer {
                                        user {
                                            login
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                languages(first: 20, orderBy: {field: SIZE, direction: DESC}) {
                    edges {
                        size
                        node {
                            name
                            color
                        }
                    }
                }
                releases(first: 10, orderBy: {field: CREATED_AT, direction: DESC}) {
                    totalCount
                    nodes {
                        name
                        tagName
                        publishedAt
                        url
                        isDraft
                        isPrerelease
                    }
                }
            }
        }
    }
}
"""

def graphql_request(query, variables):
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN is not set.")

    request = urllib.request.Request(
        GRAPHQL_URL,
        data=json.dumps(
            {
                "query": query,
                "variables": variables,
            }
        ).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": f"{USERNAME}-profile-updater",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub GraphQL request failed with HTTP {error.code}: {body}"
        ) from error

    if payload.get("errors"):
        raise RuntimeError(
            "GitHub GraphQL returned errors: "
            + json.dumps(payload["errors"], ensure_ascii=False)
        )

    return payload["data"]

def fetch_profile_data():
    repositories = []
    cursor = None

    activity_since = (
        datetime.now(timezone.utc)
        - timedelta(days=ACTIVITY_WINDOW_DAYS)
    ).isoformat().replace("+00:00", "Z")

    while True:
        data = graphql_request(
            REPOSITORIES_QUERY,
            {
                "login": USERNAME,
                "after": cursor,
                "activitySince": activity_since,
            },
        )

        user = data.get("user")

        if not user:
            raise RuntimeError(f"GitHub user not found: {USERNAME}")


        repository_connection = user["repositories"]
        repositories.extend(repository_connection["nodes"])

        page_info = repository_connection["pageInfo"]

        if not page_info["hasNextPage"]:
            break

        cursor = page_info["endCursor"]

    return {
        "repositories": repositories,
    }

def format_number(value):
    return f"{value:,}"

def project_repositories(repositories):
    return [
        repository
        for repository in repositories
        if not repository["isArchived"]
        and repository["name"] not in EXCLUDED_REPOSITORIES
    ]

def aggregate_languages(repositories):
    totals = defaultdict(int)
    colors = {}

    for repository in project_repositories(repositories):
        for edge in repository["languages"]["edges"]:
            language = edge["node"]["name"]
            totals[language] += edge["size"]

            if language not in colors:
                colors[language] = edge["node"]["color"] or "#8b949e"

    ordered = sorted(
        totals.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        {
            "name": name,
            "bytes": size,
            "color": colors[name],
        }
        for name, size in ordered
    ]

def render_snapshot_svg(
    profile,
    languages,
    mobile=False,
):
    repositories = profile["repositories"]

    total_stars = sum(
        repository["stargazerCount"]
        for repository in repositories
    )

    total_releases = sum(
        repository["releases"]["totalCount"]
        for repository in repositories
    )

    metrics = [
        ("Total stars", format_number(total_stars)),
        ("Total releases", format_number(total_releases)),
    ]

    metric_positions = [95, 275]
    metric_markup = []

    for x, (label, value) in zip(
        metric_positions,
        metrics,
    ):
        metric_markup.append(
            f'''
    <g transform="translate({x} 115)">
        <text class="value" x="0" y="0" text-anchor="middle">{escape(value)}</text>
        <text class="secondary" x="0" y="30" text-anchor="middle">{escape(label)}</text>
    </g>'''
        )

    if mobile:
        svg_width = 370
        svg_height = 400
        title_size = 18

        language_card_x = 0.5
        language_card_y = 210.5

        language_content_x = 20
        language_title_y = 242
        language_bar_y = 268
        language_row_start_y = 298

        language_dot_x = 26
        language_name_x = 38
        language_percentage_x = 350

    else:
        svg_width = 760
        svg_height = 190
        title_size = 16

        language_card_x = 390.5
        language_card_y = 0.5

        language_content_x = 410
        language_title_y = 32
        language_bar_y = 58
        language_row_start_y = 88

        language_dot_x = 416
        language_name_x = 428
        language_percentage_x = 740

    top_languages = languages[:5]

    total_bytes = sum(
        language["bytes"]
        for language in languages
    )

    if total_bytes == 0:
        language_rows = f'''
    <text class="secondary" x="{language_content_x}" y="{language_row_start_y + 10}">No language data available yet.</text>'''

        bar_segments = ""

    else:
        rows_markup = []
        bar_markup = []

        bar_x = float(language_content_x)
        bar_width = 330.0

        for index, language in enumerate(
            top_languages
        ):
            percentage = (
                language["bytes"]
                / total_bytes
                * 100
            )

            y = language_row_start_y + index * 22
            color = language["color"]

            rows_markup.append(
                f'''
    <circle cx="{language_dot_x}" cy="{y - 4}" r="4" fill="{escape(color)}" />
    <text class="primary" x="{language_name_x}" y="{y}">{escape(language["name"])}</text>
    <text class="secondary" x="{language_percentage_x}" y="{y}" text-anchor="end">{percentage:.1f}%</text>'''
            )

            segment_width = (
                bar_width
                * language["bytes"]
                / total_bytes
            )

            bar_markup.append(
                f'<rect x="{bar_x:.2f}" y="{language_bar_y}" width="{segment_width:.2f}" height="10" fill="{escape(color)}" />'
            )

            bar_x += segment_width

        language_rows = "".join(rows_markup)
        bar_segments = "\n    ".join(bar_markup)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" role="img" aria-labelledby="title desc">
    <title id="title">{escape(USERNAME)} GitHub Snapshot</title>
    <desc id="desc">GitHub statistics and language distribution for {escape(USERNAME)}.</desc>

    <style>
        .card {{
            fill: transparent;
            stroke: #d1d9e0b3;
        }}

        .title {{
            fill: #1f2328;
            font: 600 {title_size}px -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
        }}

        .value {{
            fill: #1f2328;
            font: 600 28px -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
        }}

        .primary {{
            fill: #1f2328;
            font: 16px -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
        }}

        .secondary {{
            fill: #59636e;
            font: 16px -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
        }}

        .rule {{
            stroke: #d1d9e0b3;
        }}

        .bar-background {{
            fill: #59636e;
            fill-opacity: 0.12;
        }}

        @media (prefers-color-scheme: dark) {{
            .card {{
                stroke: #3d444db3;
            }}

            .title,
            .value,
            .primary {{
                fill: #f0f6fc;
            }}

            .secondary {{
                fill: #9198a1;
            }}

            .rule {{
                stroke: #3d444db3;
            }}

            .bar-background {{
                fill: #9198a1;
                fill-opacity: 0.18;
            }}
        }}
    </style>

    <defs>
        <clipPath id="language-bar-clip">
            <rect x="{language_content_x}" y="{language_bar_y}" width="330" height="10" rx="5" />
        </clipPath>
    </defs>

    <!-- GitHub overview -->
    <rect class="card" x="0.5" y="0.5" width="369" height="189" rx="6" />

    <text class="title" x="20" y="32">GitHub overview</text>

    <line class="rule" x1="20" y1="51" x2="350" y2="51" />
    <line class="rule" x1="185" y1="72" x2="185" y2="160" />

    {''.join(metric_markup)}

    <!-- Languages -->
    <rect class="card" x="{language_card_x}" y="{language_card_y}" width="369" height="189" rx="6" />

    <text class="title" x="{language_content_x}" y="{language_title_y}">Languages</text>

    <rect class="bar-background" x="{language_content_x}" y="{language_bar_y}" width="330" height="10" rx="5" />

    <g clip-path="url(#language-bar-clip)">
        {bar_segments}
    </g>

    {language_rows}
</svg>
'''

def parse_github_date(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def own_commit_dates(repository):
    default_branch = repository.get("defaultBranchRef") or {}
    target = default_branch.get("target") or {}
    history = target.get("history") or {}
    commits = history.get("nodes") or []

    username = USERNAME.casefold()
    dates = []

    for commit in commits:
        author_user = ((commit.get("author") or {}).get("user") or {})
        committer_user = ((commit.get("committer") or {}).get("user") or {})

        author_login = (author_user.get("login") or "").casefold()
        committer_login = (committer_user.get("login") or "").casefold()

        if username not in {author_login, committer_login}:
            continue

        dates.append(
            parse_github_date(commit["committedDate"])
        )

    return dates

def repository_activity(repository, now):
    commit_dates = own_commit_dates(repository)

    since_7d = now - timedelta(days=7)
    since_14d = now - timedelta(days=14)

    commits_7d = sum(
        date >= since_7d
        for date in commit_dates
    )

    commits_14d = sum(
        date >= since_14d
        for date in commit_dates
    )

    commits_30d = len(commit_dates)

    active_days_14d = len({
        date.date()
        for date in commit_dates
        if date >= since_14d
    })

    latest_commit_age = None

    if commit_dates:
        latest_commit_age = (
            now - max(commit_dates)
        ).days

    created_age = (
        now - parse_github_date(repository["createdAt"])
    ).days

    latest_release_age = None

    published_releases = [
        release
        for release in repository["releases"]["nodes"]
        if not release["isDraft"]
        and release["publishedAt"]
    ]

    if published_releases:
        latest_release_age = (
            now
            - max(
                parse_github_date(release["publishedAt"])
                for release in published_releases
            )
        ).days

    return {
        "commits_7d": commits_7d,
        "commits_14d": commits_14d,
        "commits_30d": commits_30d,
        "active_days_14d": active_days_14d,
        "latest_commit_age": latest_commit_age,
        "created_age": created_age,
        "latest_release_age": latest_release_age,
    }

def qualifies_for_building_now(activity):
    commits_7d = activity["commits_7d"]
    commits_14d = activity["commits_14d"]
    active_days_14d = activity["active_days_14d"]
    created_age = activity["created_age"]

    sustained_recent_work = (
        commits_7d >= 2
        and active_days_14d >= 2
    )

    concentrated_recent_work = commits_7d >= 4

    continuing_work = (
        commits_7d >= 1
        and commits_14d >= 4
        and active_days_14d >= 3
    )

    new_project_work = (
        created_age <= 14
        and commits_7d >= 2
    )

    return any(
        (
            sustained_recent_work,
            concentrated_recent_work,
            continuing_work,
            new_project_work,
        )
    )

def building_activity_score(activity):
    commits_7d = activity["commits_7d"]
    commits_14d = activity["commits_14d"]
    commits_30d = activity["commits_30d"]
    active_days_14d = activity["active_days_14d"]
    latest_commit_age = activity["latest_commit_age"]

    score = 0.0

    score += min(commits_7d, 10) * 4.0

    score += min(
        max(commits_14d - commits_7d, 0),
        10,
    ) * 1.25

    score += min(
        max(commits_30d - commits_14d, 0),
        20,
    ) * 0.2

    score += min(active_days_14d, 10) * 2.0

    if latest_commit_age is not None:
        if latest_commit_age <= 1:
            score += 6.0
        elif latest_commit_age <= 3:
            score += 4.0
        elif latest_commit_age <= 7:
            score += 2.0

    if activity["created_age"] <= 14:
        score += 2.0

    latest_release_age = activity["latest_release_age"]

    if (
        latest_release_age is not None
        and latest_release_age <= 7
    ):
        score += 1.0

    return score

def collect_building_now(repositories):
    now = datetime.now(timezone.utc)
    candidates = []

    for repository in project_repositories(repositories):
        activity = repository_activity(
            repository,
            now,
        )

        if not qualifies_for_building_now(activity):
            continue

        candidates.append(
            {
                "repository": repository,
                "activity": activity,
                "score": building_activity_score(activity),
            }
        )

    candidates.sort(
        key=lambda item: (
            item["score"],
            parse_github_date(
                item["repository"]["pushedAt"]
                or item["repository"]["createdAt"]
            ),
        ),
        reverse=True,
    )

    return candidates[:BUILDING_NOW_LIMIT]

def relative_commit_age(days):
    if days == 0:
        return "today"

    if days == 1:
        return "1d ago"

    return f"{days}d ago"

def primary_language(repository):
    language_edges = repository["languages"]["edges"]

    if not language_edges:
        return "No language data"

    return language_edges[0]["node"]["name"]

def render_building_now(items):
    if not items:
        return "_No active repositories detected right now._"

    lines = []

    for item in items:
        repository = item["repository"]
        activity = item["activity"]

        description = (
            (repository["description"] or "No description.")
            .replace("\r", " ")
            .replace("\n", " ")
            .strip()
        )

        language = primary_language(repository)

        activity_parts = [language]

        latest_commit_age = activity["latest_commit_age"]

        if latest_commit_age is not None:
            activity_parts.append(
                f"updated {relative_commit_age(latest_commit_age)}"
            )

        activity_text = " · ".join(activity_parts)

        lines.append(
            f'- **[{repository["name"]}]({repository["url"]})**'
            f' — {description}  \n'
            f'  *{activity_text}*'
        )

    return "\n".join(lines)
def collect_recent_releases(repositories):
    releases = []

    for repository in project_repositories(repositories):
        for release in repository["releases"]["nodes"]:
            if release["isDraft"] or not release["publishedAt"]:
                continue

            releases.append(
                {
                    "repository": repository["name"],
                    "name": release["name"] or release["tagName"],
                    "url": release["url"],
                    "publishedAt": release["publishedAt"],
                    "isPrerelease": release["isPrerelease"],
                }
            )

    releases.sort(
        key=lambda release: parse_github_date(release["publishedAt"]),
        reverse=True,
    )

    return releases[:RECENT_RELEASE_LIMIT]

def render_recent_releases(releases):
    if not releases:
        return "_No published releases yet._"

    def release_line(release):
        suffix = (
            " (pre-release)"
            if release["isPrerelease"]
            else ""
        )

        published = release["publishedAt"][:10]

        return (
            f'- [{release["repository"]} — {release["name"]}]'
            f'({release["url"]})'
            f'{suffix} — {published}'
        )

    visible = releases[:RECENT_RELEASE_VISIBLE]
    hidden = releases[RECENT_RELEASE_VISIBLE:]

    lines = [
        release_line(release)
        for release in visible
    ]

    if hidden:
        lines.extend(
            [
                "",
                "<details>",
                "<summary>More releases</summary>",
                "",
            ]
        )

        lines.extend(
            release_line(release)
            for release in hidden
        )

        lines.extend(
            [
                "",
                "</details>",
            ]
        )

    return "\n".join(lines)
def render_recent_repositories(repositories):
    recent = sorted(
        project_repositories(repositories),
        key=lambda repository: parse_github_date(
            repository["pushedAt"]
            or repository["createdAt"]
        ),
        reverse=True,
    )[:RECENT_REPOSITORY_LIMIT]

    if not recent:
        return "_No recently updated repositories._"

    lines = []

    for repository in recent:
        description = (
            (repository["description"] or "No description.")
            .replace("\r", " ")
            .replace("\n", " ")
            .strip()
        )

        pushed = (
            repository["pushedAt"]
            or repository["createdAt"]
        )[:10]

        lines.append(
            f'- [{repository["name"]}]({repository["url"]}) — {description} — {pushed}'
        )

    return "\n".join(lines)

def replace_marked_block(content, marker, replacement):
    start_marker = f"<!-- {marker}:start -->"
    end_marker = f"<!-- {marker}:end -->"

    start = content.find(start_marker)
    end = content.find(end_marker)

    if start == -1 or end == -1 or end < start:
        return content, False

    content_start = start + len(start_marker)

    updated = (
        content[:content_start]
        + "\n"
        + replacement.strip()
        + "\n"
        + content[end:]
    )

    return updated, True

def update_readme(
    profile,
    languages,
    building_now,
    snapshot_mode,
):
    repositories = profile["repositories"]

    if not README_PATH.exists():
        return

    content = README_PATH.read_text(encoding="utf-8")

    snapshot = render_snapshot_readme(
        profile,
        languages,
        snapshot_mode,
    )

    content, snapshot_updated = replace_marked_block(
        content,
        "snapshot",
        snapshot,
    )

    content, building_updated = replace_marked_block(
        content,
        "building_now",
        render_building_now(building_now),
    )

    content, releases_updated = replace_marked_block(
        content,
        "recent_releases",
        render_recent_releases(
            collect_recent_releases(repositories)
        ),
    )

    content, repositories_updated = replace_marked_block(
        content,
        "recent_repositories",
        render_recent_repositories(repositories),
    )

    if (
        snapshot_updated
        or building_updated
        or releases_updated
        or repositories_updated
    ):
        README_PATH.write_text(
            content,
            encoding="utf-8",
            newline="\n",
        )

def main():
    snapshot_mode = load_snapshot_mode(
        REPO_ROOT
    )

    profile = fetch_profile_data()
    repositories = profile["repositories"]
    languages = aggregate_languages(repositories)
    building_now = collect_building_now(repositories)

    PROFILE_ASSETS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    (PROFILE_ASSETS_DIR / "snapshot.svg").write_text(
        render_snapshot_svg(profile, languages),
        encoding="utf-8",
        newline="\n",
    )

    (PROFILE_ASSETS_DIR / "snapshot-mobile.svg").write_text(
        render_snapshot_svg(
            profile,
            languages,
            mobile=True,
        ),
        encoding="utf-8",
        newline="\n",
    )

    write_native_table_hybrid_assets(
        PROFILE_ASSETS_DIR,
        languages,
    )

    for legacy_name in (
        "stats.svg",
        "languages.svg",
    ):
        legacy_path = PROFILE_ASSETS_DIR / legacy_name

        if legacy_path.exists():
            legacy_path.unlink()


    update_readme(
        profile,
        languages,
        building_now,
        snapshot_mode,
    )

    print("Updated profile assets.")
    print(f"Snapshot mode: {snapshot_mode}")
    print(f"Repositories: {len(repositories)}")
    print(f"Languages: {len(languages)}")
    print(f"Building now: {len(building_now)}")

if __name__ == "__main__":
    main()
