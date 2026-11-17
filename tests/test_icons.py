"""README icons: generated, fresh, safe, and readable on their dark tile."""

from __future__ import annotations

from pathlib import Path
import re

import pytest

import generate_icons
from scripts.validate_profile import ROOT, validate_icon
from svg_common import PANEL

ICONS = ROOT / "assets/icons"


def test_committed_icons_are_exactly_what_the_generator_writes() -> None:
    expected = generate_icons.build()
    committed = {path.name: path.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
                 for path in ICONS.glob("*.svg")}
    assert committed.keys() == expected.keys(), "run python scripts/generate_all.py and commit or remove the difference"
    for name, text in expected.items():
        assert committed[name] == text, f"{name} is stale: run python scripts/generate_all.py"


def test_generation_is_repeatable_and_needs_no_network(tmp_path: Path) -> None:
    generate_icons.generate(tmp_path)
    first = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    generate_icons.generate(tmp_path)
    assert first == {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    assert all(b"\r\n" not in data and b"http" not in data.replace(b"http://www.w3.org/2000/svg", b"")
               for data in first.values())


@pytest.mark.parametrize("path", sorted(ICONS.glob("*.svg")), ids=lambda path: path.name)
def test_committed_icons_are_static_and_self_contained(path: Path) -> None:
    validate_icon(path)


@pytest.mark.parametrize("unsafe", [
    '<script>alert(1)</script>',
    '<image href="https://example.com/a.png"/>',
    '<path d="M0 0" onclick="alert(1)"/>',
    '<path d="M0 0" style="fill:url(https://example.com/a.svg#p)"/>',
    '<path d="M0 0" fill="url(https://example.com/a.svg#p)"/>',
    '<animate attributeName="opacity" values="0;1" dur="1s"/>',
    '<style>path { fill: red }</style>',
])
def test_unsafe_icon_content_is_rejected(tmp_path: Path, unsafe: str) -> None:
    icon = tmp_path / "icon.svg"
    icon.write_text((ICONS / "python.svg").read_text(encoding="utf-8").replace("</svg>", unsafe + "</svg>"),
                    encoding="utf-8")
    with pytest.raises(ValueError):
        validate_icon(icon)


def luminance(colour: str) -> float:
    channels = [int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = (c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def test_every_mark_reads_on_the_dark_tile() -> None:
    tile = luminance(PANEL)
    for slug, icon in generate_icons.load().items():
        assert re.fullmatch(r"#[0-9A-F]{6}", icon["color"]) and re.fullmatch(r"#[0-9A-F]{6}", icon["brand"])
        ratio = (luminance(icon["color"]) + 0.05) / (tile + 0.05)
        assert ratio >= 3.9, f"{slug} is hard to see on the tile ({ratio:.1f}:1)"


def test_readme_only_uses_icons_that_exist_and_names_each_technology() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    used = set(re.findall(r'\./assets/icons/([\w-]+\.(?:svg|png))', readme))
    assert used and all((ICONS / name).is_file() for name in used)
    stack = readme.split("## Stack", 1)[1].split("<details>", 1)[0]
    tiles = re.findall(r'<img src="\./assets/icons/([\w-]+)\.svg"[^>]*alt="([^"]*)"', stack)
    assert len(tiles) >= 10
    titles = {slug: icon["title"] for slug, icon in generate_icons.load().items()}
    for slug, alt in tiles:
        assert alt == titles[slug], f"the {slug} tile needs its name as alt text"
