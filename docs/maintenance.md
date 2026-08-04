# Maintenance

## Local commands

From the repository root:

```bash
python scripts/generate_all.py      # rebuilds assets/kj-agent-cli.svg
python scripts/validate_profile.py
python -m pytest -q
```

Use `STATIC=1 python scripts/generate_all.py` on macOS/Linux, or `$env:STATIC='1'; python scripts/generate_all.py` in PowerShell, to omit animations. Static builds are the right output for screenshots and for reduced-motion review — see [design-system.md](design-system.md).

## The wordmark is built separately

`assets/kj-wordmark.svg` sits outside `generate_all.py`. It only changes when its text, font or framing does, and its renderer needs numpy and Pillow, which CI does not install:

```bash
python -m pip install -r scripts/requirements-wordmark.txt
python scripts/generate_wordmark.py
```

That exclusion has a cost: CI regenerates and diff-checks everything `generate_all.py` builds, so those assets cannot go stale — the wordmark can. It happened once, when renaming the shell prompt updated the generator and left the committed SVG showing the old host. `tests/test_wordmark_freshness.py` now regenerates the wordmark and fails if the committed bytes differ.

The same file asserts `HANDOFF >= BOOT_END`. `HANDOFF` in `scripts/generate_agent_cli.py` is a hand-kept copy of `BOOT_END` in `scripts/generate_wordmark.py`, because importing across the two would drag numpy into CI; the test is what keeps them in step. Both tests `importorskip` numpy and Pillow, so they skip in CI and guard the machine that actually rebuilds the asset.

Details in [3d-ascii-wordmark.md](3d-ascii-wordmark.md).

## Content and links

Update the copy in `README.md` and the `ROWS` table in `scripts/generate_agent_cli.py` — that table is what the agent panel streams. Update featured repository links and descriptions only after checking their public repository pages. Keep private architecture, credentials, and unsupported metrics out of both Markdown and SVGs.

## Workflow

`Validate profile` is the only workflow. It runs the tests, regenerates the deterministic assets, diff-checks them, and validates README references and SVG safety. It holds `contents: read` and writes nothing; `tests/test_workflows.py` asserts that no workflow ever gains write access without a deliberate decision.

A second workflow used to refresh a contribution heatmap on a nightly cron. It was removed along with the heatmap, the fetcher, and the parser when the calendar left the README — it was fetching GitHub every night to commit a 68 KB asset nothing rendered. All of it is recoverable from git history if the calendar comes back.

Action references are pinned to full commit SHAs with the corresponding release in a comment. When upgrading, verify the release tag and replacement SHA from the official action repository.
