# Braille hand intro and wordmark

The profile uses [the animated hero](../assets/kj-wordmark-animated.svg): two
shaded hands reach toward a green signal, withdraw, and reveal **KJ-AIML**.
The [still version](../assets/kj-wordmark.svg) shows the same final composition.
Both use an 855 by 300 canvas and stay below the 500 KB asset budget.

The owner supplied [pi-ter](https://github.com/KJ-AIML/pi-ter) as the visual
reference. The hand fields are vendored at a fixed revision; their source and
encoding are documented in [scripts/data](../scripts/data/README.md).

## Pipeline

`scripts/generate_braille.py` generates both variants without network access.

1. Draw `KJ-AIML` with the bundled IBM Plex Mono Bold font and apply an oblique
   shear to the mask.
2. Build the bevel from successive mask erosions, light the front surface, and
   place an offset lavender extrusion behind it.
3. Sample the surfaces into a dithered dot grid. Group round SVG strokes by shade
   to keep the asset compact and independent of installed Braille fonts.
4. Decode the two local alpha/luminance hand fields. Extend the wrist texture
   beyond the viewport so the hands remain attached while moving.
5. Emit the still composition, or add a finite SMIL opacity/translation timeline.

The bundled font's exact source and open font license are included in
[assets/fonts](../assets/fonts/). No additional renderer dependency is needed.

## Timing

| Time | Composition |
| --- | --- |
| 0-1.45 seconds | Hands enter; a small Hello World greeting appears |
| 1.45-2.75 seconds | Hands reach toward the center |
| 2.65-3.55 seconds | A restrained green signal passes between the fingertips |
| 3.35-4.65 seconds | Hands separate; Hello KJ appears briefly |
| 4.55-6 seconds | Hands withdraw and the wordmark settles into view |
| After 6 seconds | The complete still composition remains visible |

The introduction plays once per image load. A replay button is available in the
local profile preview. Essential facts and links stay in ordinary Markdown.

## Fallback

The wordmark group is visible in the underlying SVG. SMIL hides it for the intro
and then restores it. The hand scene has zero base opacity. A viewer that ignores
animation therefore displays the complete wordmark immediately, with no overlapping
hand scene. The README also selects the still file for `prefers-reduced-motion`
and provides a direct still-artwork link.

## Regeneration and review

```bash
python -m pip install -r scripts/requirements.txt -r scripts/requirements-wordmark.txt
python scripts/generate_all.py
python scripts/validate_profile.py
python -m pytest -q
```

For a separate animation experiment:

```bash
python scripts/generate_braille.py --mode intro --out /tmp/kj-braille.svg
```

Generation defaults to the static variant. The profile build explicitly selects
`intro` for `kj-wordmark-animated.svg`. Inspect the artwork at desktop and phone
widths. A static SVG renderer checks the fallback only; live playback needs an
SVG animation-capable viewer. During this change, key frames were also sampled
from the SVG's opacity/translation timelines and rendered offline. Browser
playback was not verified in the automated environment.

## Earlier ASCII experiment

`scripts/generate_wordmark.py` retains the previous extruded ASCII renderer and
its `static`, `rock`, `once`, and `spin` modes. It is no longer selected by the
profile build. Its `WORDMARK_*` environment overrides only affect that legacy
renderer. Write its experimental output outside `assets/` to avoid replacing the
profile artwork. Historical design notes remain in `docs/superpowers/`.
