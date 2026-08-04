"""Render the profile as an AI agent CLI session.

The panel boots like an agent terminal (Claude Code / Grok Build / Codex): a
welcome card, then `whoami` types itself at the prompt, a thinking badge spins,
and the answer streams in line by line.

Streaming is a per-line clipPath whose width steps left to right, which is what
makes it read as characters arriving rather than as a row fading in. Typing uses
the same trick with discrete steps of one cell, so the caret lands on glyph
boundaries. No JavaScript -- GitHub runs SMIL in <img> but never scripts.
"""

from __future__ import annotations

import os
from pathlib import Path

from svg_common import (ACCENT, BG2, BORDER, CHROME_H, HOST, PANEL,
                        close_svg, svg_head, terminal_chrome, xml)

WIDTH = 860
HEIGHT = 550
CONTENT_H = HEIGHT - CHROME_H   # everything below sits in the translated group
CELL = 8.4              # monospace advance at the body size, for caret steps
PROMPT = "whoami"

# "KJ" put through the wordmark's own renderer -- extruded to a 3D slab, lit, and
# rasterized to the density ramp -- then baked here as a literal. Same pipeline as
# the panel above, so the two marks are the same object at two sizes.
#
# Baked rather than computed because that renderer needs numpy and Pillow, which
# CI does not install. To re-bake (e.g. a different pose or width):
#
#   WORDMARK_TEXT=KJ WORDMARK_COLS=22 WORDMARK_ROW_MARGIN=0 \
#       python scripts/generate_wordmark.py --preview
LOGO = [
    "SSS   *SSS      *sss",
    "SSS *SSSSS      =sss",
    "SSSSSSSSS       =sss",
    "SSSSSSS         =sss",
    "SSSSSSSS    **ss=sss",
    "SSSS SSSS   *sssssss",
    "SSS   SSSSs `sssssss",
    "SSS    SSS     ss",
]
LOGO_SIZE = 10
LOGO_STEP = 12
LOGO_CELL = 6.0         # advance per cell; textLength pins it so the grid holds
LOGO_RAMP = " .`:-=+*csS#%@"
LOGO_BUCKET = [0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 3, 3, 3, 3]
LOGO_SHADE = ["muted", "dim", "text", "signal"]


def logo_runs(line: str) -> list[tuple[int, str, int]]:
    """Split a baked row into (column, text, shade) runs of one tone each.

    Blanks stay inside the open run instead of breaking it, the same rule the
    wordmark uses, so a row costs a handful of elements rather than one per cell.
    """
    runs: list[tuple[int, str, int]] = []
    buf: list[str] = []
    start, bucket = 0, -1
    for col, char in enumerate(line):
        if char == " ":
            if buf:
                buf.append(" ")
            continue
        shade = LOGO_BUCKET[LOGO_RAMP.index(char)]
        if buf and shade != bucket:
            runs.append((start, "".join(buf).rstrip(), bucket))
            buf = []
        if not buf:
            start, bucket = col, shade
        buf.append(char)
    if buf:
        runs.append((start, "".join(buf).rstrip(), bucket))
    return [run for run in runs if run[1]]

ROWS = [
    ("Role", "AI Engineer · Founder", "ok"),
    ("Focus", "Agent infrastructure", "info"),
    ("Building", "Axtra Intellion", "warn"),
    ("Core", "ALMS · AXGA", "info"),
    ("Exploring", "Tracer", "warn"),
    ("Stack", "Python · Rust · TypeScript", "text"),
    ("Infra", "GCP · Docker · E2B", "text"),
    ("Mode", "Remote-first · Bangkok", "text"),
    ("Principle", "Build it. Validate it. Reliable.", "ok"),
]

# ---- timeline (seconds) ---------------------------------------------------
# Both panels start animating the moment the page loads, so without a handoff
# they compete and the eye has to pick one. The card and a blinking caret land
# early -- the panel is never blank, it just reads as a CLI waiting for input --
# and the session itself holds until the wordmark above has finished its boot.
#
# HANDOFF must stay >= generate_wordmark.BOOT_END. It is duplicated rather than
# imported because that module needs numpy/Pillow, which CI does not install.
HANDOFF = 13.6          # wordmark BOOT_END is 13.5s
T_CARD = 0.8            # welcome card lands, caret starts blinking
T_TYPE = HANDOFF        # caret starts typing
TYPE_STEP = 0.11        # per character
T_THINK = T_TYPE + len(PROMPT) * TYPE_STEP + 0.25
THINK_DUR = 0.85
T_STREAM = T_THINK + THINK_DUR
LINE_STEP = 0.26        # gap between streamed lines
LINE_DUR = 0.34         # how long one line takes to arrive
T_TAIL = T_STREAM + len(ROWS) * LINE_STEP + 0.2

