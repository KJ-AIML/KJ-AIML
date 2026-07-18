from __future__ import annotations

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_hero import generate as generate_hero
from generate_system_card import generate as generate_card
from generate_system_map import generate as generate_map
from render_contribution_heatmap import generate as generate_heatmap


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    generate_hero(ROOT / "assets/kj-hero.svg", static)
    generate_card(ROOT / "assets/kj-system-card.svg", static)
    generate_map(ROOT / "assets/kj-system-map.svg", static)
    generate_heatmap(ROOT / "data/contributions.json", ROOT / "assets/contribution-heatmap.svg", static)
    print(f"Generated profile visuals ({'static' if static else 'animated'} mode).")


if __name__ == "__main__":
    main()
