from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import xml.etree.ElementTree as ET

from PIL import Image


# ---------------------------------------------------------------------------
# Export configuration
# ---------------------------------------------------------------------------

BACKGROUND_ASPECT_RATIO = (16, 9)
BACKGROUND_BASE_WIDTH = 1920
BACKGROUND_WIDTHS = [1920, 2560, 3840, 5120]

LOGO_ASPECT_RATIO = (1, 1)
LOGO_WIDTHS = [256, 512, 1024]

# Local runs skip PNGs that are newer than their source SVG.
# CI forces regeneration when visual assets change.
FORCE_PNG_EXPORT = os.environ.get("FORCE_PNG_EXPORT") == "1"
SKIP_UP_TO_DATE = not FORCE_PNG_EXPORT

REPO_ROOT = Path(__file__).resolve().parent.parent

BACKGROUNDS_SVG_DIR = REPO_ROOT / "assets" / "backgrounds" / "svg"
BACKGROUNDS_PNG_DIR = REPO_ROOT / "assets" / "backgrounds" / "png"

LOGOS_SVG_DIR = REPO_ROOT / "assets" / "logos" / "svg"
LOGOS_PNG_DIR = REPO_ROOT / "assets" / "logos" / "png"

PROFILE_DIR = REPO_ROOT / "assets" / "profile"

CANONICAL_LOGO_SOURCE = (
    LOGOS_SVG_DIR / "hittite_sun_disk_golden_crescent.svg"
)

REVERSED_LOGO_SOURCE = (
    LOGOS_SVG_DIR
    / "hittite_sun_disk_golden_crescent-reversed.svg"
)

BACKGROUND_SOURCE = (
    BACKGROUNDS_SVG_DIR / "eagle_background.svg"
)

HEADER_DIR = PROFILE_DIR / "header"

WINDOWS_INKSCAPE = Path(
    r"C:\Program Files\Inkscape\bin\inkscape.com"
)

created_count = 0
skipped_count = 0
error_count = 0


# ---------------------------------------------------------------------------
# SVG synchronization
# ---------------------------------------------------------------------------

# The primary logo is the canonical source for the emblem.
#
# These definition IDs are renamed inside embedded copies so that they
# remain compatible with the existing eagle/header SVG structure.
EMBEDDED_ID_MAP = {
    "golden-crescent-gradient":
        "emblem-golden-crescent-gradient",

    "hittite-disk-clip":
        "emblem-hittite-disk-clip",
}

DEFINITION_ELEMENTS = (
    (
        "radialGradient",
        "golden-crescent-gradient",
        True,
    ),

    (
        "clipPath",
        "hittite-disk-clip",
        True,
    ),
)

EMBLEM_ELEMENTS = (
    (
        "circle",
        "golden-crescent-base",
        False,
    ),
    (
        "circle",
        "hittite-disk-outer",
        False,
    ),
    (
        "circle",
        "hittite-disk-inner",
        False,
    ),
    (
        "g",
        "hittite-disk-pattern",
        True,
    ),
)


def read_text(path):
    return (
        path.read_text(encoding="utf-8")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )


def write_text(path, text):
    # Write LF and UTF-8 without BOM on every platform.
    path.write_bytes(text.encode("utf-8"))


def element_pattern(tag, element_id, container):
    escaped_tag = re.escape(tag)
    escaped_id = re.escape(element_id)

    if container:
        return re.compile(
            rf'(?ms)'
            rf'^(?P<indent>[ \t]*)'
            rf'<{escaped_tag}\b'
            rf'(?=[^>\n]*\bid="{escaped_id}")'
            rf'[^>]*>'
            rf'.*?'
            rf'^[ \t]*</{escaped_tag}>'
        )

    return re.compile(
        rf'(?m)'
        rf'^(?P<indent>[ \t]*)'
        rf'<{escaped_tag}\b'
        rf'(?=[^>\n]*\bid="{escaped_id}")'
        rf'[^>]*?/>'
    )


