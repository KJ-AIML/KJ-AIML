"""Hello hero: two articulated dot hands reach and touch, and the owner's handle
forms between them.

The hand artwork and the six-second pacing come from the owner's pi-ter project
(see data/README.md). Everything else is generated here, offline.

* Each hand is dithered once into dots, and every dot is bound to a bone:
  forearm -> wrist -> index finger -> its middle joint, or the other fingers.
* The motion comes from the joints. The arm swings about an off-canvas elbow, the
  wrist starts limp and lifts, the index finger extends late in the reach, the
  last inch is slower, both fingers recoil at the touch, and the fingers relax
  before the wrist on the way out.
* A joint bends over several thin strips, each turning a fraction of the angle,
  so the dots stretch across a knuckle instead of cracking. The dots ride on the
  skin in nested SVG groups; nothing is re-dithered while the hands move.
* The handle is extruded and lit by generate_wordmark's point shell, then kept
  at dot resolution. The spark's particles fly into its shape before it lights.
* Dots are dashed strokes, not Braille glyphs, so they are square and crisp on
  every OS and font.

The animated file's base state is its final frame (`static-fallback`); SMIL hides
that frame and plays the scene over it. A viewer that ignores animation sees the
handle and caption immediately. `static` mode writes the same final frame as a
still for reduced-motion visitors.
"""

from __future__ import annotations

import argparse
import base64
import functools
import json
import math
from pathlib import Path
import zlib

import numpy as np

import generate_wordmark as shell
from svg_common import BG, BG2, BORDER, CHROME_H, DOTS, MUTED, xml

ROOT = Path(__file__).resolve().parents[1]
NAME = "kjct0s_"
CAPTION = "Hello KJ"
GREETING = "Hello World"
PROMPT = "KJ@AI-ENGINEER: ~$ ./hello-kj"

# ---------------------------------------------------------------- geometry
COLS, ROWS = 168, 40                     # dot cells; a cell is 2 x 4 dots
CELL_W, CELL_H = 5.0, 10.0
DP = CELL_W / 2                          # dot pitch, px
WIDTH = 855
X0 = (WIDTH - COLS * CELL_W) / 2
Y0 = CHROME_H + 8
HEIGHT = int(Y0 + ROWS * CELL_H + 12)
SCALE = min(COLS / 736, ROWS * 2 / 280)  # cells per reference unit; pi-ter's scene is 736 x 480
OX = (COLS - 736 * SCALE) / 2
OY = ROWS / 2 - 225 * SCALE / 2
K = 2 * SCALE                            # dots per reference unit
NAME_COLS = 116
NAME_YAW = math.radians(-6)              # less turn than the legacy wordmark, so letters keep their counters

T_END = 6.4
STEPS = 154                              # motion samples, about 24 per second
TOUCH = 2.74

BAYER = np.array([0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5])
GREEN = "#69ff43"
GLINT = "#b6ff9c"
HAND_SHADES = ["#3d433d", "#596059", "#7a807a", "#9ea49e", "#c3c8c3", "#e8ece8"]
NAME_SHADES = ["#4f5965", "#77818c", "#a1aab4", "#c9d1d9", "#e9eef3", "#ffffff"]
DOT_SIZE = [1.35, 1.5, 1.65, 1.78, 1.9, 2.0]     # px; brighter dots are larger
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
EASE_OUT = "0.15 0.85 0.35 1"
EASE_IN_OUT = "0.55 0 0.35 1"

# Joints, in pi-ter reference units, read off the source images. Angles are SVG
# degrees (positive is clockwise on screen). Every joint is 0 in the drawn pose,
# which is the pose the hands hold at the touch.
RIGS = [
    {   # left hand: enters from the left, wrist drooping, index finger lower right
        "elbow": (-190, 172),
        "wrist": {"p": (165, 138), "d": (0.934, 0.358), "L": 44, "n": 7},
        "fingers": [
            {"name": "index", "p": (233, 160), "d": (0.526, 0.850), "L": 16, "n": 4,
             "poly": [(222, 150), (248, 152), (270, 195), (267, 213), (250, 213), (245, 200),
                      (241.5, 190), (236, 180), (228, 168)],
             "child": {"name": "pip", "p": (246, 181), "d": (0.526, 0.850), "L": 12, "n": 3}},
            {"name": "others", "p": (210, 176), "d": (0.25, 0.968), "L": 18, "n": 3,
             "poly": [(186, 176), (228, 168), (236, 180), (241.5, 190), (245, 200), (250, 213),
                      (244, 226), (184, 226), (176, 196)]},
        ],
    },
    {   # right hand: enters from the right, index finger pointing left
        "elbow": (925, 335),
        "wrist": {"p": (595, 269), "d": (-0.985, -0.171), "L": 44, "n": 7},
        "fingers": [
            {"name": "index", "p": (527, 253), "d": (-0.988, -0.153), "L": 16, "n": 4,
             "poly": [(446, 234), (470, 230), (530, 239), (535, 262), (503, 264), (487, 259),
                      (463, 255), (448, 253)],
             "child": {"name": "pip", "p": (492, 247), "d": (-0.988, -0.153), "L": 12, "n": 3}},
            {"name": "others", "p": (528, 290), "d": (-1.0, 0.0), "L": 18, "n": 3,
             "poly": [(470, 262), (487, 259), (503, 264), (530, 266), (532, 320), (500, 322),
                      (468, 314)]},
        ],
    },
]
ARM_SLOPE = (-0.055, 0.05)               # top-edge slope of each forearm where its image ends


