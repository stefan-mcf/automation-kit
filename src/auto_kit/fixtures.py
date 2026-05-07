"""Fixture loading utilities for pattern tests."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> dict[str, Any]:
    """Load a JSON fixture file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Fixture not found: {path}")
    with open(path) as f:
        return dict(json.load(f))


def load_json_lines(path: str | Path) -> list[dict[str, Any]]:
    """Load a JSON Lines fixture file (one JSON object per line)."""
    path = Path(path)
    results: list[dict[str, Any]] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(dict(json.loads(line)))
    return results


def load_csv(path: str | Path) -> list[dict[str, str]]:
    """Load a CSV fixture and return list of dicts."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Fixture not found: {path}")
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def save_json(path: str | Path, data: Any, indent: int = 2) -> None:
    """Save data to a JSON fixture file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=indent, default=str)


def ensure_fixtures_dir(pattern_path: str | Path) -> Path:
    """Ensure fixtures directory exists for a pattern."""
    fixtures_dir = Path(pattern_path) / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    return fixtures_dir
