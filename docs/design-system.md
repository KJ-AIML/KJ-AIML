# KJ-AIML profile design system

## Concept

The profile is an AI infrastructure command center: a terminal boot screen, a compact system identity card, a vertical execution map, and a contribution trace. It uses the reference article's self-contained SVG/SMIL methodology while keeping the content and composition original.

## Tokens

| Token | Value | Use |
| --- | --- | --- |
| Background | `#0D1117` | SVG canvas |
| Elevated panel | `#161B22` | Cards and nodes |
| Primary text | `#E6EDF3` | Body copy |
| Muted text | `#8B949E` | Metadata |
| Border | `#30363D` | Structure |
| Mint | `#59F3C0` | Primary signal |
| Blue | `#7AA2F7` | Secondary signal |
| Yellow | `#F2CC60` | Status/warning signal |

Typography is a system monospace stack so GitHub renders the assets without external fonts. The main grid is 860px wide; the identity card and system map are 420px wide, and the heatmap is 860px wide.

## Motion and accessibility

Animations are SMIL-only, play once, and freeze on a fully readable state. Base opacity remains readable even if GitHub declines to animate the SVG. `STATIC=1` omits animated elements for screenshots, reduced-motion review, and deterministic fallback assets. No JavaScript, remote fonts, external stylesheets, or remote images are used.

## Content rules

Plain Markdown carries the meaningful identity and project descriptions. Repository claims link to public sources and avoid stars, adoption numbers, or status claims that cannot be verified. Contribution metrics are limited to the displayed public period.

## Difference from the reference

The article's methodology informed the self-contained SVG generators, public contribution parsing, and scheduled refresh. This profile uses a restrained infrastructure console, no portrait, no third-party widgets, no looping typewriter effect, and a source-backed project list tailored to KJ-AIML.
