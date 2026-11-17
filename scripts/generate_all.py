from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_agent_cli import generate as generate_agent_cli
from generate_hello import generate as generate_hello
from generate_icons import generate as generate_icons


def main() -> None:
    generate_agent_cli(ROOT / "assets/kj-agent-cli.svg", static=True)
    generate_hello(ROOT / "assets/kj-hello-still.svg", mode="static")
    generate_hello(ROOT / "assets/kj-hello.svg", mode="intro")
    generate_icons(ROOT / "assets/icons")
    print("Generated all profile visuals (animated hero, its still, the CLI panel, and the icons).")


if __name__ == "__main__":
    main()
