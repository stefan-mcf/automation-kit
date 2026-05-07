"""Tests for public project, package, and CLI naming."""

from __future__ import annotations

import importlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def pyproject_text() -> str:
    return (ROOT / "pyproject.toml").read_text()


def test_distribution_name_remains_repo_name() -> None:
    assert re.search(r'^name = "automation-kit"$', pyproject_text(), flags=re.MULTILINE)


def test_python_package_is_auto_kit() -> None:
    module = importlib.import_module("auto_kit")

    assert module.__version__ == "0.1.0"


def test_console_command_is_auto_kit() -> None:
    text = pyproject_text()

    assert re.search(r'^auto-kit = "auto_kit\.cli:app"$', text, flags=re.MULTILINE)
    assert 'automation-kit = "' + 'auto' + 'mation_kit.cli:app"' not in text
