from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import os

from contributions import load_data
from svg_common import BG, BLUE, BORDER, MINT, MUTED, PANEL, TEXT, close_svg, svg_head, xml


COLORS = ["#161B22", "#0E4429", "#006D32", "#26A641", "#59F3C0"]


def generate(data_path: Path, output_path: Path, static: bool = False) -> None:
    records, metrics = load_data(data_path)
    width, height = 860, 218
    out = [svg_head("KJ contribution trace", "One-year contribution calendar fetched from KJ-AIML's public GitHub profile.", width, height)]
    out.append(f'<rect width="{width}" height="{height}" rx="14" fill="{BG}"/><rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" fill="none" stroke="{BORDER}"/>')
    out.append(f'<text x="24" y="32" font-size="15" class="text">CONTRIBUTION TRACE</text>')
    total = metrics.get("total")
    total_label = f"{total:,} contributions" if isinstance(total, int) else "contribution levels"
    period = f"{metrics.get('displayed_from', 'unknown')} → {metrics.get('displayed_to', 'unknown')}"
    out.append(f'<text x="24" y="52" font-size="11" class="muted">{xml(total_label)} · {xml(period)}</text>')
    cell = 11
    gap = 3
    x0, y0 = 24, 78
    for index, item in enumerate(records[: 53 * 7]):
        day = date.fromisoformat(item.day)
        column = index // 7
        row = day.weekday() if index < 7 else index % 7
        x, y = x0 + column * (cell + gap), y0 + row * (cell + gap)
        level = max(0, min(4, item.level))
        delay = 0 if static else min(2.3, index * 0.006)
        fill = COLORS[level]
        if static:
            out.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{fill}"/>')
        else:
            out.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{fill}" opacity="0.5"><animate attributeName="opacity" values="0.5;1" dur="0.45s" begin="{delay:.2f}s" fill="freeze"/></rect>')
    out.append(f'<text x="24" y="186" font-size="10" class="muted">Less</text>')
    for index, color in enumerate(COLORS):
        out.append(f'<rect x="{62 + index * 16}" y="178" width="11" height="11" rx="3" fill="{color}"/>')
    out.append(f'<text x="148" y="186" font-size="10" class="muted">More</text>')
    if metrics.get("current_streak") is not None:
        out.append(f'<text x="680" y="186" font-size="10" fill="{MINT}">streak {metrics["current_streak"]}d · max {metrics["longest_streak"]}d</text>')
    out.append(close_svg())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/contributions.json"))
    parser.add_argument("--output", type=Path, default=Path("assets/contribution-heatmap.svg"))
    args = parser.parse_args()
    generate(args.data, args.output, os.environ.get("STATIC") == "1")
