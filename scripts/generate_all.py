from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_agent_cli import generate as generate_agent_cli
from generate_wordmark import generate as generate_wordmark


def main() -> None:
    generate_agent_cli(ROOT / "assets/kj-agent-cli.svg", static=True)
    generate_wordmark(ROOT / "assets/kj-wordmark.svg", mode="static")
    print("Generated both profile visuals (static mode).")


if __name__ == "__main__":
    main()
