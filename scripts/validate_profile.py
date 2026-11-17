"""Offline checks for this profile's static SVGs and declared animated hero.

This is a build check, not a general SVG sanitizer or a substitute for rendering
the artwork. Local links are checked without requesting public URLs.
"""

from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
import math
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ANIMATED_ASSET = "kj-hello.svg"
STILL_ASSET = "kj-hello-still.svg"
ASSET_NAMES = (STILL_ASSET, "kj-agent-cli.svg", ANIMATED_ASSET)
HERO_MAX_HEIGHT = 450          # at the 855px display width
SVG_NS = "http://www.w3.org/2000/svg"
MAX_SVG_BYTES = 500_000
STATIC_TAGS = {
    "svg", "title", "desc", "style", "defs", "g", "path", "rect", "circle",
    "ellipse", "line", "polyline", "polygon", "text", "tspan", "linearGradient",
    "radialGradient", "stop",
}
ANIMATION_TARGETS = {
    "animate": {"opacity", "x1", "x2"},
    "set": {"opacity", "fill"},
    "animateTransform": {"transform"},
}
# Joints rotate and arms slide. Scaling and skewing could hide or distort text.
TRANSFORM_ANIMATIONS = {"translate", "rotate"}
# A gradient's endpoints may move (the glint across the finished name); nothing else may.
GRADIENT_ENDPOINTS = {"x1", "x2"}
STYLE_PROPERTIES = {
    "fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin",
    "stroke-dasharray", "stroke-dashoffset", "font-family", "font-size", "font-weight", "text-anchor",
    "letter-spacing", "white-space", "opacity", "fill-opacity", "stroke-opacity",
    "stop-color", "stop-opacity", "paint-order", "dominant-baseline",
}
HIDING_PROPERTIES = {"clip", "clip-path", "mask", "filter", "display", "visibility"}
ICON_TAGS = {"svg", "title", "g", "path", "rect", "circle", "ellipse", "text"}
MAX_ICON_BYTES = 20_000
UNSAFE_XML = br"<!\s*(?:DOCTYPE|ENTITY)\b|<\?(?!xml(?:\s|\?>))"


def _number(value: str, label: str, *, positive: bool = False) -> float:
    try:
        number = float(value.removesuffix("px"))
    except ValueError as exc:
        raise ValueError(f"invalid {label}: {value!r}") from exc
    if not math.isfinite(number) or (positive and number <= 0):
        raise ValueError(f"invalid {label}: {value!r}")
    return number


def _declarations(style: str) -> dict[str, str]:
    declarations = {}
    for declaration in style.split(";"):
        if not declaration.strip():
            continue
        name, separator, value = declaration.partition(":")
        name, value = name.strip().lower(), value.strip()
        if not separator or name not in STYLE_PROPERTIES or not value:
            raise ValueError(f"unsupported SVG style: {declaration!r}")
        if "\\" in value or "!" in value or "@" in value:
            raise ValueError(f"unsupported SVG style value: {value!r}")
        declarations[name] = value
    return declarations


SIMPLE_SELECTOR = r"[.#]?[A-Za-z_][\w-]*"
REDUCED_MOTION = re.compile(
    r"@media\s*\(\s*prefers-reduced-motion\s*:\s*reduce\s*\)\s*\{((?:[^{}]*\{[^{}]*\})*)\s*\}")


def _check_reduced_motion(block: str) -> None:
    """The one at-rule the animated hero may carry: show the final frame to visitors who ask for less motion.

    It may hide the animated scene, force content visible, and paint strokes a flat
    colour. It may not hide anything else, so it cannot be used to conceal text.
    """
    for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", block):
        names = [selector.strip() for selector in selectors.split(",")]
        if not all(re.fullmatch(SIMPLE_SELECTOR, name) for name in names):
            raise ValueError(f"unsupported reduced-motion selector: {selectors!r}")
        for declaration in filter(str.strip, body.split(";")):
            name, _, value = declaration.partition(":")
            name, value = name.strip().lower(), value.replace("!important", "").strip()
            hides_scene = name == "opacity" and value == "0" and names == ["#animated-scene"]
            shows = name == "opacity" and value == "1"
            flat_stroke = name == "stroke" and re.fullmatch(r"#[0-9a-fA-F]{6}", value)
            if not (hides_scene or shows or flat_stroke):
                raise ValueError(f"unsupported reduced-motion style: {declaration!r}")


