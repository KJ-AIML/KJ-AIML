# Hand artwork source

`pi-ter-hands.json` contains the alpha/luminance fields from the profile owner's
[pi-ter repository](https://github.com/KJ-AIML/pi-ter), specifically
[fields.mjs at 45821bb](https://github.com/KJ-AIML/pi-ter/blob/45821bb0b1d1bf13036547681622ae879ef5af7a/extensions/hello-pi/assets/fields.mjs).
The owner supplied that repository as the visual reference on 2026-11-17.

The two fields are losslessly compressed with zlib and encoded as base64.
Decoded bytes are row-major pairs of uint8 alpha and luminance. Their original
position and dimensions are retained. The source revision is recorded in the
JSON. Generation is entirely offline and requires no JavaScript runtime.

The profile generator adapts the hand gesture and six-second pacing from
[scene.mjs](https://github.com/KJ-AIML/pi-ter/blob/45821bb0b1d1bf13036547681622ae879ef5af7a/extensions/hello-pi/scene.mjs).
The shaded wordmark is generated independently from the bundled, OFL-licensed
IBM Plex Mono font. This provenance record does not assign a new license to the
upstream artwork.
