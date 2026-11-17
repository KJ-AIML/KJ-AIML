# The earlier 3D ASCII renderer

`scripts/generate_wordmark.py` is the profile's first renderer. It draws text as
an extruded slab made of ASCII characters and can animate it with its `rock`,
`once`, and `spin` modes. The profile no longer shows its output.

It stays in the repository for one reason: [the hello hero](hello-hero.md) uses
its point shell. `build_shell` rasterizes text with the bundled font and returns
the surface points and normals of the extruded letters, and the hero reads this
module's camera, lighting, and fog constants so the handle keeps the same
material.

Its own modes still run and are covered by `tests/test_legacy_wordmark.py`:

```bash
python scripts/generate_wordmark.py --mode rock --out /tmp/wordmark.svg
```

`--out` is required, so an experiment never lands in `assets/`. The
`WORDMARK_*` environment variables affect only this renderer's own output.
Earlier design notes are in `docs/superpowers/`.
