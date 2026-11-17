from __future__ import annotations

from pathlib import Path

import pytest

from generate_hello import CAPTION
from scripts.validate_profile import ANIMATED_ASSET, ASSET_NAMES, MAX_SVG_BYTES, ROOT, validate_svg


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
def test_committed_assets_are_readable_svg(name: str) -> None:
    validate_svg(ROOT / "assets" / name, allow_animation=name == ANIMATED_ASSET)


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


def test_animated_hero_requires_explicit_opt_in() -> None:
    with pytest.raises(ValueError):
        validate_svg(ROOT / "assets" / ANIMATED_ASSET)


def test_animated_hero_retains_a_visible_nonanimated_frame() -> None:
    root = validate_svg(ROOT / "assets" / ANIMATED_ASSET, allow_animation=True)
    ns = "{http://www.w3.org/2000/svg}"
    fallback = root.find(f"{ns}g[@id='static-fallback']")
    scene = root.find(f"{ns}g[@id='animated-scene']")
    assert fallback is not None and fallback.get("opacity", "1") == "1"
    assert CAPTION in "".join(fallback.itertext())
    assert fallback.findall(f".//{ns}path"), "the fallback must draw the handle, not only its caption"
    assert scene is not None and scene.get("opacity") == "0"
    # Ignoring SMIL leaves the complete fallback visible and the entire intro hidden.
    for element in fallback.iter():
        assert element.get("opacity", "1") != "0"


@pytest.mark.parametrize("unsafe", [
    '<set attributeName="href" to="https://example.com/" begin="0s"/>',
    '<set attributeName="fill" to="url(https://example.com/a.svg)" begin="0s"/>',
    '<animate attributeName="opacity" values="0;1" begin="click" dur="1s"/>',
    '<script>alert(1)</script>',
    # Joints may rotate and arms may slide; nothing may scale, skew or morph.
    '<animateTransform attributeName="transform" type="scale" values="1;0" dur="1s"/>',
    '<animateTransform attributeName="transform" type="skewX" values="0;80" dur="1s"/>',
    '<animate attributeName="d" values="M0 0;M9 9" dur="1s"/>',
    # Only a gradient's own endpoints may move.
    '<animate attributeName="x1" values="0;10" dur="1s"/>',
    '<rect width="4" height="4"><animate attributeName="x2" values="0;10" dur="1s"/></rect>',
    '<linearGradient id="g2"><animate attributeName="x1" values="0;oops" dur="1s"/></linearGradient>',
])
def test_animation_does_not_allow_scripts_external_resources_or_link_mutation(tmp_path, unsafe) -> None:
    content = (ROOT / "assets" / ANIMATED_ASSET).read_text(encoding="utf-8")
    path = tmp_path / "animated.svg"
    path.write_text(content.replace("</svg>", unsafe + "</svg>"), encoding="utf-8")
    with pytest.raises(ValueError):
        validate_svg(path, allow_animation=True)


def test_hero_shows_its_final_frame_under_reduced_motion() -> None:
    """GitHub wraps README images in links, which can stop a picture source from applying.

    The hero therefore also carries the rule itself: with reduced motion the scene
    is hidden and the finished frame is forced visible, whatever SMIL is doing.
    """
    import re

    root = validate_svg(ROOT / "assets" / ANIMATED_ASSET, allow_animation=True)
    ns = "{http://www.w3.org/2000/svg}"
    css = "".join(root.find(f"{ns}style").itertext())
    block = re.search(r"@media \(prefers-reduced-motion:reduce\)\{(.*)\}$", css)
    assert block, "the hero needs its reduced-motion rule"
    rules = dict(re.findall(r"([^{}]+)\{([^{}]*)\}", block[1]))
    assert rules["#animated-scene"] == "opacity:0!important"
    assert rules[".f"] == "opacity:1!important"
    fallback = root.find(f"{ns}g[@id='static-fallback']")
    hidden_until_revealed = [element for element in fallback.iter()
                             if element.find(f"{ns}animate[@attributeName='opacity']") is not None]
    assert hidden_until_revealed and all(element.get("class") == "f" for element in hidden_until_revealed)
    # Flat strokes replace the moving gradient, so nothing sweeps across the handle.
    painted = {path.get("class") for path in fallback.iter(f"{ns}path")}
    assert painted and all(f".{name}" in rules and rules[f".{name}"].startswith("stroke:#") for name in painted)


@pytest.mark.parametrize("css", [
    "@media (prefers-reduced-motion:reduce){text{opacity:0!important}}",
    "@media (prefers-reduced-motion:reduce){.f{opacity:0!important}}",
    "@media (prefers-reduced-motion:reduce){.f{display:none}}",
    "@media (prefers-reduced-motion:reduce){.f{stroke:url(https://example.com/a.svg#p)}}",
    "@media (prefers-reduced-motion:reduce){.f > text{opacity:1}}",
    "@media screen{.f{opacity:1}}",
    '@import "https://example.com/style.css";',
])
def test_reduced_motion_rule_cannot_hide_content_or_load_anything(tmp_path, css) -> None:
    content = (ROOT / "assets" / ANIMATED_ASSET).read_text(encoding="utf-8")
    path = tmp_path / "animated.svg"
    path.write_text(content.replace("</style>", css + "</style>", 1), encoding="utf-8")
    with pytest.raises(ValueError):
        validate_svg(path, allow_animation=True)


def test_static_files_may_not_carry_media_rules(tmp_path) -> None:
    with pytest.raises(ValueError):
        check_svg(tmp_path, svg('<style>@media (prefers-reduced-motion:reduce){.f{opacity:1!important}}</style>'
                                '<text x="10" y="30">Readable content</text>'))
