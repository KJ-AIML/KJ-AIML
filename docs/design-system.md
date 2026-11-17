# KJ-AIML profile design

The profile pairs a terminal/ASCII identity with ordinary Markdown. A visitor can
read the name, focus, projects, contribution evidence, and contact link immediately,
including when images are unavailable.

## Reading order

1. Name, engineering focus, location, and LinkedIn.
2. The animated ASCII hero, with a still alternative for reduced motion.
3. Production experience and the Axtra Intellion venture.
4. Four current projects and a merged contribution outside this account.
5. Working stack and an invitation to connect.

Project descriptions use single-column paragraphs so they wrap naturally on a
phone. Technologies support the work examples. Public claims and their verification
sources live in [the source notes](profile-refresh/sources.md).

## Artwork

The main profile uses [the animated wordmark](../assets/kj-wordmark-animated.svg):
the original boot sequence, particle transitions, "WELCOME TO MY AI WORLD", and
a rocking 3D ASCII mark. Its 855 × 312 canvas preserves the space the intro needs.
The owner explicitly asked to keep this animation after reviewing the static draft.

The name, headline, experience, and links remain in ordinary Markdown and never
wait for the animation. A picture source selects the compact
[static wordmark](../assets/kj-wordmark.svg) when the visitor requests reduced
motion. A visible still-artwork link offers the same alternative manually. The
animated SVG also contains a visible rest frame for viewers without SMIL support.

The optional panel below preserves the CLI visual language for reuse. It is a
static illustration. It carries no information that is necessary to understand
the profile.

<img src="../assets/kj-agent-cli.svg" width="855" alt="Static terminal illustration describing agent infrastructure and the Python, Rust, and TypeScript stack" />

All SVGs include a title and description and contain no scripts or remote
resources. Only the dedicated animated hero uses SMIL; the compact wordmark and
CLI illustration remain static. The hero's terminal readouts describe its visual
construction rather than pretending to fetch live profile statistics.

## Palette and typography

| Token | Value | Use |
| --- | --- | --- |
| Background | `#0d1117` | Canvas |
| Panel top | `#111722` | Terminal gradient |
| Border | `#30363d` | Frame and rules |
| Signal | `#e6edf3` | Primary emphasis |
| Text | `#c9d1d9` | Body copy |
| Dim | `#8b949e` | Secondary copy |
| Muted | `#7d8590` | Chrome and captions |

The wordmark uses glyph density and neutral shades to distinguish letter faces
from extruded walls. Its geometry is generated from the bundled IBM Plex Mono
Bold font, with the font's license and source recorded in
[assets/fonts](../assets/fonts/). It does not depend on an installed operating
system font. SVG text uses a local monospace fallback stack and fixed text lengths;
no font is downloaded when a visitor opens the profile.

See [the renderer notes](3d-ascii-wordmark.md) and
[maintenance instructions](maintenance.md) for reproducible generation and checks.
