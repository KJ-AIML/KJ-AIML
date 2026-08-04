# KJ-AIML profile design system

## Concept

The profile is an AI infrastructure command center: a 3D ASCII wordmark, a terminal boot screen, a compact system identity card, a vertical execution map, and a contribution trace. Sections are separated by shell-prompt headings (`KJ@AI-INFRA ~ $ ./systems.sh`) so the README reads as one console session. It uses the reference article's self-contained SVG/SMIL methodology while keeping the content and composition original.

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

The contribution scale uses GitHub's calendar greens so the graph reads the way it does on every other profile, and the traffic-light window dots (`#ff5f56` / `#ffbd2e` / `#27c93f`) are the same convention.

The ASCII wordmark itself stays neutral. Its shading *is* the density ramp, and a hue there would flatten the face-versus-wall contrast that carries the depth — see [3d-ascii-wordmark.md](3d-ascii-wordmark.md).

Typography is a system monospace stack so GitHub renders the assets without external fonts. The main grid is 860px wide; the identity card and system map are 420px wide, the heatmap is 860px wide, and the wordmark is 855px wide (rendered at display size — see [3d-ascii-wordmark.md](3d-ascii-wordmark.md)).

## Motion and accessibility

Animations are SMIL-only and freeze on a fully readable state. The panel animations play once; the wordmark is the one exception — its boot sequence plays once and hands over to a rock loop that never leaves the word illegible. Base opacity remains readable even if GitHub declines to animate the SVG. `STATIC=1` omits animated elements for screenshots, reduced-motion review, and deterministic fallback assets. No JavaScript, remote fonts, external stylesheets, or remote images are used.

## Content rules

Plain Markdown carries the meaningful identity and project descriptions. Repository claims link to public sources and avoid stars, adoption numbers, or status claims that cannot be verified. Contribution metrics are limited to the displayed public period.

## Difference from the reference

The article's methodology informed the self-contained SVG generators, public contribution parsing, and scheduled refresh. This profile uses a restrained infrastructure console, no portrait, no third-party widgets, no looping typewriter effect, and a source-backed project list tailored to KJ-AIML.
