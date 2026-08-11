from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

# Output sizes for background and logo PNGs.
BACKGROUND_ASPECT_RATIO = (16, 9)
BACKGROUND_BASE_WIDTH = 1920
BACKGROUND_WIDTHS = [1920, 2560, 3840, 5120]

LOGO_ASPECT_RATIO = (1, 1)
LOGO_WIDTHS = [256, 512, 1024]

# Local runs skip PNGs that are newer than their source SVG.
# CI forces regeneration when source assets change.
FORCE_PNG_EXPORT = os.environ.get("FORCE_PNG_EXPORT") == "1"
SKIP_UP_TO_DATE = not FORCE_PNG_EXPORT

REPO_ROOT = Path(__file__).resolve().parent.parent

BACKGROUNDS_SVG_DIR = REPO_ROOT / "assets" / "backgrounds" / "svg"
BACKGROUNDS_PNG_DIR = REPO_ROOT / "assets" / "backgrounds" / "png"

LOGOS_SVG_DIR = REPO_ROOT / "assets" / "logos" / "svg"
LOGOS_PNG_DIR = REPO_ROOT / "assets" / "logos" / "png"

BACKGROUND_SOURCE = BACKGROUNDS_SVG_DIR / "eagle_background.svg"

PROFILE_HEADER = (
    REPO_ROOT
    / "assets"
    / "profile"
    / "header.svg"
)

WINDOWS_INKSCAPE = Path(
    r"C:\Program Files\Inkscape\bin\inkscape.com"
)

created_count = 0
skipped_count = 0
error_count = 0

def find_inkscape():
    executable = shutil.which("inkscape") or shutil.which("inkscape.com")

    if executable:
        return executable

    if WINDOWS_INKSCAPE.exists():
        return str(WINDOWS_INKSCAPE)

    return None

INKSCAPE = find_inkscape()

def is_up_to_date(source, target):
    # Re-export only when the SVG is newer than the PNG.
    return target.exists() and target.stat().st_mtime >= source.stat().st_mtime

def run_inkscape_export(source, target, width, height):
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

def export_svg(source, target, width, height):
    global created_count, skipped_count, error_count

    try:
        if SKIP_UP_TO_DATE and is_up_to_date(source, target):
            print(f"Skipped: {target.relative_to(REPO_ROOT)}")
            skipped_count += 1
            return

        target.parent.mkdir(parents=True, exist_ok=True)

        run_inkscape_export(
            source,
            target,
            width,
            height,
        )

        print(f"Created: {target.relative_to(REPO_ROOT)}")
        created_count += 1

    except Exception as error:
        print(f"Error: {target.relative_to(REPO_ROOT)} -> {error}")
        error_count += 1

def export_profile_header():
    if not BACKGROUND_SOURCE.exists():
        raise FileNotFoundError(
            f"Background SVG not found: {BACKGROUND_SOURCE}"
        )

    source = BACKGROUND_SOURCE.read_text(
        encoding="utf-8"
    )

    original_geometry = (
        'width="1920" height="1080" '
        'viewBox="0 0 1920 1080"'
    )

    header_geometry = (
        'width="760" height="380" '
        'viewBox="160 140 1600 800"'
    )

    if original_geometry not in source:
        raise RuntimeError(
            "Could not find the expected eagle SVG geometry."
        )

    header = source.replace(
        original_geometry,
        header_geometry,
        1,
    )

    header = header.replace(
        "Yusseter Eagle Background",
        "Yusseter Profile Header",
        1,
    )

    PROFILE_HEADER.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    PROFILE_HEADER.write_text(
        header,
        encoding="utf-8",
        newline="\n",
    )

    print(
        f"Updated: {PROFILE_HEADER.relative_to(REPO_ROOT)}"
    )
def export_backgrounds():
    global created_count, skipped_count, error_count

    if not BACKGROUND_SOURCE.exists():
        raise FileNotFoundError(
            f"Background SVG not found: {BACKGROUND_SOURCE}"
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

        output_name = f"{BACKGROUND_SOURCE.stem}-{width}x{height}.png"
        output_path = BACKGROUNDS_PNG_DIR / output_name

        if SKIP_UP_TO_DATE and is_up_to_date(
            BACKGROUND_SOURCE,
            output_path,
        ):
            print(f"Skipped: {output_path.relative_to(REPO_ROOT)}")
            skipped_count += 1
            continue

        pending_outputs.append(
            (width, height, output_path)
        )

    if not pending_outputs:
        return

    BACKGROUNDS_PNG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_png = Path(temp_dir) / "eagle_background.png"

            run_inkscape_export(
                BACKGROUND_SOURCE,
                base_png,
                BACKGROUND_BASE_WIDTH,
                base_height,
            )

            with Image.open(base_png) as image:
                background_image = image.convert("RGB")

            for width, height, output_path in pending_outputs:
                canvas = Image.new(
                    "RGB",
                    (width, height),
                    "#ffffff",
                )

                x = (width - BACKGROUND_BASE_WIDTH) // 2
                y = (height - base_height) // 2

                canvas.paste(
                    background_image,
                    (x, y),
                )

                canvas.save(output_path)

                created_count += 1
                print(
                    f"Created: {output_path.relative_to(REPO_ROOT)}"
                )

    except Exception as error:
        error_count += len(pending_outputs)
        print(
            f"Error: {BACKGROUND_SOURCE.relative_to(REPO_ROOT)} -> {error}"
        )

def export_logos():
    if not LOGOS_SVG_DIR.exists():
        raise FileNotFoundError(
            f"Logo SVG directory not found: {LOGOS_SVG_DIR}"
        )

    svg_files = sorted(
        LOGOS_SVG_DIR.glob("*.svg")
    )

    if not svg_files:
        print("No logo SVG files found.")
        return

    for svg_file in svg_files:
        for width in LOGO_WIDTHS:
            height = round(
                width
                * LOGO_ASPECT_RATIO[1]
                / LOGO_ASPECT_RATIO[0]
            )

            output_name = f"{svg_file.stem}-{width}x{height}.png"
            output_path = LOGOS_PNG_DIR / output_name

            export_svg(
                svg_file,
                output_path,
                width,
                height,
            )

def main():
    if not INKSCAPE:
        print("Error: Inkscape CLI was not found.")
        print(
            r"Expected location: C:\Program Files\Inkscape\bin\inkscape.com"
        )
        sys.exit(1)

    print("Starting visual asset export...")

    export_profile_header()
    export_backgrounds()
    export_logos()

    print()
    print(f"Created: {created_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Errors:  {error_count}")

if __name__ == "__main__":
    main()
