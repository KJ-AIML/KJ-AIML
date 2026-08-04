"""Small helpers shared by the deterministic SVG generators."""

from __future__ import annotations

from html import escape


# Terminal palette. Hierarchy is carried by brightness rather than hue: the
# wordmark shades an ASCII density ramp, and a saturated fill next to it flattens
# the face-versus-wall contrast that reads as depth. The traffic-light dots and
# the contribution greens are the only colour in the profile, and both mean
# something. See docs/design-system.md.
BG = "#0d1117"          # base canvas / bottom of the panel gradient
BG2 = "#111722"         # top of the panel gradient
PANEL = "#161b22"       # elevated surfaces inside a window
BORDER = "#30363d"      # window frame and rules
TEXT = "#c9d1d9"        # body ink
SIGNAL = "#e6edf3"      # brightest step, for the line that matters most
DIM = "#8b949e"         # de-emphasised but still readable
MUTED = "#7d8590"       # metadata, captions, titlebar labels

DOTS = ["#ff5f56", "#ffbd2e", "#27c93f"]
CHROME_H = 30           # titlebar height; content sits below it

# Colour is reserved for state, never decoration -- GitHub's own status palette,
# so a row reads as a condition rather than as styling.
ACCENT = {"ok": "#3fb950", "info": "#79c0ff", "warn": "#d29922", "bad": "#f85149"}

HOST = "KJ@AI-ENGINEER"  # the shell prompt every panel and README header uses


def xml(value: object) -> str:
    return escape(str(value), quote=True)


def svg_head(title: str, description: str, width: int, height: int) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
  <title>{xml(title)}</title>
  <desc>{xml(description)}</desc>
  <style>
    text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }}
    .panel {{ fill: {PANEL}; stroke: {BORDER}; }}
    .muted {{ fill: {MUTED}; }}
    .text {{ fill: {TEXT}; }}
    .signal {{ fill: {SIGNAL}; }}
    .dim {{ fill: {DIM}; }}
    .ok {{ fill: {ACCENT["ok"]}; }}
    .info {{ fill: {ACCENT["info"]}; }}
    .warn {{ fill: {ACCENT["warn"]}; }}
    .bad {{ fill: {ACCENT["bad"]}; }}
  </style>
'''


def terminal_chrome(width: int, height: int, label: str) -> str:
    """Window frame for a panel: gradient body, border, titlebar and dots.

    Content is expected to be wrapped in translate(0, CHROME_H) so a panel can
    gain the titlebar without every y coordinate inside it moving.
    """
    return (
        f'<defs><linearGradient id="wbg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
        f'</linearGradient></defs>'
        f'<rect width="{width}" height="{height}" rx="14" fill="url(#wbg)"/>'
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="14" fill="none" stroke="{BORDER}"/>'
        f'<line x1="0" y1="{CHROME_H}" x2="{width}" y2="{CHROME_H}" stroke="{BORDER}"/>'
        + "".join(
            f'<circle cx="{20 + i * 16}" cy="{CHROME_H / 2:.0f}" r="4.5" fill="{dot}"/>'
            for i, dot in enumerate(DOTS)
        )
        + f'<text x="{width / 2:.0f}" y="{CHROME_H / 2 + 4:.0f}" font-size="11.5" '
          f'text-anchor="middle" class="muted">{xml(label)}</text>'
    )


def close_svg() -> str:
    return "</svg>\n"
