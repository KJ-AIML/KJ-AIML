# 3D ASCII wordmark

[The committed wordmark](../assets/kj-wordmark.svg) renders **KJ-AIML** as an
extruded slab, shaded with ASCII characters. It is a compact, static rest pose
that is visible as soon as the SVG loads. The geometry is generated locally;
viewing it requires no script, external font, or animation support.

## Pipeline

| Stage | Purpose |
| --- | --- |
| `build_shell()` | Draw the text with the bundled bold font, threshold a mask, and extrude its surface points |
| `project()` | Rotate the surface, cull back faces, apply perspective, lighting, and depth fog |
| `fit()` | Fit the projected points into the character grid |
| `rasterize()` | Resolve depth and map brightness to ASCII density |
| `emit()` | Write a visible SVG frame using neutral shades and fixed text lengths |

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

This rebuilds the wordmark and the optional CLI panel. CI installs NumPy and
Pillow and verifies both assets; no renderer test is skipped for missing packages.

For a wordmark-only build, `python scripts/generate_wordmark.py` also defaults
to the static pose. `--preview` prints an ASCII frame in the terminal.

## Experimental modes

The renderer retains `rock`, `once`, and `spin` modes as explicit options. They
precompute multiple frames and use SVG animation to switch between them. They
are not used by the profile build and do not pass its static-asset checks.

Use the generator's `--help` for the available output and mode arguments, and
write experiments outside `assets/` so they cannot replace a committed asset.
The original boot sequence and timing remain implementation details of these
legacy modes, not part of the profile's reading flow.

`WORDMARK_TEXT`, `WORDMARK_FONT`, `WORDMARK_FONT_INDEX`, `WORDMARK_TILT`,
`WORDMARK_COLS`, and `WORDMARK_ROW_MARGIN` support local geometry experiments.
Leave them unset when reproducing committed output. The bundled font is the
default even when other fonts are installed.