SPINNER = ["|", "/", "-", "\\"]


def generate(path: Path, static: bool = False) -> None:
    out = [svg_head(
        "KJ agent CLI session",
        "An AI agent command-line session: the prompt whoami is typed, then the "
        "answer streams in with role, focus, stack, infrastructure and working "
        "principle for KJ, an AI Engineer and Founder.",
        WIDTH, HEIGHT)]
    out.append(terminal_chrome(WIDTH, HEIGHT, f"{HOST}: ~$ ./kj-agent"))
    out.append(f'<g transform="translate(0,{CHROME_H})">')

    def reveal(at: float) -> str:
        """Open a group that fades in at `at`, or a plain one in static mode."""
        if static:
            return "<g>"
        return f'<g opacity="0"><set attributeName="opacity" to="1" begin="{at:.2f}s"/>'

    # ---- welcome card -----------------------------------------------------
    out.append(reveal(T_CARD))
    out.append(f'<rect x="24" y="22" width="{WIDTH - 48}" height="118" rx="8" '
               f'fill="{BG2}" stroke="{BORDER}"/>')
    for i, line in enumerate(LOGO):
        y = 40 + i * LOGO_STEP
        for col, body, shade in logo_runs(line):
            out.append(
                f'<text x="{44 + col * LOGO_CELL:.0f}" y="{y}" font-size="{LOGO_SIZE}" '
                f'class="{LOGO_SHADE[shade]}" xml:space="preserve" '
                f'textLength="{len(body) * LOGO_CELL:.0f}" lengthAdjust="spacing">'
                f'{xml(body)}</text>')
    out.append(f'<text x="190" y="52" font-size="15" font-weight="700" class="text">'
               f'kj-agent<tspan class="muted" font-weight="400"> 0.4.2</tspan></text>')
    out.append(f'<text x="190" y="80" font-size="13" class="warn">'
               f'Agent infrastructure session ready.</text>')
    out.append(f'<text x="190" y="100" font-size="13" class="muted">'
               f'Ask anything. Answers stream from the profile.</text>')
    for i, (item, key) in enumerate([("Selected systems", "ctrl+s"),
                                     ("Contact", "ctrl+k")]):
        out.append(f'<text x="600" y="{80 + i * 20}" font-size="12" class="text">{item}</text>')
        out.append(f'<text x="{WIDTH - 44}" y="{80 + i * 20}" font-size="12" '
                   f'class="muted" text-anchor="end">{key}</text>')
    out.append("</g>")

    # ---- prompt line ------------------------------------------------------
    prompt_y = 186
    text_x = 68
    out.append(reveal(T_CARD))
    out.append(f'<text x="44" y="{prompt_y}" font-size="15" class="ok">&#8250;</text>')
    if static:
        out.append(f'<text x="{text_x}" y="{prompt_y}" font-size="15" class="text">{PROMPT}</text>')
    else:
        # discrete width steps of one cell: the reveal lands on glyph boundaries
        steps = ";".join(f"{i * CELL:.1f}" for i in range(len(PROMPT) + 1))
        keys = ";".join(f"{i / len(PROMPT):.4f}" for i in range(len(PROMPT) + 1))
        out.append(f'<clipPath id="typing"><rect x="{text_x}" y="{prompt_y - 15}" '
                   f'height="20" width="0"><animate attributeName="width" '
                   f'values="{steps}" keyTimes="{keys}" calcMode="discrete" '
                   f'dur="{len(PROMPT) * TYPE_STEP:.2f}s" begin="{T_TYPE:.2f}s" '
                   f'fill="freeze"/></rect></clipPath>')
        out.append(f'<text x="{text_x}" y="{prompt_y}" font-size="15" class="text" '
                   f'clip-path="url(#typing)">{PROMPT}</text>')
        # The caret blinks at column 0 through the whole handoff wait, so the
        # panel reads as a CLI idling for input rather than as a broken image.
        # Then it walks with the text and leaves when the agent takes over.
        caret_x = ";".join(f"{text_x + i * CELL:.1f}" for i in range(len(PROMPT) + 1))
        out.append(
            f'<g><set attributeName="opacity" to="0" begin="{T_THINK:.2f}s"/>'
            f'<rect y="{prompt_y - 13}" width="8" height="16" fill="{ACCENT["ok"]}" '
            f'x="{text_x}">'
            f'<animate attributeName="x" values="{caret_x}" keyTimes="{keys}" '
            f'calcMode="discrete" dur="{len(PROMPT) * TYPE_STEP:.2f}s" '
            f'begin="{T_TYPE:.2f}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
            f'dur="0.9s" repeatCount="indefinite"/></rect></g>')
    out.append("</g>")   # closes reveal(T_CARD) around the prompt line

    # ---- thinking badge ---------------------------------------------------
    if not static:
        badge_y = 222
        out.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{T_THINK:.2f}s"/>'
                   f'<set attributeName="opacity" to="0" begin="{T_STREAM:.2f}s"/>')
        out.append(f'<rect x="44" y="{badge_y - 15}" width="132" height="22" rx="11" '
                   f'fill="{PANEL}" stroke="{BORDER}"/>')
        for i, frame in enumerate(SPINNER):
            out.append(
                f'<text x="58" y="{badge_y}" font-size="12" class="warn" opacity="0">'
                f'{xml(frame)}<animate attributeName="opacity" values="0;1;0" '
                f'keyTimes="0;{i / len(SPINNER):.4f};{(i + 1) / len(SPINNER):.4f}" '
                f'calcMode="discrete" dur="0.48s" begin="{T_THINK:.2f}s" '
                f'repeatCount="indefinite"/></text>')
        out.append(f'<text x="74" y="{badge_y}" font-size="12" class="muted">Thinking…</text>')
        out.append("</g>")

    # ---- streamed answer --------------------------------------------------
    for i, (label, value, tone) in enumerate(ROWS):
        y = 258 + i * 23
        begin = T_STREAM + i * LINE_STEP
        clip = ""
        if not static:
            out.append(f'<clipPath id="ln{i}"><rect x="44" y="{y - 16}" height="21" width="0">'
                       f'<animate attributeName="width" from="0" to="{WIDTH - 88}" '
                       f'begin="{begin:.2f}s" dur="{LINE_DUR:.2f}s" fill="freeze"/>'
                       f'</rect></clipPath>')
            clip = f' clip-path="url(#ln{i})"'
        out.append(f'<g{clip}>')
        out.append(f'<text x="44" y="{y}" font-size="13" class="{tone if tone != "text" else "dim"}">&#9679;</text>')
        out.append(f'<text x="66" y="{y}" font-size="13" class="muted">{xml(label)}</text>')
        out.append(f'<text x="180" y="{y}" font-size="13" class="{tone}">{xml(value)}</text>')
        out.append("</g>")

    out.append(reveal(T_TAIL))
    out.append(f'<text x="44" y="{CONTENT_H - 50}" font-size="12" class="info">'
               f'spec &#8594; orchestrate &#8594; execute &#8594; validate &#8594; ship</text>')
    out.append("</g>")

    # ---- status bar -------------------------------------------------------
    out.append(f'<line x1="24" y1="{CONTENT_H - 34}" x2="{WIDTH - 24}" '
               f'y2="{CONTENT_H - 34}" stroke="{BORDER}"/>')
    out.append(f'<text x="44" y="{CONTENT_H - 14}" font-size="11.5" class="muted">'
               f'Tip: every panel on this profile is generated, not hand-drawn.</text>')
    out.append(f'<text x="{WIDTH - 44}" y="{CONTENT_H - 14}" font-size="11.5" '
               f'class="muted" text-anchor="end">kj-agent 0.4.2 &#183; '
               f'<tspan class="ok">[stable]</tspan></text>')

    out.append("</g>")
    out.append(close_svg())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    generate(Path("assets/kj-agent-cli.svg"), os.environ.get("STATIC") == "1")