def extract_element(text, tag, element_id, container):
    match = element_pattern(
        tag,
        element_id,
        container,
    ).search(text)

    if not match:
        raise ValueError(
            f"Could not find SVG element: "
            f"<{tag} id=\"{element_id}\">"
        )

    return textwrap.dedent(
        match.group(0)
    ).strip()


def reindent(fragment, indent):
    lines = (
        textwrap.dedent(fragment)
        .strip()
        .splitlines()
    )

    return "\n".join(
        indent + line if line else ""
        for line in lines
    )


def replace_element(
    text,
    tag,
    element_id,
    container,
    replacement,
):
    pattern = element_pattern(
        tag,
        element_id,
        container,
    )

    match = pattern.search(text)

    if not match:
        raise ValueError(
            f"Could not replace SVG element: "
            f"<{tag} id=\"{element_id}\">"
        )

    replacement = reindent(
        replacement,
        match.group("indent"),
    )

    return (
        text[:match.start()]
        + replacement
        + text[match.end():]
    )


def remap_embedded_ids(fragment):
    for source_id, target_id in EMBEDDED_ID_MAP.items():
        fragment = fragment.replace(
            f'id="{source_id}"',
            f'id="{target_id}"',
        )

        fragment = fragment.replace(
            f'url(#{source_id})',
            f'url(#{target_id})',
        )

        fragment = fragment.replace(
            f'href="#{source_id}"',
            f'href="#{target_id}"',
        )

    return fragment


def element_fill(
    text,
    tag,
    element_id,
    container=False,
):
    fragment = extract_element(
        text,
        tag,
        element_id,
        container,
    )

    match = re.search(
        r'\bfill="(#[0-9a-fA-F]{6})"',
        fragment,
    )

    if not match:
        raise ValueError(
            f"Could not read fill color from: {element_id}"
        )

    return match.group(1).lower()


def header_background_color(text):
    match = re.search(
        r'\.header-background\s*\{'
        r'[^}]*?'
        r'\bfill:\s*'
        r'(#[0-9a-fA-F]{6})'
        r'\s*;',
        text,
        flags=re.DOTALL,
    )

    if not match:
        raise ValueError(
            "Could not read header background color."
        )

    return match.group(1).lower()


def replace_color(text, old_color, new_color):
    if old_color.lower() == new_color.lower():
        return text

    return re.sub(
        re.escape(old_color),
        new_color,
        text,
        flags=re.IGNORECASE,
    )


def swap_brand_colors(
    fragment,
    canonical_plum,
    canonical_background,
):
    plum_token = "__CANONICAL_PLUM__"
    background_token = "__CANONICAL_BACKGROUND__"

    fragment = re.sub(
        re.escape(canonical_plum),
        plum_token,
        fragment,
        flags=re.IGNORECASE,
    )

    fragment = re.sub(
        re.escape(canonical_background),
        background_token,
        fragment,
        flags=re.IGNORECASE,
    )

    fragment = fragment.replace(
        plum_token,
        canonical_background,
    )

    fragment = fragment.replace(
        background_token,
        canonical_plum,
    )

    return fragment


def validate_svg_text(text, path):
    try:
        ET.fromstring(text)
    except ET.ParseError as error:
        raise ValueError(
            f"Invalid generated SVG for {path}: {error}"
        ) from error


