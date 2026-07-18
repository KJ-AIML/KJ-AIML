# Maintenance

## Local commands

From the repository root:

```bash
python scripts/fetch_contributions.py
python scripts/generate_all.py
python scripts/validate_profile.py
python -m pytest -q
```

Use `STATIC=1 python scripts/generate_all.py` on macOS/Linux or `$env:STATIC='1'; python scripts/generate_all.py` in PowerShell to omit one-time SVG animations. Fetching uses the public GitHub contribution HTML, a descriptive user agent, a timeout, bounded retries, and only replaces the JSON after a validated parse.

## Content and links

Update the copy in `README.md` and the rows in `scripts/generate_system_card.py`. Update featured repository links and descriptions only after checking their public repository pages. Keep private architecture, credentials, and unsupported metrics out of both Markdown and SVGs.

## Workflow

Run the `Refresh profile contribution art` workflow manually with `workflow_dispatch` when desired. It stages only `data/contributions.json` and `assets/contribution-heatmap.svg`. The validation workflow runs tests, regeneration, determinism, SVG safety, and README reference checks.

If GitHub changes the calendar markup, save a small HTML response in `data/fixtures/`, update `ContributionParser` in `scripts/contributions.py`, and run the parser tests before changing the workflow.

Action references are pinned to full commit SHAs with the corresponding release in a comment. When upgrading, verify the release tag and replacement SHA from the official action repository, then update both workflow files together.
