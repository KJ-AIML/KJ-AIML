"""Explicit animation experiments must retain room for their status sequence."""

import xml.etree.ElementTree as ET

import pytest

from generate_wordmark import generate


@pytest.mark.parametrize("mode", ["rock", "once", "spin"])
def test_legacy_animation_status_text_fits_canvas(tmp_path, mode) -> None:
    animated = tmp_path / f"{mode}.svg"
    generate(animated, mode=mode)
    root = ET.parse(animated).getroot()
    height = float(root.attrib["height"])
    clipped = [
        "".join(element.itertext()).strip()
        for element in root.iter("{http://www.w3.org/2000/svg}text")
        if not 0 < float(element.attrib["y"]) < height
    ]
    assert not clipped, f"{mode} text outside the canvas: {clipped}"
