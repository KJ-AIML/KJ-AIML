# KJ-AIML profile design system

## Concept

The profile is one console session, and only two panels carry it. A 3D ASCII wordmark boots at the top, then an AI agent CLI answers `whoami` — the prompt types itself, a thinking badge spins, and the answer streams in line by line, the way Claude Code or Grok Build render a turn. Sections are separated by shell-prompt headings (`KJ@AI-ENGINEER ~ $ ./systems.sh`) so the page reads as a continuous terminal. It uses the reference article's self-contained SVG/SMIL methodology while keeping the content and composition original.

The agent panel's welcome card carries a small "KJ" mark that is not a separate drawing — it is `KJ` run through the wordmark's own renderer, extruded and lit and rasterized to the same density ramp, then baked into `generate_agent_cli.py` as a literal. Baked rather than computed because that renderer needs numpy and Pillow and CI installs neither; the re-bake command is in the comment above `LOGO`. The two marks are the same object at two sizes, which is why they read as one system rather than as a logo and a picture of a logo.

The agent panel (`scripts/generate_agent_cli.py`) replaced a side-by-side identity card and system map. Two half-width panels competing at the same level read as a dashboard rather than as a session, and the split forced the eye to choose a starting point; a single streaming answer has one reading order and carries the same content.

Streaming is a per-line `clipPath` whose width steps left to right — that is what makes it read as characters arriving rather than as a row fading in. The prompt types with the same trick in discrete one-cell steps, so the caret always lands on a glyph boundary instead of halfway through a letter.

### Attention handoff

Every SVG on the page starts animating the moment it loads, so two animated panels compete and the reader has to pick one. The agent panel's welcome card and a blinking caret land at 0.8s — the panel is never blank, it reads as a CLI idling for input — and the session itself holds until `HANDOFF`, after the wordmark above has finished booting. The blinking caret is what makes the wait read as *waiting* rather than as a broken image.

`HANDOFF` must stay at or above `generate_wordmark.BOOT_END` (13.5s). It is duplicated as a constant rather than imported, because `generate_wordmark` needs numpy and Pillow and CI installs neither. If the wordmark's intro timing changes, move `HANDOFF` with it.

## Tokens

Every asset is a terminal window: a `#111722` → `#0d1117` vertical gradient, a `#30363d` frame, a titlebar carrying traffic-light dots and the command that would have produced the panel. `terminal_chrome()` in `scripts/svg_common.py` draws all of it, and each generator wraps its content in `translate(0, CHROME_H)` so gaining a titlebar does not move any interior coordinate.

Hierarchy is carried by brightness rather than hue. The wordmark shades an ASCII density ramp, and a saturated fill beside it flattens the face-versus-wall contrast that reads as depth, so the whole profile stays neutral and the eye follows weight instead of colour.

| Token | Value | Use |
| --- | --- | --- |
| Background | `#0d1117` | SVG canvas, bottom of the panel gradient |
| Panel top | `#111722` | Top of the panel gradient |
| Elevated panel | `#161b22` | Cards and nodes |
| Border | `#30363d` | Window frame and rules |
| Signal | `#e6edf3` | Brightest step, the line that matters most |
| Text / Ink | `#c9d1d9` | Body copy |
| Dim | `#8b949e` | De-emphasised but still readable |
| Muted | `#7d8590` | Metadata, captions, titlebar labels |

Colour is reserved for state, never decoration. The static panels stay neutral; the wordmark's boot sequence uses GitHub's own status colours so each row and panel reads as a condition rather than as styling:

| Accent | Value | Means |
| --- | --- | --- |
| `ok` | `#3fb950` | Passed, resolved, verified |
| `info` | `#79c0ff` | Identifiers and labels |
| `warn` | `#d29922` | In progress, external dependency |
| `bad` | `#f85149` | Alarm — pulses, and only alarm panels pulse |

The traffic-light window dots (`#ff5f56` / `#ffbd2e` / `#27c93f`) are the one other place hue appears, and they are a convention rather than a decision.

The ASCII wordmark itself stays neutral. Its shading *is* the density ramp, and a hue there would flatten the face-versus-wall contrast that carries the depth — see [3d-ascii-wordmark.md](3d-ascii-wordmark.md).

Typography is a system monospace stack so GitHub renders the assets without external fonts. The main grid is 860px wide: the agent panel is 860, and the wordmark is 855 because it renders at display size — see [3d-ascii-wordmark.md](3d-ascii-wordmark.md).

## Motion and accessibility

Animations are SMIL-only and freeze on a fully readable state. The panel animations play once; the wordmark is the one exception — its boot sequence plays once and hands over to a rock loop that never leaves the word illegible. Base opacity remains readable even if GitHub declines to animate the SVG. No JavaScript, remote fonts, external stylesheets, or remote images are used.

### Motion, honestly

**`prefers-reduced-motion` is not honoured, and cannot be.** An earlier version of `svg_head()` shipped a `@media (prefers-reduced-motion: reduce) { .animated { animation: none } }` rule. It did nothing twice over: no element ever carried `class="animated"`, and CSS `animation` has no effect on SMIL `<animate>` elements — no CSS property can stop them. The rule has been removed rather than left as decoration that reads like a feature.

What that leaves: the wordmark's rock loop repeats indefinitely inside an `<img>`, which a visitor cannot pause. That is a real accessibility cost on a public page and it is a deliberate trade, not an oversight. Two ways out if it should be paid down:

- Give the rock a finite `repeatCount` so it settles on the rest pose. Costs the perpetual motion.
- Ship the `STATIC=1` renders, which omit animated elements entirely. `STATIC=1 python scripts/generate_all.py` still produces every panel in a fully readable frozen state, and is the right build for screenshots and reduced-motion review.

## Content rules

Plain Markdown carries the meaningful identity and project descriptions. Repository claims link to public sources and avoid stars, adoption numbers, or status claims that cannot be verified.

A contribution calendar used to sit at the bottom of the page. It was removed because a heatmap of squares says nothing a reader can act on, and keeping it accurate cost a nightly job that fetched GitHub and committed a 68 KB asset. The generators, the parser and the workflow went with it; git history has them if that judgement changes.

## Difference from the reference

The article's methodology informed the self-contained SVG generators and the deterministic build. This profile uses a restrained infrastructure console, no portrait, no third-party widgets, and a source-backed project list tailored to KJ-AIML.
