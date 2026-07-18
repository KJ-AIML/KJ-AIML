"""Parsing and metrics for the public GitHub contribution calendar."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from typing import Any


COUNT_RE = re.compile(r"([\d,]+)\s+contributions?", re.IGNORECASE)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class Contribution:
    day: str
    level: int
    count: int | None


class ContributionParser(HTMLParser):
    """Accept GitHub's calendar cells without depending on CSS class names."""

    def __init__(self) -> None:
        super().__init__()
        self.records: dict[str, dict[str, Any]] = {}
        self.in_tooltip = False
        self.tooltip_text: list[str] = []
        self.pending_day: str | None = None
        self.period: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "div" and attributes.get("data-graph-url", "").endswith("/contributions"):
            for key in ("data-from", "data-to"):
                if attributes.get(key):
                    self.period[key[5:]] = str(attributes[key]).split(" ", 1)[0]
        if tag == "td" and attributes.get("data-date"):
            day = str(attributes["data-date"])
            if not DATE_RE.match(day):
                return
            try:
                level = int(attributes.get("data-level", "0"))
            except ValueError:
                level = 0
            self.pending_day = day
            self.records[day] = {"date": day, "level": max(0, min(4, level)), "count": None}
        if tag in {"tool-tip", "span"} and self.pending_day and (tag == "tool-tip" or attributes.get("data-type") == "label"):
            self.in_tooltip = True
            self.tooltip_text = []

    def handle_data(self, data: str) -> None:
        if self.in_tooltip:
            self.tooltip_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.in_tooltip and tag in {"tool-tip", "span"}:
            text = " ".join("".join(self.tooltip_text).split())
            match = COUNT_RE.search(text)
            if self.pending_day and self.pending_day in self.records:
                level = int(self.records[self.pending_day]["level"])
                self.records[self.pending_day]["count"] = int(match.group(1).replace(",", "")) if match else (0 if level == 0 else None)
            self.in_tooltip = False
            self.tooltip_text = []
            self.pending_day = None


def parse_contribution_html(html: str) -> tuple[list[Contribution], dict[str, str]]:
    parser = ContributionParser()
    parser.feed(html)
    if not parser.records:
        raise ValueError("No contribution cells found in the response")
    records = [Contribution(item["date"], item["level"], item["count"]) for item in parser.records.values()]
    records.sort(key=lambda item: item.day)
    return records, parser.period


def _days(records: list[Contribution]) -> list[tuple[date, int | None]]:
    if not records:
        return []
    values = {date.fromisoformat(item.day): item.count for item in records}
    start, end = min(values), max(values)
    result: list[tuple[date, int | None]] = []
    current = start
    while current <= end:
        result.append((current, values.get(current, 0)))
        current += timedelta(days=1)
    return result


def calculate_metrics(records: list[Contribution]) -> dict[str, Any]:
    days = _days(records)
    known_counts = [count for _, count in days]
    total = sum(known_counts) if all(count is not None for count in known_counts) else None
    active = [day for day, count in days if count is not None and count > 0]
    longest = current = 0
    run = 0
    for _, count in days:
        if count is not None and count > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    for _, count in reversed(days):
        if count is not None and count > 0:
            current += 1
        else:
            break
    weekdays = {name: 0 for name in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")}
    for day, count in days:
        if count is not None:
            weekdays[day.strftime("%a")] += count
    most_active_day = max(weekdays, key=weekdays.get) if total else None
    return {
        "displayed_from": records[0].day if records else None,
        "displayed_to": records[-1].day if records else None,
        "days": len(records),
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "most_active_day": most_active_day,
    }


def load_data(path: Path) -> tuple[list[Contribution], dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("contributions"), list):
        raise ValueError("Contribution data must contain a contributions list")
    records = [Contribution(str(item["date"]), int(item["level"]), item.get("count")) for item in payload["contributions"]]
    if not records:
        raise ValueError("Contribution data is empty")
    return records, dict(payload.get("metrics") or calculate_metrics(records))


def write_data(path: Path, records: list[Contribution], period: dict[str, str]) -> None:
    payload = {
        "source": "https://github.com/users/KJ-AIML/contributions",
        "period": period,
        "metrics": calculate_metrics(records),
        "contributions": [{"date": item.day, "level": item.level, "count": item.count} for item in records],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
