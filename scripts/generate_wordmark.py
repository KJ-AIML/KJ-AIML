"""Render "KJ-AIML" as an extruded 3D wordmark rasterized to ASCII, behind a
boot sequence, emitted as a self-contained SMIL SVG (GitHub runs SVG animation
in <img>, never JS).

Pipeline: draw the text with a bold TTF -> threshold to a mask -> extrude the
mask along +z into a surface point shell (front cap, back cap, boundary walls)
-> rotate / project each frame -> z-buffer splat into a character grid, char
picked by Lambert shading of the surface normal. Rotation is a pre-rendered
flipbook: one <g> per frame, cycled by a discrete opacity animation.

The intro plays once ahead of the loop: a status readout checks itself off,
colour-coded alert panels bury it, the screen clears, then each word of WORDS
resolves and blows apart. One particle set carries the debris through every
word, seats into a loading bar, and finally reassembles as the wordmark. See
docs/3d-ascii-wordmark.md.

Method follows docs/design-system.md's reference article. Unlike the other
generators this one is NOT wired into generate_all.py -- the output is a static
artifact that only changes when the text, font or framing does, so CI never
needs numpy/Pillow. Regenerate with:

    python -m pip install -r scripts/requirements-wordmark.txt
    python scripts/generate_wordmark.py

Env overrides: STATIC=1 (frozen frame), WORDMARK_TEXT, WORDMARK_FONT,
WORDMARK_FONT_INDEX, WORDMARK_TILT, WORDMARK_COLS, WORDMARK_ROW_MARGIN.
"""

from __future__ import annotations

import argparse
import html
import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from svg_common import ACCENT, BG, BG2, BORDER as FRAME, DOTS, MUTED as TITLE_TEXT, xml

ROOT = Path(__file__).resolve().parents[1]

# ---- palette --------------------------------------------------------------
# Panel chrome and the semantic accents come from svg_common so there is one
# copy to change. Only the shading ramp is local, because it belongs to this
# renderer rather than to the design system.
#
# The density ramp is already a dither, so give it a tonal range instead of one
# flat fill: dim characters sit back, dense ones come forward at near-white. The
# shading is carried twice over -- by glyph density and by value -- which is what
# makes the extrusion walls separate from the letter faces at this resolution.
# The wordmark stays neutral; a hue here would flatten the face-versus-wall
# contrast that carries the depth. ACCENT is only for the intro scenes.
SHADES = ["#4a5058", "#7d8590", "#b1bac4", "#f0f6fc"]
# Ramp index (1..13) -> shade bucket; index 0 is blank and never drawn. The cuts
# are set off the measured histogram, not an even split of the ramp: the fixed
# light puts 79% of inked cells on indices 9 and 10 and nothing above 10, so an
# even split leaves the brightest shade unused and the art reads flat.
BUCKETS = [0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 3, 3, 3, 3]

# ---- geometry / grid ------------------------------------------------------
COLS = int(os.environ.get("WORDMARK_COLS", 91))
ROWS = 0                # derived from the art -- see fit()
ROW_MARGIN = int(os.environ.get("WORDMARK_ROW_MARGIN", 4))   # blank rows top and bottom
CELL_W = 9.0
CELL_H = 15.5

# Seven characters need the full 91-column grid, and even there each glyph only
# gets ~13 columns. The counters in A and the valley in M are the tight spots:
# below that width they get narrower than the sideways offset the rotation gives
# the extrusion walls, the walls fill them, and the name rasterizes as a brick.
# Even stroke weight is what keeps the shading consistent across a glyph.
FONT_CANDIDATES = [
    os.environ.get("WORDMARK_FONT", ""),
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/verdanab.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Futura.ttc",
]
FONT_INDEX = int(os.environ.get("WORDMARK_FONT_INDEX", 0))   # face within a .ttc
TEXT = os.environ.get("WORDMARK_TEXT", "KJ-AIML")
INTRO_WORD_COLS = {
    "WELCOME": 91,
    "TO": 55,
    "MY": 55,
    "AI": 55,
    "WORLD": 91,
}
REST_YAW = math.radians(-13)

MASK_H = 300            # glyph raster height in mask px (drives point density)
TRACKING = 0.20         # extra letter-spacing, in em. the gaps must survive the
                        # extrusion offset or neighbours rasterize as one slab.
LINE_GAP = 1.20         # baseline-to-baseline, in cap heights (multi-line only)
DEPTH_FRAC = 0.26       # extrusion depth as a fraction of glyph height. the ref
                        # runs 0.34 on three letters; seven need shallower walls
                        # or they close A's counter and M's valley.
TILT_DEG = float(os.environ.get("WORDMARK_TILT", 4.0))
                        # tilt slants the baseline in screen space, so the bottom
                        # row frays at the ends of the swing -- keep it shallow.