def sync_reversed_logo(
    canonical_text,
    canonical_plum,
    canonical_background,
):
    target_text = read_text(
        REVERSED_LOGO_SOURCE
    )

    updated = target_text

    # Keep the reversed palette tied to the canonical palette:
    # canonical plum -> reversed background
    # canonical background -> reversed foreground
    old_reversed_plum = element_fill(
        target_text,
        "circle",
        "hittite-disk-inner",
    )

    old_reversed_light = element_fill(
        target_text,
        "circle",
        "hittite-disk-outer",
    )

    updated = replace_color(
        updated,
        old_reversed_plum,
        canonical_plum,
    )

    updated = replace_color(
        updated,
        old_reversed_light,
        canonical_background,
    )

    # Gradient remains identical to the canonical logo.
    gradient = extract_element(
        canonical_text,
        "radialGradient",
        "golden-crescent-gradient",
        True,
    )

    updated = replace_element(
        updated,
        "radialGradient",
        "golden-crescent-gradient",
        True,
        gradient,
    )

    clip = extract_element(
        canonical_text,
        "clipPath",
        "hittite-disk-clip",
        True,
    )

    updated = replace_element(
        updated,
        "clipPath",
        "hittite-disk-clip",
        True,
        clip,
    )

    for tag, element_id, container in EMBLEM_ELEMENTS:
        fragment = extract_element(
            canonical_text,
            tag,
            element_id,
            container,
        )

        # The gold crescent itself keeps the canonical gradient.
        if element_id != "golden-crescent-base":
            fragment = swap_brand_colors(
                fragment,
                canonical_plum,
                canonical_background,
            )

        updated = replace_element(
            updated,
            tag,
            element_id,
            container,
            fragment,
        )

    validate_svg_text(
        updated,
        REVERSED_LOGO_SOURCE,
    )

    if updated != target_text:
        write_text(
            REVERSED_LOGO_SOURCE,
            updated,
        )

        print(
            "Synced: "
            f"{REVERSED_LOGO_SOURCE.relative_to(REPO_ROOT)}"
        )
    else:
        print(
            "Already synced: "
            f"{REVERSED_LOGO_SOURCE.relative_to(REPO_ROOT)}"
        )



def validate_detailed_outline(canonical_text, target_path):
    canonical = ET.fromstring(canonical_text)
    target = ET.parse(target_path).getroot()

    def by_id(root, value):
        return next(
            (e for e in root.iter() if e.get("id") == value),
            None,
        )

    def shape(element):
        if element is None:
            raise ValueError("Missing Hittite geometry.")

        return (
            element.tag.rsplit("}", 1)[-1],
            tuple(sorted(
                (k, v)
                for k, v in element.attrib.items()
                if k not in ("id", "fill", "clip-path")
            )),
            tuple(shape(child) for child in element),
        )

    if by_id(target, "hittite-disk-pattern-outline") is None:
        raise ValueError(
            "Detailed Hittite outline layer is missing."
        )

    for element_id in (
        "golden-crescent-base",
        "hittite-disk-outer",
        "hittite-disk-inner",
        "hittite-disk-pattern",
    ):
        if shape(by_id(canonical, element_id)) != shape(
            by_id(target, element_id)
        ):
            raise ValueError(
                "Detailed Hittite outline requires regeneration: "
                f"{element_id} geometry changed."
            )

    if shape(
        by_id(canonical, "hittite-disk-clip")
    ) != shape(
        by_id(target, "emblem-hittite-disk-clip")
    ):
        raise ValueError(
            "Detailed Hittite outline requires regeneration: "
            "clip geometry changed."
        )

    original_gradient = by_id(
        canonical, "golden-crescent-gradient"
    )
    outline_gradient = by_id(
        target, "hittite-outline-gradient"
    )

    if original_gradient is None or outline_gradient is None:
        raise ValueError("Missing Hittite outline gradient.")

    def stops(element):
        return [
            (child.get("offset"), child.get("stop-color"))
            for child in element
        ]

    if stops(original_gradient) != stops(outline_gradient):
        raise ValueError(
            "Detailed Hittite outline gradient requires review "
            "after canonical gradient changes."
        )


