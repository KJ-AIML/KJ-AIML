from __future__ import annotations

from pathlib import Path

import yaml


def test_workflows_have_explicit_safe_permissions() -> None:
    update = yaml.safe_load(Path(".github/workflows/update-profile-art.yml").read_text(encoding="utf-8"))
    validate = yaml.safe_load(Path(".github/workflows/validate-profile.yml").read_text(encoding="utf-8"))
    assert update["permissions"] == {"contents": "write"}
    assert validate["permissions"] == {"contents": "read"}
    assert "workflow_dispatch" in update[True] or "workflow_dispatch" in update.get("on", {})
    update_text = Path(".github/workflows/update-profile-art.yml").read_text(encoding="utf-8")
    assert "git add data/contributions.json assets/contribution-heatmap.svg" in update_text
    assert "git add ." not in update_text
    assert "PAT" not in update_text
