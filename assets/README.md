# Assets

This directory contains the visual assets used by the Yusseter profile.

## Structure

- `logos/`: Hittite Sun Disk and Golden Crescent logo sources and PNG exports.
- `backgrounds/`: Double-headed eagle background source and PNG exports.

SVG files are the canonical source assets. PNG files are generated from them using `scripts/update_visual_assets.py`.

## Naming

Underscores separate words within the same asset name:

`hittite_sun_disk_golden_crescent.svg`

Hyphens separate variants and generated output properties:

`hittite_sun_disk_golden_crescent-reversed.svg`

`hittite_sun_disk_golden_crescent-reversed-512x512.png`

Generated PNG files should not be edited manually.
