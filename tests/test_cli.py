"""Tests for the auto-kit CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Generator

import pytest
from typer.testing import CliRunner

from auto_kit.cli import app

runner = CliRunner()
REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PATTERNS = {
    "calendar-booking",
    "csv-to-crm",
    "email-parser",
    "lead-enrichment",
    "product-creative-pack",
    "slack-alerts",
    "webhook-router",
}


@pytest.fixture
def isolated_pattern(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a valid pattern under tmp_path/patterns/ so discover_patterns works."""
    patterns_dir = tmp_path / "patterns"
    patterns_dir.mkdir()
    pattern_dir = patterns_dir / "test-pattern"
    pattern_dir.mkdir()
    (pattern_dir / "fixtures").mkdir()
    (pattern_dir / "python").mkdir()

    with open(pattern_dir / "workflow.json", "w") as f:
        json.dump(
            {
                "name": "Test Pattern",
                "description": "A test",
                "nodes": [{"name": "N1", "type": "noOp"}],
            },
            f,
        )
    with open(pattern_dir / "fixtures/expected_output.json", "w") as f:
        json.dump({"result": "ok"}, f)
    with open(pattern_dir / "fixtures/input.json", "w") as f:
        json.dump({"input": "ok"}, f)
    with open(pattern_dir / "python/main.py", "w") as f:
        f.write("def run(pattern_path=None):\n    return {'result': 'ok'}\n")
    with open(pattern_dir / "python/test_main.py", "w") as f:
        f.write("def test_placeholder():\n    assert True\n")
    with open(pattern_dir / "README.md", "w") as f:
        f.write("# Test Pattern\n" * 20)

    yield pattern_dir


class TestCLIListPatterns:
    def test_list_no_patterns(self, tmp_path: Path) -> None:
        """Run from a temp dir with no patterns/ directory."""
        original = Path.cwd()
        try:
            os.chdir(str(tmp_path))
            result = runner.invoke(app, ["list-patterns"])
            assert result.exit_code == 0
            assert "No patterns found" in result.stdout
        finally:
            os.chdir(str(original))

    def test_list_with_pattern(self, isolated_pattern: Path) -> None:
        """Run from tmp dir with patterns/ containing a test pattern."""
        original = Path.cwd()
        try:
            os.chdir(str(isolated_pattern.parent.parent))
            result = runner.invoke(app, ["list-patterns"])
            assert result.exit_code == 0
            assert "test-pattern" in result.stdout
        finally:
            os.chdir(str(original))

    def test_auto_kit_list_patterns_shows_every_shipped_pattern(self) -> None:
        original = Path.cwd()
        try:
            os.chdir(str(REPO_ROOT))
            result = runner.invoke(app, ["list-patterns"])
        finally:
            os.chdir(str(original))

        assert result.exit_code == 0
        assert "Found 7 pattern(s)" in result.stdout
        for pattern_name in EXPECTED_PATTERNS:
            assert pattern_name in result.stdout


class TestCLIValidate:
    def test_validate_valid_pattern(self, isolated_pattern: Path) -> None:
        result = runner.invoke(app, ["validate", str(isolated_pattern)])
        assert result.exit_code == 0
        assert "PASS" in result.stdout

    def test_validate_missing_pattern(self, tmp_path: Path) -> None:
        missing = tmp_path / "nonexistent"
        result = runner.invoke(app, ["validate", str(missing)])
        assert result.exit_code != 0
        assert "Missing required file" in result.stdout

    def test_auto_kit_validate_csv_to_crm_pattern(self) -> None:
        result = runner.invoke(app, ["validate", str(REPO_ROOT / "patterns" / "csv-to-crm")])

        assert result.exit_code == 0
        assert "[PASS]" in result.stdout
        assert "patterns/csv-to-crm" in result.stdout


class TestCLIRun:
    def test_run_valid_pattern(self, isolated_pattern: Path) -> None:
        result = runner.invoke(app, ["run", str(isolated_pattern)])
        assert result.exit_code == 0
        assert "PASS" in result.stdout

    def test_run_invalid_path(self) -> None:
        result = runner.invoke(app, ["run", "/does/not/exist"])
        assert result.exit_code != 0

    def test_auto_kit_run_csv_to_crm_pattern(self) -> None:
        result = runner.invoke(app, ["run", str(REPO_ROOT / "patterns" / "csv-to-crm")])

        assert result.exit_code == 0
        assert "csv-to-crm" in result.stdout
        assert "PASS" in result.stdout

    def test_auto_kit_run_product_creative_pack_pattern(self) -> None:
        result = runner.invoke(app, ["run", str(REPO_ROOT / "patterns" / "product-creative-pack")])

        assert result.exit_code == 0
        assert "product-creative-pack" in result.stdout
        assert "PASS" in result.stdout


class TestCLIMCPValidate:
    def test_mcp_validate_passes_for_shipped_registry(self) -> None:
        original = Path.cwd()
        try:
            os.chdir(str(REPO_ROOT))
            result = runner.invoke(app, ["mcp-validate"])
        finally:
            os.chdir(str(original))

        assert result.exit_code == 0
        assert "MCP registry valid" in result.stdout
        assert "sectors" in result.stdout
        assert "capabilities" in result.stdout

    def test_mcp_serve_help_documents_stdio_server(self) -> None:
        result = runner.invoke(app, ["mcp-serve", "--help"])

        assert result.exit_code == 0
        assert "Run the Automation Kit MCP server over stdio" in result.stdout


class TestCLIValidateAll:
    def test_validate_all_with_patterns(self, isolated_pattern: Path) -> None:
        original = Path.cwd()
        try:
            os.chdir(str(isolated_pattern.parent.parent))
            result = runner.invoke(app, ["validate-all"])
            assert result.exit_code == 0
            assert "PASS" in result.stdout or "passed" in result.stdout
        finally:
            os.chdir(str(original))

    def test_auto_kit_validate_all_covers_all_shipped_patterns(self) -> None:
        original = Path.cwd()
        try:
            os.chdir(str(REPO_ROOT))
            result = runner.invoke(app, ["validate-all"])
        finally:
            os.chdir(str(original))

        assert result.exit_code == 0
        assert "7 pattern(s): 7 passed, 0 failed" in result.stdout
        for pattern_name in EXPECTED_PATTERNS:
            assert f"Checking {pattern_name}" in result.stdout
