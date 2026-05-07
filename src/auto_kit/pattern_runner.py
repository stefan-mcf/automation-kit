"""Pattern runner: validate workflow JSON, load fixtures, run patterns, compare output."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from auto_kit.models import PatternResult
from auto_kit.workflow_schema import WorkflowJSON


def load_workflow_json(pattern_path: str | Path) -> WorkflowJSON:
    """Load and validate a pattern's workflow.json file."""
    path = Path(pattern_path) / "workflow.json"
    if not path.exists():
        raise FileNotFoundError(f"workflow.json not found in {pattern_path}")
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict) and "name" in data:
        return WorkflowJSON(**data)
    raise ValueError(f"Invalid workflow.json: missing required fields in {path}")


def run_pattern_module(pattern_path: str | Path, fixture_name: str = "default") -> PatternResult:
    """Run a pattern's main.py against a fixture and compare with expected output."""
    pattern_path = Path(pattern_path)
    pattern_name = pattern_path.name

    # Import the pattern's main module
    main_py = pattern_path / "python" / "main.py"
    if not main_py.exists():
        return PatternResult(
            pattern_name=pattern_name,
            fixture_name=fixture_name,
            passed=False,
            errors=[f"main.py not found: {main_py}"],
        )

    spec = importlib.util.spec_from_file_location(f"{pattern_name}_main", main_py)
    if spec is None or spec.loader is None:
        return PatternResult(
            pattern_name=pattern_name,
            fixture_name=fixture_name,
            passed=False,
            errors=[f"Could not load module from {main_py}"],
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{pattern_name}_main"] = module
    spec.loader.exec_module(module)

    # Load input fixture
    fixtures_dir = pattern_path / "fixtures"
    expected_path = fixtures_dir / "expected_output.json"

    if not expected_path.exists():
        return PatternResult(
            pattern_name=pattern_name,
            fixture_name=fixture_name,
            passed=False,
            errors=[f"Expected output not found: {expected_path}"],
        )

    with open(expected_path) as f:
        expected_output = json.load(f)

    # Run the pattern's main function
    if not hasattr(module, "run"):
        return PatternResult(
            pattern_name=pattern_name,
            fixture_name=fixture_name,
            passed=False,
            errors=[f"run() function not found in {main_py}"],
        )

    try:
        actual_output = module.run(pattern_path=str(pattern_path))
    except Exception as e:
        return PatternResult(
            pattern_name=pattern_name,
            fixture_name=fixture_name,
            passed=False,
            errors=[f"run() raised exception: {e}"],
        )

    passed = actual_output == expected_output
    return PatternResult(
        pattern_name=pattern_name,
        fixture_name=fixture_name,
        passed=passed,
        actual_output=dict(actual_output),
        expected_output=dict(expected_output),
        errors=[] if passed else ["Output mismatch"],
    )


def validate_pattern(pattern_path: str | Path) -> list[str]:
    """Validate that a pattern directory has all required files. Returns list of issues."""
    pattern_path = Path(pattern_path)
    issues: list[str] = []

    required_files = [
        "workflow.json",
        "fixtures/expected_output.json",
        "python/main.py",
        "README.md",
    ]

    for f in required_files:
        if not (pattern_path / f).exists():
            issues.append(f"Missing required file: {f}")

    # Check for at least one test file (any test_*.py)
    py_dir = pattern_path / "python"
    if py_dir.exists():
        test_files = list(py_dir.glob("test_*.py"))
        if not test_files:
            issues.append("Missing test file: python/test_*.py")
    else:
        issues.append("Missing required file: python/test_main.py")

    # Validate workflow.json if it exists
    wf_path = pattern_path / "workflow.json"
    if wf_path.exists():
        try:
            load_workflow_json(pattern_path)
        except Exception as e:
            issues.append(f"Invalid workflow.json: {e}")

    return issues


def discover_patterns(base_path: str | Path = "patterns") -> list[Path]:
    """Discover all pattern directories under the patterns folder."""
    base = Path(base_path)
    if not base.exists():
        return []
    return sorted([p for p in base.iterdir() if p.is_dir() and (p / "workflow.json").exists()])
