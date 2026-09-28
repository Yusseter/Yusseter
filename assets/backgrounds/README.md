# Backgrounds

This directory contains the double-headed eagle background used by
the Yusseter profile.

## Eagle Background

`svg/eagle_background.svg` is the canonical vector source.

Additional variants:

- `svg/eagle_background-outlined.svg`: detailed gold outline.
- `svg/eagle_background-outlined-minimal.svg`: minimal gold outline.

All three SVG sources have independent PNG exports.

The composition uses a deep plum double-headed eagle on a white background,
with the Hittite Sun Disk and Golden Crescent emblem at its center.

When PNG backgrounds are generated, the eagle retains its 1920x1080 base
visual size while the surrounding white canvas expands for larger resolutions.

## PNG Exports

PNG files are generated with `scripts/update_visual_assets.py` at:

- 1920x1080
- 2560x1440
- 3840x2160
- 5120x2880

Generated filenames include the output resolution:

`eagle_background-3840x2160.png`

`eagle_background-outlined-3840x2160.png`

`eagle_background-outlined-minimal-3840x2160.png`

Generated PNG files should not be edited manually.