def sync_embedded_logo(
    target_path,
    canonical_text,
    canonical_plum,
    canonical_background,
    preserve_detailed_outline=False,
):
    target_text = read_text(target_path)
    updated = target_text

    # Keep the branded background and plum palette synchronized
    # with the canonical logo.
    old_plum = element_fill(
        target_text,
        "circle",
        "hittite-disk-outer",
    )

    if target_path.parent == HEADER_DIR:
        old_background = header_background_color(
            target_text
        )
    else:
        old_background = element_fill(
            target_text,
            "rect",
            "background",
        )

    updated = replace_color(
        updated,
        old_plum,
        canonical_plum,
    )

    updated = replace_color(
        updated,
        old_background,
        canonical_background,
    )

    # Synchronize definitions.
    for (
        tag,
        canonical_id,
        container,
    ) in DEFINITION_ELEMENTS:
        fragment = extract_element(
            canonical_text,
            tag,
            canonical_id,
            container,
        )

        fragment = remap_embedded_ids(
            fragment
        )

        target_id = EMBEDDED_ID_MAP[
            canonical_id
        ]

        updated = replace_element(
            updated,
            tag,
            target_id,
            container,
            fragment,
        )

    # Synchronize the visible emblem geometry.
    for (
        tag,
        element_id,
        container,
    ) in EMBLEM_ELEMENTS:
        if (
            preserve_detailed_outline
            and element_id == "hittite-disk-pattern"
        ):
            continue

        fragment = extract_element(
            canonical_text,
            tag,
            element_id,
            container,
        )

        fragment = remap_embedded_ids(
            fragment
        )

        updated = replace_element(
            updated,
            tag,
            element_id,
            container,
            fragment,
        )

    validate_svg_text(
        updated,
        target_path,
    )

    if updated != target_text:
        write_text(
            target_path,
            updated,
        )

        print(
            "Synced: "
            f"{target_path.relative_to(REPO_ROOT)}"
        )
    else:
        print(
            "Already synced: "
            f"{target_path.relative_to(REPO_ROOT)}"
        )


# Keep source SVGs independent from the one active profile header.
SUPPORTED_HEADER_BACKGROUNDS = (
    "eagle_background.svg",
    "eagle_background-outlined.svg",
    "eagle_background-outlined-minimal.svg",
)


def load_header_settings():
    config_path = REPO_ROOT / "profile_config.json"
    if not config_path.exists():
        return BACKGROUND_SOURCE, True

    config = json.loads(read_text(config_path))
    if not isinstance(config, dict):
        raise ValueError("profile_config.json must be an object.")

    header = config.get("header", {})
    if not isinstance(header, dict):
        raise ValueError("profile_config.json: header must be an object.")

    name = header.get("background_svg", "eagle_background.svg")
    rules = header.get("side_rules", True)

    if name not in SUPPORTED_HEADER_BACKGROUNDS:
        raise ValueError(f"Unsupported header background_svg: {name!r}")
    if type(rules) is not bool:
        raise ValueError("header.side_rules must be true or false.")

    return BACKGROUNDS_SVG_DIR / name, rules


def unique_match(pattern, text, label):
    matches = list(re.finditer(pattern, text, flags=re.DOTALL))
    if len(matches) != 1:
        raise ValueError(f"{label}: expected 1 match, found {len(matches)}")
    return matches[0]


def group_span(text, element_id):
    opening = unique_match(
        r'<g\b(?=[^>]*\bid="' + re.escape(element_id)
        + r'")[^>]*>',
        text,
        element_id,
    )
    depth = 0
    for tag in re.finditer(r'</?g(?=[\s>])[^>]*>', text[opening.start():]):
        token = tag.group(0)
        if token.startswith('</g'):
            depth -= 1
        elif not token.endswith('/>'):
            depth += 1
        if depth == 0:
            return opening.start(), opening.start() + tag.end()
    raise ValueError(f"Unclosed SVG group: {element_id}")


