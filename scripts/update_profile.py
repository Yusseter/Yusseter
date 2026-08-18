from collections import defaultdict
from datetime import datetime, timedelta, timezone
from html import escape
import json
import os
import re
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

from profile_renderers import (
    load_snapshot_mode,
    render_snapshot_readme,
    write_native_table_hybrid_assets,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

PROFILE_ASSETS_DIR = REPO_ROOT / "assets" / "profile"
LANGUAGE_ASSETS_DIR = PROFILE_ASSETS_DIR / "languages"
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
RECENT_COMMIT_LIMIT = 5
RECENT_COMMIT_SEARCH_LIMIT = 50

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
                            committedDate
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

def rest_json_request(url, params=None):
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN is not set.")

    if params:
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}"

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
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode(
            "utf-8",
            errors="replace",
        )
        raise RuntimeError(
            f"GitHub REST request failed with HTTP "
            f"{error.code}: {body}"
        ) from error

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

def github_time_label(value, now=None):
    timestamp = parse_github_date(value)
    current = now or datetime.now(timezone.utc)

    elapsed_seconds = max(
        int((current - timestamp).total_seconds()),
        0,
    )

    # GitHub's relative-time element switches to an absolute
    # date at its default 30-day threshold.
    if elapsed_seconds >= 30 * 24 * 60 * 60:
        months = (
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        )

        absolute = (
            f"{months[timestamp.month - 1]} "
            f"{timestamp.day}"
        )

        if timestamp.year != current.year:
            absolute += f", {timestamp.year}"

        return absolute

    # GitHub displays very recent timestamps as "now",
    # then keeps second-level precision until 55 seconds.
    if elapsed_seconds < 10:
        return "now"

    if elapsed_seconds < 55:
        return f"{elapsed_seconds} seconds ago"

    seconds = elapsed_seconds % 60
    minutes = elapsed_seconds // 60

    if seconds >= 55:
        minutes += 1

    if minutes < 55:
        unit = "minute" if minutes == 1 else "minutes"
        return f"{minutes} {unit} ago"

    # Minutes round into hours at 55 minutes.
    minute_remainder = minutes % 60
    hours = minutes // 60

    if minute_remainder >= 55:
        hours += 1

    if hours < 21:
        unit = "hour" if hours == 1 else "hours"
        return f"{hours} {unit} ago"

    # Around 21 hours GitHub begins using day-level wording.
    days = hours // 24
    hour_remainder = hours % 24

    if days == 0:
        days = 1
    elif hour_remainder >= 12:
        days += 1

    if days == 1:
        return "yesterday"

    if days < 6:
        return f"{days} days ago"

    # Around six days GitHub rounds to weeks.
    weeks = (days + 3) // 7

    # Four rounded weeks become "last month" while the
    # timestamp is still inside the 30-day relative window.
    if weeks >= 4:
        return "last month"

    if weeks == 1:
        return "last week"

    return f"{weeks} weeks ago"

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

def seti_language_icon_asset_path(language, mobile=False):
    if language == "No language data":
        return None

    stem = normalized_seti_icon_stem(language)

    if not stem:
        return None

    suffix = "-mobile" if mobile else ""

    return LANGUAGE_ASSETS_DIR / f"{stem}{suffix}.svg"

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

def write_seti_language_assets(items):
    LANGUAGE_ASSETS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    desired_names = set()

    for item in items:
        language = primary_language(item["repository"])
        asset_path = seti_language_icon_asset_path(language)
        mobile_asset_path = seti_language_icon_asset_path(
            language,
            mobile=True,
        )
        icon_url = seti_language_icon_url(language)

        if not asset_path or not mobile_asset_path or not icon_url:
            continue

        desired_names.add(asset_path.name)
        desired_names.add(mobile_asset_path.name)

        request = urllib.request.Request(
            icon_url,
            headers={
                "User-Agent": f"{USERNAME}-profile-updater",
            },
            method="GET",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=10,
            ) as response:
                svg_text = response.read().decode("utf-8")

            normalized_svg = normalize_seti_icon_svg(
                svg_text,
                SETI_ICON_VERTICAL_SHIFT_PX,
            )
            mobile_normalized_svg = normalize_seti_icon_svg(
                svg_text,
                SETI_ICON_MOBILE_VERTICAL_SHIFT_PX,
            )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            UnicodeDecodeError,
            ValueError,
        ):
            continue

        asset_path.write_text(
            normalized_svg.rstrip() + "\n",
            encoding="utf-8",
            newline="\n",
        )
        mobile_asset_path.write_text(
            mobile_normalized_svg.rstrip() + "\n",
            encoding="utf-8",
            newline="\n",
        )

    for asset_path in LANGUAGE_ASSETS_DIR.glob("*.svg"):
        if asset_path.name not in desired_names:
            asset_path.unlink()

