"""Sculpted dot artwork: pi-ter hand gesture -> a shaded KJ-AIML wordmark.

Only local geometry, opacity and translation are emitted. Source hand fields
and their provenance are in data/. IBM Plex Mono is bundled under assets/fonts/.
"""

from __future__ import annotations

import argparse
import base64
from collections import defaultdict
import json
from pathlib import Path
import zlib

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from svg_common import xml

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 855, 300
BG, GREEN = "#080b0f", "#9af2b4"
FONT = ROOT / "assets/fonts/IBMPlexMono-Bold.ttf"
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6],
                  [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 + 1 / 32


def dot_paths(points: list[tuple[float, float, str]], diameter: float) -> str:
    """Group round, almost-zero-length strokes by shade: compact font-free dots."""
    shades: dict[str, list[str]] = defaultdict(list)
    for x, y, color in points:
        shades[color].append(f"M{x:.1f},{y:.1f}h.01")
    return "\n".join(
        f'<path d="{"".join(parts)}" fill="none" stroke="{color}" '
        f'stroke-width="{diameter}" stroke-linecap="round"/>'
        for color, parts in sorted(shades.items())
    )


def wordmark() -> str:
    font = ImageFont.truetype(str(FONT), 180)
    bbox = font.getbbox("KJ-AIML")
    mask = Image.new("L", (bbox[2] - bbox[0], bbox[3] - bbox[1]))
    ImageDraw.Draw(mask).text((-bbox[0], -bbox[1]), "KJ-AIML", font=font, fill=255)
    mask.thumbnail((650, 120), Image.Resampling.LANCZOS)
    # Upper edge leans right. The geometry is baked; no SVG font is required.
    skew = 0.23
    mask = mask.transform((mask.width + int(skew * mask.height) + 1, mask.height),
                          Image.Transform.AFFINE,
                          (1, skew, -skew * mask.height, 0, 1, 0),
                          resample=Image.Resampling.BICUBIC)
    shape = Image.new("L", (mask.width + 36, mask.height + 36))
    shape.paste(mask, (8, 8))
    solid = np.asarray(shape) > 127
    inside = np.zeros(solid.shape, dtype=float)
    eroded = shape.point(lambda value: 255 if value > 127 else 0)
    for _ in range(6):
        inside += np.asarray(eroded) > 127
        eroded = eroded.filter(ImageFilter.MinFilter(3))
    gy, gx = np.gradient(inside)
    yy, xx = np.indices(solid.shape)
    light = np.zeros(solid.shape, dtype=float)
    # Back-to-front extrusion, with a low lavender wall and a bright bevel.
    for depth in range(14, 0, -1):
        shifted = np.zeros_like(solid)
        shifted[depth:, depth:] = solid[:-depth, :-depth]
        light[shifted] = (51 + 29 * (1 - depth / 14)
                          + 9 * np.sin(yy[shifted] * .45))
    face = 190 + 33 * np.cos((yy - 8) / max(mask.height, 1) * 2 * np.pi)
    face += 10 * np.sin(xx * .014)
    bevel = np.clip(193 - 53 * gx - 85 * gy, 80, 249)
    light[solid] = np.where(inside < 5, bevel, face)[solid]
    xoff = (WIDTH - shape.width) / 2
    yoff = (HEIGHT - shape.height) / 2 - 7
    points = []
    pitch = 2.45
    for cy, y in enumerate(np.arange(0.8, shape.height, pitch)):
        for cx, x in enumerate(np.arange(0.8, shape.width, pitch)):
            value = light[int(y), int(x)]
            if value <= 0:
                continue
            if value < 100 and value / 100 < BAYER[cy % 4, cx % 4]:
                continue
            if value < 100:
                # Lavender shadow, with sufficient separation from the black canvas.
                q = round(value / 8) * 8
                rgb = (int(q * .92), int(q * .80), min(255, int(q * 1.38)))
            else:
                q = min(248, round(value / 10) * 10)
                rgb = (q, min(255, q + 3), min(255, q + 9))
            color = "#" + "".join(f"{channel:02x}" for channel in rgb)
            points.append((x + xoff, y + yoff, color))
    return dot_paths(points, 1.68)


def hands() -> list[str]:
    data = json.loads((Path(__file__).parent / "data/pi-ter-hands.json").read_text())
    scale = WIDTH / 736
    result = []
    for index, field in enumerate(data["fields"]):
        raw = zlib.decompress(base64.b64decode(field["data"]))
        values = np.frombuffer(raw, dtype=np.uint8).reshape(field["h"], field["w"], 2)
        points = []
        start = -190 if index == 0 else field["x"]
        stop = field["x"] + field["w"] if index == 0 else 926
        pitch = 2.6
        for cy, y in enumerate(np.arange(field["y"] + .65, field["y"] + field["h"] - 1, pitch)):
            for cx, x in enumerate(np.arange(start + .65, stop - 1, pitch)):
                sample_x = x
                # Continue the wrist beyond the edges so the reaching hands stay attached.
                if index == 0 and x < 0:
                    sample_x = x % 24
                if index == 1 and x > 734:
                    sample_x = 712 + (x - 736) % 22
                ix = min(field["w"] - 1, max(0, int(sample_x - field["x"])))
                iy = int(y - field["y"])
                alpha, luminance = values[iy, ix] / 255
                if alpha * (.42 + .58 * luminance) <= BAYER[cy % 4, cx % 4]:
                    continue
                q = round((98 + 140 * luminance) / 12) * 12
                color = "#" + "".join(f"{channel:02x}" for channel in (q, q, min(255, q + 4)))
                points.append((x * scale, (y - 225) * scale + HEIGHT / 2, color))
        result.append(dot_paths(points, 1.52))
    return result


def animate(attribute: str, times: list[float], values: list[str], *,
            duration: float = 6, spline: bool = False, transform: bool = False) -> str:
    tag = "animateTransform" if transform else "animate"
    extra = ' type="translate"' if transform else ""
    if spline:
        extra += (' calcMode="spline" keySplines="'
                  + ";".join(["0.42 0 0.58 1"] * (len(times) - 1)) + '"')
    return (f'<{tag} attributeName="{attribute}"{extra} '
            f'begin="0s" dur="{duration:g}s" fill="freeze" '
            f'keyTimes="{";".join(f"{t / duration:.6f}" for t in times)}" '
            f'values="{";".join(values)}"/>')


def caption() -> str:
    return ('<text x="427.5" y="260" text-anchor="middle" font-size="11.5" '
            'letter-spacing="2.6" fill="#a9a6b7">KONGPHOP JAMREANSUK</text>')


def intro() -> str:
    chunks = ['<g id="animated-scene" opacity="0">',
              animate("opacity", [0, 4.4, 5.5, 6], ["1", "1", "0", "0"])]
    scale = WIDTH / 736
    times = [0, 1.45, 2.75, 3.15, 4.3, 5.6, 6]
    for index, geometry in enumerate(hands()):
        xs = [-115, 0, 82, 82, 20, -180, -180]
        ys = [0, 0, 28, 28, 6, 0, 0]
        if index:
            xs = [-value for value in xs]
            ys = [0, 0, -9, -9, -2, 0, 0]
        offsets = [f"{x * scale:.2f} {y * scale:.2f}" for x, y in zip(xs, ys)]
        chunks.extend([
            f'<g id="hand-{index}">',
            animate("transform", times, offsets, spline=True, transform=True),
            animate("opacity", [0, .65, 6], ["0", "1", "1"]),
            geometry, '</g>',
        ])
    # A small signal at the near-touch, rather than a full-screen particle effect.
    x, y = 357 * scale, (234 - 225) * scale + HEIGHT / 2
    for i in range(8):
        angle = i * np.pi / 4
        dx, dy = 24 * np.cos(angle), 16 * np.sin(angle)
        chunks.extend([
            '<g opacity="0">',
            animate("opacity", [0, 2.65, 2.8, 3.55, 6], ["0", "0", ".85", "0", "0"]),
            animate("transform", [0, 2.65, 3.55, 6],
                    ["0 0", "0 0", f"{dx:.2f} {dy:.2f}", f"{dx:.2f} {dy:.2f}"],
                    transform=True),
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.15" fill="{GREEN}"/>',
            '</g>',
        ])
    for label, times in [("Hello World", [0, .5, .9, 1.55, 1.9, 6]),
                         ("Hello KJ", [0, 3.35, 3.7, 4.3, 4.65, 6])]:
        chunks.extend([
            f'<text x="{x:.2f}" y="{y + 4:.2f}" text-anchor="middle" '
            f'font-size="13" fill="{GREEN}" opacity="0">{xml(label)}',
            animate("opacity", times, ["0", "0", "1", "1", "0", "0"]),
            '</text>',
        ])
    chunks.append('</g>')
    return "\n".join(chunks)


def generate(out: Path, mode: str = "static") -> None:
    if mode not in {"static", "intro"}:
        raise ValueError(f"unknown Braille wordmark mode: {mode}")
    description = ("A pearl and lavender KJ-AIML wordmark sculpted from Braille-like dots. "
                   "Kongphop Jamreansuk.")
    if mode == "intro":
        description = ("Two shaded dot hands reach toward one another, exchange a green signal, "
                       "and withdraw as KJ-AIML appears. The six-second intro settles on the "
                       "wordmark. Without animation, the wordmark is visible immediately.")
    chunks = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img">',
        '<title>KJ-AIML / Kongphop Jamreansuk</title>',
        f'<desc>{description}</desc>',
        '<style>text { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }</style>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{BG}"/>',
        '<g id="static-fallback">',
    ]
    if mode == "intro":
        chunks.extend([
            animate("opacity", [0, 4.55, 5.85, 6], ["0", "0", "1", "1"], spline=True),
            animate("transform", [0, 4.55, 6], ["0 10", "0 10", "0 0"],
                    spline=True, transform=True),
        ])
    chunks.extend([wordmark(), caption(), '</g>'])
    if mode == "intro":
        chunks.append(intro())
    chunks.append('</svg>\n')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(chunks), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("static", "intro"), default="static")
    parser.add_argument("--out", type=Path, default=ROOT / "assets/kj-wordmark.svg")
    options = parser.parse_args()
    generate(options.out, options.mode)
