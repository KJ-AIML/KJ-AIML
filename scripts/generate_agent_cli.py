"""Render a compact, static terminal illustration for the design notes.

The public profile keeps its facts in Markdown. This optional companion artwork
contains only the generic focus and language stack, visible immediately.
"""

from __future__ import annotations

from pathlib import Path

from svg_common import BORDER, close_svg, svg_head, terminal_chrome, xml

ROOT = Path(__file__).resolve().parents[1]
WIDTH = 855
HEIGHT = 216

# A small rest-pose sample from the same fixed-font 3D renderer as the wordmark.
# Re-bake with WORDMARK_TEXT=KJ WORDMARK_COLS=22 and --preview when changing the
# wordmark's geometry. Keeping the grid literal makes this illustration simple.
LOGO = [
    " SSSS *SSS    *ssssss",
    " SSSScSSSS    =ssssss",
    " SSSSSSSS        =sss",
    " SSSSSSS         =sss",
    " SSSSSSSS        =sss",
    " SSSSSSSSS   ssssssss",
    " SSSS SSSS   ssssssss",
    " SSSS  SSSS    ssss",
]
LOGO_SIZE = 12
LOGO_STEP = 14
LOGO_CELL = 7.2
LOGO_RAMP = " .`:-=+*csS#%@"
LOGO_BUCKET = [0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 3, 3, 3, 3]
LOGO_SHADE = ["muted", "dim", "text", "signal"]

ROWS = [
    ("Focus", "Agent infrastructure"),
    ("Build", "Backends / developer tools"),
    ("Stack", "Python / Rust / TypeScript"),
]


def logo_runs(line: str) -> list[tuple[int, str, int]]:
    """Split a baked row into (column, text, shade) runs of one tone each."""
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


def generate(path: Path, static: bool = True) -> None:
    """Write the static illustration; retain ``static`` for caller compatibility.

    Both values intentionally produce the same complete artwork. There is no
    animated CLI mode or simulated interaction in this panel.
    """
    out = [svg_head(
        "KJ-AIML engineering notes",
        "A static terminal illustration with a small three-dimensional KJ ASCII "
        "monogram. Focus: agent infrastructure. Build: backends and developer "
        "tools. Stack: Python, Rust and TypeScript.",
        WIDTH, HEIGHT)]
    out.append(terminal_chrome(WIDTH, HEIGHT, "KJ-AIML / engineering notes"))

    for i, line in enumerate(LOGO):
        y = 74 + i * LOGO_STEP
        for col, body, shade in logo_runs(line):
            out.append(
                f'<text x="{36 + col * LOGO_CELL:.1f}" y="{y}" '
                f'font-size="{LOGO_SIZE}" class="{LOGO_SHADE[shade]}" '
                f'xml:space="preserve" textLength="{len(body) * LOGO_CELL:.1f}" '
                f'lengthAdjust="spacing">{xml(body)}</text>')

    out.append(f'<line x1="220" y1="60" x2="220" y2="184" stroke="{BORDER}"/>')
    for i, (label, value) in enumerate(ROWS):
        y = 80 + i * 43
        out.append(f'<text x="250" y="{y}" font-size="14" class="muted">'
                   f'{xml(label)}</text>')
        out.append(f'<text x="338" y="{y}" font-size="20" '
                   f'class="{"signal" if i == 0 else "text"}">{xml(value)}</text>')

    out.append(close_svg())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    generate(ROOT / "assets/kj-agent-cli.svg")
