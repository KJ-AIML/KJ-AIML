from __future__ import annotations

import os
from pathlib import Path

from svg_common import BG, BLUE, BORDER, MINT, MUTED, PANEL, TEXT, YELLOW, close_svg, svg_head, xml


def generate(path: Path, static: bool = False) -> None:
    nodes = [
        ("Human requirement", "intent", MINT),
        ("Specification & planning", "ALMS", BLUE),
        ("Agent orchestration", "LangGraph / skills", YELLOW),
        ("Harness & sandbox execution", "tooling", BLUE),
        ("Validation", "traceable checks", MINT),
        ("Deployable backend / tool", "ship", TEXT),
    ]
    out = [svg_head("KJ AI infrastructure system map", "A vertical flow from human requirements through planning, orchestration, execution, validation, and deployable systems.", 420, 430)]
    out.append(f'<rect width="420" height="430" rx="14" fill="{BG}"/><rect x="1" y="1" width="418" height="428" rx="14" fill="none" stroke="{BORDER}"/>')
    out.append(f'<text x="24" y="34" font-size="15" class="text">SYSTEM FLOW / <tspan class="mint">one pass</tspan></text>')
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
    out.extend([f'<text x="24" y="408" font-size="10" class="muted">products and tools attach at the layers that need them</text>', close_svg()])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    generate(Path("assets/kj-system-map.svg"), os.environ.get("STATIC") == "1")
