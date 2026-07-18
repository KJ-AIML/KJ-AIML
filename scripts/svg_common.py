"""Small helpers shared by the deterministic SVG generators."""

from __future__ import annotations

from html import escape


BG = "#0D1117"
PANEL = "#161B22"
TEXT = "#E6EDF3"
MUTED = "#8B949E"
BORDER = "#30363D"
MINT = "#59F3C0"
BLUE = "#7AA2F7"
YELLOW = "#F2CC60"


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
    .mint {{ fill: {MINT}; }}
    .blue {{ fill: {BLUE}; }}
    .yellow {{ fill: {YELLOW}; }}
    @media (prefers-reduced-motion: reduce) {{ .animated {{ animation: none !important; }} }}
  </style>
'''


def close_svg() -> str:
    return "</svg>\n"

