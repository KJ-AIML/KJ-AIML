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