CAM_DIST = 6.0          # camera distance in world units (1.0 == wordmark width)
FOCAL = 4.15            # pulled back + long lens: a near camera foreshortens the
                        # far letter enough that it reads as a rendering fault.
FIT = 0.92              # fraction of the grid the widest pose may use

RAMP = " .`:-=+*csS#%@"                       # sparse/dim -> dense/bright, 0 blank
# Keyed close to the view axis: letter faces stay solid and dense while the
# extruded walls fall away dimmer, and that contrast gap is the 3D read. A
# side-heavy light makes the walls out-shine the faces instead.
LIGHT = np.array([-0.15, -0.45, -1.00])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
AMBIENT = 0.22
FOG = 0.34              # how much the far end dims, 0..1
FOG_SPAN = 0.55         # world-units of depth the fog ramp covers

PAD = 18
TITLEBAR_H = 30

# ---- intro ----------------------------------------------------------------
# Plays once, then the rock loop takes over at BOOT_END. Every phase is a
# pre-rendered SMIL keyframe, same constraint as the flipbook:
#   status  -- a telemetry readout checks itself off row by row
#   alert   -- panels stack over it until the screen is buried
#   clear   -- everything drops out
#   words   -- each word of WORDS resolves, holds, and blows apart
#   bar     -- the debris seats into a loading bar that fills 0 -> 100%
#   burst   -- bar detonates and the debris reassembles into the wordmark
# The whole run is ~13.5s, which is long for a README. Every duration below is a
# knob; WORD_HOLD sets how long each word stays readable and SCENE_* carry the
# most time for the least information, so shrink those first.
SCENE_STATUS = 1.9      # rows tick in and check off
SCENE_ALERT = 2.0       # panels pile up over the readout
SCENE_CLEAR = 0.3       # screen empties
# Each word uses the final mark's projected 3D ASCII material. Particles remain
# transition debris: they converge, disappear while the form is readable, then
# blow outward toward the next station.
WORDS = [("WELCOME", "s3"), ("TO", "s3"), ("MY", "s3"),
         ("AI", "info"), ("WORLD", "ok")]
WORD_HOLD = 0.95        # word legible before it goes -- the readability knob
WORD_BURST = 0.35       # word -> scatter -> next word
BOOT_FILL = 1.5         # seconds spent filling the bar
BOOT_BURST = 0.5        # bar -> scattered debris
BOOT_FORM = 0.8         # debris -> wordmark silhouette

STATUS_END = SCENE_STATUS
ALERT_END = STATUS_END + SCENE_ALERT
WORDS_START = ALERT_END + SCENE_CLEAR
WORD_CYCLE = WORD_HOLD + WORD_BURST
BAR_START = WORDS_START + len(WORDS) * WORD_CYCLE
BOOT_END = BAR_START + BOOT_FILL + BOOT_BURST + BOOT_FORM

BAR_CELLS = 64          # segments in the loading bar
BAR_CELL_W = 8.0
BAR_GAP = 3.0
BAR_H = 16.0
PCT_STEPS = 21          # 0%, 5% ... 100%
PARTICLES = 200         # debris pixels; each carries the whole intro's keyframes
PARTICLE = 4.0          # pixel size, px
DOT_PITCH = 9.0         # sampling grid for word glyphs -- the dot-matrix look


def font_path() -> str:
    for candidate in FONT_CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    raise SystemExit("no bold TTF found; set WORDMARK_FONT")


