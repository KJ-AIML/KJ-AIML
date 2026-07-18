from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

from scripts.generate_all import main


def test_expected_svgs_are_valid_and_safe() -> None:
    main()
    for path in (Path("assets") / name for name in ("kj-hero.svg", "kj-system-card.svg", "kj-system-map.svg", "contribution-heatmap.svg")):
        content = path.read_text(encoding="utf-8")
        root = ET.fromstring(content)
        tags = {element.tag.rsplit("}", 1)[-1] for element in root.iter()}
        assert {"title", "desc"}.issubset(tags)
        assert "<script" not in content.lower()
        content_without_namespace = content.lower().replace('xmlns="http://www.w3.org/2000/svg"', "")
        assert "http://" not in content_without_namespace
        assert "https://" not in content_without_namespace
        assert path.stat().st_size < 500_000


def test_generation_is_deterministic() -> None:
    main()
    first = {path.name: path.read_bytes() for path in Path("assets").glob("*.svg")}
    main()
    second = {path.name: path.read_bytes() for path in Path("assets").glob("*.svg")}
    assert first == second
