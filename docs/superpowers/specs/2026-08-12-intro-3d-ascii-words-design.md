# Intro 3D ASCII Words Design

## Goal

Replace the ordinary text surfaces used for `Welcome / To / My / AI / World`
with forms produced by the same 3D ASCII renderer as the final `KJ-AIML`
wordmark. Preserve the existing boot narrative, timing, particles, loading bar,
terminal frame, and final reveal.

## Approved visual system

- `WELCOME` and `WORLD` use the full 91-column form.
- `TO`, `MY`, and `AI` use a centered 55-column form.
- Every word uses the same Arial Bold source mask, extrusion depth, camera,
  4-degree tilt, Lambert lighting, depth fog, density ramp, and neutral shade
  buckets as `KJ-AIML`.
- Intro words are uppercase so they share the final mark's silhouette language.
- The short forms keep the same 9 px cell width and 15.5 px cell height. They
  are not stretched to fill the 91-column stage.
- `WORLD` is the visual benchmark for proportion, depth, and readability.
- `KJ-AIML` remains unchanged and is still the strongest, final form.

## Animation behavior

Each intro word replaces the existing solid SVG `<text>` at its current point
in the sequence. Its 3D ASCII cells appear while the existing debris converges,
hold for the existing `WORD_HOLD`, and disappear into the existing
`WORD_BURST`. Particle paths, word order, scene durations, semantic status
colors outside the word surfaces, the loading bar, and the final wordmark rock
loop remain unchanged.

The intro word surfaces use the final mark's neutral shade ramp rather than the
current `s3`, `info`, and `ok` text colors. Color remains reserved for system
state and debris; geometry and value carry the identity words.

## Generator structure

Extract the existing shell projection and rasterization path into a helper that
accepts text and column count and returns a shaded grid plus its fitted bounds.
The final `KJ-AIML` frames continue to call that path with 91 columns. The intro
word layer calls it once per unique word using the approved width mapping:

```python
INTRO_WORD_COLS = {
    "WELCOME": 91,
    "TO": 55,
    "MY": 55,
    "AI": 55,
    "WORLD": 91,
}
```

Emit each word as SVG `<text>` cells using the existing density glyphs and
shade classes. Center the emitted grid within the current art area. Do not add
new fonts, raster images, JavaScript, CSS animation, or remote assets.

## Validation

- Add focused tests for the width mapping, uppercase labels, centered short
  forms, and absence of the former solid intro-word `<text>` nodes.
- Regenerate `assets/kj-wordmark.svg` and pass the freshness test.
- Pass `python3 scripts/validate_profile.py` and `python3 -m pytest -q` in the
  isolated renderer environment.
- Confirm the committed SVG remains self-contained and deterministic.
- Visually inspect the complete animated boot sequence at the README display
  width, paying particular attention to counters in `WORLD`, `MY`, and `AI`.

## Scope boundaries

This change does not alter README copy, profile pins, account metadata, agent
CLI animation, boot timing, particle count, final wordmark geometry, or the
perpetual rock loop. The already-approved README collaboration line remains a
separate uncommitted change.
