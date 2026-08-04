from __future__ import annotations

from pathlib import Path

import yaml


def test_validate_workflow_has_explicit_safe_permissions() -> None:
    path = Path(".github/workflows/validate-profile.yml")
    workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert workflow["permissions"] == {"contents": "read"}
    text = path.read_text(encoding="utf-8")
    assert "PAT" not in text
    assert "git add ." not in text


def test_no_workflow_writes_to_the_repo() -> None:
    """The contribution refresh job was the only writer, and it is gone.

    Anything reintroducing `contents: write` should be a deliberate decision, not
    something that arrives with a copied workflow.
    """
    for path in Path(".github/workflows").glob("*.yml"):
        workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert workflow["permissions"] == {"contents": "read"}, path
