from collections import defaultdict
from datetime import datetime, timedelta, timezone
from html import escape
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

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

def render_stats_svg(profile):
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

    positions = [95, 275]
    metric_markup = []

    for x, (label, value) in zip(
        positions,
        metrics,
    ):
        metric_markup.append(
            f'''
    <g transform="translate({x} 101)">
        <text class="value" x="0" y="0" text-anchor="middle">{escape(value)}</text>
        <text class="label" x="0" y="25" text-anchor="middle">{escape(label)}</text>
    </g>'''
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="370" height="170" viewBox="0 0 370 170" role="img" aria-labelledby="title desc">
    <title id="title">{escape(USERNAME)} GitHub Stats</title>
    <desc id="desc">Aggregated GitHub statistics for {escape(USERNAME)}.</desc>

    <style>
        .card {{
            fill: #ffffff;
            stroke: #d0d7de;
        }}

        .title {{
            fill: #491d34;
            font: 600 16px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        }}

        .value {{
            fill: #1f2328;
            font: 600 27px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        }}

        .label {{
            fill: #656d76;
            font: 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        }}

        .rule {{
            stroke: #d0d7de;
        }}

        @media (prefers-color-scheme: dark) {{
            .card {{
                fill: #0d1117;
                stroke: #30363d;
            }}

            .title {{
                fill: #c8ad67;
            }}

            .value {{
                fill: #e6edf3;
            }}

            .label {{
                fill: #8b949e;
            }}

            .rule {{
                stroke: #30363d;
            }}
        }}
    </style>

    <rect class="card" x="0.5" y="0.5" width="369" height="169" rx="8" />

    <text class="title" x="20" y="31">GitHub overview</text>

    <line class="rule" x1="20" y1="47" x2="350" y2="47" />
    <line class="rule" x1="185" y1="66" x2="185" y2="141" />

    {''.join(metric_markup)}
</svg>
'''
def render_languages_svg(languages):
    top_languages = languages[:5]

    total_bytes = sum(
        language["bytes"]
        for language in languages
    )

    if total_bytes == 0:
        rows = '''
    <text class="muted" x="20" y="91">No language data available yet.</text>'''

        bar_segments = ""

    else:
        rows_markup = []
        bar_markup = []

        bar_x = 20.0
        bar_width = 330.0

        for index, language in enumerate(
            top_languages
        ):
            percentage = (
                language["bytes"]
                / total_bytes
                * 100
            )

            y = 84 + index * 18
            color = language["color"]

            rows_markup.append(
                f'''
    <circle cx="26" cy="{y - 4}" r="4" fill="{escape(color)}" />
    <text class="language" x="38" y="{y}">{escape(language["name"])}</text>
    <text class="percentage" x="350" y="{y}" text-anchor="end">{percentage:.1f}%</text>'''
            )

            segment_width = (
                bar_width
                * language["bytes"]
                / total_bytes
            )

            bar_markup.append(
                f'<rect x="{bar_x:.2f}" y="52" width="{segment_width:.2f}" height="10" fill="{escape(color)}" />'
            )

            bar_x += segment_width

        rows = "".join(rows_markup)
        bar_segments = "\n    ".join(bar_markup)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="370" height="170" viewBox="0 0 370 170" role="img" aria-labelledby="title desc">
    <title id="title">{escape(USERNAME)} Top Languages</title>
    <desc id="desc">Language distribution across public non-archived project repositories owned by {escape(USERNAME)}.</desc>

    <style>
        .card {{
            fill: #ffffff;
            stroke: #d0d7de;
        }}

        .title {{
            fill: #491d34;
            font: 600 16px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        }}

        .language {{
            fill: #1f2328;
            font: 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        }}

        .percentage,
        .muted {{
            fill: #656d76;
            font: 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        }}

        .bar-background {{
            fill: #eaeef2;
        }}

        @media (prefers-color-scheme: dark) {{
            .card {{
                fill: #0d1117;
                stroke: #30363d;
            }}

            .title {{
                fill: #c8ad67;
            }}

            .language {{
                fill: #e6edf3;
            }}

            .percentage,
            .muted {{
                fill: #8b949e;
            }}

            .bar-background {{
                fill: #21262d;
            }}
        }}
    </style>

    <defs>
        <clipPath id="language-bar-clip">
            <rect x="20" y="52" width="330" height="10" rx="5" />
        </clipPath>
    </defs>

    <rect class="card" x="0.5" y="0.5" width="369" height="169" rx="8" />

    <text class="title" x="20" y="31">Languages</text>

    <rect class="bar-background" x="20" y="52" width="330" height="10" rx="5" />

    <g clip-path="url(#language-bar-clip)">
        {bar_segments}
    </g>

    {rows}
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

        activity_text = (
            f'{language}'
            f' · {activity["commits_7d"]} commits / 7d'
            f' · {activity["active_days_14d"]} active days / 14d'
        )

        latest_commit_age = activity["latest_commit_age"]

        if latest_commit_age is not None:
            activity_text += (
                f" · last commit "
                f"{relative_commit_age(latest_commit_age)}"
            )

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

def update_readme(repositories, building_now):
    if not README_PATH.exists():
        return

    content = README_PATH.read_text(encoding="utf-8")

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

    if building_updated or releases_updated or repositories_updated:
        README_PATH.write_text(
            content,
            encoding="utf-8",
            newline="\n",
        )

def main():
    profile = fetch_profile_data()
    repositories = profile["repositories"]
    languages = aggregate_languages(repositories)
    building_now = collect_building_now(repositories)

    PROFILE_ASSETS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    (PROFILE_ASSETS_DIR / "stats.svg").write_text(
        render_stats_svg(profile),
        encoding="utf-8",
        newline="\n",
    )

    (PROFILE_ASSETS_DIR / "languages.svg").write_text(
        render_languages_svg(languages),
        encoding="utf-8",
        newline="\n",
    )


    update_readme(repositories, building_now)

    print("Updated profile assets.")
    print(f"Repositories: {len(repositories)}")
    print(f"Languages: {len(languages)}")
    print(f"Building now: {len(building_now)}")

if __name__ == "__main__":
    main()