def num(value: float) -> str:
    """Shortest fixed-point form with at most two decimals."""
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def to_dot(point) -> tuple[float, float]:
    """Reference point -> continuous dot coordinates."""
    return point[0] * K + 2 * OX, point[1] * K + 4 * OY


def pivot_px(point) -> tuple[float, float]:
    """Reference point -> the pixel space the dot paths are drawn in."""
    gx, gy = to_dot(point)
    return gx * DP, (gy - 0.5) * DP


def to_canvas(px: np.ndarray, py: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Continuous dot coordinates -> SVG pixels."""
    return X0 + px * DP, Y0 + py * DP


# ------------------------------------------------------------ hand artwork
@functools.lru_cache(maxsize=None)
def fields() -> tuple[dict, ...]:
    data = json.loads((Path(__file__).parent / "data/pi-ter-hands.json").read_text(encoding="utf-8"))
    out = []
    for field in data["fields"]:
        raw = np.frombuffer(zlib.decompress(base64.b64decode(field["data"])), dtype=np.uint8)
        raw = raw.reshape(field["h"], field["w"], 2)
        out.append({**{key: field[key] for key in "xywh"}, "a": raw[..., 0] / 255.0, "l": raw[..., 1] / 255.0})
    return tuple(out)


def sample(i: int, x: np.ndarray, y: np.ndarray) -> list[np.ndarray]:
    """Bilinear (alpha, luminance). Past the image edge the forearm continues as
    a sheared mirror image, so its top edge stays straight instead of kinking."""
    field = fields()[i]
    x, y = x.astype(float).copy(), y.astype(float).copy()
    mirror = field["x"] + 1 if i == 0 else field["x"] + field["w"] - 2
    beyond = x < mirror if i == 0 else x > mirror
    y[beyond] -= 2 * ARM_SLOPE[i] * (x[beyond] - mirror)
    x[beyond] = 2 * mirror - x[beyond]
    xx, yy = x - field["x"], y - field["y"]
    inside = (xx >= 0) & (yy >= 0) & (xx < field["w"] - 1) & (yy < field["h"] - 1)
    ix = np.clip(np.floor(xx).astype(int), 0, field["w"] - 2)
    iy = np.clip(np.floor(yy).astype(int), 0, field["h"] - 2)
    fx, fy = xx - ix, yy - iy
    out = []
    for channel in ("a", "l"):
        g = field[channel]
        value = (g[iy, ix] * (1 - fx) * (1 - fy) + g[iy, ix + 1] * fx * (1 - fy)
                 + g[iy + 1, ix] * (1 - fx) * fy + g[iy + 1, ix + 1] * fx * fy)
        out.append(np.where(inside, value, 0.0))
    return out


def in_polygon(x: np.ndarray, y: np.ndarray, polygon) -> np.ndarray:
    inside = np.zeros(x.shape, bool)
    for k in range(len(polygon)):
        (x1, y1), (x2, y2) = polygon[k], polygon[(k + 1) % len(polygon)]
        inside ^= ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1)
    return inside


def build_hand(i: int) -> dict:
    """Dither one hand in its drawn pose and bind every dot to a bone."""
    rig = RIGS[i]
    lo, hi = (-135, 285) if i == 0 else (430, 870)
    gxs, gys = np.meshgrid(np.arange(math.floor(to_dot((lo, 0))[0]), math.ceil(to_dot((hi, 0))[0])),
                           np.arange(-24, ROWS * 4 + 24))
    gx, gy = gxs.ravel(), gys.ravel()
    x = (gx + 0.5 - 2 * OX) / K
    y = (gy + 0.5 - 4 * OY) / K
    alpha, luma = sample(i, x, y)
    # The gain makes lit skin solid; without it the highlights keep regular dither holes.
    on = np.minimum(1.0, alpha * (0.42 + 0.58 * luma) * 1.12) > (BAYER[(gy % 4) * 4 + gx % 4] + 0.5) / 16
    gx, gy, x, y, luma = gx[on], gy[on], x[on], y[on], luma[on]

    def level(joint, mask):
        along = (x - joint["p"][0]) * joint["d"][0] + (y - joint["p"][1]) * joint["d"][1]
        strip = np.rint(np.clip((along + joint["L"] / 2) / joint["L"], 0, 1) * joint["n"]).astype(int)
        strip[~mask] = 0
        return strip

    wrist = level(rig["wrist"], np.ones(x.shape, bool))
    finger = np.full(x.shape, -1)
    knuckle = np.zeros(x.shape, int)
    middle = np.zeros(x.shape, int)
    for index, spec in enumerate(rig["fingers"]):
        inside = in_polygon(x, y, spec["poly"])
        strip = level(spec, inside)
        chosen = strip > 0
        if not (wrist[chosen] == rig["wrist"]["n"]).all():
            raise ValueError("a finger region overlaps the wrist blend")
        finger[chosen], knuckle[chosen] = index, strip[chosen]
        if "child" in spec:
            middle[chosen] = level(spec["child"], inside & (strip == spec["n"]))[chosen]
    return {"gx": gx, "gy": gy, "tone": np.clip((luma * 6).astype(int), 0, 5),
            "wrist": wrist, "finger": finger, "knuckle": knuckle, "middle": middle}


# ------------------------------------------------------------------ motion
def ease(x: float) -> float:
    """Minimum-jerk ease: how a relaxed limb moves between two poses."""
    x = min(1.0, max(0.0, x))
    return x * x * x * (10 + x * (-15 + 6 * x))


def recoil(t: float) -> float:
    u = t - TOUCH
    return math.exp(-u / 0.17) * math.sin(2 * math.pi * u / 0.44) if u > 0 else 0.0


def pose(i: int, t: float, retreat: float, close=((0.0, 0.0), (0.0, 0.0))) -> dict:
    """Joint angles and arm offset (reference units) for hand i at time t."""
    lead = 0.07 if i == 0 else 0.0                 # the pointing hand reaches first
    enter = ease(t / 1.5)
    reach = 0.86 * ease((t - 1.22 - lead) / 1.05) + 0.14 * ease((t - 2.34) / 0.40)
    leave = ease((t - 3.02) / 1.5)
    wrist_up = ease((t - 1.35 - lead) / 1.2)       # the wrist follows the arm
    wrist_limp = ease((t - 3.12) / 1.5)
    extend = ease((t - 1.75 - lead) / 0.9)         # fingers open late in the reach
    relax = ease((t - 3.0) / 1.1)                  # ...and let go first
    kick = recoil(t)
    inch = ease((t - 2.34) / 0.40) * (1 - leave)   # closing the last inch before the touch
    cx, cy = close[i][0] * inch, close[i][1] * inch
    life = 0.5 * math.sin(2 * math.pi * 0.9 * t + i * 1.7) * ease(t) * (1 - ease((t - 4.2) / 1.2))
    if i == 0:
        return {"tx": -115 * (1 - enter) + 82 * reach - retreat * leave + cx - 5 * kick,
                "ty": 28 * reach - 22 * leave + cy,
                "arm": 5 - 2.5 * enter - 2.5 * reach - 5 * leave,
                "wrist": 14 * (1 - wrist_up) + 16 * wrist_limp + 2 * kick + life,
                "index": 16 * (1 - extend) + 14 * relax + 7 * kick,
                "pip": 12 * (1 - extend) + 10 * relax + 4 * kick,
                "others": 10 * (1 - extend) + 12 * relax + 2 * kick}
    return {"tx": 115 * (1 - enter) - 82 * reach + retreat * leave + cx + 4 * kick,
            "ty": -9 * reach + 7 * leave + cy,
            "arm": -4 + 2 * enter + 2 * reach - 4 * leave,
            "wrist": -8 * (1 - wrist_up) - 12 * wrist_limp - 2 * kick - life,
            "index": -22 * (1 - extend) - 18 * relax - 8 * kick,
            "pip": -16 * (1 - extend) - 12 * relax - 5 * kick,
            "others": -6 * (1 - extend) - 8 * relax - 2 * kick}


def rotate(px, py, pivot, degrees):
    radians = np.radians(degrees)
    c, s = np.cos(radians), np.sin(radians)
    dx, dy = px - pivot[0], py - pivot[1]
    return pivot[0] + dx * c - dy * s, pivot[1] + dx * s + dy * c


def place(i: int, hand: dict, p: dict) -> tuple[np.ndarray, np.ndarray]:
    """Where every dot of a hand is for one pose, in continuous dot coordinates."""
    rig = RIGS[i]
    px, py = hand["gx"] + 0.5, hand["gy"] + 0.5
    for index, spec in enumerate(rig["fingers"]):
        mine = hand["finger"] == index
        if "child" in spec:
            child = spec["child"]
            px, py = rotate(px, py, to_dot(child["p"]),
                            np.where(mine, p[child["name"]] * hand["middle"] / child["n"], 0.0))
        px, py = rotate(px, py, to_dot(spec["p"]), np.where(mine, p[spec["name"]] * hand["knuckle"] / spec["n"], 0.0))
    wrist = rig["wrist"]
    px, py = rotate(px, py, to_dot(wrist["p"]), p["wrist"] * hand["wrist"] / wrist["n"])
    px, py = rotate(px, py, to_dot(rig["elbow"]), p["arm"])
    return px + p["tx"] * K, py + p["ty"] * K


# ------------------------------------------------------------------- name
def build_name() -> dict:
    """The handle as an extruded, lit slab, splatted at dot resolution.

    The shell comes from generate_wordmark. The projection is redone here in
    float64 with explicit sums: a float32 matrix product can round differently
    from one BLAS build to the next, and a dot that moves changes the file.
    """
    points, normals = shell.build_shell(NAME)
    points, normals = points.astype(np.float64), normals.astype(np.float64)
    tilt = math.radians(shell.TILT_DEG)
    ct, st, cw, sw = math.cos(tilt), math.sin(tilt), math.cos(NAME_YAW), math.sin(NAME_YAW)
    turn = ((cw, 0.0, sw), (st * sw, ct, -st * cw), (-ct * sw, st, ct * cw))     # rot_x(tilt) @ rot_y(yaw)

    def apply(v):
        return [v[:, 0] * row[0] + v[:, 1] * row[1] + v[:, 2] * row[2] for row in turn]

    x, y, z = apply(points)
    nx, ny, nz = apply(normals)
    seen = nz < 0.0                                # the camera sits at -z
    x, y, z, nx, ny, nz = (v[seen] for v in (x, y, z, nx, ny, nz))
    depth = z + shell.CAM_DIST
    x, y = x * shell.FOCAL / depth, y * shell.FOCAL / depth
    light = [float(v) for v in shell.LIGHT]
    lit = shell.AMBIENT + (1 - shell.AMBIENT) * np.clip(nx * light[0] + ny * light[1] + nz * light[2], 0, 1)
    lit = lit * (1.0 - shell.FOG * (np.clip((depth - shell.CAM_DIST) / shell.FOG_SPAN, -1.0, 1.0) + 1.0) / 2.0)
    steps = len(shell.RAMP) - 1
    shade = np.clip(np.round(lit * steps).astype(int), 1, steps)

    dots_wide = NAME_COLS * 2
    scale = (dots_wide - 1) / (x.max() - x.min())
    px = np.round((x - x.min()) * scale).astype(int)
    py = np.round((y - y.min()) * scale).astype(int)
    rows = math.ceil((int(py.max()) + 1) / 4)
    py += (rows * 4 - int(py.max()) - 1) // 2
    grid = np.zeros((rows * 4, dots_wide), np.int16)
    order = np.argsort(-depth, kind="stable")      # far to near; the nearest point wins
    grid[py[order], px[order]] = shade[order]
    gy, gx = np.nonzero(grid)
    luma = (grid[gy, gx] - 1) / max(int(grid.max()) - 1, 1)
    on = 0.30 + 0.70 * luma > (BAYER[(gy % 4) * 4 + gx % 4] + 0.5) / 16 * 0.85
    return {"gx": gx[on], "gy": gy[on], "tone": np.clip((luma[on] * 6).astype(int), 0, 5), "rows": rows}


# ----------------------------------------------------------------- layout
GRID_X0, GRID_Y0, GRID_W, GRID_H = -90, -30, COLS + 180, ROWS + 60       # cell grid for clearance checks


def cell_mask(cx: np.ndarray, cy: np.ndarray) -> np.ndarray:
    grid = np.zeros((GRID_H, GRID_W), bool)
    cx, cy = cx - GRID_X0, cy - GRID_Y0
    ok = (cx >= 0) & (cx < GRID_W) & (cy >= 0) & (cy < GRID_H)
    grid[cy[ok], cx[ok]] = True
    return grid


def widen(mask: np.ndarray, dx: int, dy: int) -> np.ndarray:
    out = np.zeros_like(mask)
    for sy in range(-dy, dy + 1):
        for sx in range(-dx, dx + 1):
            out[max(sy, 0):GRID_H + min(sy, 0), max(sx, 0):GRID_W + min(sx, 0)] |= \
                mask[max(-sy, 0):GRID_H + min(-sy, 0), max(-sx, 0):GRID_W + min(-sx, 0)]
    return out


@functools.lru_cache(maxsize=None)
def layout() -> dict:
    """Everything both modes share: the dots, the motion, and the reveal schedule."""
    hands = [build_hand(0), build_hand(1)]
    name = build_name()
    centre_x, centre_y = 357 * SCALE + OX, 232 * SCALE / 2 + OY          # pi-ter's meeting point, in cells
    nx0 = round(centre_x - NAME_COLS / 2)
    ny0 = round(centre_y - name["rows"] / 2) - 1
    ncx, ncy = name["gx"] // 2 + nx0, name["gy"] // 4 + ny0
    air = widen(cell_mask(ncx, ncy), 3, 1)

    # How far apart the fingertips are in the drawn pose, and so how far each hand still has to go.
    tips = []
    for i in (0, 1):
        spec = RIGS[i]["fingers"][0]
        px, py = place(i, hands[i], pose(i, TOUCH, 0.0))
        tip = (hands[i]["finger"] == 0) & (hands[i]["middle"] == spec["child"]["n"])
        far = np.argmax(px[tip] * spec["d"][0] + py[tip] * spec["d"][1])
        tips.append((float(px[tip][far]), float(py[tip][far])))
    gap = (tips[1][0] - tips[0][0], tips[1][1] - tips[0][1])
    distance = math.hypot(*gap)
    share = max(0.0, 0.5 - 1.0 / distance)         # leave about two dots of air between the tips
    close = ((gap[0] * share / K, gap[1] * share / K), (-gap[0] * share / K, -gap[1] * share / K))
    meet = ((tips[0][0] + tips[1][0]) / 2, (tips[0][1] + tips[1][1]) / 2)

    def occupied(t: float, retreat: float) -> np.ndarray:
        grid = np.zeros((GRID_H, GRID_W), bool)
        for i in (0, 1):
            px, py = place(i, hands[i], pose(i, t, retreat, close))
            grid |= cell_mask(np.floor(px / 2).astype(int), np.floor(py / 4).astype(int))
        return grid

    retreat = 62                                   # pull the hands back until the name has clear air
    while retreat < 420 and (occupied(T_END, retreat) & air).any():
        retreat += 4
    times = [k * T_END / STEPS for k in range(STEPS + 1)]
    poses = [[pose(i, t, retreat, close) for t in times] for i in (0, 1)]

    # The name lights from the centre outward, each strip only once the hands have left it.
    strips = 14
    strip = np.minimum(strips - 1, (np.abs(name["gx"] / 2 + 0.25 - NAME_COLS / 2) / (NAME_COLS / 2) * strips)
                       .astype(int))
    track = [(k / 30, occupied(k / 30, retreat)) for k in range(87, int(T_END * 30) + 1)]
    reveal = {}
    for b in range(strips):
        mine = strip == b
        if mine.any():
            zone = widen(cell_mask(ncx[mine], ncy[mine]), 2, 0)
            clear = next((t for t, grid in track if not (grid & zone).any()), T_END)
            reveal[b] = max(3.45 + b * 0.05, clear + 0.06)
    return {"hands": hands, "name": name, "nx0": nx0, "ny0": ny0, "centre": (centre_x, centre_y),
            "meet": meet, "gap": distance, "close": close, "retreat": retreat, "times": times,
            "poses": poses, "strip": strip, "reveal": reveal}


# -------------------------------------------------------------------- emit
def lattice_paths(gx, gy, tone, prefix: str, stroke=None) -> str:
    """One path per tone. Each subpath is a run of lit dots on one row, drawn as
    a dashed stroke: square dots, a fraction of the bytes of one element each."""
    out = []
    for t in range(len(DOT_SIZE)):
        mine = tone == t
        if not mine.any():
            continue
        order = np.lexsort((gx[mine], gy[mine]))
        xs, ys = gx[mine][order].tolist(), gy[mine][order].tolist()
        d, start, prev, row = [], xs[0], xs[0], ys[0]
        for x, y in zip(xs[1:] + [None], ys[1:] + [None]):
            if x is not None and y == row and x == prev + 1:
                prev = x
                continue
            d.append(f"M{num(start * DP)} {num(row * DP)}h{num((prev - start + 1) * DP - 0.1)}")
            start, prev, row = x, x, y
        paint = f' stroke="{stroke(t)}"' if stroke else ""
        out.append(f'<path class="{prefix}{t}"{paint} d="{"".join(d)}"/>')
    return "".join(out)


def dot_css(prefix: str, shades) -> str:
    return "".join(
        f".{prefix}{t}{{fill:none;{'stroke:' + shades[t] + ';' if shades else ''}stroke-width:{num(size)};"
        f"stroke-dasharray:{num(size)} {num(DP - size)};stroke-dashoffset:{num((DP + size) / 2)}}}"
        for t, size in enumerate(DOT_SIZE))


def spin(angles) -> str:
    return (f'<animateTransform attributeName="transform" type="rotate" '
            f'values="{";".join(num(a) for a in angles)}" dur="{num(T_END)}s" fill="freeze"/>')


def joint(pivot, strips: int, angles, dots_at, at_full: str = "") -> str:
    """A bending joint: nested strips, each turning 1/strips of the angle about the pivot."""
    px, py = pivot_px(pivot)
    turn = spin([a / strips for a in angles])
    out = ""
    for k in range(strips, 0, -1):
        body = f'<g transform="translate({num(-px)} {num(-py)})">{dots_at(k)}{at_full if k == strips else ""}</g>'
        out = f"<g>{turn}{body}{out}</g>"
    return f'<g transform="translate({num(px)} {num(py)})">{out}</g>'


def rigged_hand(i: int, hand: dict, poses: list[dict]) -> str:
    rig = RIGS[i]
    series = {key: [p[key] for p in poses] for key in poses[0]}

    def dots(mask) -> str:
        return lattice_paths(hand["gx"][mask], hand["gy"][mask], hand["tone"][mask], "h")

    fingers = ""
    for index, spec in enumerate(rig["fingers"]):
        mine = hand["finger"] == index
        child = ""
        if "child" in spec:
            c = spec["child"]
            child = joint(c["p"], c["n"], series[c["name"]], lambda k, m=mine: dots(m & (hand["middle"] == k)))
        fingers += joint(spec["p"], spec["n"], series[spec["name"]],
                         lambda k, m=mine: dots(m & (hand["knuckle"] == k) & (hand["middle"] == 0)), child)
    wrist = rig["wrist"]
    free = hand["finger"] == -1
    bending = joint(wrist["p"], wrist["n"], series["wrist"], lambda k: dots(free & (hand["wrist"] == k)), fingers)
    ex, ey = pivot_px(rig["elbow"])
    slide = ";".join(f'{num(p["tx"] * K * DP)} {num(p["ty"] * K * DP)}' for p in poses)
    return (
        f'<g opacity="0"><animate attributeName="opacity" values="0;1;1;0.36;0.36" '
        f'keyTimes="0;{0.8 / T_END:.4f};{4.0 / T_END:.4f};{5.1 / T_END:.4f};1" dur="{num(T_END)}s" fill="freeze" '
        f'calcMode="spline" keySplines="{EASE_OUT};0 0 1 1;{EASE_IN_OUT};0 0 1 1"/>'
        f'<g><animateTransform attributeName="transform" type="translate" values="{slide}" '
        f'dur="{num(T_END)}s" fill="freeze"/><g transform="translate({num(ex)} {num(ey)})"><g>{spin(series["arm"])}'
        f'<g transform="translate({num(-ex)} {num(-ey)})">{dots(hand["wrist"] == 0)}{bending}</g></g></g></g></g>')


def resting_hand(i: int, hand: dict, p: dict) -> str:
    """A hand frozen in one pose, as plain squares: the still has no transforms to rotate."""
    px, py = place(i, hand, p)
    x, y = px * DP, (py - 0.5) * DP
    keep = (x > -X0 - 4) & (x < WIDTH - X0 + 4) & (y > -Y0) & (y < HEIGHT - Y0 + 4)
    out = []
    for t, size in enumerate(DOT_SIZE):
        mine = keep & (hand["tone"] == t)
        if mine.any():
            d = "".join(f"M{num(a - size / 2)} {num(b)}h{num(size)}" for a, b in zip(x[mine].tolist(), y[mine].tolist()))
            out.append(f'<path class="s{t}" d="{d}"/>')
    return "".join(out)


def fade(values: str, key_times: str, begin: float, duration: float, splines: str | None = None) -> str:
    spline = f' calcMode="spline" keySplines="{splines}"' if splines else ""
    return (f'<animate attributeName="opacity" values="{values}" keyTimes="{key_times}" '
            f'begin="{begin:.3f}s" dur="{duration:.3f}s" fill="freeze"{spline}/>')


def from_start(appear: float, ramp: float, splines: str | None = None) -> str:
    """Hidden from the first frame, then fading in: for content that is visible without SMIL."""
    a, b = appear / T_END, min(1.0, (appear + ramp) / T_END)
    spline = f' calcMode="spline" keySplines="0 0 1 1;{splines};0 0 1 1"' if splines else ""
    return (f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{a:.4f};{b:.4f};1" '
            f'begin="0s" dur="{num(T_END)}s" fill="freeze"{spline}/>')


def text_at(cell_x: float, cell_y: float, size: float, body: str, extra: str = "") -> str:
    return (f'<text x="{X0 + cell_x * CELL_W:.1f}" y="{Y0 + cell_y * CELL_H + size * 0.35:.1f}" fill="{GREEN}" '
            f'font-family="{MONO}" font-size="{num(size)}" text-anchor="middle" xml:space="preserve"{extra}>{body}</text>')


def flashing(variants: list[tuple[float, str]], cell_x: float, cell_y: float, size: float, end: float) -> str:
    """Text that changes in steps: each variant shows from its time until the next one's."""
    parts = []
    for k, (t, body) in enumerate(variants):
        until = variants[k + 1][0] if k + 1 < len(variants) else end
        parts.append(text_at(cell_x, cell_y, size,
                             f'<set attributeName="opacity" to="1" begin="{t:.3f}s"/>'
                             f'<set attributeName="opacity" to="0" begin="{until:.3f}s"/>{xml(body)}', ' opacity="0"'))
    return "".join(parts)


def chrome() -> str:
    """Window frame and titlebar, drawn last so nothing ever paints over them."""
    lights = "".join(f'<circle cx="{18 + k * 18}" cy="{CHROME_H // 2}" r="5" fill="{dot}"/>'
                     for k, dot in enumerate(DOTS))
    return (f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="14" fill="none" stroke="{BORDER}"/>'
            f'<line x1="0" y1="{CHROME_H}" x2="{WIDTH}" y2="{CHROME_H}" stroke="{BORDER}"/>{lights}'
            f'<text x="{num(WIDTH / 2)}" y="{CHROME_H // 2 + 4}" fill="{MUTED}" font-family="{MONO}" '
            f'font-size="11.5" text-anchor="middle">{xml(PROMPT)}</text>')


def generate(out: Path, mode: str = "static") -> None:
    if mode not in {"static", "intro"}:
        raise ValueError(f"unknown hero mode: {mode}")
    scene = layout()
    hands, name, strip, reveal = scene["hands"], scene["name"], scene["strip"], scene["reveal"]
    nx0, ny0 = scene["nx0"], scene["ny0"]
    centre_x, centre_y = scene["centre"]
    ngx, ngy = name["gx"] + nx0 * 2, name["gy"] + ny0 * 4
    caption_row = ny0 + name["rows"] + 2.2
    space = f'transform="translate({num(X0)} {num(Y0 + DP / 2)})"'
    intro = mode == "intro"

    description = (f"The handle {NAME} as an extruded 3D wordmark made of dots, between two dimmed hands, "
                   f"above the words {CAPTION}.")
    if intro:
        description = (f"Two hands drawn in dots reach toward each other while {GREETING} appears. Their index "
                       f"fingers extend and touch, and a green spark bursts. The sparks fly into the shape of "
                       f"the handle {NAME}, which lights up as an extruded 3D wordmark while the hands relax "
                       f"and withdraw, followed by the words {CAPTION}. It plays once, in about six seconds, "
                       f"and holds. Without animation, the handle and caption are visible immediately.")
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img">',
        f'<title>{xml(CAPTION)}: {xml(NAME)}</title>',
        f'<desc>{xml(description)}</desc>',
    ]
    left, right, band = nx0 * 2 * DP, (nx0 + NAME_COLS) * 2 * DP, 150.0
    if intro:
        # For visitors who ask for reduced motion the file shows its final frame at once: the
        # scene is hidden, the finished handle and caption are forced visible, and the handle is
        # painted flat so the glint cannot cross it. An !important rule outranks SMIL.
        calm = ("@media (prefers-reduced-motion:reduce){#animated-scene{opacity:0!important}"
                ".f{opacity:1!important}"
                + "".join(f".n{t}{{stroke:{shade}}}" for t, shade in enumerate(NAME_SHADES)) + "}")
        parts.append(f'<style>{dot_css("h", HAND_SHADES)}{dot_css("n", None)}'
                     f'.g{{fill:none;stroke:{GREEN};stroke-width:1.5;stroke-dasharray:1.5 1;stroke-dashoffset:2}}'
                     f'{calm}</style>')
    else:
        parts.append(f'<style>{dot_css("n", NAME_SHADES)}' + "".join(
            f".s{t}{{fill:none;stroke:{HAND_SHADES[t]};stroke-width:{num(size)}}}"
            for t, size in enumerate(DOT_SIZE)) + "</style>")
    parts.append(f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}"/>'
                 f'<stop offset="1" stop-color="{BG}"/></linearGradient>')
    if intro:                                      # a pale-green glint that crosses the finished name once
        sweep_at, sweep_for = 5.0, 1.1
        for t, base in enumerate(NAME_SHADES):
            moves = "".join(
                f'<animate attributeName="{end}" values="{num(a)};{num(b)}" keyTimes="0;1" begin="{sweep_at:.1f}s" '
                f'dur="{sweep_for:.1f}s" fill="freeze" calcMode="spline" keySplines="{EASE_IN_OUT}"/>'
                for end, a, b in (("x1", left - band, right), ("x2", left, right + band)))
            parts.append(f'<linearGradient id="sw{t}" gradientUnits="userSpaceOnUse" x1="{num(left - band)}" y1="0" '
                         f'x2="{num(left)}" y2="0"><stop offset="0" stop-color="{base}"/>'
                         f'<stop offset="0.5" stop-color="{GLINT}"/><stop offset="1" stop-color="{base}"/>'
                         f'{moves}</linearGradient>')
    parts.append(f'</defs><rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#bg)"/>')

    if not intro:
        resting = [pose(i, T_END, scene["retreat"], scene["close"]) for i in (0, 1)]
        parts.append(f'<g {space} opacity="0.36">{resting_hand(0, hands[0], resting[0])}'
                     f'{resting_hand(1, hands[1], resting[1])}</g>')
        parts.append(f'<g {space}>{lattice_paths(ngx, ngy, name["tone"], "n")}</g>')
        parts.append(text_at(centre_x, caption_row, 14.0, xml(CAPTION)))
        parts.append(chrome() + "</svg>\n")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("".join(parts), encoding="utf-8", newline="\n")
        return

    # ---- the final frame. It is the file's base state; the animation only hides it until its moment.
    caption_at = max(reveal.values()) + 0.2
    settled = caption_at + len(CAPTION) / 12
    lit = [f'<g id="static-fallback"><g {space}>']
    for b, at in sorted(reveal.items()):
        mine = strip == b
        lit.append(f'<g class="f">{from_start(at, 0.45, EASE_OUT)}'
                   f'{lattice_paths(ngx[mine], ngy[mine], name["tone"][mine], "n", lambda t: f"url(#sw{t})")}</g>')
    lit.append("</g>" + text_at(
        centre_x, caption_row, 14.0,
        f'<animate attributeName="opacity" values="0;1;1" keyTimes="0;{settled / T_END:.4f};1" begin="0s" '
        f'dur="{num(T_END)}s" fill="freeze" calcMode="discrete"/>{xml(CAPTION)}', ' class="f"') + "</g>")
    parts.append("".join(lit))

    # ---- the scene, hidden unless SMIL runs
    play = ['<g id="animated-scene" opacity="0"><set attributeName="opacity" to="1" begin="0s"/>',
            f'<g {space}>{rigged_hand(0, hands[0], scene["poses"][0])}'
            f'{rigged_hand(1, hands[1], scene["poses"][1])}</g>']

    # the greeting fades in, holds, and decodes away
    variants = [(0.45, GREETING)]
    for k in range(len(GREETING)):
        t = 1.65 + k / 14
        variants.append((t, "".join(" " if c == " " else (" .:+#"[int(t * 21 + j * 3) % 5] if j < k else c)
                                    for j, c in enumerate(GREETING))))
    play.append(f'<g opacity="0">{fade("0;1", "0;1", 0.45, 0.4, EASE_OUT)}{fade("1;0", "0;1", 2.0, 0.4)}'
                f'{flashing(variants, centre_x, centre_y, 13.0, 2.45)}</g>')

    # the spark bursts where the fingertips meet, then its particles fly into the name
    sx, sy = to_canvas(np.array([scene["meet"][0]]), np.array([scene["meet"][1]]))
    sx, sy = float(sx[0]), float(sy[0])
    rng = np.random.default_rng(11)
    order = np.lexsort((name["gx"], name["gy"]))
    fliers, dust, burst_at, burst_for = 240, 90, TOUCH - 0.02, 0.5
    for j in range(fliers + dust):
        angle = j * 2.399963 + float(rng.uniform(-0.2, 0.2))
        radius = (22 + 185 * float(rng.uniform(0, 1)) ** 0.8) * CELL_W * SCALE
        bx, by = math.cos(angle) * radius, math.sin(angle) * radius * 0.55
        if j < fliers:
            dot = order[int(j * len(order) / fliers)]
            tx = X0 + (nx0 * 2 + int(name["gx"][dot]) + 0.5) * DP - sx
            ty = Y0 + (ny0 * 4 + int(name["gy"][dot]) + 0.5) * DP - sy
            size = 2.2 if j % 3 else 2.8
            flight = max(reveal[int(strip[dot])] - burst_at, burst_for + 0.25)
            play.append(
                f'<rect x="{sx - size / 2:.1f}" y="{sy - size / 2:.1f}" width="{size}" height="{size}" '
                f'fill="{GREEN}" opacity="0"><animateTransform attributeName="transform" type="translate" '
                f'values="0,0;{bx:.1f},{by:.1f};{tx:.1f},{ty:.1f}" keyTimes="0;{burst_for / flight:.3f};1" '
                f'calcMode="spline" keySplines="{EASE_OUT};{EASE_IN_OUT}" begin="{burst_at:.2f}s" '
                f'dur="{flight:.3f}s" fill="freeze"/>'
                + fade("0;1;0.85;0", f"0;{0.06 / (flight + 0.3):.3f};{flight / (flight + 0.3):.3f};1",
                       burst_at, flight + 0.3) + "</rect>")
        else:
            play.append(
                f'<rect x="{sx - 1:.1f}" y="{sy - 1:.1f}" width="2" height="2" fill="{GREEN}" opacity="0">'
                f'<animateTransform attributeName="transform" type="translate" '
                f'values="0,0;{bx * 1.5:.1f},{by * 1.5:.1f}" keyTimes="0;1" calcMode="spline" '
                f'keySplines="{EASE_OUT}" begin="{burst_at:.2f}s" dur="1.5s" fill="freeze"/>'
                + fade("0;0.9;0", "0;0.1;1", burst_at, 1.5) + "</rect>")

    # each strip of the name flickers green just before its dots light
    ncx, ncy = name["gx"] // 2 + nx0, name["gy"] // 4 + ny0
    play.append(f"<g {space}>")
    for b, at in sorted(reveal.items()):
        mine = strip == b
        fx, fy = [], []
        for cx, cy in sorted(set(zip(ncx[mine].tolist(), ncy[mine].tolist()))):
            bits = int(rng.integers(1, 256))
            for q in range(8):
                if bits >> q & 1:
                    fx.append(cx * 2 + q % 2)
                    fy.append(cy * 4 + q // 2)
        flicker = lattice_paths(np.array(fx), np.array(fy), np.zeros(len(fx), int), "g").replace('class="g0"', 'class="g"')
        play.append(f'<g opacity="0">{fade("0;0.9;0", "0;0.35;1", at - 0.18, 0.5)}{flicker}</g>')
    play.append("</g>")

    # the caption decodes under the name, then hands over to the final text
    decoding = []
    for k in range(len(CAPTION)):
        t = caption_at + k / 12
        decoding.append((t, "".join(" " if c == " " else (c if j < k else "_+:.#"[int(t * 24 + j * 7) % 5])
                                    for j, c in enumerate(CAPTION))))
    play.append(f'<g opacity="0">{fade("0;1", "0;1", caption_at, 0.4, EASE_OUT)}'
                f'{flashing(decoding, centre_x, caption_row, 14.0, settled)}</g></g>')
    parts.append("".join(play))
    parts.append(chrome() + "</svg>\n")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(parts), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mode", choices=("static", "intro"), default="static")
    parser.add_argument("--out", type=Path, default=ROOT / "assets/kj-hello-still.svg")
    options = parser.parse_args()
    generate(options.out, options.mode)
