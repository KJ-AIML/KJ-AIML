from __future__ import annotations

import os
from pathlib import Path

from svg_common import CHROME_H, DIM, INK, SIGNAL, TEXT, close_svg, svg_head, terminal_chrome, xml


def generate(path: Path, static: bool = False) -> None:
    rows = [
        ("Role", "AI Engineer · Founder", SIGNAL),
        ("Focus", "Agent infrastructure", INK),
        ("Building", "Axtra Intellion", DIM),
        ("Core", "ALMS · AXGA", TEXT),
        ("Exploring", "Tracer", INK),
        ("Stack", "Python · Rust · TypeScript", TEXT),
        ("Infra", "GCP · Docker · E2B", TEXT),
        ("Mode", "Remote-first", TEXT),
        ("Principle", "Build it. Validate it. Reliable.", SIGNAL),
    ]
    width, height = 420, 360 + CHROME_H
    out = [svg_head("KJ system identity card", "Neofetch-inspired identity card for KJ-AIML.", width, height)]
    out.append(terminal_chrome(width, height, "KJ@AI-INFRA: ~$ ./whoami --card"))
    out.append(f'<g transform="translate(0,{CHROME_H})">')
    out.append(f'<text x="24" y="38" font-size="16" class="signal">KJ-AIML@github</text>')
    out.append(f'<text x="24" y="58" font-size="12" class="muted">────────────────────────────────</text>')
    for index, (key, value, color) in enumerate(rows):
        y = 88 + index * 28
        delay = 0 if static else index * 0.12
        opacity = "1" if static else "0.35"
        out.append(f'<g opacity="{opacity}"><text x="24" y="{y}" font-size="12" class="muted">{xml(key):<10}</text><text x="122" y="{y}" font-size="12" fill="{color}">{xml(value)}</text>')
        if not static:
            out.append(f'<animate attributeName="opacity" values="0.35;1" dur="0.45s" begin="{delay:.2f}s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="0 3;0 0" dur="0.45s" begin="{delay:.2f}s" fill="freeze"/>')
        out.append('</g>')
    out.extend([f'<text x="24" y="340" font-size="11" class="muted">status: designing reliable systems</text>', '</g>', close_svg()])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    generate(Path("assets/kj-system-card.svg"), os.environ.get("STATIC") == "1")