def compose_header(target_path, source_path, side_rules,
                   canonical_plum, canonical_background):
    current = read_text(target_path)
    source = read_text(source_path)

    # Preserve existing header-only CSS, frame, positioning and sizes.
    old_plum = element_fill(
        current, "circle", "hittite-disk-outer"
    )
    old_background = header_background_color(current)
    updated = replace_color(current, old_plum, canonical_plum)
    updated = replace_color(
        updated, old_background, canonical_background
    )

    source_defs = unique_match(
        r'<defs>.*?</defs>', source, "source defs"
    ).group(0)

    old_defs = unique_match(
        r'<defs>.*?</defs>', updated, "header defs"
    )

    new_defs = old_defs.group(0)

    # Synchronize shared definitions without moving header-only ones.
    for tag, identifier in (
        ("radialGradient", "emblem-golden-crescent-gradient"),
        ("clipPath", "emblem-hittite-disk-clip"),
    ):
        fragment = extract_element(
            source_defs, tag, identifier, True
        )
        new_defs = replace_element(
            new_defs, tag, identifier, True, fragment
        )

    # Remove previously selected variant-only gradients.
    extra_gradients = (
        "eagle-outline-golden-gradient",
        "hittite-outline-gradient",
    )

    for identifier in extra_gradients:
        pattern = (
            r'(?m)^[ \t]*<radialGradient\b'
            r'(?=[^>]*\bid="'
            + re.escape(identifier)
            + r'")[^>]*>.*?</radialGradient>[ \t]*\n?'
        )

        new_defs, removed = re.subn(
            pattern,
            "",
            new_defs,
            flags=re.DOTALL,
        )

        if removed > 1:
            raise ValueError(
                f"Duplicate header gradient: {identifier}"
            )

    # Insert only gradients required by the selected background.
    for identifier in extra_gradients:
        pattern = (
            r'<radialGradient\b(?=[^>]*\bid="'
            + re.escape(identifier)
            + r'")[^>]*>.*?</radialGradient>'
        )

        match = re.search(
            pattern, source_defs, flags=re.DOTALL
        )

        if match is None:
            continue

        closing = re.search(
            r'(?m)^([ \t]*)</defs>', new_defs
        )

        if closing is None:
            raise ValueError("Header closing defs tag not found.")

        insertion = (
            closing.group(1)
            + "\t"
            + match.group(0)
            + "\n"
        )

        new_defs = (
            new_defs[:closing.start()]
            + insertion
            + new_defs[closing.start():]
        )

    updated = (
        updated[:old_defs.start()]
        + new_defs
        + updated[old_defs.end():]
    )

    begin, end = group_span(source, "eagle-layout")
    selected_art = source[begin:end]

    # Preserve the original header's CSS-controlled chest ring.
    if source_path.name == "eagle_background.svg":
        ring = (
            f'fill="none" stroke="{canonical_background}" '
            'stroke-width="5.0"'
        )

        if selected_art.count(ring) != 1:
            raise ValueError(
                "Canonical header chest ring was not found."
            )

        selected_art = selected_art.replace(
            ring,
            'fill="none" stroke-width="5.0"  '
            'class="emblem-background-stroke"',
            1,
        )

    begin, end = group_span(updated, "eagle-layout")
    updated = updated[:begin] + selected_art + updated[end:]

    # Reversible: do not delete rule geometry or its gradients.
    count = [0]
    def toggle(match):
        tag = match.group(0)
        if not re.search(
            r'class="header-rule-(?:primary|accent)"', tag
        ):
            return tag
        count[0] += 1
        tag = tag.replace('<line display="none"', '<line', 1)
        if not side_rules:
            tag = tag.replace('<line', '<line display="none"', 1)
        return tag

    updated = re.sub(r'<line\b[^>]*?/>', toggle, updated,
                     flags=re.DOTALL)
    if count[0] != 4:
        raise ValueError(
            f"Expected four header side rules, found {count[0]}"
        )

    validate_svg_text(updated, target_path)
    if updated != current:
        write_text(target_path, updated)
        print(f"Generated: {target_path.relative_to(REPO_ROOT)}")
    else:
        print(f"Already generated: {target_path.relative_to(REPO_ROOT)}")


