from collections import defaultdict
from datetime import datetime, timedelta, timezone
from html import escape
import json
import os
import re
import time
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

from profile_renderers import (
    load_profile_config,
    render_snapshot_readme,
    write_native_table_hybrid_assets,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

PROFILE_ASSETS_DIR = REPO_ROOT / "assets" / "profile"
GENERATED_PROFILE_ASSETS_DIR = PROFILE_ASSETS_DIR / "generated"
LANGUAGE_ASSETS_DIR = (
    GENERATED_PROFILE_ASSETS_DIR
    / "languages"
)
SNAPSHOT_ASSETS_DIR = (
    GENERATED_PROFILE_ASSETS_DIR
    / "snapshot"
)
README_PATH = REPO_ROOT / "README.md"

USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER", "Yusseter")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

BUILDING_NOW_LIMIT = 4
ACTIVITY_WINDOW_DAYS = 30

RECENT_RELEASE_VISIBLE = 3
RECENT_RELEASE_LIMIT = 8
RECENT_COMMIT_LIMIT = 5
RECENT_COMMIT_SEARCH_LIMIT = 50
RECENT_COMMIT_SEARCH_RETRY_DELAYS = (1, 3)
GITHUB_REQUEST_RETRY_DELAYS = (1, 3, 7)
TRANSIENT_GITHUB_HTTP_CODES = {429, 500, 502, 503, 504}

GRAPHQL_URL = "https://api.github.com/graphql"
SEARCH_COMMITS_URL = "https://api.github.com/search/commits"

SETI_UI_REVISION = "2d6c5e68b4ded73c92dac291845ee44e1182d511"
SETI_ICON_RAW_BASE_URL = (
    "https://raw.githubusercontent.com/jesseweed/seti-ui/"
    f"{SETI_UI_REVISION}/icons"
)

SETI_LANGUAGE_ICON_OVERRIDES = {
    "C++": "cpp",
    "C#": "c-sharp",
    "F#": "f-sharp",
    "Objective-C": "objective-c",
    "Objective-C++": "objective-cpp",
    "PowerShell": "powershell",
    "Shell": "shell",
    "Jupyter Notebook": "jupyter",
    "Vim Script": "vim",
}

SETI_ICON_RENDER_HEIGHT = 20
SETI_ICON_VERTICAL_SHIFT_PX = 3.0
SETI_ICON_MOBILE_VERTICAL_SHIFT_PX = 2.0

_SETI_ICON_AVAILABILITY = {}

# Fetch all owned repositories visible to the token; each profile
# section decides what can safely be published.
REPOSITORIES_QUERY = """
query($login: String!, $after: String, $activitySince: GitTimestamp!) {
    user(login: $login) {

        repositories(
            first: 100
            after: $after
            ownerAffiliations: OWNER
            orderBy: {field: PUSHED_AT, direction: DESC}
        ) {
            pageInfo {
                hasNextPage
                endCursor
            }
            nodes {
                name
                nameWithOwner
                url
                description
                isArchived
                isFork
                isPrivate
                stargazerCount
                pushedAt
                createdAt
                defaultBranchRef {
                    target {
                        ... on Commit {
                            committedDate
                            history(first: 50, since: $activitySince) {
                                nodes {
                                    oid
                                    url
                                    messageHeadline
                                    messageBody
                                    authoredDate
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
                        isLatest
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

    for attempt in range(
        len(GITHUB_REQUEST_RETRY_DELAYS) + 1
    ):
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
            with urllib.request.urlopen(
                request,
                timeout=30,
            ) as response:
                payload = json.load(response)

        except urllib.error.HTTPError as error:
            try:
                body = error.read().decode(
                    "utf-8",
                    errors="replace",
                )
            finally:
                error.close()

            if (
                error.code in TRANSIENT_GITHUB_HTTP_CODES
                and attempt
                < len(GITHUB_REQUEST_RETRY_DELAYS)
            ):
                delay = GITHUB_REQUEST_RETRY_DELAYS[
                    attempt
                ]

                print(
                    "Warning: GitHub GraphQL returned "
                    f"HTTP {error.code}; retrying in "
                    f"{delay}s."
                )
                time.sleep(delay)
                continue

            raise RuntimeError(
                "GitHub GraphQL request failed with "
                f"HTTP {error.code}: {body}"
            ) from error

        except (
            urllib.error.URLError,
            TimeoutError,
        ) as error:
            if attempt < len(
                GITHUB_REQUEST_RETRY_DELAYS
            ):
                delay = GITHUB_REQUEST_RETRY_DELAYS[
                    attempt
                ]

                print(
                    "Warning: GitHub GraphQL request "
                    f"failed temporarily; retrying in "
                    f"{delay}s."
                )
                time.sleep(delay)
                continue

            raise RuntimeError(
                "GitHub GraphQL request failed after "
                f"retries: {error}"
            ) from error

        if payload.get("errors"):
            raise RuntimeError(
                "GitHub GraphQL returned errors: "
                + json.dumps(
                    payload["errors"],
                    ensure_ascii=False,
                )
            )

        return payload["data"]

    raise RuntimeError(
        "GitHub GraphQL retry loop exited unexpectedly."
    )


def rest_json_request(url, params=None):
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN is not set.")

    if params:
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}"

    for attempt in range(
        len(GITHUB_REQUEST_RETRY_DELAYS) + 1
    ):
        request = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
                "User-Agent": f"{USERNAME}-profile-updater",
            },
            method="GET",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=30,
            ) as response:
                return json.load(response)

        except urllib.error.HTTPError as error:
            try:
                body = error.read().decode(
                    "utf-8",
                    errors="replace",
                )
            finally:
                error.close()

            if (
                error.code in TRANSIENT_GITHUB_HTTP_CODES
                and attempt
                < len(GITHUB_REQUEST_RETRY_DELAYS)
            ):
                delay = GITHUB_REQUEST_RETRY_DELAYS[
                    attempt
                ]

                print(
                    "Warning: GitHub REST returned "
                    f"HTTP {error.code}; retrying in "
                    f"{delay}s."
                )
                time.sleep(delay)
                continue

            raise RuntimeError(
                "GitHub REST request failed with HTTP "
                f"{error.code}: {body}"
            ) from error

        except (
            urllib.error.URLError,
            TimeoutError,
        ) as error:
            if attempt < len(
                GITHUB_REQUEST_RETRY_DELAYS
            ):
                delay = GITHUB_REQUEST_RETRY_DELAYS[
                    attempt
                ]

                print(
                    "Warning: GitHub REST request failed "
                    f"temporarily; retrying in {delay}s."
                )
                time.sleep(delay)
                continue

            raise RuntimeError(
                "GitHub REST request failed after "
                f"retries: {error}"
            ) from error

    raise RuntimeError(
        "GitHub REST retry loop exited unexpectedly."
    )


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

def repository_full_name(repository):
    return (
        repository.get("nameWithOwner")
        or f'{USERNAME}/{repository["name"]}'
    )


def release_repositories(repositories):
    return [
        repository
        for repository in repositories
        if not repository["isArchived"]
        and not repository.get("isFork", False)
        and not repository.get("isPrivate", False)
    ]


def activity_repositories(repositories):
    return [
        repository
        for repository in repositories
        if not repository["isArchived"]
        and not repository.get("isPrivate", False)
    ]


def snapshot_repositories(
    repositories,
    contribution_forks,
):
    contribution_forks = {
        repository.casefold()
        for repository in contribution_forks
    }

    return [
        repository
        for repository in repositories
        if not (
            repository.get("isFork", False)
            and repository_full_name(
                repository
            ).casefold() in contribution_forks
        )
    ]


def build_snapshot_profile(
    profile,
    contribution_forks,
):
    return {
        **profile,
        "repositories": snapshot_repositories(
            profile["repositories"],
            contribution_forks,
        ),
    }


def aggregate_languages(repositories):
    totals = defaultdict(int)
    colors = {}

    for repository in repositories:
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
    latest_commit_at = None

    if commit_dates:
        latest_commit = max(commit_dates)

        latest_commit_age = (
            now - latest_commit
        ).days

        latest_commit_at = (
            latest_commit
            .astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )

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
        "latest_commit_at": latest_commit_at,
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

    def latest_commit_key(item):
        value = item["activity"].get(
            "latest_commit_at"
        )

        if value:
            return parse_github_date(value)

        return datetime.min.replace(
            tzinfo=timezone.utc
        )

    for repository in activity_repositories(
        repositories
    ):
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
                "score": building_activity_score(
                    activity
                ),
            }
        )

    # Activity score chooses which repositories qualify
    # for the limited Building now slots.
    candidates.sort(
        key=lambda item: (
            item["score"],
            latest_commit_key(item),
        ),
        reverse=True,
    )

    selected = candidates[:BUILDING_NOW_LIMIT]

    # Presentation order is chronological: newest real
    # user-associated activity first.
    selected.sort(
        key=latest_commit_key,
        reverse=True,
    )

    return selected


def render_relative_time(value):
    timestamp = parse_github_date(value).astimezone(timezone.utc)
    datetime_value = (
        timestamp.isoformat()
        .replace("+00:00", "Z")
    )
    fallback = (
        f"{timestamp.strftime('%b')} "
        f"{timestamp.day}, "
        f"{timestamp.year}"
    )

    return (
        f'<relative-time datetime="{datetime_value}">'
        f'{fallback}'
        f'</relative-time>'
    )

def primary_language(repository):
    language_edges = repository["languages"]["edges"]

    if not language_edges:
        return "No language data"

    return language_edges[0]["node"]["name"]

def normalized_seti_icon_stem(language):
    override = SETI_LANGUAGE_ICON_OVERRIDES.get(language)

    if override:
        return override

    parts = []
    pending_dash = False

    for character in language.casefold():
        if character.isalnum():
            if pending_dash and parts:
                parts.append("-")
            parts.append(character)
            pending_dash = False
        else:
            pending_dash = True

    return "".join(parts).strip("-")

def seti_language_icon_url(language):
    if language == "No language data":
        return None

    stem = normalized_seti_icon_stem(language)

    if not stem:
        return None

    encoded_name = urllib.parse.quote(
        f"{stem}.svg",
        safe="",
    )
    icon_url = f"{SETI_ICON_RAW_BASE_URL}/{encoded_name}"

    cached = _SETI_ICON_AVAILABILITY.get(icon_url)

    if cached is not None:
        return icon_url if cached else None

    request = urllib.request.Request(
        icon_url,
        headers={
            "User-Agent": f"{USERNAME}-profile-updater",
        },
        method="HEAD",
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            available = 200 <= response.status < 400
    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        TimeoutError,
    ):
        available = False

    _SETI_ICON_AVAILABILITY[icon_url] = available

    return icon_url if available else None

def seti_language_icon_asset_path(
    language,
    mobile=False,
    light=False,
):
    if language == "No language data":
        return None

    stem = normalized_seti_icon_stem(language)

    if not stem:
        return None

    theme = "light" if light else "dark"
    viewport = "mobile" if mobile else "desktop"

    return (
        LANGUAGE_ASSETS_DIR
        / theme
        / viewport
        / f"{stem}.svg"
    )



def normalize_seti_icon_svg(svg_text, vertical_shift_px):
    match = re.search(
        r'\bviewBox="([^"]+)"',
        svg_text,
    )

    if not match:
        raise ValueError("Seti SVG is missing a viewBox.")

    values = match.group(1).split()

    if len(values) != 4:
        raise ValueError("Seti SVG has an invalid viewBox.")

    min_x, min_y, width, height = map(float, values)

    if height <= 0:
        raise ValueError("Seti SVG has an invalid viewBox height.")

    shift = (
        height
        * vertical_shift_px
        / SETI_ICON_RENDER_HEIGHT
    )

    adjusted_viewbox = " ".join(
        f"{value:g}"
        for value in (
            min_x,
            min_y + shift,
            width,
            height,
        )
    )

    return (
        svg_text[:match.start(1)]
        + adjusted_viewbox
        + svg_text[match.end(1):]
    )


def darken_seti_color(color):
    if not re.fullmatch(
        r"#[0-9A-Fa-f]{6}",
        color,
    ):
        raise ValueError(
            f"Invalid Seti color: {color}"
        )

    channels = [
        int(color[index:index + 2], 16)
        for index in (1, 3, 5)
    ]

    # Match VS Code's Seti generator:
    # Math.round(channel * 0.9).
    darkened = [
        int(channel * 0.9 + 0.5)
        for channel in channels
    ]

    return "#" + "".join(
        f"{channel:02x}"
        for channel in darkened
    )


def make_seti_light_svg(svg_text):
    return re.sub(
        r"#[0-9A-Fa-f]{6}\b",
        lambda match: darken_seti_color(
            match.group(0)
        ),
        svg_text,
    )


def write_seti_language_assets(items):
    LANGUAGE_ASSETS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    desired_paths = set()

    for item in items:
        language = primary_language(
            item["repository"]
        )

        asset_path = seti_language_icon_asset_path(
            language
        )
        mobile_asset_path = (
            seti_language_icon_asset_path(
                language,
                mobile=True,
            )
        )
        light_asset_path = (
            seti_language_icon_asset_path(
                language,
                light=True,
            )
        )
        mobile_light_asset_path = (
            seti_language_icon_asset_path(
                language,
                mobile=True,
                light=True,
            )
        )

        icon_url = seti_language_icon_url(language)

        asset_paths = (
            asset_path,
            mobile_asset_path,
            light_asset_path,
            mobile_light_asset_path,
        )

        if (
            any(path is None for path in asset_paths)
            or not icon_url
        ):
            continue

        desired_paths.update(asset_paths)

        request = urllib.request.Request(
            icon_url,
            headers={
                "User-Agent": (
                    f"{USERNAME}-profile-updater"
                ),
            },
            method="GET",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=10,
            ) as response:
                svg_text = response.read().decode(
                    "utf-8"
                )

            light_svg_text = make_seti_light_svg(
                svg_text
            )

            variants = (
                (
                    asset_path,
                    svg_text,
                    SETI_ICON_VERTICAL_SHIFT_PX,
                ),
                (
                    mobile_asset_path,
                    svg_text,
                    SETI_ICON_MOBILE_VERTICAL_SHIFT_PX,
                ),
                (
                    light_asset_path,
                    light_svg_text,
                    SETI_ICON_VERTICAL_SHIFT_PX,
                ),
                (
                    mobile_light_asset_path,
                    light_svg_text,
                    SETI_ICON_MOBILE_VERTICAL_SHIFT_PX,
                ),
            )

            normalized_variants = [
                (
                    path,
                    normalize_seti_icon_svg(
                        source,
                        vertical_shift,
                    ),
                )
                for path, source, vertical_shift
                in variants
            ]

        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            UnicodeDecodeError,
            ValueError,
        ):
            continue

        for path, normalized_svg in (
            normalized_variants
        ):
            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            path.write_text(
                normalized_svg.rstrip() + "\n",
                encoding="utf-8",
                newline="\n",
            )

    for asset_path in LANGUAGE_ASSETS_DIR.rglob(
        "*.svg"
    ):
        if asset_path not in desired_paths:
            asset_path.unlink()

    directories = sorted(
        (
            path
            for path in LANGUAGE_ASSETS_DIR.rglob("*")
            if path.is_dir()
        ),
        key=lambda path: len(path.parts),
        reverse=True,
    )

    for directory in directories:
        if not any(directory.iterdir()):
            directory.rmdir()



def render_language_metadata(language):
    escaped_language = escape(language)

    if language == "No language data":
        return escaped_language

    asset_path = seti_language_icon_asset_path(
        language
    )
    mobile_asset_path = (
        seti_language_icon_asset_path(
            language,
            mobile=True,
        )
    )
    light_asset_path = (
        seti_language_icon_asset_path(
            language,
            light=True,
        )
    )
    mobile_light_asset_path = (
        seti_language_icon_asset_path(
            language,
            mobile=True,
            light=True,
        )
    )

    asset_paths = (
        asset_path,
        mobile_asset_path,
        light_asset_path,
        mobile_light_asset_path,
    )

    def asset_src(path):
        relative = path.relative_to(
            LANGUAGE_ASSETS_DIR
        ).as_posix()

        return (
            "./assets/profile/generated/"
            f"languages/{relative}"
        )

    if (
        all(path is not None for path in asset_paths)
        and all(
            path.exists()
            for path in asset_paths
        )
    ):
        icon_src = asset_src(asset_path)
        mobile_icon_src = asset_src(
            mobile_asset_path
        )
        light_icon_src = asset_src(
            light_asset_path
        )
        mobile_light_icon_src = asset_src(
            mobile_light_asset_path
        )

        picture = (
            "<picture>"
            '<source media="'
            '(prefers-color-scheme: light) '
            'and (max-width: 600px)" '
            f'srcset="{mobile_light_icon_src}">'
            '<source media="'
            '(prefers-color-scheme: dark) '
            'and (max-width: 600px)" '
            f'srcset="{mobile_icon_src}">'
            '<source media="'
            '(prefers-color-scheme: light)" '
            f'srcset="{light_icon_src}">'
            '<source media="'
            '(prefers-color-scheme: dark)" '
            f'srcset="{icon_src}">'
            f'<img src="{icon_src}" alt="" '
            f'height="{SETI_ICON_RENDER_HEIGHT}" '
            'align="texttop">'
            "</picture>"
        )
    else:
        icon_src = (
            seti_language_icon_url(language)
            or "./assets/profile/icons/language_default.svg"
        )

        picture = (
            f'<picture><img src="{icon_src}" alt="" '
            f'height="{SETI_ICON_RENDER_HEIGHT}" '
            'align="texttop"></picture>'
        )

    query = urllib.parse.urlencode(
        {
            "tab": "repositories",
            "language": language.casefold(),
        }
    )
    url = f"https://github.com/{USERNAME}?{query}"

    return (
        f'<a href="{escape(url, quote=True)}">'
        f"{picture}{escaped_language}"
        "</a>"
    )




def render_building_now(items):
    if not items:
        return "*Nothing is actively being built in public right now.*"

    lines = []

    for item in items:
        repository = item["repository"]

        raw_description = repository["description"]

        if raw_description:
            description = (
                raw_description
                .replace("\r", " ")
                .replace("\n", " ")
                .strip()
            )
        else:
            description = "*No description.*"

        language = primary_language(repository)

        updated_at = (
            item["activity"].get(
                "latest_commit_at"
            )
        )

        metadata_parts = []

        if updated_at:
            metadata_parts.append(
                f"Updated {render_relative_time(updated_at)}"
            )

        metadata_parts.append(
            render_language_metadata(language)
        )

        metadata = " · ".join(metadata_parts)

        lines.append(
            f'- [**{repository["name"]}**]'
            f'({repository["url"]})'
            f' — {description}<br>\n'
            f'  <sub><blockquote>{metadata}'
            f'</blockquote></sub>'
        )

    return "\n".join(lines)


def collect_recent_releases(repositories):
    releases = []

    for repository in release_repositories(repositories):
        for release in repository["releases"]["nodes"]:
            if release["isDraft"] or not release["publishedAt"]:
                continue

            releases.append(
                {
                    "name": release["name"] or release["tagName"],
                    "tagName": release["tagName"],
                    "url": release["url"],
                    "repositoryUrl": repository["url"],
                    "publishedAt": release["publishedAt"],
                    "isPrerelease": release["isPrerelease"],
                    "isLatest": release["isLatest"],
                }
            )

    releases.sort(
        key=lambda release: parse_github_date(release["publishedAt"]),
        reverse=True,
    )

    return releases[:RECENT_RELEASE_LIMIT]

def render_recent_releases(releases):
    if not releases:
        return "*No published releases yet.*"

    def release_line(release):
        status = ""

        if release["isLatest"]:
            status = (
                ' [<img src="./assets/profile/icons/releases/latest.svg"'
                ' alt="Latest" height="24" align="absmiddle">]'
                f'({release["url"]})'
            )
        elif release["isPrerelease"]:
            status = (
                ' [<img src="./assets/profile/icons/releases/prerelease.svg"'
                ' alt="Pre-release" height="24" align="absmiddle">]'
                f'({release["url"]})'
            )

        released_text = (
            f'Released '
            f'{render_relative_time(release["publishedAt"])}'
        )

        tag_path = urllib.parse.quote(
            release["tagName"],
            safe="/",
        )
        tag_url = (
            f'{release["repositoryUrl"]}/tree/{tag_path}'
        )

        return (
            f'- [**{release["name"]}**]({release["url"]})'
            f'{status}<br>\n'
            f'  <sub><blockquote>{released_text} · '
            f'[<img src="./assets/profile/icons/releases/tag.svg" '
            f'alt="" height="18" align="texttop"> '
            f'{release["tagName"]}]'
            f'({tag_url})</blockquote></sub>'
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

def collect_owned_recent_commits(repositories):
    username = USERNAME.casefold()
    commits = []

    for repository in repositories:
        if repository.get("isPrivate", False):
            continue

        target = (
            (repository.get("defaultBranchRef") or {})
            .get("target")
            or {}
        )

        history = (
            (target.get("history") or {})
            .get("nodes")
            or []
        )

        for commit in history:
            author_user = (
                (commit.get("author") or {})
                .get("user")
                or {}
            )
            author_login = (
                author_user.get("login") or ""
            ).casefold()

            if author_login != username:
                continue

            authored_date = (
                commit.get("authoredDate")
                or commit.get("committedDate")
            )

            if not authored_date:
                continue

            commits.append(
                {
                    "repositoryName": repository["name"],
                    "repositoryUrl": repository["url"],
                    "oid": commit["oid"],
                    "url": commit["url"],
                    "messageHeadline": (
                        commit["messageHeadline"]
                        or commit["oid"]
                    ),
                    "messageBody": (
                        commit["messageBody"] or ""
                    ),
                    "committedDate": authored_date,
                }
            )

    return commits

def fetch_searched_recent_commits():
    payload = None

    for attempt in range(
        len(RECENT_COMMIT_SEARCH_RETRY_DELAYS) + 1
    ):
        payload = rest_json_request(
            SEARCH_COMMITS_URL,
            {
                "q": f"author:{USERNAME} is:public",
                "sort": "author-date",
                "order": "desc",
                "per_page": RECENT_COMMIT_SEARCH_LIMIT,
            },
        )

        if not payload.get("incomplete_results"):
            break

        if attempt == len(
            RECENT_COMMIT_SEARCH_RETRY_DELAYS
        ):
            print(
                "Warning: GitHub commit search remained "
                "incomplete; preserving Recent commits."
            )
            return None

        time.sleep(
            RECENT_COMMIT_SEARCH_RETRY_DELAYS[attempt]
        )

    username = USERNAME.casefold()

    commits = []
    seen_oids = set()

    for item in payload.get("items") or []:
        repository = item.get("repository") or {}
        full_name = repository.get("full_name") or ""

        if not full_name:
            continue

        if repository.get("private"):
            continue

        author = item.get("author") or {}
        author_login = (
            author.get("login") or ""
        ).casefold()

        if author_login != username:
            continue

        oid = item.get("sha") or ""

        if not oid or oid in seen_oids:
            continue

        commit_data = item.get("commit") or {}

        message = (
            commit_data.get("message") or ""
        ).replace("\r\n", "\n").replace("\r", "\n").strip()

        headline, separator, body = message.partition("\n")

        committed_date = (
            (commit_data.get("author") or {})
            .get("date")
            or
            (commit_data.get("committer") or {})
            .get("date")
        )

        commit_url = item.get("html_url")
        repository_url = repository.get("html_url")

        if (
            not committed_date
            or not commit_url
            or not repository_url
        ):
            continue

        owner_login = (
            (repository.get("owner") or {})
            .get("login")
            or ""
        )

        repository_name = (
            repository.get("name")
            or full_name
        )

        if owner_login.casefold() != username:
            repository_name = full_name

        commits.append(
            {
                "repositoryName": repository_name,
                "repositoryUrl": repository_url,
                "oid": oid,
                "url": commit_url,
                "messageHeadline": headline.strip() or oid,
                "messageBody": (
                    body.strip()
                    if separator
                    else ""
                ),
                "committedDate": committed_date,
            }
        )

        seen_oids.add(oid)

        if len(commits) >= RECENT_COMMIT_LIMIT:
            break

    return commits

def collect_recent_commits(repositories):
    searched_commits = fetch_searched_recent_commits()

    if searched_commits is None:
        return None

    commits_by_oid = {
        commit["oid"]: commit
        for commit in searched_commits
    }

    # Prefer GraphQL data for repositories owned by USERNAME,
    # including forks, because it is available immediately after a
    # push, before Commit Search necessarily finishes indexing it.
    for commit in collect_owned_recent_commits(repositories):
        commits_by_oid[commit["oid"]] = commit

    commits = sorted(
        commits_by_oid.values(),
        key=lambda commit: parse_github_date(
            commit["committedDate"]
        ),
        reverse=True,
    )

    return commits[:RECENT_COMMIT_LIMIT]

def render_recent_commits(commits):
    if not commits:
        return "*No authored commits found.*"

    lines = []

    for commit in commits:
        repository_name = escape(
            commit["repositoryName"]
        )
        headline = escape(
            (commit["messageHeadline"] or commit["oid"])
            .strip()
        )
        short_oid = commit["oid"][:7]

        lines.append(
            f'- [**{repository_name}**]'
            f'({commit["repositoryUrl"]})'
            f' — [{headline}]({commit["url"]})<br>\n'
            f'  <sub><blockquote>'
            f'Committed '
            f'{render_relative_time(commit["committedDate"])}'
            f' · [<img src="./assets/profile/icons/commit.svg" '
            f'alt="" height="18" align="texttop"> '
            f'{short_oid}]({commit["url"]})'
            f'</blockquote></sub>'
        )

        body = (commit["messageBody"] or "").strip()

        if body:
            body_html = (
                escape(body)
                .replace("\r", "")
                .replace("\n", "<br>")
            )

            lines.append(
                '  <details>\n'
                '  <summary>Details</summary>\n'
                f'  <p>{body_html}</p>\n'
                '  </details>'
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
    snapshot_profile,
    languages,
    building_now,
    recent_commits,
    snapshot_mode,
):
    repositories = profile["repositories"]

    if not README_PATH.exists():
        return

    content = README_PATH.read_text(encoding="utf-8")

    snapshot = render_snapshot_readme(
        snapshot_profile,
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

    commits_updated = False

    if recent_commits is not None:
        content, commits_updated = replace_marked_block(
            content,
            "recent_commits",
            render_recent_commits(recent_commits),
        )

    if (
        snapshot_updated
        or building_updated
        or releases_updated
        or commits_updated
    ):
        README_PATH.write_text(
            content,
            encoding="utf-8",
            newline="\n",
        )

def main():
    config = load_profile_config(
        REPO_ROOT
    )
    snapshot_mode = config["snapshot_mode"]
    contribution_forks = config[
        "contribution_forks"
    ]

    profile = fetch_profile_data()
    repositories = profile["repositories"]
    snapshot_profile = build_snapshot_profile(
        profile,
        contribution_forks,
    )
    languages = aggregate_languages(
        snapshot_profile["repositories"]
    )
    building_now = collect_building_now(repositories)
    recent_commits = collect_recent_commits(repositories)

    PROFILE_ASSETS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_seti_language_assets(building_now)

    SNAPSHOT_ASSETS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    (SNAPSHOT_ASSETS_DIR / "desktop.svg").write_text(
        render_snapshot_svg(
            snapshot_profile,
            languages,
        ),
        encoding="utf-8",
        newline="\n",
    )

    (SNAPSHOT_ASSETS_DIR / "mobile.svg").write_text(
        render_snapshot_svg(
            snapshot_profile,
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
        snapshot_profile,
        languages,
        building_now,
        recent_commits,
        snapshot_mode,
    )

    print("Updated profile assets.")
    print(f"Snapshot mode: {snapshot_mode}")
    print("Repository data loaded.")
    print(f"Languages: {len(languages)}")
    print(f"Building now: {len(building_now)}")
    if recent_commits is None:
        print("Recent commits: preserved")
    else:
        print(f"Recent commits: {len(recent_commits)}")

if __name__ == "__main__":
    main()
