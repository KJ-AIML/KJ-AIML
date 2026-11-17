"""Explicit animation experiments must retain room for their status sequence."""

import xml.etree.ElementTree as ET

import pytest

from generate_wordmark import generate
from scripts.validate_profile import ROOT


@pytest.mark.parametrize("mode", ["rock", "once", "spin"])
def test_legacy_text_fits_without_changing_static_output(tmp_path, mode) -> None:
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

    static = tmp_path / "static.svg"
    generate(static)
    expected = (ROOT / "assets/kj-wordmark.svg").read_bytes().replace(b"\r\n", b"\n")
    assert static.read_bytes() == expected
