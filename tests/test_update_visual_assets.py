from pathlib import Path
import importlib.util
import re
import shutil
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
VISUAL_SCRIPT = (
    REPO_ROOT
    / "scripts"
    / "update_visual_assets.py"
)


def load_visual_module():
    pil_stub = types.ModuleType("PIL")
    pil_stub.Image = types.SimpleNamespace()

    spec = importlib.util.spec_from_file_location(
        "update_visual_assets_for_tests",
        VISUAL_SCRIPT,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "Could not load update_visual_assets.py."
        )

    module = importlib.util.module_from_spec(spec)

    with patch.dict(
        sys.modules,
        {"PIL": pil_stub},
    ):
        spec.loader.exec_module(module)

    return module


visuals = load_visual_module()


class VisualAssetSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        relative_files = [
            Path(
                "assets/logos/svg/"
                "hittite_sun_disk_golden_crescent.svg"
            ),
            Path(
                "assets/logos/svg/"
                "hittite_sun_disk_golden_crescent-reversed.svg"
            ),
            Path(
                "assets/backgrounds/svg/"
                "eagle_background.svg"
            ),
        ]

        for relative_path in relative_files:
            source = REPO_ROOT / relative_path
            target = self.root / relative_path

            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(source, target)

        self.header_dir = (
            self.root
            / "assets"
            / "profile"
            / "header"
        )

        self.header_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        source_header_dir = (
            REPO_ROOT
            / "assets"
            / "profile"
            / "header"
        )

        for source in source_header_dir.glob(
            "*.svg"
        ):
            shutil.copy2(
                source,
                self.header_dir / source.name,
            )

        self.canonical_logo = (
            self.root
            / "assets"
            / "logos"
            / "svg"
            / "hittite_sun_disk_golden_crescent.svg"
        )

        self.reversed_logo = (
            self.root
            / "assets"
            / "logos"
            / "svg"
            / "hittite_sun_disk_golden_crescent-reversed.svg"
        )

        self.background = (
            self.root
            / "assets"
            / "backgrounds"
            / "svg"
            / "eagle_background.svg"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def patched_paths(self):
        return patch.multiple(
            visuals,
            REPO_ROOT=self.root,
            LOGOS_SVG_DIR=(
                self.root
                / "assets"
                / "logos"
                / "svg"
            ),
            LOGOS_PNG_DIR=(
                self.root
                / "assets"
                / "logos"
                / "png"
            ),
            BACKGROUNDS_SVG_DIR=(
                self.root
                / "assets"
                / "backgrounds"
                / "svg"
            ),
            BACKGROUNDS_PNG_DIR=(
                self.root
                / "assets"
                / "backgrounds"
                / "png"
            ),
            PROFILE_DIR=(
                self.root
                / "assets"
                / "profile"
            ),
            CANONICAL_LOGO_SOURCE=(
                self.canonical_logo
            ),
            REVERSED_LOGO_SOURCE=(
                self.reversed_logo
            ),
            BACKGROUND_SOURCE=(
                self.background
            ),
            HEADER_DIR=(
                self.header_dir
            ),
        )

    def test_syncs_all_header_variants_and_is_idempotent(
        self,
    ):
        future_header = (
            self.header_dir
            / "future.svg"
        )

        shutil.copy2(
            self.header_dir / "desktop.svg",
            future_header,
        )

        canonical_text = visuals.read_text(
            self.canonical_logo
        )

        canonical_plum = visuals.element_fill(
            canonical_text,
            "circle",
            "hittite-disk-outer",
        )

        marker_color = "#123456"

        header_paths = sorted(
            self.header_dir.glob("*.svg")
        )

        self.assertGreaterEqual(
            len(header_paths),
            3,
        )

        for path in header_paths:
            original = visuals.read_text(path)

            changed, replacements = re.subn(
                re.escape(canonical_plum),
                marker_color,
                original,
                flags=re.IGNORECASE,
            )

            self.assertGreater(
                replacements,
                0,
                path.name,
            )

            path.write_text(
                changed,
                encoding="utf-8",
                newline="\n",
            )

        with (
            self.patched_paths(),
            patch("builtins.print"),
        ):
            visuals.sync_visual_assets()

            first_pass = {
                path.relative_to(self.root):
                    path.read_bytes()
                for path in (
                    self.reversed_logo,
                    self.background,
                    *header_paths,
                )
            }

            visuals.sync_visual_assets()

            second_pass = {
                path.relative_to(self.root):
                    path.read_bytes()
                for path in (
                    self.reversed_logo,
                    self.background,
                    *header_paths,
                )
            }

        for path in header_paths:
            synced = visuals.read_text(path)

            self.assertNotIn(
                marker_color,
                synced,
                path.name,
            )

            self.assertIn(
                canonical_plum,
                synced.lower(),
                path.name,
            )

        self.assertEqual(
            first_pass,
            second_pass,
        )

    def test_requires_at_least_one_header_svg(self):
        empty_header_dir = (
            self.root
            / "empty-header"
        )

        empty_header_dir.mkdir()

        with (
            self.patched_paths(),
            patch.object(
                visuals,
                "HEADER_DIR",
                empty_header_dir,
            ),
            patch("builtins.print"),
        ):
            with self.assertRaisesRegex(
                FileNotFoundError,
                "No profile header SVG files found",
            ):
                visuals.sync_visual_assets()


class VisualAssetWorkflowTests(unittest.TestCase):
    def test_workflow_covers_header_sync_contract(self):
        workflow = (
            REPO_ROOT
            / ".github"
            / "workflows"
            / "update_visual_assets.yml"
        ).read_text(
            encoding="utf-8"
        )

        self.assertIn(
            '- "assets/profile/header/**"',
            workflow,
        )

        self.assertIn(
            "git add -A -- assets/profile/header",
            workflow,
        )

        self.assertNotIn(
            "assets/profile/header/desktop.svg",
            workflow,
        )

        self.assertIn(
            '- "tests/test_update_visual_assets.py"',
            workflow,
        )

        self.assertIn(
            'python -m unittest discover -s tests '
            '-p "test_update_visual_assets.py"',
            workflow,
        )


if __name__ == "__main__":
    unittest.main()
