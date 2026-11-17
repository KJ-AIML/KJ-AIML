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
- The main profile embeds only the wordmark. The agent panel remains an
  optional static design artifact, documented outside the main profile.

## Visual/build contract

- Keep `assets/kj-wordmark.svg` and `assets/kj-agent-cli.svg` static, and generate
  `assets/kj-wordmark-animated.svg` for the default README hero.
- The owner explicitly requested their animation back on 2026-11-17. Restore
  the boot sequence, particle transitions, and rocking ASCII wordmark. Essential
  profile copy stays readable in Markdown throughout the animation.
- Select the static wordmark with a `prefers-reduced-motion` picture source and
  provide a visible still-image link. The animated SVG must show its rest frame
  if SVG animation is unsupported. No scripts or external resources in any SVG.
- Keep the static wordmark compact (height <= 220 at width 855). The animated
  canvas retains the space its intro needs, with a 500 KB asset limit.
- Agent panel: compact static illustration with factual generic focus/stack, no
  simulated thinking delay, keyboard shortcuts, fake version, or obsolete status.
- Bundle an openly licensed bold font and its license under `assets/fonts/`.
  The wordmark's default font must use that file on every OS, not host font search.
- `python scripts/generate_all.py` regenerates all three committed assets.
  `STATIC=1` remains a compatibility alias for that complete build; static and
  animated outputs now have separate filenames. Root resolution is independent of cwd.
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
2. Regenerate all artifacts and verify byte-for-byte freshness. A changed
   generator without rebuilt output must fail validation.
3. Check static artifacts for readable text and absence of animation. Check the
   animated hero's declared animation targets and its no-animation fallback. All
   assets require dimensions, size budgets, metadata, and no active/external content.
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

## Visual direction correction (owner reference, 2026-11-17)

The owner rejected the restored boot-log hero and supplied
`https://github.com/KJ-AIML/pi-ter` as the visual reference. This supersedes the
boot/particle/rock requirement above. Use the sculpted Braille hand artwork and
short, deliberate gesture from that repository, followed by an original shaded
`KJ-AIML` wordmark. Keep a black canvas, pearl highlights, lavender depth, and
one green contact accent. The intro resolves in six seconds. No terminal window
chrome, fabricated telemetry, or repeated full-scene boot loop.

This is a focused S1 artwork change: a new deterministic Python generator plus
locally vendored hand fields, the two generated wordmark assets, build selection,
README image description, and maintenance notes. Profile facts and the optional
CLI illustration are outside the change. The old renderer remains available for
experiments, with its existing animation tests. No dependencies are added.

Both new variants use the same 855 by 300 canvas to avoid a layout jump when
reduced motion is selected. The static height allowance changes accordingly.
Keep a visible static fallback when SMIL is unavailable and keep the 500 KB
asset limit. The generator emits ordinary geometry rather than requiring an
installed Braille font. Record the upstream revision and artwork provenance.

Done: inspect key animation frames and the final composition at desktop/phone
widths, verify the finite timeline reaches the still frame, run the existing
generation/freshness/safety checks, and refresh the local preview. Browser
playback remains a separate manual check when automated browser access is
unavailable. Rollback is limited to this visual change; no publishing is included.

## Hero and layout revision (owner-approved, 2026-11-17)

The owner reviewed live previews and replaced the sculpted `KJ-AIML` hero. Where
this section and the ones above differ, this one applies.

- **Hero:** the pi-ter hands stay and are now articulated, with an elbow, a
  wrist, and finger joints, inside the profile's terminal window. They touch, a
  spark forms the handle `kjct0s_` as an extruded dot wordmark, and `Hello KJ`
  appears. The owner chose the handle over `KJ-AIML`. The animation and its still
  share an 855 by 450 canvas.
- **Rules kept:** essential facts stay in Markdown; reduced motion selects the
  still; the animated file shows its final frame without SVG animation; nothing
  loops; no scripts or external resources; the 500 KB asset limit.
- **Validation:** the hero may also rotate groups and move a gradient's
  endpoints. Scaling, skewing, and every other animated attribute stay rejected.
- **Companies:** the owner is also Co-founder & CTO of Talvyn Labs, which is
  named and linked ahead of Axtra Intellion.
- **Layout:** link buttons under the headline; six projects as picture cards
  with one sentence each; a row of technology icons with the full stack folded
  beneath it. Every image is a local file. Icons use each brand's colour on a
  dark tile, which the owner picked over grey marks and over solid colour tiles.
- **Files:** `scripts/generate_hello.py` and `scripts/generate_icons.py` are
  added. `scripts/generate_braille.py` and the two `kj-wordmark` images are removed.
- **Not included:** publishing, GitHub account settings, pinned repositories,
  and other repositories.
