# KJ-AIML profile design

The profile pairs sculpted terminal artwork with ordinary Markdown. A visitor can
read the name, focus, projects, contribution evidence, and contact link immediately,
including when images are unavailable.

## Reading order

1. Name, engineering focus, location, and LinkedIn.
2. A six-second Braille hand gesture and wordmark, with a still alternative.
3. Production experience and the Axtra Intellion venture.
4. Four current projects and a merged contribution outside this account.
5. Working stack and an invitation to connect.

Project descriptions use single-column paragraphs so they wrap naturally on a
phone. Technologies support the work examples. Public claims and their verification
sources live in [the source notes](profile-refresh/sources.md).

## Artwork

The main profile uses [the animated wordmark](../assets/kj-wordmark-animated.svg).
Two shaded hands reach toward a small green signal, separate, and give way to a
pearl and lavender `KJ-AIML` mark. The six-second sequence settles into the still
composition. The owner supplied [pi-ter](https://github.com/KJ-AIML/pi-ter) as
the reference after rejecting the earlier boot-log design. The hand fields and
gesture come from that repository; the new wordmark is generated locally.

The name, headline, experience, and links remain in ordinary Markdown and never
wait for the animation. A picture source selects the
[static wordmark](../assets/kj-wordmark.svg) when the visitor requests reduced
motion. A visible still-artwork link offers the same alternative manually. The
animated SVG also contains a visible rest frame for viewers without SMIL support.
Both variants are 855 by 300, preserving the layout when motion is disabled.

The optional panel below preserves the CLI visual language for reuse. It is a
static illustration. It carries no information that is necessary to understand
the profile.

<img src="../assets/kj-agent-cli.svg" width="855" alt="Static terminal illustration describing agent infrastructure and the Python, Rust, and TypeScript stack" />

All SVGs include a title and description and contain no scripts or remote
resources. Only the dedicated animated hero uses SMIL; the still wordmark and
CLI illustration remain static. The hero consists entirely of artwork and the
owner's name.

## Palette and typography

| Token | Value | Use |
| --- | --- | --- |
| Background | `#080b0f` | Open canvas |
| Contact | `#9af2b4` | Hand signal and brief greeting |
| Front face | Pearl gray to white | Lit letter surfaces |
| Extrusion | Muted lavender | Depth behind the letters |
| Caption | `#a9a6b7` | Owner's name |

The wordmark uses dot density, bevel lighting, and an offset extrusion. Its
geometry is generated from the bundled IBM Plex Mono
Bold font, with the font's license and source recorded in
[assets/fonts](../assets/fonts/). It does not depend on an installed operating
system font. Dots are round SVG strokes, so the visitor does not need a Braille
font. Small captions use a local monospace fallback; no font is downloaded.

See [the renderer notes](3d-ascii-wordmark.md) and
[maintenance instructions](maintenance.md) for reproducible generation and checks.