def sync_visual_assets():
    header_background, side_rules = load_header_settings()
    background_sources = sorted(
        BACKGROUNDS_SVG_DIR.glob("eagle_background*.svg")
    )

    header_sources = sorted(
        HEADER_DIR.glob("*.svg")
    )

    if not header_sources:
        raise FileNotFoundError(
            "No profile header SVG files found in: "
            f"{HEADER_DIR}"
        )

    required_sources = (
        CANONICAL_LOGO_SOURCE,
        REVERSED_LOGO_SOURCE,
        BACKGROUND_SOURCE,
        header_background,
        *background_sources,
        *header_sources,
    )

    for path in required_sources:
        if not path.exists():
            raise FileNotFoundError(
                f"Visual asset not found: {path}"
            )

        ET.parse(path)

    canonical_text = read_text(
        CANONICAL_LOGO_SOURCE
    )

    # Validate derived geometry before modifying any SVG.
    for background_source in background_sources:
        if background_source.name == "eagle_background-outlined.svg":
            validate_detailed_outline(
                canonical_text,
                background_source,
            )

    canonical_plum = element_fill(
        canonical_text,
        "circle",
        "hittite-disk-outer",
    )

    canonical_background = element_fill(
        canonical_text,
        "rect",
        "background",
    )

    print("Synchronizing canonical logo dependencies...")

    sync_reversed_logo(
        canonical_text,
        canonical_plum,
        canonical_background,
    )

    for background_source in background_sources:
        sync_embedded_logo(
            background_source,
            canonical_text,
            canonical_plum,
            canonical_background,
            preserve_detailed_outline=(
                background_source.name
                == "eagle_background-outlined.svg"
            ),
        )

    for header_source in header_sources:
        compose_header(
            header_source,
            header_background,
            side_rules,
            canonical_plum,
            canonical_background,
        )

    print(
        "Canonical source: "
        f"{CANONICAL_LOGO_SOURCE.relative_to(REPO_ROOT)}"
    )


# ---------------------------------------------------------------------------
# PNG export
# ---------------------------------------------------------------------------

def find_inkscape():
    executable = (
        shutil.which("inkscape")
        or shutil.which("inkscape.com")
    )

    if executable:
        return executable

    if WINDOWS_INKSCAPE.exists():
        return str(WINDOWS_INKSCAPE)

    return None


INKSCAPE = find_inkscape()


def is_up_to_date(source, target):
    return (
        target.exists()
        and target.stat().st_mtime
        >= source.stat().st_mtime
    )


