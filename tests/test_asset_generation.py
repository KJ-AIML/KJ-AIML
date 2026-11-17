"""All committed assets must be complete and reproducible on every OS."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

# Required imports intentionally fail collection when renderer dependencies are
# absent. CI and the documented local command install both requirements files.
from generate_agent_cli import generate as generate_agent_cli
from generate_wordmark import generate as generate_wordmark
from scripts.validate_profile import ANIMATED_ASSET, ASSET_NAMES, ROOT, validate_svg


@pytest.fixture(scope="module")
def generated_runs(tmp_path_factory: pytest.TempPathFactory) -> list[dict[str, bytes]]:
    workspace = tmp_path_factory.mktemp("profile-build")
    shutil.copytree(ROOT / "scripts", workspace / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    (workspace / "assets").mkdir()
    if (ROOT / "assets/fonts").exists():
        shutil.copytree(ROOT / "assets/fonts", workspace / "assets/fonts")
    outside = tmp_path_factory.mktemp("unrelated-cwd")
    runs = []
    for static in (None, None, "1"):
        for name in ASSET_NAMES:
            (workspace / "assets" / name).unlink(missing_ok=True)
        environment = os.environ.copy()
        environment.pop("STATIC", None)
        if static is not None:
            environment["STATIC"] = static
        result = subprocess.run(
            [sys.executable, str(workspace / "scripts/generate_all.py")],
            cwd=outside, env=environment, capture_output=True, text=True, timeout=120,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        outputs = {}
        for name in ASSET_NAMES:
            path = workspace / "assets" / name
            assert path.is_file(), f"generate_all.py did not produce {name}"
            validate_svg(path, allow_animation=name == ANIMATED_ASSET)
            outputs[name] = path.read_bytes()
        runs.append(outputs)
    assert not list(outside.iterdir()), "generation wrote files relative to the caller's cwd"
    return runs


@pytest.mark.parametrize("name", ASSET_NAMES)
def test_committed_assets_are_fresh(name: str, generated_runs: list[dict[str, bytes]]) -> None:
    # Git may check text out as CRLF on Windows. Only that transport conversion
    # is normalized; every other byte, including whitespace, must match.
    committed = (ROOT / "assets" / name).read_bytes().replace(b"\r\n", b"\n")
    assert committed == generated_runs[0][name], f"{name} is stale: run python scripts/generate_all.py"


def test_repeated_and_explicit_static_builds_are_identical(generated_runs: list[dict[str, bytes]]) -> None:
    assert generated_runs[0] == generated_runs[1] == generated_runs[2]
    assert all(b"\r\n" not in content for content in generated_runs[0].values())


@pytest.mark.parametrize(("name", "generate"), [
    ("kj-wordmark.svg", generate_wordmark),
    ("kj-agent-cli.svg", generate_agent_cli),
])
def test_public_generator_defaults_are_static(name, generate, tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("STATIC", raising=False)
    output = tmp_path / name
    generate(output)
    validate_svg(output)
    assert output.read_bytes() == (ROOT / "assets" / name).read_bytes().replace(b"\r\n", b"\n")