# ---------------------------------------------------------------- point shell
def build_shell(text: str = TEXT) -> tuple[np.ndarray, np.ndarray]:
    """Rasterize text, then return (points Nx3, normals Nx3) for its surface."""
    path = font_path()
    probe = text.replace("\n", "")
    size = MASK_H
    for _ in range(40):                       # shrink until one line fits the raster
        font = ImageFont.truetype(path, size, index=FONT_INDEX)
        left, top, right, bottom = font.getbbox(probe)
        if bottom - top <= MASK_H:
            break
        size = int(size * 0.92)
    height = bottom - top
    track = int(round(TRACKING * size))
    lines = text.split("\n")
    line_h = int(round(height * LINE_GAP))

    def line_w(s: str) -> float:
        return sum(font.getlength(c) for c in s) + track * (len(s) - 1)

    total_w = int(round(max(line_w(s) for s in lines))) + 8
    total_h = line_h * (len(lines) - 1) + height + 8
    image = Image.new("L", (total_w, total_h), 0)
    draw = ImageDraw.Draw(image)
    for index, line in enumerate(lines):
        pen = 4.0 + (total_w - 8 - line_w(line)) / 2.0        # center each line
        base = -top + 4 + index * line_h
        for char in line:                                     # glyph by glyph, for tracking
            draw.text((pen, base), char, font=font, fill=255)
            pen += font.getlength(char) + track
    mask = np.array(image) > 127
    xs_any = np.nonzero(mask.any(0))[0]
    ys_any = np.nonzero(mask.any(1))[0]
    mask = mask[ys_any[0]:ys_any[-1] + 1, xs_any[0]:xs_any[-1] + 1]

    rows, cols = mask.shape
    depth = max(4, int(round(rows * DEPTH_FRAC)))
    cy, cx = np.nonzero(mask)

    points, normals = [], []
    # The front cap sits a hair proud of z=0, where the side walls begin. Without
    # the bias the two tie in the z-buffer and the letter faces come out streaked
    # with wall-shaded pixels. Walls still show past the silhouette, where they
    # belong, because yaw shifts them clear of the cap footprint.
    front = np.stack([cx, cy, np.full_like(cx, -0.6, dtype=float)], 1)
    points.append(front)
    normals.append(np.tile([0.0, 0.0, -1.0], (len(front), 1)))
    back = np.stack([cx, cy, np.full_like(cx, depth)], 1).astype(float)
    points.append(back)
    normals.append(np.tile([0.0, 0.0, 1.0], (len(back), 1)))

    # side walls: boundary pixels extruded through the full depth
    padded = np.pad(mask, 1)
    empty_r = ~padded[1:-1, 2:]
    empty_l = ~padded[1:-1, :-2]
    empty_d = ~padded[2:, 1:-1]
    empty_u = ~padded[:-2, 1:-1]
    edge = mask & (empty_r | empty_l | empty_d | empty_u)
    ey, ex = np.nonzero(edge)
    nx = empty_r[ey, ex].astype(float) - empty_l[ey, ex].astype(float)
    ny = empty_d[ey, ex].astype(float) - empty_u[ey, ex].astype(float)
    length = np.sqrt(nx * nx + ny * ny)
    length[length == 0] = 1.0
    nx, ny = nx / length, ny / length
    for z in np.linspace(0, depth, max(3, depth // 2)):
        points.append(np.stack([ex, ey, np.full_like(ex, z, dtype=float)], 1))
        normals.append(np.stack([nx, ny, np.zeros_like(nx)], 1))

    P = np.concatenate(points).astype(np.float32)
    N = np.concatenate(normals).astype(np.float32)
    P[:, 0] -= cols / 2.0                     # center on the origin, normalize to 1.0 wide
    P[:, 1] -= rows / 2.0
    P[:, 2] -= depth / 2.0
    P /= float(cols)
    return P, N


def rot_y(a: float) -> np.ndarray:
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], np.float32)


def rot_x(a: float) -> np.ndarray:
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], np.float32)


def project(P: np.ndarray, N: np.ndarray, yaw: float):
    """Rotate + perspective-divide. Returns visible (x, y, depth, shade index)."""
    M = rot_x(math.radians(TILT_DEG)) @ rot_y(yaw)
    p = P @ M.T
    n = N @ M.T
    visible = n[:, 2] < 0.0                   # camera sits at -z
    p, n = p[visible], n[visible]

    z = p[:, 2] + CAM_DIST
    f = FOCAL / z
    lambert = n @ LIGHT
    intensity = AMBIENT + (1 - AMBIENT) * np.clip(lambert, 0, 1)
    t = np.clip((z - CAM_DIST) / FOG_SPAN, -1.0, 1.0)          # depth fog
    intensity *= 1.0 - FOG * (t + 1.0) / 2.0
    idx = np.clip((intensity * (len(RAMP) - 1)).round().astype(int), 1, len(RAMP) - 1)
    return p[:, 0] * f, p[:, 1] * f, z, idx


def fit(projected) -> tuple[float, float, float]:
    """Width-driven scale + offset. Derives the row count from the art so the
    panel hugs the wordmark instead of leaving dead terminal space."""
    global ROWS
    xs = np.concatenate([q[0] for q in projected])
    ys = np.concatenate([q[1] for q in projected])
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    aspect = CELL_W / CELL_H
    scale = FIT * (COLS - 1) / (x1 - x0)
    ROWS = int(math.ceil((y1 - y0) * aspect * scale)) + 1 + 2 * ROW_MARGIN
    cx = (COLS - 1) / 2.0 - (x0 + x1) / 2.0 * scale
    cy = (ROWS - 1) / 2.0 - (y0 + y1) / 2.0 * scale * aspect
    return scale, cx, cy