def _css_rules(root: ET.Element, *, allow_animation: bool = False) -> list[tuple[str, dict[str, str]]]:
    rules = []
    for style in root.iter(f"{{{SVG_NS}}}style"):
        css = re.sub(r"/\*.*?\*/", "", "".join(style.itertext()), flags=re.S)
        if allow_animation:
            for block in REDUCED_MOTION.findall(css):
                _check_reduced_motion(block)
            css = REDUCED_MOTION.sub("", css)
        pattern = r"([^{}]+)\{([^{}]*)\}"
        if re.sub(pattern, "", css).strip():
            raise ValueError("unsupported SVG stylesheet")
        for selectors, body in re.findall(pattern, css):
            declarations = _declarations(body)
            for selector in selectors.split(","):
                selector = selector.strip()
                if not re.fullmatch(SIMPLE_SELECTOR, selector):
                    raise ValueError(f"unsupported SVG selector: {selector!r}")
                rules.append((selector, declarations))
    # Presentation attributes < tag rules < class rules < ID rules < inline style.
    return sorted(rules, key=lambda rule: 2 if rule[0][0] == "#" else rule[0][0] == ".")


def _check_values(properties: dict[str, str], ids: set[str], *, allow_animation: bool = False) -> None:
    for name, value in properties.items():
        local_name = name.rsplit("}", 1)[-1].lower()
        if local_name.startswith("on") or local_name in HIDING_PROPERTIES:
            raise ValueError(f"active or hiding SVG attribute: {local_name}")
        if local_name in {"href", "src", "base"}:
            if not value.startswith("#") or value[1:] not in ids:
                raise ValueError(f"external or missing SVG reference: {value!r}")
        if local_name in {"opacity", "fill-opacity", "stroke-opacity", "font-size"}:
            number = _number(value, local_name, positive=not allow_animation or local_name == "font-size")
            if number < 0:
                raise ValueError(f"negative SVG attribute: {local_name}")
        for match in re.finditer(r"url\s*\(([^)]*)\)", value, re.I):
            target = match[1].strip().strip("\"'")
            if not target.startswith("#") or target[1:] not in ids:
                raise ValueError(f"external or missing SVG reference: {target!r}")
        if re.search(r"url\s*\(", re.sub(r"url\s*\([^)]*\)", "", value, flags=re.I), re.I):
            raise ValueError(f"invalid SVG resource reference: {value!r}")


