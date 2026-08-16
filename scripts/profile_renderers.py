
from html import escape
import json
from pathlib import Path


DEFAULT_SNAPSHOT_MODE = "full_svg"

SUPPORTED_SNAPSHOT_MODES = {
    "full_svg",
    "native_table_hybrid",
}


def load_snapshot_mode(repo_root):
    config_path = (
        Path(repo_root)
        / "profile_renderer.json"
    )

    if not config_path.exists():
        return DEFAULT_SNAPSHOT_MODE

    try:
        config = json.loads(
            config_path.read_text(
                encoding="utf-8"
            )
        )
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Invalid profile_renderer.json: "
            f"{error}"
        ) from error

    if not isinstance(config, dict):
        raise RuntimeError(
            "profile_renderer.json must "
            "contain a JSON object."
        )

    snapshot_mode = config.get(
        "snapshot_mode",
        DEFAULT_SNAPSHOT_MODE,
    )

    if snapshot_mode not in SUPPORTED_SNAPSHOT_MODES:
        supported = ", ".join(
            sorted(SUPPORTED_SNAPSHOT_MODES)
        )

        raise RuntimeError(
            f"Unsupported snapshot_mode: "
            f"{snapshot_mode!r}. "
            f"Expected one of: {supported}."
        )

    return snapshot_mode


def render_bar_svg(languages):
    top_languages = languages[:5]

    total_bytes = sum(
        language["bytes"]
        for language in languages
    )

    bar_width = 330.0
    bar_x = 0.0
    segments = []

    if total_bytes:
        for language in top_languages:
            width = (
                bar_width
                * language["bytes"]
                / total_bytes
            )

            segments.append(
                f'        <rect '
                f'x="{bar_x:.2f}" '
                f'y="0" '
                f'width="{width:.2f}" '
                f'height="10" '
                f'fill="{escape(language["color"].lower())}" />'
            )

            bar_x += width

    segments_markup = "\n".join(
        segments
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="330" height="10" viewBox="0 0 330 10" role="img" aria-label="Language distribution">
    <style>
        .track {{
            fill: #59636e;
            fill-opacity: 0.12;
        }}

        @media (prefers-color-scheme: dark) {{
            .track {{
                fill: #9198a1;
                fill-opacity: 0.18;
            }}
        }}
    </style>

    <defs>
        <clipPath id="bar-clip">
            <rect x="0" y="0" width="330" height="10" rx="5" />
        </clipPath>
    </defs>

    <rect class="track" x="0" y="0" width="330" height="10" rx="5" />

    <g clip-path="url(#bar-clip)">
{segments_markup}
    </g>
</svg>
'''


def render_dot_svg(color):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="8" height="16" viewBox="0 0 8 16" role="presentation" aria-hidden="true">
    <circle cx="4" cy="10" r="4" fill="{escape(color.lower())}" />
</svg>
'''


def render_spacer_svg(width, height):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="presentation" aria-hidden="true">
    <rect width="{width}" height="{height}" fill="transparent" />
</svg>
'''


def write_native_table_hybrid_assets(
    profile_assets_dir,
    languages,
):
    hybrid_dir = (
        Path(profile_assets_dir)
        / "native_table_hybrid"
    )

    hybrid_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        hybrid_dir
        / "languages_bar.svg"
    ).write_text(
        render_bar_svg(languages),
        encoding="utf-8",
        newline="\n",
    )

    (
        hybrid_dir
        / "card_width.svg"
    ).write_text(
        render_spacer_svg(
            330,
            1,
        ),
        encoding="utf-8",
        newline="\n",
    )

    (
        hybrid_dir
        / "card_height.svg"
    ).write_text(
        render_spacer_svg(
            1,
            20,
        ),
        encoding="utf-8",
        newline="\n",
    )

    for dot_path in hybrid_dir.glob(
        "dot-*.svg"
    ):
        dot_path.unlink()

    for index, language in enumerate(
        languages[:5],
        start=1,
    ):
        (
            hybrid_dir
            / f"dot-{index}.svg"
        ).write_text(
            render_dot_svg(
                language["color"]
            ),
            encoding="utf-8",
            newline="\n",
        )


def format_number(value):
    return f"{value:,}"


def render_native_table_hybrid(
    profile,
    languages,
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

    top_languages = languages[:5]

    total_bytes = sum(
        language["bytes"]
        for language in languages
    )

    if top_languages and total_bytes:
        names = []
        percentages = []

        for index, language in enumerate(
            top_languages,
            start=1,
        ):
            percentage = (
                language["bytes"]
                / total_bytes
                * 100
            )

            names.append(
                '<img '
                'src="./assets/profile/'
                'native_table_hybrid/'
                f'dot-{index}.svg" '
                'width="8" height="16" '
                'alt=""> '
                f'{escape(language["name"])}'
            )

            percentages.append(
                f"{percentage:.1f}%"
            )

        names_markup = (
            "<br>\n      ".join(names)
        )

        percentages_markup = (
            "<br>\n      ".join(
                percentages
            )
        )

        languages_row = f'''  <tr>
    <td width="285" align="left" valign="top">
      {names_markup}
    </td>
    <td width="65" align="right" valign="top">
      {percentages_markup}
    </td>
  </tr>'''

    else:
        languages_row = '''  <tr>
    <td colspan="2" align="left">
      No language data available yet.
    </td>
  </tr>'''

    return f'''<table align="left" width="370">
  <tr>
    <td colspan="2" align="left" valign="middle">
      <h3>GitHub overview</h3>
      <img src="./assets/profile/native_table_hybrid/card_width.svg" width="330" height="1" alt="">
    </td>
  </tr>
  <tr>
    <td width="185" align="center" valign="middle">
      <h2>{escape(format_number(total_stars))}</h2>
      Total stars<br>
      <img src="./assets/profile/native_table_hybrid/card_height.svg" width="1" height="20" alt="">
    </td>
    <td width="185" align="center" valign="middle">
      <h2>{escape(format_number(total_releases))}</h2>
      Total releases<br>
      <img src="./assets/profile/native_table_hybrid/card_height.svg" width="1" height="20" alt="">
    </td>
  </tr>
</table>

<table align="right" width="370">
  <tr>
    <td colspan="2" align="left" valign="middle">
      <h3>Languages</h3>
      <img src="./assets/profile/native_table_hybrid/languages_bar.svg" width="330" height="10" alt="Language distribution">
    </td>
  </tr>
{languages_row}
</table>

<br clear="all">'''


def render_snapshot_readme(
    profile,
    languages,
    snapshot_mode,
):
    if snapshot_mode == "full_svg":
        return '''<p align="center">
  <picture>
    <source media="(max-width: 600px)" srcset="./assets/profile/snapshot-mobile.svg">
    <img src="./assets/profile/snapshot.svg" width="100%" alt="GitHub overview and languages">
  </picture>
</p>'''

    if snapshot_mode == "native_table_hybrid":
        return render_native_table_hybrid(
            profile,
            languages,
        )

    raise RuntimeError(
        f"Unsupported snapshot mode: "
        f"{snapshot_mode!r}"
    )
