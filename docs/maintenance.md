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

`generate_all.py` rebuilds **all three** committed SVGs, using paths resolved
from the script's location. It works from another working directory. Static and
animated wordmarks have separate filenames; the optional CLI panel is static.
`STATIC=1` is a compatibility alias for the same complete build. Select the static
artifact by filename, not by replacing the animated asset's content.

If Python is managed through uv, the equivalent command prefix is:

```bash
uv run --no-project --python 3.12 --with-requirements scripts/requirements.txt --with-requirements scripts/requirements-wordmark.txt python scripts/generate_all.py
```

Run the validator and pytest with the same dependency environment. Inspect changed
artwork at its full width and at a phone-sized width before committing it. A static
SVG render checks the artwork; it does not replace a live GitHub layout check.

## Editing content

Keep essential facts in `README.md`. Update project descriptions after checking
their public source and quick start. Use specific work and linked contributions
as evidence; avoid unverified adoption, performance, or employment claims.
Record the source and review date in [the source notes](profile-refresh/sources.md).

The optional CLI illustration is defined in `scripts/generate_agent_cli.py`.
Changing its content requires regenerating the SVG. It is documented on the
design page rather than embedded in the profile's main reading flow.

## Reproducible artwork

The profile renderer is `scripts/generate_braille.py`. It uses the bundled font
in `assets/fonts/` and the locally stored hand fields in `scripts/data/`. Keep
their source records with them. Rebuild all assets after changing the generator.

The `intro` mode reaches its final still composition in six seconds. Both hero
variants use an 855 by 300 canvas. The older `generate_wordmark.py` remains an
independent ASCII experiment; its modes and `WORDMARK_*` overrides do not control
the profile build. Write those experiments to separate files. Validation permits
the dedicated hero's opacity, fill, and translation animations, while rejecting
scripts, external resources, link mutation, and animation in static artifacts.
See [the renderer notes](3d-ascii-wordmark.md).

## CI

`Validate profile` installs the complete dependency set on Ubuntu and Windows.
Tests cover generation from an unrelated working directory, deterministic output,
all committed assets' freshness, SVG safety, reduced-motion source references,
and read-only workflow permissions. Missing renderer dependencies fail instead of
silently skipping the wordmark checks.

Freshness comparisons normalize checkout line endings so Windows CRLF does not
produce a false difference; repeated generated output must still be byte-identical.
The workflow also regenerates all assets and checks that Git sees no asset changes.

The workflow has `contents: read` and never publishes or commits generated files.
Action references are pinned to full commit SHAs. When upgrading them, verify the
release and replacement SHA against the official action repository.
