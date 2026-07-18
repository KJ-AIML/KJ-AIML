from __future__ import annotations

from pathlib import Path

import pytest

from scripts.contributions import calculate_metrics, parse_contribution_html, write_data


FIXTURE = Path("data/fixtures/contributions-sample.html").read_text(encoding="utf-8")


def test_parses_fixture_and_calculates_metrics() -> None:
    records, period = parse_contribution_html(FIXTURE)
    metrics = calculate_metrics(records)
    assert len(records) == 7
    assert period == {"from": "2026-01-04", "to": "2026-01-10"}
    assert metrics["total"] == 14
    assert metrics["longest_streak"] == 2
    assert metrics["current_streak"] == 0
    assert metrics["most_active_day"] == "Thu"


def test_missing_optional_label_is_zero_for_zero_level() -> None:
    records, _ = parse_contribution_html(FIXTURE)
    assert records[3].count == 0


def test_invalid_html_is_rejected() -> None:
    with pytest.raises(ValueError, match="No contribution cells"):
        parse_contribution_html("<html><body>not a calendar</body></html>")


def test_invalid_fetch_does_not_replace_valid_data() -> None:
    output = Path(__file__).resolve().parents[1] / ".test-contributions.tmp.json"
    try:
        records, period = parse_contribution_html(FIXTURE)
        write_data(output, records, period)
        before = output.read_text(encoding="utf-8")
        with pytest.raises(ValueError):
            parse_contribution_html("<div data-graph-url='/users/KJ-AIML/contributions'></div>")
        assert output.read_text(encoding="utf-8") == before
    finally:
        output.unlink(missing_ok=True)
