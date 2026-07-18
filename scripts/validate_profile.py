from __future__ import annotations

from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from contributions import load_data

ROOT = Path(__file__).resolve().parents[1]
SVG_DIR = ROOT / "assets"
EXPECTED = ["kj-hero.svg", "kj-system-card.svg", "kj-system-map.svg", "contribution-heatmap.svg"]


def main() -> None:
    load_data(ROOT / "data/contributions.json")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for name in EXPECTED:
        path = SVG_DIR / name
        if not path.exists():
            raise SystemExit(f"missing asset: {path}")
        if path.stat().st_size >= 500_000:
            raise SystemExit(f"asset too large: {path}")
        root = ET.fromstring(path.read_text(encoding="utf-8"))
        tags = {element.tag.rsplit("}", 1)[-1] for element in root.iter()}
        if not {"title", "desc"}.issubset(tags):
            raise SystemExit(f"missing title/desc: {path}")
        svg_text = path.read_text(encoding="utf-8").lower().replace('xmlns="http://www.w3.org/2000/svg"', "")
        if "<script" in svg_text or "http://" in svg_text or "https://" in svg_text:
            raise SystemExit(f"unsafe external content: {path}")
    for reference in re.findall(r'(?:src|href)=["\'](\.?/[^"\']+)["\']', readme):
        if not (ROOT / reference).exists():
            raise SystemExit(f"broken local reference: {reference}")
    forbidden = ("mcp_token", "YOUR_TOKEN", "TODO", "PLACEHOLDER", "visitor counter")
    lower = readme.lower()
    for token in forbidden:
        if token.lower() in lower:
            raise SystemExit(f"forbidden placeholder/token in README: {token}")
    print("Profile validation passed.")


if __name__ == "__main__":
    main()