def rasterize(q, scale: float, cx: float, cy: float) -> np.ndarray:
    """Z-buffer splat one projected frame into a ROWS x COLS grid of ramp indices.

    Indices rather than characters: emit() needs the index to pick both the glyph
    and its shade, and preview() can turn them back into text.
    """
    x, y, z, idx = q
    col = np.round(cx + x * scale).astype(int)
    row = np.round(cy + y * scale * (CELL_W / CELL_H)).astype(int)
    ok = (col >= 0) & (col < COLS) & (row >= 0) & (row < ROWS)
    col, row, z, idx = col[ok], row[ok], z[ok], idx[ok]

    grid = np.zeros((ROWS, COLS), np.int8)
    order = np.argsort(-z)                    # far -> near, nearest wins
    grid[row[order], col[order]] = idx[order]
    return grid


def grid_rows(grid: np.ndarray) -> list[str]:
    """Ramp indices back to text, for --preview."""
    return ["".join(RAMP[i] for i in r) for r in grid]


def render_text_grid(text: str, cols: int, yaw: float = REST_YAW,
                     max_rows: int | None = None) -> np.ndarray:
    """Render one text object with the wordmark material at a requested width."""
    global COLS, ROWS
    previous_cols, previous_rows = COLS, ROWS
    try:
        COLS = cols
        points, normals = build_shell(text)
        projected = project(points, normals, yaw)
        if max_rows is None:
            scale, cx, cy = fit([projected])
        else:
            x, y = projected[0], projected[1]
            x0, x1, y0, y1 = x.min(), x.max(), y.min(), y.max()
            aspect = CELL_W / CELL_H
            width_scale = FIT * (cols - 1) / (x1 - x0)
            height_scale = (max_rows - 1 - 2 * ROW_MARGIN) / ((y1 - y0) * aspect)
            scale = min(width_scale, height_scale)
            ROWS = max_rows
            cx = (cols - 1) / 2.0 - (x0 + x1) / 2.0 * scale
            cy = (max_rows - 1) / 2.0 - (y0 + y1) / 2.0 * scale * aspect
        return rasterize(projected, scale, cx, cy)
    finally:
        COLS, ROWS = previous_cols, previous_rows


def intro_word_grids(max_rows: int) -> dict[str, np.ndarray]:
    """Render approved intro forms inside the final wordmark's art height."""
    return {
        word: render_text_grid(word, cols, REST_YAW, max_rows)
        for word, cols in INTRO_WORD_COLS.items()
    }


# -------------------------------------------------------------- boot sequence
def target_cells(grid: np.ndarray, art_top: float) -> list[tuple[float, float]]:
    """Pixel centres of every inked cell in the rest pose, thinned to PARTICLES.

    Even stride rather than a random sample: the debris lands spread across the
    whole wordmark instead of clumping, and the output stays byte-identical run
    to run, which the determinism test depends on.
    """
    cells = [
        (PAD + col * CELL_W, art_top + row * CELL_H)
        for row, line in enumerate(grid)
        for col, value in enumerate(line)
        if value != 0
    ]
    if len(cells) <= PARTICLES:
        return cells
    stride = len(cells) / PARTICLES
    return [cells[int(i * stride)] for i in range(PARTICLES)]