def run_inkscape_export(
    source,
    target,
    width,
    height,
):
    subprocess.run(
        [
            INKSCAPE,
            str(source),
            "--export-area-page",
            "--export-type=png",
            f"--export-filename={target}",
            f"--export-width={width}",
            f"--export-height={height}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def export_svg(
    source,
    target,
    width,
    height,
):
    global created_count
    global skipped_count
    global error_count

    try:
        if (
            SKIP_UP_TO_DATE
            and is_up_to_date(source, target)
        ):
            print(
                "Skipped: "
                f"{target.relative_to(REPO_ROOT)}"
            )

            skipped_count += 1
            return

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        run_inkscape_export(
            source,
            target,
            width,
            height,
        )

        print(
            "Created: "
            f"{target.relative_to(REPO_ROOT)}"
        )

        created_count += 1

    except Exception as error:
        print(
            "Error: "
            f"{target.relative_to(REPO_ROOT)} "
            f"-> {error}"
        )

        error_count += 1


def background_fill(source):
    root = ET.parse(source).getroot()

    for element in root.iter():
        if element.get("id") == "background":
            color = element.get("fill", "")

            if re.fullmatch(r"#[0-9a-fA-F]{6}", color):
                return color

            raise ValueError(
                f"Invalid background fill: {source}"
            )

    raise ValueError(
        f"Background element not found: {source}"
    )


def export_background_variant(source):
    global created_count
    global skipped_count
    global error_count

    if not source.exists():
        raise FileNotFoundError(
            "Background SVG not found: "
            f"{source}"
        )

    base_height = round(
        BACKGROUND_BASE_WIDTH
        * BACKGROUND_ASPECT_RATIO[1]
        / BACKGROUND_ASPECT_RATIO[0]
    )

    pending_outputs = []

    for width in BACKGROUND_WIDTHS:
        height = round(
            width
            * BACKGROUND_ASPECT_RATIO[1]
            / BACKGROUND_ASPECT_RATIO[0]
        )

        output_name = (
            f"{source.stem}"
            f"-{width}x{height}.png"
        )

        output_path = (
            BACKGROUNDS_PNG_DIR
            / output_name
        )

        if (
            SKIP_UP_TO_DATE
            and is_up_to_date(
                source,
                output_path,
            )
        ):
            print(
                "Skipped: "
                f"{output_path.relative_to(REPO_ROOT)}"
            )

            skipped_count += 1
            continue

        pending_outputs.append(
            (
                width,
                height,
                output_path,
            )
        )

    if not pending_outputs:
        return

    BACKGROUNDS_PNG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_png = (
                Path(temp_dir)
                / "eagle_background.png"
            )

            run_inkscape_export(
                source,
                base_png,
                BACKGROUND_BASE_WIDTH,
                base_height,
            )

            with Image.open(base_png) as image:
                background_image = image.convert(
                    "RGB"
                )

            background_color = background_fill(source)

            for (
                width,
                height,
                output_path,
            ) in pending_outputs:
                canvas = Image.new(
                    "RGB",
                    (width, height),
                    background_color,
                )

                x = (
                    width
                    - BACKGROUND_BASE_WIDTH
                ) // 2

                y = (
                    height
                    - base_height
                ) // 2

                canvas.paste(
                    background_image,
                    (x, y),
                )

                canvas.save(
                    output_path
                )

                created_count += 1

                print(
                    "Created: "
                    f"{output_path.relative_to(REPO_ROOT)}"
                )

    except Exception as error:
        error_count += len(
            pending_outputs
        )

        print(
            "Error: "
            f"{source.relative_to(REPO_ROOT)} "
            f"-> {error}"
        )


def export_backgrounds():
    if not BACKGROUND_SOURCE.exists():
        raise FileNotFoundError(
            f"Background SVG not found: {BACKGROUND_SOURCE}"
        )

    for source in sorted(
        BACKGROUNDS_SVG_DIR.glob("eagle_background*.svg")
    ):
        export_background_variant(source)


def export_logos():
    if not LOGOS_SVG_DIR.exists():
        raise FileNotFoundError(
            "Logo SVG directory not found: "
            f"{LOGOS_SVG_DIR}"
        )

    svg_files = sorted(
        LOGOS_SVG_DIR.glob("*.svg")
    )

    if not svg_files:
        print(
            "No logo SVG files found."
        )
        return

    for svg_file in svg_files:
        for width in LOGO_WIDTHS:
            height = round(
                width
                * LOGO_ASPECT_RATIO[1]
                / LOGO_ASPECT_RATIO[0]
            )

            output_name = (
                f"{svg_file.stem}"
                f"-{width}x{height}.png"
            )

            output_path = (
                LOGOS_PNG_DIR
                / output_name
            )

            export_svg(
                svg_file,
                output_path,
                width,
                height,
            )


def main():
    if not INKSCAPE:
        print(
            "Error: Inkscape CLI was not found."
        )

        print(
            r"Expected location: "
            r"C:\Program Files\Inkscape\bin\inkscape.com"
        )

        sys.exit(1)

    try:
        sync_visual_assets()
    except Exception as error:
        print(
            f"Visual asset synchronization failed: {error}"
        )
        sys.exit(1)

    print()
    print("Starting PNG export...")

    export_backgrounds()
    export_logos()

    print()
    print(f"Created: {created_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Errors:  {error_count}")

    if error_count:
        sys.exit(1)


if __name__ == "__main__":
    main()
