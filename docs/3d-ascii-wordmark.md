# 3D ASCII wordmark

The wordmark renders **KJ-AIML** as an extruded slab, shaded with ASCII characters.
The profile uses [the animated hero](../assets/kj-wordmark-animated.svg), with the
original boot sequence, word/particle transitions, and a rocking rest pose.
[The compact static version](../assets/kj-wordmark.svg) is selected by the README
for reduced motion and is also linked directly. Both are generated locally and
require no scripts or external resources.

## Pipeline

| Stage | Purpose |
| --- | --- |
| `build_shell()` | Draw the text with the bundled bold font, threshold a mask, and extrude its surface points |
| `project()` | Rotate the surface, cull back faces, apply perspective, lighting, and depth fog |
| `fit()` | Fit the projected points into the character grid |
| `rasterize()` | Resolve depth and map brightness to ASCII density |
| `emit()` | Write either a static frame or SMIL scene using neutral shades and fixed text lengths |

The surface contains front and back caps plus walls around the text outline.
Brightness selects both a density-ramp character and a neutral shade, so the
letter faces remain distinct from the walls. A small front-cap depth offset
prevents ties in the rasterizer from cutting streaks through the letters.

The default grid has 91 columns, with 9px cells and 18px side padding, producing
an 855px-wide asset. `WORDMARK_ROW_MARGIN` defaults to zero for the static build.
Explicit animated modes retain at least four blank rows above and below the
wordmark to accommodate their status sequence.

The source font is bundled IBM Plex Mono Bold. Its exact upstream source, hash,
and open font license are included in [assets/fonts](../assets/fonts/). Using
the same input font on every platform removes the old Arial/DejaVu/Futura
selection difference from the build.

## Regeneration

```bash
python -m pip install -r scripts/requirements.txt -r scripts/requirements-wordmark.txt
python scripts/generate_all.py
python -m pytest -q
```

This rebuilds both wordmark variants and the optional CLI panel. CI installs
NumPy and Pillow and verifies all assets; no renderer test is skipped for missing packages.

For a wordmark-only build, `python scripts/generate_wordmark.py` also defaults
to the static pose. `--preview` prints an ASCII frame in the terminal.

## Animation and fallback

The profile build explicitly selects `rock` for `kj-wordmark-animated.svg`.
The intro takes approximately 13.5 seconds, then a 20-frame sequence rocks the
wordmark. Name, headline, and all meaningful profile facts stay visible in
Markdown while this plays. The animation's terminal readouts are visual effects;
they do not claim current repository counts or fetch live profile data.

A visible rest frame is hidden at time zero only when SMIL runs. The animated
scene has zero base opacity and becomes visible through SMIL. A viewer that
ignores animation therefore displays the rest frame instead of a blank panel
or overlapping scenes. The README's picture source separately respects
`prefers-reduced-motion` by selecting the compact static file.

The `once` and `spin` modes remain available for experiments. They precompute
multiple frames and use SVG animation to switch between them.

Use the generator's `--help` for the available output and mode arguments, and
write experiments outside `assets/` so they cannot replace a committed asset.

`WORDMARK_TEXT`, `WORDMARK_FONT`, `WORDMARK_FONT_INDEX`, `WORDMARK_TILT`,
`WORDMARK_COLS`, and `WORDMARK_ROW_MARGIN` support local geometry experiments.
Leave them unset when reproducing committed output. The bundled font is the
default even when other fonts are installed.