def word_cells(word: str, art_top: float, art_h: float,
               width: float) -> list[tuple[float, float]]:
    """Dot-matrix cell centres for one word, resampled to exactly PARTICLES.

    Sampled on a DOT_PITCH grid rather than per pixel: the word reads as a dot
    matrix instead of a solid blob, which is the same language as the ASCII
    wordmark it eventually becomes. Fewer grid cells than particles just means
    some particles share a dot, which is invisible.
    """
    path = font_path()
    max_w, max_h = width * 0.62, art_h * 0.46
    size = 260
    for _ in range(60):
        font = ImageFont.truetype(path, size, index=FONT_INDEX)
        left, top, right, bottom = font.getbbox(word)
        if right - left <= max_w and bottom - top <= max_h:
            break
        size = int(size * 0.92)

    image = Image.new("L", (right - left + 4, bottom - top + 4), 0)
    ImageDraw.Draw(image).text((-left + 2, -top + 2), word, font=font, fill=255)
    mask = np.array(image) > 127

    step = int(DOT_PITCH)
    cells = [
        (x, y)
        for y in range(0, mask.shape[0] - step + 1, step)
        for x in range(0, mask.shape[1] - step + 1, step)
        if mask[y:y + step, x:x + step].any()
    ]
    ox = (width - mask.shape[1]) / 2
    oy = art_top + (art_h - mask.shape[0]) / 2
    points = [(ox + x, oy + y) for x, y in cells]
    return [points[i * len(points) // PARTICLES] for i in range(PARTICLES)]


def scene_status(art_top: float, art_h: float, width: float) -> str:
    """A telemetry readout that checks itself off row by row."""
    rows = [
        ("PROFILE.SCAN", "OK", "ok"),
        ("REPOSITORIES", "4 PUBLIC", "ok"),
        ("ORCHESTRATION", "ALMS / LANGGRAPH", "info"),
        ("HARNESS", "MULTI-REPO", "info"),
        ("VALIDATION", "TRACEABLE", "ok"),
        ("CONTRIB.FEED", "PUBLIC ENDPOINT", "warn"),
        ("ASSET.PIPELINE", "DETERMINISTIC", "ok"),
        ("RUNTIME", "SMIL / NO JS", "info"),
    ]
    left = PAD + 26
    right = width - PAD - 26
    parts = [f'<g><set attributeName="opacity" to="0" begin="{ALERT_END:.2f}s"/>']
    parts.append(f'<text x="{left}" y="{art_top + 20:.0f}" font-size="10.5" '
                 f'class="s1">KJ-AIML / profile-scan &#183; access level 3F &#183; '
                 f'public data only</text>')

    for i, (label, value, tone) in enumerate(rows):
        y = art_top + 56 + i * 24
        begin = 0.15 + i * (SCENE_STATUS - 0.55) / len(rows)
        parts.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{begin:.2f}s"/>')
        parts.append(f'<text x="{left - 16}" y="{y:.0f}" font-size="13" class="s0">|</text>')
        parts.append(f'<text x="{right + 8}" y="{y:.0f}" font-size="13" class="s0">|</text>')
        # the box flips a beat after the row lands, so the check reads as a result
        parts.append(f'<text x="{left}" y="{y:.0f}" font-size="13" class="s1">[ ]'
                     f'<set attributeName="opacity" to="0" begin="{begin + 0.22:.2f}s"/></text>')
        parts.append(f'<text x="{left}" y="{y:.0f}" font-size="13" class="ok" opacity="0">[x]'
                     f'<set attributeName="opacity" to="1" begin="{begin + 0.22:.2f}s"/></text>')
        parts.append(f'<text x="{left + 34}" y="{y:.0f}" font-size="13" class="info">'
                     f'{html.escape(label)}</text>')
        parts.append(f'<text x="{right}" y="{y:.0f}" font-size="13" class="{tone}" '
                     f'text-anchor="end" opacity="0">{html.escape(value)}'
                     f'<set attributeName="opacity" to="1" begin="{begin + 0.22:.2f}s"/></text>')
        parts.append("</g>")
    parts.append("</g>")
    return "".join(parts)


def scene_alerts(art_top: float, art_h: float, width: float) -> str:
    """Panels stack over the readout until the screen is buried, then clear."""
    panels = [
        (0.06, 0.10, "TRACE 0x4F2A", "reading public endpoint", "warn"),
        (0.46, 0.04, "SCAN /repos", "4 matched", "info"),
        (0.22, 0.34, "ALERT", "unsigned asset in tree", "bad"),
        (0.62, 0.28, "TRACE 0x91C7", "deterministic rebuild", "warn"),
        (0.10, 0.58, "ALERT", "identity not yet resolved", "bad"),
        (0.52, 0.62, "SCAN /assets", "5 svg &#183; 0 remote", "info"),
        (0.34, 0.46, "RESOLVING", "kj-aiml", "bad"),
    ]
    panel_w, panel_h = 212.0, 50.0
    # stagger over part of the scene, so the finished stack sits for a beat
    # before it clears instead of the last panel flashing and vanishing
    span = SCENE_ALERT * 0.62
    parts = [f'<g><set attributeName="opacity" to="0" begin="{ALERT_END:.2f}s"/>']
    for i, (fx, fy, title, body, tone) in enumerate(panels):
        x = PAD + fx * (width - 2 * PAD - panel_w)
        y = art_top + fy * (art_h - panel_h)
        begin = STATUS_END + i * span / len(panels)
        edge = ACCENT[tone]
        # alarm panels pulse; the scans and traces sit still, so the red carries
        # the eye instead of every panel competing for it
        pulse = ('<animate attributeName="opacity" values="1;0.45;1" dur="0.55s" '
                 'repeatCount="indefinite"/>' if tone == "bad" else "")
        parts.append(
            f'<g opacity="0"><set attributeName="opacity" to="1" begin="{begin:.2f}s"/>'
            f'<rect x="{x:.0f}" y="{y:.0f}" width="{panel_w:.0f}" height="{panel_h:.0f}" '
            f'rx="6" fill="{BG}" stroke="{edge}"/>'
            f'<rect x="{x:.0f}" y="{y:.0f}" width="{panel_w:.0f}" height="17" rx="6" fill="{edge}"/>'
            f'<text x="{x + 9:.0f}" y="{y + 13:.0f}" font-size="10" fill="{BG}" '
            f'font-weight="700">{title}{pulse}</text>'
            f'<text x="{x + 9:.0f}" y="{y + 36:.0f}" font-size="11" class="{tone}">{body}</text>'
            f'</g>'
        )
    parts.append("</g>")
    return "".join(parts)


def grid_group(grid: np.ndarray, art_top: float, x_offset: float,
               extra: str = "") -> str:
    """Emit a shaded ASCII grid as compact runs of SVG text cells."""
    font_size = CELL_H * 0.92
    out_rows: list[str] = []
    for ry, row in enumerate(grid):
        y = art_top + ry * CELL_H + CELL_H * 0.78
        run: list[str] = []
        run_start = 0
        bucket = -1

        def flush() -> None:
            if not run:
                return
            body = "".join(run).rstrip()
            if body:
                out_rows.append(
                    f'<text xml:space="preserve" x="{x_offset + run_start * CELL_W:.0f}" '
                    f'y="{y:.1f}" font-size="{font_size:.1f}" class="s{bucket}" '
                    f'textLength="{len(body) * CELL_W:.0f}" '
                    f'lengthAdjust="spacing">{html.escape(body)}</text>'
                )
            run.clear()

        for cx_i, value in enumerate(row):
            if value == 0:
                if run:
                    run.append(" ")
                continue
            shade = BUCKETS[value]
            if run and shade != bucket:
                flush()
            if not run:
                run_start, bucket = cx_i, shade
            run.append(RAMP[value])
        flush()
    return f"<g{extra}>" + "".join(out_rows) + "</g>"


def boot_sequence(rest: np.ndarray, art_top: float, art_w: float, art_h: float,
                  width: float) -> str:
    """Loading bar -> burst -> reassembly into the wordmark. Plays once."""
    bar_w = BAR_CELLS * (BAR_CELL_W + BAR_GAP) - BAR_GAP
    bar_x = (width - bar_w) / 2
    bar_y = art_top + art_h / 2 - BAR_H / 2
    parts = [f'<g opacity="0"><set attributeName="opacity" to="1" begin="{BAR_START:.2f}s"/>'
             f'<set attributeName="opacity" to="0" begin="{BAR_START + BOOT_FILL:.2f}s"/>']

    parts.append(f'<text x="{bar_x:.1f}" y="{bar_y - 14:.0f}" font-size="12.5" class="s3">'
                 f'{html.escape(TEXT)}</text>')
    for step in range(PCT_STEPS):
        pct = round(step * 100 / (PCT_STEPS - 1))
        begin = BAR_START + step * BOOT_FILL / PCT_STEPS
        hide = ("" if step == PCT_STEPS - 1 else
                f'<set attributeName="opacity" to="0" begin="{begin + BOOT_FILL / PCT_STEPS:.3f}s"/>')
        parts.append(f'<text x="{bar_x + bar_w:.1f}" y="{bar_y - 14:.0f}" font-size="12.5" '
                     f'fill="{TITLE_TEXT}" text-anchor="end" opacity="0">{pct:3d}%'
                     f'<set attributeName="opacity" to="1" begin="{begin:.3f}s"/>{hide}</text>')

    for i in range(BAR_CELLS):
        x = bar_x + i * (BAR_CELL_W + BAR_GAP)
        parts.append(f'<rect x="{x:.1f}" y="{bar_y:.1f}" width="{BAR_CELL_W:.0f}" '
                     f'height="{BAR_H:.0f}" fill="{FRAME}">'
                     f'<set attributeName="fill" to="{SHADES[3]}" '
                     f'begin="{BAR_START + i * BOOT_FILL / BAR_CELLS:.3f}s"/></rect>')

    parts.append(f'<text x="{bar_x:.1f}" y="{bar_y + BAR_H + 22:.0f}" font-size="11" '
                 f'fill="{TITLE_TEXT}">reconstructing identity from surface points</text>')
    parts.append("</g>")

    # One particle set carries the whole show. Each rect gets a single
    # animateTransform whose values walk every station in order:
    #   word 0 -> scatter -> word 1 -> ... -> word N -> bar seat -> scatter -> wordmark
    # Spelling five words with five separate effects would cost five times the
    # elements for the same picture; the chain is why this stays one rect each.
    word_pts = [word_cells(word, art_top, art_h, width) for word, _ in WORDS]
    targets = target_cells(rest, art_top)
    span = BOOT_END - WORDS_START

    def at(t: float) -> str:
        return f"{t / span:.4f}"

    word_grids = intro_word_grids(rest.shape[0])
    k_in = 0.18 / WORD_CYCLE
    k_hold = WORD_HOLD / WORD_CYCLE
    k_out = (WORD_HOLD + 0.12) / WORD_CYCLE
    for w, (word, _tone) in enumerate(WORDS):
        grid = word_grids[word]
        x_offset = PAD + (COLS - grid.shape[1]) * CELL_W / 2
        anim = (f'<animate attributeName="opacity" values="0;1;1;0;0" '
                f'keyTimes="0;{k_in:.4f};{k_hold:.4f};{k_out:.4f};1" '
                f'dur="{WORD_CYCLE:.2f}s" begin="{WORDS_START + w * WORD_CYCLE:.2f}s" '
                f'fill="freeze"/>')
        group = grid_group(
            grid, art_top, x_offset,
            f' data-intro-word="{word}" opacity="0"',
        )
        parts.append(group.replace("</g>", anim + "</g>"))

    for i in range(PARTICLES):
        seat = i % BAR_CELLS
        bx = bar_x + seat * (BAR_CELL_W + BAR_GAP) + (BAR_CELL_W - PARTICLE) / 2
        by = bar_y + (BAR_H - PARTICLE) / 2
        # golden-angle scatter: fans evenly, and no RNG keeps the file byte-stable
        angle = 2.399963229728653 * i
        radius = 0.42 * art_w * (0.35 + 0.65 * ((i * 7) % 11) / 10.0)
        # vertical throw is scaled to the panel's aspect so the debris stays inside
        # the viewport -- anything past the edge is clipped and reads as a dropout
        sx, sy = math.cos(angle) * radius, math.sin(angle) * radius * (art_h / art_w)

        stops: list[tuple[float, float, float]] = []
        fades: list[tuple[float, float]] = []
        for w, cells in enumerate(word_pts):
            wx, wy = cells[i]
            start = w * WORD_CYCLE
            stops.append((start, wx, wy))                       # converged on the word
            stops.append((start + WORD_HOLD, wx, wy))
            burst = start + WORD_HOLD + WORD_BURST * 0.55       # blown apart
            stops.append((burst, wx + sx, wy + sy))
            # visible converging, gone while the glyphs are legible, back on the
            # way out -- so the debris never competes with the word it just built
            fades.append((start, 1.0))
            fades.append((start + 0.20, 0.0))
            fades.append((start + WORD_HOLD, 0.0))
            fades.append((start + WORD_HOLD + WORD_BURST * 0.35, 1.0))
        bar_at = len(WORDS) * WORD_CYCLE
        stops.append((bar_at, bx, by))                          # seat into the bar
        stops.append((bar_at + BOOT_FILL, bx, by))
        stops.append((bar_at + BOOT_FILL + BOOT_BURST, bx + sx, by + sy))
        stops.append((span, *targets[i % len(targets)]))        # land on the wordmark
        # dark while parked in the bar, so the seated particles do not fleck it
        fades.append((bar_at, 0.0))
        fades.append((bar_at + BOOT_FILL, 0.0))
        fades.append((bar_at + BOOT_FILL + 0.06, 1.0))
        fades.append((span - 0.18, 1.0))
        fades.append((span, 0.0))

        values = ";".join(f"{x:.0f} {y:.0f}" for _, x, y in stops)
        key_times = ";".join(at(t) for t, _, _ in stops)
        fade_values = ";".join(f"{o:.2f}" for _, o in fades)
        fade_times = ";".join(at(t) for t, _ in fades)
        parts.append(
            f'<rect width="{PARTICLE:.0f}" height="{PARTICLE:.0f}" class="s3" opacity="0">'
            f'<animate attributeName="opacity" values="{fade_values}" '
            f'keyTimes="{fade_times}" dur="{span:.2f}s" '
            f'begin="{WORDS_START:.2f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="{values}" keyTimes="{key_times}" dur="{span:.2f}s" '
            f'begin="{WORDS_START:.2f}s" fill="freeze"/></rect>'
        )
    return "".join(parts)


# ---------------------------------------------------------------------- svg
def emit(frames: list[np.ndarray], mode: str, out: Path, dur: float) -> None:
    art_w = COLS * CELL_W
    art_h = ROWS * CELL_H
    width = art_w + PAD * 2
    height = TITLEBAR_H + art_h + PAD
    art_top = TITLEBAR_H + PAD * 0.3
    count = len(frames)

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" role="img" font-family="ui-monospace, '
        f'SFMono-Regular, Menlo, Monaco, Consolas, &quot;Liberation Mono&quot;, monospace">',
        f'<title>{xml(f"{TEXT} 3D ASCII wordmark")}</title>',
        f'<desc>{xml(f"The handle {TEXT} extruded into a 3D slab and rasterized to ASCII characters, rocking on its vertical axis inside a terminal panel.")}</desc>',
        '<style>'
        + "".join(f'.s{i}{{fill:{c}}}' for i, c in enumerate(SHADES))
        + "".join(f'.{k}{{fill:{v}}}' for k, v in ACCENT.items())
        + '</style>',
        '<defs><linearGradient id="wbg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
        '</linearGradient></defs>',
        f'<rect width="{width:.0f}" height="{height:.0f}" rx="14" fill="url(#wbg)"/>',
        f'<rect x="0.5" y="0.5" width="{width-1:.0f}" height="{height-1:.0f}" rx="14" '
        f'fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{width:.0f}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]
    for i, dot in enumerate(DOTS):
        parts.append(f'<circle cx="{PAD + i * 18}" cy="{TITLEBAR_H / 2}" r="5" fill="{dot}"/>')
    parts.append(f'<text x="{width / 2:.0f}" y="{TITLEBAR_H / 2 + 4:.0f}" fill="{TITLE_TEXT}" '
                 f'font-size="11.5" text-anchor="middle">KJ@AI-ENGINEER: ~$ ./wordmark.sh --3d</text>')

    def frame_group(grid: np.ndarray, extra: str = "") -> str:
        return grid_group(grid, art_top, PAD, extra)

    if mode == "static":                      # frozen frame 0 -- STATIC=1 fallback
        parts.append(frame_group(frames[0]))
        parts.append("</svg>\n")
        out.write_text("".join(parts), encoding="utf-8")
        print(f"wrote {out} (static)")
        return

    parts.append(scene_status(art_top, art_h, width))
    parts.append(scene_alerts(art_top, art_h, width))
    parts.append(boot_sequence(frames[0], art_top, art_w, art_h, width))

    if mode == "once":
        # play the flipbook once, then hold the last frame (the rest pose)
        step = dur / count
        for i, rows in enumerate(frames):
            begin = BOOT_END + i * step
            sets = f'<set attributeName="opacity" to="1" begin="{begin:.3f}s"/>'
            if i != count - 1:
                sets += f'<set attributeName="opacity" to="0" begin="{begin + step:.3f}s"/>'
            parts.append(frame_group(rows, ' opacity="0"').replace("</g>", sets + "</g>"))
    else:
        # cycle forever; frame i owns the [i/n, (i+1)/n] slice of the loop
        for i, rows in enumerate(frames):
            if i == 0:
                values, key_times = "1;0", f"0;{1 / count:.5f}"
            else:
                values, key_times = "0;1;0", f"0;{i / count:.5f};{(i + 1) / count:.5f}"
            anim = (f'<animate attributeName="opacity" calcMode="discrete" values="{values}" '
                    f'keyTimes="{key_times}" dur="{dur:.2f}s" begin="{BOOT_END:.2f}s" '
                    f'repeatCount="indefinite"/>')
            parts.append(frame_group(rows, ' opacity="0"').replace("</g>", anim + "</g>"))

    parts.append("</svg>\n")
    svg = "".join(parts)
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out}  {len(svg) / 1024:.1f} KB  {count} frames  {width:.0f}x{height:.0f}")


def generate(out: Path, mode: str = "rock", frames_count: int | None = None,
             dur: float | None = None, preview: bool = False) -> None:
    P, N = build_shell()
    rest = REST_YAW                           # the 3/4 pose the wordmark rests in
    if mode == "spin":
        count = frames_count or 36
        yaws = [rest + 2 * math.pi * i / count for i in range(count)]
        dur = dur or 7.0
    elif mode == "once":
        count = frames_count or 32
        yaws = [rest + 2 * math.pi * i / count for i in range(count)] + [rest]
        dur = dur or 3.6
    else:                                     # rock: ping-pong, cosine-eased
        count = frames_count or 20
        amp = math.radians(11)
        yaws = [rest + amp * math.sin(2 * math.pi * i / count) for i in range(count)]
        dur = dur or 5.0

    projected = [project(P, N, yaw) for yaw in yaws]
    scale, cx, cy = fit(projected)
    frames = [rasterize(q, scale, cx, cy) for q in projected]

    if preview:
        for row in grid_rows(frames[0]):
            print(row.rstrip())
        return
    emit(frames, mode, out, dur)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["spin", "once", "rock", "static"],
                        default="static" if os.environ.get("STATIC") == "1" else "rock")
    parser.add_argument("--out", default=str(ROOT / "assets/kj-wordmark.svg"))
    parser.add_argument("--frames", type=int, default=None)
    parser.add_argument("--dur", type=float, default=None)
    parser.add_argument("--preview", action="store_true", help="print frame 0 to stdout")
    args = parser.parse_args()
    generate(Path(args.out), args.mode, args.frames, args.dur, args.preview)


if __name__ == "__main__":
    main()
