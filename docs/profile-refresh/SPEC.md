# Profile refresh

## Objective and scope

Make the public GitHub profile immediately understandable, useful on a phone,
and supported by public evidence. Preserve the original terminal/ASCII identity.
This is a local, reversible profile and asset-build change. Publishing, changing
GitHub account settings, and editing other repositories are outside this change.

## Content contract

- Essential identity, focus, stack, project descriptions, evidence, and contact
  links live in ordinary Markdown. No facts depend on an image or animation.
- Feature current public projects: Heli-Harness, MemCtrl, ALMS, and Samo. Describe
  concrete behavior and link to source, quick starts, or releases.
- Include the verified merged OpenIDEA contribution, with its original PR link.
- Use only corroborated professional facts. Resolve conflicting employment and
  alias information with the owner before adding it. Do not copy private data,
  contact phone numbers, unsupported metrics, or claims from search snippets.
- The main profile embeds only the compact wordmark. The agent panel remains an
  optional static design artifact, documented outside the main profile.

## Visual/build contract

- Keep `assets/kj-wordmark.svg` and `assets/kj-agent-cli.svg` as generated artifacts.
- Both committed artifacts are fully readable without animation and contain no
  animation elements, JavaScript, external resources, or fake interactive controls.
- Wordmark: preserve 3D ASCII construction; default static, compact framing, target
  height <= 220 at width 855. Keep long animation only as an explicit legacy option
  if practical. Do not introduce new remote widgets or bitmap hero artwork.
- Agent panel: compact static illustration with factual generic focus/stack, no
  simulated thinking delay, keyboard shortcuts, fake version, or obsolete status.
- Bundle an openly licensed bold font and its license under `assets/fonts/`.
  The wordmark's default font must use that file on every OS, not host font search.
- `python scripts/generate_all.py` regenerates both committed assets. `STATIC=1`
  has the same complete static behavior. Root resolution is independent of cwd.
- The existing `generate(path: Path, static: bool = ...)` CLI-panel entry point and
  `generate(out: Path, mode: str = ..., ...)` wordmark entry point remain callable.

## Integration and ownership

- Controller: README, research/source notes, design/maintenance documentation,
  `scripts/generate_all.py`, integration, and final renders/review.
- Artwork worktree: `scripts/generate_wordmark.py`,
  `scripts/generate_agent_cli.py`, `scripts/svg_common.py`, and `assets/**` only.
- Quality worktree: `.github/workflows/validate-profile.yml`, `tests/**`,
  `scripts/validate_profile.py`, and dependency requirements only.
- Dependencies remain Python 3.12, pytest, PyYAML, NumPy, and Pillow with pinned
  versions. CI installs the full renderer requirements and skips no test module.

## Verification

1. Run all tests with the documented full dependency set.
2. Regenerate both artifacts and verify byte-for-byte freshness. A changed
   generator without rebuilt output must fail validation.
3. Check both static artifacts for readable text, dimensions, file-size budget,
   title/description, and absence of active/external SVG content.
4. Validate Markdown and HTML local references and the profile's public links.
5. Render assets at full width and phone width. Review profile text independently
   of images. Live browser checks are additional when a browser is available.
6. Confirm only scoped changes remain in git. Restore via reverting the scoped
   commits if needed; never overwrite unrelated work.

## Risks and acceptance

The primary risks are stale generated assets, platform-dependent fonts, hiding
essential facts in decorative artwork, and overstating public evidence. Font
vendoring, complete CI, ordinary Markdown, and source links address these risks.
No numerical rating is a guarantee; acceptance is a readable, truthful, maintained
profile with reproducible artifacts and current passing checks.

## Positioning addendum (owner-confirmed 2026-11-17)

- **Audience:** people hiring for AI platform or AI engineering roles, and
  potential collaborators. kjsc.dev says the owner is open to both.
- **Headline:** the CV's "AI engineer for LLM systems, agents, and inference
  infrastructure", plus "Co-founder & CTO at Axtra Intellion".
- **Principle:** "Make it exist first, make it production-ready next." This
  replaces the older "make it good later" wording.
- **Employer work** is described by domain (LLM serving, Thai speech-to-text with
  PII masking, document and compliance AI, agent-assist), without employer
  names. The CV on kjsc.dev carries names and dates.
- **Axtra Intellion (AXTL)** is named and described. Its staging URL stays
  unlinked until it serves a public page.
- **Order:** identity → production work → AXTL → open source → stack → contact.
  Production experience leads because it is the strongest signal for the target
  roles.