def render_language_metadata(language):
    escaped_language = escape(language)

    if language == "No language data":
        return escaped_language

    asset_path = seti_language_icon_asset_path(language)
    mobile_asset_path = seti_language_icon_asset_path(
        language,
        mobile=True,
    )

    if (
        asset_path
        and mobile_asset_path
        and asset_path.exists()
        and mobile_asset_path.exists()
    ):
        icon_src = (
            "./assets/profile/languages/"
            f"{asset_path.name}"
        )
        mobile_icon_src = (
            "./assets/profile/languages/"
            f"{mobile_asset_path.name}"
        )

        picture = (
            '<picture>'
            f'<source media="(max-width: 600px)" '
            f'srcset="{mobile_icon_src}">'
            f'<img src="{icon_src}" alt="" '
            f'height="{SETI_ICON_RENDER_HEIGHT}" '
            f'align="texttop">'
            '</picture>'
        )
    else:
        icon_src = (
            seti_language_icon_url(language)
            or "./assets/profile/language-default.svg"
        )
        picture = (
            f'<picture><img src="{icon_src}" alt="" '
            f'height="{SETI_ICON_RENDER_HEIGHT}" '
            f'align="texttop"></picture>'
        )

    return picture + escaped_language

def render_building_now(items):
    if not items:
        return "*Nothing is actively being built in public right now.*"

    lines = []
    now = datetime.now(timezone.utc)

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

        target = (
            (repository.get("defaultBranchRef") or {})
            .get("target")
            or {}
        )

        updated_at = target.get("committedDate")

        metadata_parts = []

        if updated_at:
            metadata_parts.append(
                f"Updated {github_time_label(updated_at, now)}"
            )

        metadata_parts.append(
            render_language_metadata(language)
        )

        metadata = " · ".join(metadata_parts)

        lines.append(
            f'- [**{repository["name"]}**]({repository["url"]})'
            f' — {description}<br>\n'
            f'  <sub><blockquote>{metadata}</blockquote></sub>'
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

    now = datetime.now(timezone.utc)

    def release_line(release):
        status = ""

        if release["isLatest"]:
            status = (
                ' [<img src="./assets/profile/release-latest.svg"'
                ' alt="Latest" height="24" align="absmiddle">]'
                f'({release["url"]})'
            )
        elif release["isPrerelease"]:
            status = (
                ' [<img src="./assets/profile/release-prerelease.svg"'
                ' alt="Pre-release" height="24" align="absmiddle">]'
                f'({release["url"]})'
            )

        time_label = github_time_label(
            release["publishedAt"],
            now,
        )

        released_text = f"Released this {time_label}"

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
            f'[<img src="./assets/profile/release-tag.svg" '
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

def fetch_recent_commits():
    payload = rest_json_request(
        SEARCH_COMMITS_URL,
        {
            "q": f"author:{USERNAME} is:public",
            "sort": "author-date",
            "order": "desc",
            "per_page": RECENT_COMMIT_SEARCH_LIMIT,
        },
    )

    if payload.get("incomplete_results"):
        raise RuntimeError(
            "GitHub commit search returned incomplete results."
        )

    username = USERNAME.casefold()
    placeholder_full_name = (
        f"{USERNAME}/Placeholder"
    ).casefold()

    commits = []
    seen_oids = set()

    for item in payload.get("items") or []:
        repository = item.get("repository") or {}
        full_name = repository.get("full_name") or ""

        if not full_name:
            continue

        if full_name.casefold() == placeholder_full_name:
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

def render_recent_commits(commits):
    if not commits:
        return "*No authored commits found.*"

    now = datetime.now(timezone.utc)
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
            f'{github_time_label(commit["committedDate"], now)}'
            f' · [{short_oid}]({commit["url"]})'
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
                '  <summary>Commit description</summary>\n'
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
    snapshot_mode = load_snapshot_mode(
        REPO_ROOT
    )

    profile = fetch_profile_data()
    repositories = profile["repositories"]
    languages = aggregate_languages(repositories)
    building_now = collect_building_now(repositories)
    recent_commits = fetch_recent_commits()

    PROFILE_ASSETS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_seti_language_assets(building_now)

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
        recent_commits,
        snapshot_mode,
    )

    print("Updated profile assets.")
    print(f"Snapshot mode: {snapshot_mode}")
    print(f"Repositories: {len(repositories)}")
    print(f"Languages: {len(languages)}")
    print(f"Building now: {len(building_now)}")
    print(f"Recent commits: {len(recent_commits)}")

if __name__ == "__main__":
    main()
