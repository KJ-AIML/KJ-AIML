# Vendored data

## Hand artwork

`pi-ter-hands.json` contains the alpha/luminance fields from the profile owner's
[pi-ter repository](https://github.com/KJ-AIML/pi-ter), specifically
[fields.mjs at 45821bb](https://github.com/KJ-AIML/pi-ter/blob/45821bb0b1d1bf13036547681622ae879ef5af7a/extensions/hello-pi/assets/fields.mjs).
The owner supplied that repository as the visual reference on 2026-11-17.

The two fields are losslessly compressed with zlib and encoded as base64.
Decoded bytes are row-major pairs of uint8 alpha and luminance. Their original
position and dimensions are retained. The source revision is recorded in the
JSON. Generation is entirely offline and requires no JavaScript runtime.

`scripts/generate_hello.py` adapts the reaching gesture and the six-second
pacing from
[scene.mjs](https://github.com/KJ-AIML/pi-ter/blob/45821bb0b1d1bf13036547681622ae879ef5af7a/extensions/hello-pi/scene.mjs).
The joints that articulate the hands, and the handle that forms between them,
are this repository's own work; the handle's geometry comes from the bundled,
OFL-licensed IBM Plex Mono font. This record does not assign a new license to
the upstream artwork.

## Icon glyphs

`icons.json` holds the technology marks the README uses, taken from
[Simple Icons](https://simpleicons.org) 16.38.0 on 2026-11-17. The collection is
released under [CC0 1.0](https://github.com/simple-icons/simple-icons/blob/develop/LICENSE.md).
Each entry keeps the mark's title, its single 24 by 24 path, the collection's
brand colour (`brand`), and the colour the profile draws it in (`color`).

`color` equals `brand` unless that colour would not be readable on the dark icon
tile. In those cases it is a lighter tone of the same hue, with two exceptions
chosen by hand: Rust's black mark uses the colour GitHub shows for the Rust
language, and Ollama's black mark uses its white form.

The marks are trademarks of their owners. They are used here only to name the
technologies the profile's text already lists.