def validate_svg(path: Path, *, allow_animation: bool = False) -> ET.Element:
    if path.stat().st_size >= MAX_SVG_BYTES:
        raise ValueError(f"asset too large: {path}")
    data = path.read_bytes()
    if re.search(UNSAFE_XML, data, re.I):
        raise ValueError(f"unsupported XML declaration: {path}")
    root = ET.fromstring(data)
    if root.tag != f"{{{SVG_NS}}}svg":
        raise ValueError(f"not an SVG document: {path}")
    width = _number(root.get("width", ""), "width", positive=True)
    height = _number(root.get("height", ""), "height", positive=True)
    if width > 1600 or height > 900:
        raise ValueError(f"SVG dimensions exceed profile budget: {path}")
    viewbox = [_number(value, "viewBox") for value in re.split(r"[\s,]+", root.get("viewBox", "").strip())]
    if viewbox != [0, 0, width, height]:
        raise ValueError(f"viewBox must match the SVG dimensions: {path}")
    if path.name in {STILL_ASSET, ANIMATED_ASSET} and height * 855 / width > HERO_MAX_HEIGHT:
        raise ValueError(f"hero exceeds {HERO_MAX_HEIGHT}px at its 855px display width")
    for tag in ("title", "desc"):
        element = root.find(f"{{{SVG_NS}}}{tag}")
        if element is None or not "".join(element.itertext()).strip():
            raise ValueError(f"missing nonempty SVG {tag}: {path}")

    ids = {element.attrib["id"] for element in root.iter() if "id" in element.attrib}
    rules = _css_rules(root, allow_animation=allow_animation)
    for _, declarations in rules:
        _check_values(declarations, ids, allow_animation=allow_animation)
    animation_count = 0
    parents = {child: parent for parent in root.iter() for child in parent}
    for element in root.iter():
        tag = element.tag.removeprefix(f"{{{SVG_NS}}}")
        allowed_tags = STATIC_TAGS | (ANIMATION_TARGETS.keys() if allow_animation else set())
        if element.tag != f"{{{SVG_NS}}}{tag}" or tag not in allowed_tags:
            raise ValueError(f"active or unsupported SVG element: {element.tag}")
        _check_values(element.attrib, ids, allow_animation=allow_animation)
        _check_values(_declarations(element.get("style", "")), ids, allow_animation=allow_animation)
        if tag in ANIMATION_TARGETS:
            animation_count += 1
            target = element.get("attributeName")
            if target not in ANIMATION_TARGETS[tag]:
                raise ValueError(f"unsupported animation target: {target}")
            if tag == "animateTransform" and element.get("type") not in TRANSFORM_ANIMATIONS:
                raise ValueError("only translation and rotation animations are supported")
            if target in GRADIENT_ENDPOINTS:
                if parents[element].tag != f"{{{SVG_NS}}}linearGradient":
                    raise ValueError("only a gradient's endpoints may be animated")
                for value in element.get("values", "").split(";"):
                    _number(value, "animated gradient endpoint")
            for timing in ("begin", "dur"):
                if timing in element.attrib and not re.fullmatch(r"\d+(?:\.\d+)?s", element.attrib[timing]):
                    raise ValueError(f"unsupported animation timing: {element.attrib[timing]}")
            if target == "opacity":
                for value in element.get("values", element.get("to", "")).split(";"):
                    if not 0 <= _number(value, "animated opacity") <= 1:
                        raise ValueError("animated opacity must be between zero and one")

    if allow_animation:
        fallback = root.find(f"{{{SVG_NS}}}g[@id='static-fallback']")
        if (animation_count == 0 or fallback is None
                or fallback.get("opacity", "1") != "1"
                or not list(fallback.iter(f"{{{SVG_NS}}}text"))):
            raise ValueError("animated hero requires a visible static fallback")

    visible_text = []

    def walk(element: ET.Element, inherited: dict[str, str], tx: float = 0, ty: float = 0,
             shown: bool = True) -> None:
        tag = element.tag.rsplit("}", 1)[-1]
        if tag in {"defs", "style", "title", "desc"}:
            return
        properties = inherited | element.attrib
        for selector, declarations in rules:
            if (selector == tag or selector == f"#{element.get('id')}"
                    or selector.startswith(".") and selector[1:] in element.get("class", "").split()):
                properties.update(declarations)
        properties.update(_declarations(element.get("style", "")))
        shown = shown and float(properties.get("opacity", "1")) > 0
        if transform := element.get("transform"):
            match = re.fullmatch(r"translate\(\s*([^,\s]+)[,\s]+([^,\s]+)\s*\)", transform)
            if match is None:
                raise ValueError(f"unsupported SVG transform: {transform!r}")
            tx += _number(match[1], "translation x")
            ty += _number(match[2], "translation y")
        if tag in {"text", "tspan"} and "".join(element.itertext()).strip():
            if properties.get("fill", "black").lower() in {"none", "transparent"}:
                raise ValueError("SVG text has no visible fill")
            x = _number(properties.get("x", "0"), "text x") + tx
            y = _number(properties.get("y", "0"), "text y") + ty
            if not 0 <= x <= width or not 0 < y <= height:
                raise ValueError("SVG text is outside the viewport")
            if tag == "text" and shown:
                visible_text.append("".join(element.itertext()).strip())
        for child in element:
            walk(child, properties, tx, ty, shown)

    walk(root, {})
    if not visible_text:
        raise ValueError(f"SVG has no visible text: {path}")
    return root


