from __future__ import annotations

from pathlib import Path

import pytest

from scripts.validate_profile import ROOT, validate_local_references


@pytest.mark.parametrize("document", [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))],
                         ids=lambda path: str(path.relative_to(ROOT)))
def test_documentation_local_references_exist(document: Path) -> None:
    validate_local_references(document, ROOT)


@pytest.mark.parametrize("link", [
    '![image](assets/panel.svg)',
    '[notes](./assets/panel.svg#details)',
    '[notes](assets/panel.svg?raw=1#details "A title")',
    '[notes](<assets/panel.svg> "A title")',
    '[notes][panel]\n\n[panel]: assets/panel.svg "A title"',
    '<IMG SRC=assets/panel.svg alt="Panel">',
    "<a href='assets/panel.svg'>Notes</a>",
])
def test_missing_markdown_and_html_targets_fail(tmp_path: Path, link: str) -> None:
    document = tmp_path / "README.md"
    document.write_text(link, encoding="utf-8")
    with pytest.raises(ValueError, match="broken local reference"):
        validate_local_references(document, tmp_path)
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets/panel.svg").write_text("image", encoding="utf-8")
    validate_local_references(document, tmp_path)


def test_paths_are_decoded_relative_to_the_document(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets/panel (v2).svg").write_text("image", encoding="utf-8")
    document = tmp_path / "docs/notes.md"
    document.write_text(
        '[`panel`](../assets/panel%20(v2).svg?raw=true#art)\n'
        '[panel](<../assets/panel (v2).svg> "Title")\n'
        '<img src="../assets/panel%20%28v2%29.svg">\n', encoding="utf-8",
    )
    validate_local_references(document, tmp_path)


def test_balanced_parentheses_and_linked_images_are_checked(tmp_path: Path) -> None:
    document = tmp_path / "README.md"
    document.write_text('[![panel](panel(v2).svg)](notes(v2).md)', encoding="utf-8")
    (tmp_path / "panel(v2).svg").write_text("image", encoding="utf-8")
    with pytest.raises(ValueError, match=r"notes\(v2\).md"):
        validate_local_references(document, tmp_path)
    (tmp_path / "notes(v2).md").write_text("notes", encoding="utf-8")
    validate_local_references(document, tmp_path)


def test_public_urls_fragments_and_examples_are_not_local_files(tmp_path: Path) -> None:
    document = tmp_path / "README.md"
    document.write_text('''
[public](https://github.com/KJ-AIML/heli-harness)
[public](HTTPS://example.com/a_(b))
![public](//example.com/panel.svg)
[email](mailto:hello@example.com)
[section](#projects)
<a href="https://example.com/?a=1&amp;b=2">Public</a>
<a href="//example.com/docs">Public</a>
`[example](missing.md)`
<!-- <img src="missing.svg"> [comment](missing.md) -->
```markdown
[example](missing.md)
<img src="missing.svg">
```
''', encoding="utf-8")
    validate_local_references(document, tmp_path)


def test_local_references_cannot_escape_the_repository(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    (tmp_path / "outside.md").write_text("exists outside the repo", encoding="utf-8")
    document = repository / "README.md"
    document.write_text('[outside](../outside.md)', encoding="utf-8")
    with pytest.raises(ValueError, match="broken local reference"):
        validate_local_references(document, repository)
