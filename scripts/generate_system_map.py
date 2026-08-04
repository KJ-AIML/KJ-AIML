from __future__ import annotations

import os
from pathlib import Path

from svg_common import BORDER, CHROME_H, DIM, INK, PANEL, SIGNAL, TEXT, close_svg, svg_head, terminal_chrome, xml


def generate(path: Path, static: bool = False) -> None:
    nodes = [
        ("Human requirement", "intent", SIGNAL),
        ("Specification & planning", "ALMS", INK),
        ("Agent orchestration", "LangGraph / skills", DIM),
        ("Harness & sandbox execution", "tooling", INK),
        ("Validation", "traceable checks", SIGNAL),
        ("Deployable backend / tool", "ship", TEXT),
    ]
    width, height = 420, 430 + CHROME_H
    out = [svg_head("KJ AI infrastructure system map", "A vertical flow from human requirements through planning, orchestration, execution, validation, and deployable systems.", width, height)]
    out.append(terminal_chrome(width, height, "KJ@AI-INFRA: ~$ ./stack.sh --map"))
    out.append(f'<g transform="translate(0,{CHROME_H})">')
    out.append(f'<text x="24" y="34" font-size="15" class="text">SYSTEM FLOW / <tspan class="signal">one pass</tspan></text>')
    for i, (label, detail, color) in enumerate(nodes):
        y = 56 + i * 58
        out.append(f'<line x1="42" y1="{y + 38}" x2="42" y2="{y + 58}" stroke="{BORDER}" stroke-width="2"/>') if i < len(nodes) - 1 else None
        out.append(f'<circle cx="42" cy="{y + 20}" r="13" fill="{PANEL}" stroke="{color}" stroke-width="2"/>')
        out.append(f'<text x="38" y="{y + 25}" font-size="11" fill="{color}">{i + 1:02d}</text>')
        out.append(f'<rect x="72" y="{y}" width="318" height="40" rx="8" fill="{PANEL}" stroke="{BORDER}"/>')
        delay = 0 if static else i * 0.18
        opacity = "1" if static else "0.35"
        out.append(f'<g opacity="{opacity}"><text x="88" y="{y + 17}" font-size="12" fill="{color}">{xml(label)}</text><text x="88" y="{y + 32}" font-size="10" class="muted">{xml(detail)}</text>')
        if not static:
            out.append(f'<animate attributeName="opacity" values="0.35;1" dur="0.5s" begin="{delay:.2f}s" fill="freeze"/>')
        out.append('</g>')
    out.extend([f'<text x="24" y="408" font-size="10" class="muted">products and tools attach at the layers that need them</text>', '</g>', close_svg()])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    generate(Path("assets/kj-system-map.svg"), os.environ.get("STATIC") == "1")
