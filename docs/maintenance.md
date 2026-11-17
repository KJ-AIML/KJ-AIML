# Maintenance

## Rebuild and check

Use Python 3.12 and install both pinned dependency sets:

```bash
python -m pip install -r scripts/requirements.txt -r scripts/requirements-wordmark.txt
python scripts/generate_all.py
python scripts/validate_profile.py
python -m pytest -q
git diff --check
```

`generate_all.py` rebuilds every generated image: the animated hero, its still,
the optional CLI panel, and the icons in `assets/icons/`. Paths are resolved from
the script's location, so it works from any working directory. `STATIC=1` is
accepted and changes nothing; the still and the animation have separate filenames.

If Python is managed through uv, the equivalent command prefix is:

```bash
uv run --no-project --python 3.12 --with-requirements scripts/requirements.txt --with-requirements scripts/requirements-wordmark.txt python scripts/generate_all.py
```

Run the validator and pytest in the same environment. After changing artwork,
watch the hero play in a browser and look at the page at desktop and phone
widths before committing. The tests check geometry and safety; they do not
judge how it looks.

## Editing content

Keep essential facts in `README.md`. Update a project's sentence after checking
its public source. Use specific work and linked contributions as evidence; avoid
unverified adoption, performance, or employment claims. Record the source and
review date in [the source notes](profile-refresh/sources.md).

Each project card has one sentence so the two-column grid stays readable on a
phone. To add a project, add a 760 by 475 picture to `assets/projects/`, record
where it came from in that folder's README, and add a card.

The optional CLI illustration is defined in `scripts/generate_agent_cli.py`. It
is shown on the design page, not in the profile.

## Reproducible artwork

- **Hero:** `scripts/generate_hello.py`, described in
  [the renderer notes](hello-hero.md). It uses the font in `assets/fonts/` and the
  hand fields in `scripts/data/`.
- **Icons:** `scripts/generate_icons.py`, from the glyphs and colours in
  `scripts/data/icons.json`. To add a technology, add its entry there and rebuild.
- **Company marks and project pictures** are committed as they are and are not
  regenerated. Their origins are in the READMEs beside them.

Keep each source record with its data. Rebuild everything after changing a
generator; a stale image fails the tests and CI.

Validation allows the hero to animate opacity, sliding, rotation, and a
gradient's endpoints, and to carry one reduced-motion rule that shows its final
frame. It rejects scripts, external resources, link changes, scaling, any other
at-rule, and any animation in the static files. The hero must keep a visible
final frame for viewers without SVG animation.

`scripts/generate_wordmark.py` is the earlier ASCII renderer. The hero uses its
text extrusion; see [the note on it](3d-ascii-wordmark.md).

## CI

`Validate profile` installs the complete dependency set on Ubuntu and Windows.
Tests cover generation from an unrelated working directory, deterministic
output, freshness of every generated image, SVG safety, the hero's motion and
fallback, local references including the reduced-motion source, and read-only
workflow permissions. Missing renderer dependencies fail instead of skipping.

Freshness comparisons normalize checkout line endings so Windows CRLF does not
produce a false difference; repeated output must still be byte-identical. The
workflow also regenerates all images and checks that Git sees no change in
`assets/`.

The workflow has `contents: read` and never publishes or commits generated files.
Action references are pinned to full commit SHAs. When upgrading them, verify the
release and replacement SHA against the official action repository.
