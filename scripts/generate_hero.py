from __future__ import annotations

import os
from pathlib import Path

from svg_common import BLUE, BORDER, BG, MINT, MUTED, PANEL, TEXT, YELLOW, close_svg, svg_head, xml


def generate(path: Path, static: bool = False) -> None:
    lines = [
        ("[01] Initializing agent systems...", MINT),
        ("[02] Loading infrastructure layer...", BLUE),
        ("[03] Connecting orchestration...", YELLOW),
        ("[04] Profile ready.", TEXT),
    ]
    body = [svg_head("KJ AI infrastructure profile", "Animated terminal initialization for KJ, an AI Engineer and Founder building agent infrastructure and developer tools.", 860, 280)]
    body.append(f'<rect width="860" height="280" rx="14" fill="{BG}"/>')
    body.append(f'<rect x="1" y="1" width="858" height="278" rx="14" fill="none" stroke="{BORDER}"/>')
    body.append(f'<rect x="1" y="1" width="858" height="34" rx="14" fill="{PANEL}"/>')
    body.append(f'<circle cx="24" cy="18" r="5" fill="{MINT}"/><circle cx="42" cy="18" r="5" fill="{YELLOW}"/><circle cx="60" cy="18" r="5" fill="{BLUE}"/>')
    body.append(f'<text x="84" y="23" font-size="12" class="muted">KJ-AIML / profile-init</text>')
    body.append(f'<text x="42" y="72" font-size="14" class="mint">KJ@AI-INFRA ~ $ initialize_profile</text>')
    body.append(f'<text x="42" y="126" font-size="54" font-weight="700" class="text">KJ</text>')
    body.append(f'<text x="44" y="151" font-size="16" class="blue">AI Engineer · Founder</text>')
    body.append(f'<text x="44" y="184" font-size="15" class="text">Building agent infrastructure,</text>')
    body.append(f'<text x="44" y="207" font-size="15" class="text">developer tools, and systems</text>')
    body.append(f'<text x="44" y="230" font-size="15" class="text">that make AI actually work.</text>')
    for index, (label, color) in enumerate(lines):
        y = 84 + index * 30
        delay = 0 if static else index * 0.42
        opacity = "1" if static else "0.35"
        body.append(f'<g opacity="{opacity}"><text x="524" y="{y}" font-size="13" fill="{color}">{xml(label)}</text>')
        if not static:
            body.append(f'<animate attributeName="opacity" values="0.35;1" dur="0.6s" begin="{delay:.2f}s" fill="freeze"/>')
        body.append('</g>')
    body.extend([
        f'<path d="M540 202h170 M540 202v28h170 M710 202v-28 M710 230h85" stroke="{BORDER}" fill="none"/>',
        f'<circle cx="540" cy="202" r="5" fill="{MINT}"/><circle cx="710" cy="202" r="5" fill="{BLUE}"/><circle cx="795" cy="230" r="5" fill="{YELLOW}"/>',
        f'<text x="524" y="260" font-size="11" class="muted">spec → orchestrate → execute → validate</text>',
        close_svg(),
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(body), encoding="utf-8")


if __name__ == "__main__":
    generate(Path("assets/kj-hero.svg"), os.environ.get("STATIC") == "1")
