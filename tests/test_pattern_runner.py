"""Tests for pattern runner and fixture loading."""

import json

import pytest

from auto_kit.fixtures import load_csv, load_json, load_json_lines, save_json
from auto_kit.models import PatternResult
from auto_kit.pattern_runner import discover_patterns, validate_pattern


class TestFixtures:
    def test_load_json(self, tmp_path):
        fp = tmp_path / "test.json"
        save_json(fp, {"key": "value"})
        assert load_json(fp) == {"key": "value"}

    def test_load_json_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_json("/nonexistent/file.json")

    def test_load_csv(self, tmp_path):
        fp = tmp_path / "test.csv"
        fp.write_text("name,email\nAlice,alice@test.com\nBob,bob@test.com\n")
        rows = load_csv(fp)
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"

    def test_load_json_lines(self, tmp_path):
        fp = tmp_path / "test.jsonl"
        fp.write_text('{"a": 1}\n{"b": 2}\n')
        data = load_json_lines(fp)
        assert len(data) == 2
        assert data[0]["a"] == 1

    def test_save_json_creates_dir(self, tmp_path):
        nested = tmp_path / "sub" / "out.json"
        save_json(nested, {"ok": True})
        assert nested.exists()


class TestPatternRunner:
    def test_validate_pattern_missing_files(self, tmp_path):
        issues = validate_pattern(tmp_path)
        assert len(issues) > 0
        assert any("Missing required file" in i for i in issues)

    def test_validate_pattern_valid(self, tmp_path):
        pattern_dir = tmp_path / "test-pattern"
        pattern_dir.mkdir()
        (pattern_dir / "fixtures").mkdir()
        (pattern_dir / "python").mkdir()

        # Create valid workflow.json
        with open(pattern_dir / "workflow.json", "w") as f:
            json.dump({"name": "Test", "nodes": [{"name": "N1", "type": "noOp"}]}, f)

        # Create expected output
        with open(pattern_dir / "fixtures/expected_output.json", "w") as f:
            json.dump({"result": "ok"}, f)

        # Create main.py
        with open(pattern_dir / "python/main.py", "w") as f:
            f.write("def run(pattern_path=None):\n    return {'result': 'ok'}\n")

        # Create test_main.py
        with open(pattern_dir / "python/test_main.py", "w") as f:
            f.write("def test_placeholder():\n    assert True\n")

        # Create README
        with open(pattern_dir / "README.md", "w") as f:
            f.write("# Test Pattern\n")

        issues = validate_pattern(pattern_dir)
        assert issues == []

    def test_discover_patterns_empty(self, tmp_path):
        assert discover_patterns(tmp_path) == []

    def test_pattern_result_summary(self):
        r = PatternResult(pattern_name="csv", fixture_name="default", passed=True)
        assert "PASS" in r.summary()
        r2 = PatternResult(
            pattern_name="csv", fixture_name="default", passed=False, errors=["fail"]
        )
        assert "FAIL" in r2.summary()
