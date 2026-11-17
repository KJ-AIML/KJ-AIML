"""Small local icons for the README: technology tiles and link buttons.

Every icon is a dark rounded tile, so it reads the same on GitHub's light and
dark themes without a second file. Technology marks come from the vendored
glyphs in data/icons.json and are drawn in their brand colour (see the note in
that file). Nothing is fetched at build time and no arithmetic depends on the
platform, so the output is byte-identical everywhere.
"""

from __future__ import annotations

import json
from pathlib import Path

from svg_common import BORDER, PANEL, SIGNAL, xml

ROOT = Path(__file__).resolve().parents[1]
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
GLYPH = 'transform="translate({x} 6) scale(.6667)"'      # a 24px mark at 16px

# Marks with no brand glyph to vendor are a few strokes drawn here.
DRAWN = {
    "site": ('<g fill="none" stroke="#69ff43" stroke-width="1.4"><circle cx="8" cy="8" r="6.3"/>'
             '<ellipse cx="8" cy="8" rx="2.7" ry="6.3"/><path d="M1.7 8h12.6"/></g>'),
    "cv": ('<g fill="none" stroke="#f2cc60" stroke-width="1.4" stroke-linejoin="round">'
           '<path d="M3.5 1.7h6l3 3v9.6h-9z"/><path d="M9.5 1.7v3h3M5.6 8h4.8M5.6 10.6h4.8"/></g>'),
    "linkedin": ('<rect x="1" y="1" width="14" height="14" rx="3" fill="#0A66C2"/>'
                 '<text x="8" y="12" font-family="Arial,Helvetica,sans-serif" font-size="9.5" font-weight="700" '
                 'text-anchor="middle" fill="#ffffff">in</text>'),
}
# file stem -> (label, vendored glyph or None for a drawn mark)
BUTTONS = {
    "btn-site": ("kjsc.dev", None, "site"),
    "btn-linkedin": ("LinkedIn", None, "linkedin"),
    "btn-cv": ("CV", None, "cv"),
    "btn-npm": ("heli-harness", "npm", None),
}


def load() -> dict:
    return json.loads((Path(__file__).parent / "data/icons.json").read_text(encoding="utf-8"))["icons"]


def tile(icon: dict) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 28 28" role="img">'
            f'<title>{xml(icon["title"])}</title>'
            f'<rect x=".5" y=".5" width="27" height="27" rx="6" fill="{PANEL}" stroke="{BORDER}"/>'
            f'<path {GLYPH.format(x=6)} fill="{icon["color"]}" d="{icon["path"]}"/></svg>\n')


def button(label: str, icon: dict | None, drawn: str | None) -> str:
    width = round(34 + len(label) * 7.25 + 12)
    mark = (f'<path {GLYPH.format(x=10)} fill="{icon["color"]}" d="{icon["path"]}"/>' if icon
            else f'<g transform="translate(10 6)">{DRAWN[drawn]}</g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="28" viewBox="0 0 {width} 28" role="img">'
            f'<title>{xml(label)}</title>'
            f'<rect x=".5" y=".5" width="{width - 1}" height="27" rx="6" fill="{PANEL}" stroke="{BORDER}"/>'
            f'{mark}<text x="34" y="18.5" font-family="{MONO}" font-size="12" fill="{SIGNAL}">{xml(label)}</text></svg>\n')


def build() -> dict[str, str]:
    """File name -> SVG text for every generated icon."""
    icons = load()
    files = {f"{slug}.svg": tile(icon) for slug, icon in icons.items()}
    for stem, (label, glyph, drawn) in BUTTONS.items():
        files[f"{stem}.svg"] = button(label, icons[glyph] if glyph else None, drawn)
    return files


def generate(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for name, text in build().items():
        (directory / name).write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    generate(ROOT / "assets/icons")
