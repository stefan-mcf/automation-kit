"""Cross-pattern test matrix — discovers and validates all shipped patterns."""

from __future__ import annotations

from pathlib import Path

from auto_kit.pattern_runner import discover_patterns, validate_pattern

EXPECTED_PATTERNS = {
    "calendar-booking",
    "csv-to-crm",
    "email-parser",
    "lead-enrichment",
    "product-creative-pack",
    "slack-alerts",
    "webhook-router",
}


class TestAllPatterns:
    """Automatically discover and test every pattern in the repository."""

    def test_exactly_seven_patterns_are_discovered(self) -> None:
        patterns = discover_patterns()
        names = {p.name for p in patterns}

        assert names == EXPECTED_PATTERNS
        assert len(patterns) == 7

    def test_each_pattern_validates_without_issues(self) -> None:
        for pattern_path in discover_patterns():
            issues = validate_pattern(str(pattern_path))

            assert not issues, f"{pattern_path.name} has issues: {issues}"

    def test_each_pattern_has_required_artifact_set(self) -> None:
        for pattern_path in discover_patterns():
            assert (pattern_path / "workflow.json").is_file(), (
                f"{pattern_path.name} missing workflow.json"
            )
            assert (pattern_path / "README.md").is_file(), f"{pattern_path.name} missing README.md"
            assert (pattern_path / "fixtures").is_dir(), f"{pattern_path.name} missing fixtures/"
            assert (pattern_path / "python" / "main.py").is_file(), (
                f"{pattern_path.name} missing python/main.py"
            )
            assert list((pattern_path / "python").glob("test_*.py")), (
                f"{pattern_path.name} missing python/test_*.py"
            )

    def test_each_pattern_has_input_and_expected_fixtures(self) -> None:
        for pattern_path in discover_patterns():
            fixtures_dir = pattern_path / "fixtures"
            expected_output = fixtures_dir / "expected_output.json"
            data_fixtures = [
                fixture
                for fixture in fixtures_dir.iterdir()
                if fixture.is_file()
                and fixture.name != "expected_output.json"
                and fixture.suffix in {".csv", ".json", ".jsonl"}
            ]

            assert expected_output.is_file(), f"{pattern_path.name} missing expected_output.json"
            assert data_fixtures, f"{pattern_path.name} missing input fixture file"

    def test_each_pattern_readme_is_substantial(self) -> None:
        for pattern_path in discover_patterns():
            readme = (pattern_path / "README.md").read_text()

            assert len(readme) > 50, f"{pattern_path.name} README too short ({len(readme)} chars)"

    def test_pattern_directories_match_discovered_patterns(self) -> None:
        pattern_root = Path("patterns")
        directory_names = {path.name for path in pattern_root.iterdir() if path.is_dir()}
        discovered_names = {path.name for path in discover_patterns()}

        assert directory_names == discovered_names == EXPECTED_PATTERNS
