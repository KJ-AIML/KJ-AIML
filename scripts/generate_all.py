from __future__ import annotations

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_agent_cli import generate as generate_agent_cli


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    generate_agent_cli(ROOT / "assets/kj-agent-cli.svg", static)
    print(f"Generated profile visuals ({'static' if static else 'animated'} mode).")


if __name__ == "__main__":
    main()
