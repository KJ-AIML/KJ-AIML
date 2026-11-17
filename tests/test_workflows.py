from __future__ import annotations

from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_validate_workflow_has_explicit_safe_permissions() -> None:
    path = ROOT / ".github/workflows/validate-profile.yml"
    workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert workflow["permissions"] == {"contents": "read"}
    text = path.read_text(encoding="utf-8")
    assert "PAT" not in text
    assert "git add ." not in text
    for job in workflow["jobs"].values():
        assert job.get("permissions", workflow["permissions"]) == {"contents": "read"}
        for step in job["steps"]:
            if "uses" in step:
                assert re.fullmatch(r"[^@]+@[a-f0-9]{40}", step["uses"]), step["uses"]


def test_no_workflow_writes_to_the_repo() -> None:
    """The contribution refresh job was the only writer, and it is gone.

    Anything reintroducing `contents: write` should be a deliberate decision, not
    something that arrives with a copied workflow.
    """
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert workflow["permissions"] == {"contents": "read"}, path
