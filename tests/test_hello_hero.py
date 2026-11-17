"""The hero's motion is checked as geometry: where the dots actually go."""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET

import numpy as np
import pytest

import generate_hello as hero
from scripts.validate_profile import ANIMATED_ASSET, ROOT, STILL_ASSET

NS = "{http://www.w3.org/2000/svg}"


@pytest.fixture(scope="module")
def scene() -> dict:
    return hero.layout()


def canvas(scene: dict, i: int, t: float) -> tuple[np.ndarray, np.ndarray]:
    return hero.to_canvas(*hero.place(i, scene["hands"][i], hero.pose(i, t, scene["retreat"], scene["close"])))


def cells(scene: dict, i: int, t: float) -> set[tuple[int, int]]:
    px, py = hero.place(i, scene["hands"][i], hero.pose(i, t, scene["retreat"], scene["close"]))
    return set(zip(np.floor(px / 2).astype(int).tolist(), np.floor(py / 4).astype(int).tolist()))


def name_cells(scene: dict, mask=None) -> set[tuple[int, int]]:
    name = scene["name"]
    gx, gy = (name["gx"], name["gy"]) if mask is None else (name["gx"][mask], name["gy"][mask])
    return set(zip((gx // 2 + scene["nx0"]).tolist(), (gy // 4 + scene["ny0"]).tolist()))


def test_every_dot_belongs_to_exactly_one_bone(scene) -> None:
    for i, hand in enumerate(scene["hands"]):
        rig = hero.RIGS[i]
        in_finger = hand["finger"] >= 0
        assert (hand["wrist"][in_finger] == rig["wrist"]["n"]).all(), "fingers hang off the full hand"
        assert (hand["knuckle"][in_finger] > 0).all() and (hand["knuckle"][~in_finger] == 0).all()
        for index, spec in enumerate(rig["fingers"]):
            mine = hand["finger"] == index
            assert mine.sum() > 40, f"hand {i} finger {spec['name']} has almost no dots: check its polygon"
            beyond = mine & (hand["middle"] > 0)
            assert (hand["knuckle"][beyond] == spec["n"]).all(), "the middle joint sits past the knuckle"


def test_the_touch_is_the_drawn_pose_and_the_fingertips_meet(scene) -> None:
    tips = []
    for i in (0, 1):
        p = hero.pose(i, hero.TOUCH, scene["retreat"], scene["close"])
        assert all(abs(p[joint]) < 0.01 for joint in ("arm", "index", "pip", "others")), p
        assert abs(p["wrist"]) < 1.0                 # only the small idle sway remains
        spec = hero.RIGS[i]["fingers"][0]
        hand = scene["hands"][i]
        px, py = hero.place(i, hand, p)
        tip = (hand["finger"] == 0) & (hand["middle"] == spec["child"]["n"])
        far = np.argmax(px[tip] * spec["d"][0] + py[tip] * spec["d"][1])
        tips.append((px[tip][far], py[tip][far]))
    gap = math.hypot(tips[1][0] - tips[0][0], tips[1][1] - tips[0][1])
    assert scene["gap"] > 6, "in the drawn pose the fingertips are apart; the last inch closes them"
    assert 1.0 <= gap <= 3.0, f"fingertips end {gap:.1f} dots apart"
    assert not cells(scene, 0, hero.TOUCH) & cells(scene, 1, hero.TOUCH), "the hands must not overlap"


def test_hands_never_paint_over_the_window_chrome(scene) -> None:
    """There is no clip path, so the frame is protected by where the dots go."""
    radius, edge = 14.0, 2.5
    floor = hero.HEIGHT - radius
    for t in scene["times"]:
        for i in (0, 1):
            x, y = canvas(scene, i, t)
            on_canvas = (x > -edge) & (x < hero.WIDTH + edge)
            assert (y[on_canvas] > hero.CHROME_H + edge).all(), f"hand {i} enters the titlebar at {t:.2f}s"
            assert (y[on_canvas] < hero.HEIGHT - edge).all(), f"hand {i} reaches the bottom edge at {t:.2f}s"
            # Inside either bottom corner square, a dot must stay within the frame's arc.
            for centre in (radius, hero.WIDTH - radius):
                outer = on_canvas & (y > floor) & ((x < radius) if centre == radius else (x > centre))
                reach = np.hypot(x[outer] - centre, y[outer] - floor)
                assert (reach < radius - 1).all(), f"hand {i} leaves the rounded corner at {t:.2f}s"


def test_motion_is_continuous(scene) -> None:
    for i in (0, 1):
        previous = None
        for t in scene["times"]:
            x, y = canvas(scene, i, t)
            if previous is not None:
                step = np.hypot(x - previous[0], y - previous[1]).max()
                assert step < 20, f"hand {i} jumps {step:.1f}px at {t:.2f}s"
            previous = (x, y)


def test_the_name_only_lights_where_the_hands_have_left(scene) -> None:
    for b, at in scene["reveal"].items():
        strip = name_cells(scene, scene["strip"] == b)
        for i in (0, 1):
            assert not strip & cells(scene, i, at), f"strip {b} lights under hand {i} at {at:.2f}s"
    padded = {(x + dx, y) for x, y in name_cells(scene) for dx in (-2, -1, 0, 1, 2)}
    for i in (0, 1):
        assert not padded & cells(scene, i, hero.T_END), f"hand {i} rests on the name"
    assert max(scene["reveal"].values()) + 0.45 < hero.T_END - 1.0, "the name must settle well before the end"


def dots_in(paths) -> int:
    return sum(round((float(run) + 0.1) / hero.DP)
               for path in paths for run in re.findall(r"h([\d.]+)", path.get("d", "")))


def test_animation_ends_on_the_still_and_falls_back_to_it(scene) -> None:
    intro = ET.parse(ROOT / "assets" / ANIMATED_ASSET).getroot()
    still = ET.parse(ROOT / "assets" / STILL_ASSET).getroot()
    fallback = intro.find(f"{NS}g[@id='static-fallback']")
    lit = [p for p in fallback.iter(f"{NS}path") if p.get("class", "").startswith("n")]
    drawn = [p for p in still.iter(f"{NS}path") if p.get("class", "").startswith("n")]
    assert dots_in(lit) == dots_in(drawn) == len(scene["name"]["gx"])
    assert hero.CAPTION in "".join(fallback.itertext()) and hero.CAPTION in "".join(still.itertext())
    # Every animation is finite and frozen, so the picture holds after one play.
    for element in intro.iter():
        if element.tag in {f"{NS}animate", f"{NS}animateTransform"}:
            assert element.get("fill") == "freeze" and "repeatCount" not in element.attrib
            ends = float(element.get("begin", "0s").rstrip("s")) + float(element.get("dur").rstrip("s"))
            assert ends <= hero.T_END + 0.01, f"an animation runs until {ends:.2f}s"


def test_default_mode_is_static_and_unknown_modes_fail(tmp_path) -> None:
    out = tmp_path / "hero.svg"
    hero.generate(out)
    assert out.read_bytes() == (ROOT / "assets" / STILL_ASSET).read_bytes().replace(b"\r\n", b"\n")
    with pytest.raises(ValueError):
        hero.generate(out, mode="loop")
