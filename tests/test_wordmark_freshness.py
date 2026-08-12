"""Guards for the wordmark, which sits outside the generate_all.py pipeline.

CI regenerates the generate_all.py assets and diff-checks them, so those cannot
go stale. The wordmark is excluded on purpose -- it needs numpy and Pillow, which
CI does not install -- and that exclusion means an edit to its generator can be
committed without the SVG being rebuilt. It happened once: renaming the shell
prompt updated the script and left the asset showing the old host.

These tests skip wherever numpy/Pillow are missing (which includes CI), so they
protect the machine that actually regenerates the asset.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

pytest.importorskip("numpy", reason="wordmark generator needs numpy")
pytest.importorskip("PIL", reason="wordmark generator needs Pillow")

sys.path.insert(0, str(Path("scripts").resolve()))


def test_committed_wordmark_matches_its_generator() -> None:
    """assets/kj-wordmark.svg must be what the current script produces."""
    committed = Path("assets/kj-wordmark.svg")
    assert committed.exists(), "wordmark asset is missing"
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / "kj-wordmark.svg"
        subprocess.run(
            [sys.executable, "scripts/generate_wordmark.py", "--out", str(fresh)],
            check=True, capture_output=True,
        )
        assert committed.read_bytes() == fresh.read_bytes(), (
            "assets/kj-wordmark.svg is stale — run: python scripts/generate_wordmark.py"
        )


def test_agent_panel_waits_for_the_wordmark() -> None:
    """The agent CLI must not start animating before the wordmark finishes.

    HANDOFF is a hand-kept copy of BOOT_END because importing across these two
    modules would drag numpy into CI. This is the thing that keeps them in step.
    """
    wordmark = importlib.import_module("generate_wordmark")
    agent = importlib.import_module("generate_agent_cli")
    assert agent.HANDOFF >= wordmark.BOOT_END, (
        f"agent panel starts at {agent.HANDOFF}s but the wordmark boots until "
        f"{wordmark.BOOT_END}s — the two panels would compete"
    )


def test_intro_word_widths_match_the_approved_system() -> None:
    wordmark = importlib.import_module("generate_wordmark")
    assert wordmark.INTRO_WORD_COLS == {
        "WELCOME": 91,
        "TO": 55,
        "MY": 55,
        "AI": 55,
        "WORLD": 91,
    }


@pytest.mark.parametrize("word, cols", [
    ("WELCOME", 91),
    ("TO", 55),
    ("MY", 55),
    ("AI", 55),
    ("WORLD", 91),
])
def test_intro_word_grid_uses_approved_width(word: str, cols: int) -> None:
    wordmark = importlib.import_module("generate_wordmark")
    grid = wordmark.render_text_grid(word, cols, wordmark.REST_YAW)
    assert grid.shape[1] == cols
    assert grid.any()


def test_intro_words_are_ascii_groups_not_solid_text(tmp_path: Path) -> None:
    fresh = tmp_path / "kj-wordmark.svg"
    subprocess.run(
        [sys.executable, "scripts/generate_wordmark.py", "--out", str(fresh)],
        check=True,
        capture_output=True,
    )
    svg = fresh.read_text(encoding="utf-8")
    for word in ("WELCOME", "TO", "MY", "AI", "WORLD"):
        assert f'data-intro-word="{word}"' in svg
    assert ">Welcome<" not in svg
    assert ">World<" not in svg


def test_intro_word_grids_fit_the_final_art_height() -> None:
    wordmark = importlib.import_module("generate_wordmark")
    final_grid = wordmark.render_text_grid(wordmark.TEXT, wordmark.COLS)
    for word, grid in wordmark.intro_word_grids(final_grid.shape[0]).items():
        assert grid.shape[1] == wordmark.INTRO_WORD_COLS[word]
        assert grid.shape[0] == final_grid.shape[0]
        occupied = grid.nonzero()[1]
        left = int(occupied.min())
        right = grid.shape[1] - 1 - int(occupied.max())
        assert abs(left - right) <= 2
