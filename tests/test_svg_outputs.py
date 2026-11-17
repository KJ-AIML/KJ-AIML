from __future__ import annotations

from pathlib import Path

import pytest

from scripts.validate_profile import ASSET_NAMES, MAX_SVG_BYTES, ROOT, validate_svg


def svg(body: str = '<text x="10" y="30">Readable content</text>', **attributes: str) -> str:
    attributes = {"width": "100", "height": "50", "viewBox": "0 0 100 50"} | attributes
    attrs = " ".join(f'{key}="{value}"' for key, value in attributes.items())
    return (f'<svg xmlns="http://www.w3.org/2000/svg" {attrs}>'
            '<title>Example</title><desc>A static illustration</desc>' + body + '</svg>')


def check_svg(tmp_path: Path, content: str) -> None:
    path = tmp_path / "example.svg"
    path.write_text(content, encoding="utf-8")
    validate_svg(path)


@pytest.mark.parametrize("name", ASSET_NAMES)
def test_committed_assets_are_readable_static_svg(name: str) -> None:
    validate_svg(ROOT / "assets" / name)


@pytest.mark.parametrize("body", [
    '<script>alert(1)</script>',
    '<s:script xmlns:s="http://www.w3.org/2000/svg">alert(1)</s:script>',
    '<SCRIPT>alert(1)</SCRIPT>',
    '<foreignObject><div xmlns="http://www.w3.org/1999/xhtml">HTML</div></foreignObject>',
    '<animate attributeName="opacity" values="0;1" dur="1s"/>',
    '<set attributeName="opacity" to="1" begin="10s"/>',
    '<animateTransform attributeName="transform" type="rotate" dur="1s"/>',
    '<image href="data:image/png;base64,AAAA"/>',
    '<text x="10" y="30" onload="alert(1)">Content</text>',
    '<text x="10" y="30" ONCLICK="alert(1)">Content</text>',
    '<text x="10" y="30" href="&#104;ttps://example.com/a.svg">Content</text>',
    '<text x="10" y="30" xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="//example.com/a">Content</text>',
    '<style>@import "https://example.com/style.css";</style>',
    '<style>text { fill: URL(https://example.com/a.svg#paint); }</style>',
    '<style>text { animation: fade 1s infinite; }</style>',
])
def test_active_and_external_svg_content_is_rejected(tmp_path: Path, body: str) -> None:
    with pytest.raises(ValueError):
        check_svg(tmp_path, svg(body))


@pytest.mark.parametrize("body", [
    '<g opacity="0"><text x="10" y="30">Hidden</text></g>',
    '<style>.hidden { opacity: 0; }</style><text class="hidden" x="10" y="30">Hidden</text>',
    '<text x="10" y="30" style="display:none">Hidden</text>',
    '<text x="10" y="30" visibility="hidden">Hidden</text>',
    '<text x="10" y="30" font-size="0">Hidden</text>',
    '<g fill="none"><text x="10" y="30">Hidden</text></g>',
    '<text x="10" y="30" style="fill:transparent">Hidden</text>',
    '<defs><clipPath id="typing"><rect width="0" height="40"/></clipPath></defs>'
    '<text x="10" y="30" clip-path="url(#typing)">Hidden</text>',
    '<mask id="hidden"/><text x="10" y="30" mask="url(#hidden)">Hidden</text>',
    '<g transform="translate(1000,0)"><text x="10" y="30">Offscreen</text></g>',
    '<defs><text x="10" y="30">Never painted</text></defs>',
    '<rect width="100" height="50"/>',
])
def test_hidden_or_absent_text_is_rejected(tmp_path: Path, body: str) -> None:
    with pytest.raises(ValueError):
        check_svg(tmp_path, svg(body))


@pytest.mark.parametrize("attributes", [
    {"width": "nan"}, {"width": "0"}, {"height": "-1"}, {"height": "inf"},
    {"width": "1000000000"}, {"viewBox": "0 0 nan 50"}, {"viewBox": "0 0 0 50"},
])
def test_invalid_or_excessive_dimensions_are_rejected(tmp_path: Path, attributes: dict[str, str]) -> None:
    with pytest.raises(ValueError):
        check_svg(tmp_path, svg(**attributes))


def test_empty_metadata_and_large_files_are_rejected(tmp_path: Path) -> None:
    for content in (svg().replace("<title>Example</title>", "<title/>"),
                    svg().replace("A static illustration", " "),
                    svg() + " " * MAX_SVG_BYTES):
        with pytest.raises(ValueError):
            check_svg(tmp_path, content)


def test_metadata_urls_and_internal_paint_are_safe(tmp_path: Path) -> None:
    check_svg(tmp_path, svg(
        '<defs><linearGradient id="paint"><stop stop-color="#abcdef"/></linearGradient></defs>'
        '<style>.ink { fill: url(#paint); }</style>'
        '<g transform="translate(2,3)"><text class="ink" x="10" y="30">'
        'https://example.com is ordinary text &lt;script&gt;</text></g>'
    ))
