from __future__ import annotations

from pathlib import Path
import re


def test_readme_local_images_and_plain_text() -> None:
    root = Path(".")
    readme = (root / "README.md").read_text(encoding="utf-8")
    for reference in re.findall(r'(?:src|href)=["\'](\.?/[^"\']+)["\']', readme):
        assert (root / reference).exists(), reference
    assert "AI Engineer" in readme
    assert "agent infrastructure" in readme
    assert "mcp_token" not in readme
    assert "TODO" not in readme
    assert "PLACEHOLDER" not in readme