def validate_icon(path: Path) -> None:
    """Icons are tiny static marks: a title and a few shapes, nothing active, styled or external."""
    data = path.read_bytes()
    if len(data) >= MAX_ICON_BYTES or re.search(UNSAFE_XML, data, re.I):
        raise ValueError(f"unsupported icon file: {path}")
    root = ET.fromstring(data)
    title = root.find(f"{{{SVG_NS}}}title")
    if root.tag != f"{{{SVG_NS}}}svg" or title is None or not "".join(title.itertext()).strip():
        raise ValueError(f"icon needs an SVG root and a title: {path}")
    for element in root.iter():
        tag = element.tag.removeprefix(f"{{{SVG_NS}}}")
        if element.tag != f"{{{SVG_NS}}}{tag}" or tag not in ICON_TAGS or "style" in element.attrib:
            raise ValueError(f"unsupported icon content in {path}: {element.tag}")
        _check_values(element.attrib, set())


class _HTMLReferences(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.references.extend(value for name, value in attrs if name in {"href", "src"} and value)
        for name, value in attrs:
            if name == "srcset" and value:
                self.references.extend(candidate.strip().split()[0]
                                       for candidate in value.split(",") if candidate.strip())


def _destination(text: str) -> str:
    """Read a Markdown destination, preserving balanced/escaped parentheses."""
    if text.startswith("<"):
        return text[1:].split(">", 1)[0]
    depth, result, escaped = 0, [], False
    for char in text:
        if escaped:
            result.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "(":
            depth += 1
            result.append(char)
        elif char == ")":
            if depth == 0:
                break
            depth -= 1
            result.append(char)
        elif char.isspace() and depth == 0:
            break
        else:
            result.append(char)
    return "".join(result)


def local_references(markdown: str) -> list[str]:
    # Documentation examples/comments are not rendered links.
    markdown = re.sub(r"<!--.*?-->", "", markdown, flags=re.S)
    markdown = re.sub(r"(?ms)^ {0,3}(`{3,}|~{3,})[^\n]*\n.*?^ {0,3}\1[ \t]*$", "", markdown)
    markdown = re.sub(r"(`+)(?!`)(.*?)\1", "", markdown, flags=re.S)
    html = _HTMLReferences()
    html.feed(markdown)
    references = html.references
    references.extend(_destination(markdown[match.end():]) for match in re.finditer(r"(?<!\\)\]\(\s*", markdown))
    references.extend(_destination(match[1]) for match in re.finditer(r"(?m)^ {0,3}\[[^\]\n]+\]:[ \t]*(.*)$", markdown))
    return [reference for reference in references if reference]


def validate_local_references(document: Path, repository: Path) -> None:
    repository = repository.resolve()
    for reference in local_references(document.read_text(encoding="utf-8")):
        url = urlsplit(unescape(reference))
        if url.scheme or url.netloc or not url.path:
            continue
        path = unquote(url.path)
        base = repository if path.startswith("/") else document.parent
        target = (base / path.lstrip("/")).resolve()
        if not target.is_relative_to(repository) or not target.exists():
            raise ValueError(f"broken local reference in {document}: {reference}")


def validate_profile(repository: Path = ROOT) -> None:
    for name in ASSET_NAMES:
        validate_svg(repository / "assets" / name, allow_animation=name == ANIMATED_ASSET)
    for icon in sorted((repository / "assets/icons").glob("*.svg")):
        validate_icon(icon)
    for document in [repository / "README.md", *sorted((repository / "docs").rglob("*.md"))]:
        validate_local_references(document, repository)
    readme = (repository / "README.md").read_text(encoding="utf-8").lower()
    for token in ("mcp_token", "YOUR_TOKEN", "TODO", "PLACEHOLDER", "visitor counter"):
        if token.lower() in readme:
            raise ValueError(f"forbidden placeholder/token in README: {token}")


def main() -> None:
    try:
        validate_profile()
    except (ValueError, OSError, ET.ParseError) as exc:
        raise SystemExit(str(exc)) from exc
    print("Profile validation passed.")


if __name__ == "__main__":
    main()
