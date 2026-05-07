"""Automation Kit CLI — list, validate, and run automation patterns."""

from __future__ import annotations

from pathlib import Path

import typer

from auto_kit.capability_registry import CapabilityRegistry
from auto_kit.mcp_server import main as run_mcp_server
from auto_kit.pattern_runner import (
    discover_patterns,
    load_workflow_json,
    run_pattern_module,
    validate_pattern,
)

app = typer.Typer(name="auto-kit", help="Low-code automation pattern library.")


@app.command()
def list_patterns() -> None:
    """List all available patterns."""
    patterns = discover_patterns()
    if not patterns:
        typer.echo("No patterns found.")
        return

    typer.echo(f"Found {len(patterns)} pattern(s):\n")
    for p in patterns:
        try:
            wf = load_workflow_json(p)
            desc = wf.description or "(no description)"
            typer.echo(f"  {p.name:<25} {desc}")
        except Exception:
            typer.echo(f"  {p.name:<25} (invalid workflow.json)")

    # Show patterns not discoverable via workflow.json
    base = Path("patterns")
    if base.exists():
        all_dirs = sorted(base.iterdir())
        pattern_names = {p.name for p in patterns}
        undiscovered = [d.name for d in all_dirs if d.is_dir() and d.name not in pattern_names]
        if undiscovered:
            typer.echo(f"\n{len(undiscovered)} unrecognized pattern(s) (no workflow.json):")
            for name in undiscovered:
                typer.echo(f"  {name}")


@app.command()
def validate(pattern_path: str) -> None:
    """Validate a specific pattern directory."""
    issues = validate_pattern(pattern_path)
    if not issues:
        typer.echo(f"[PASS] {pattern_path} — all valid")
    else:
        typer.echo(f"[FAIL] {pattern_path} — {len(issues)} issue(s):")
        for issue in issues:
            typer.echo(f"  - {issue}")
        raise typer.Exit(code=1)


@app.command()
def run(pattern_path: str) -> None:
    """Run a pattern's Python equivalent and compare with expected output."""
    result = run_pattern_module(pattern_path)
    typer.echo(result.summary())
    if not result.passed:
        if result.errors:
            for err in result.errors:
                typer.echo(f"  Error: {err}")
        raise typer.Exit(code=1)


@app.command(name="validate-all")
def validate_all() -> None:
    """Validate all discoverable patterns."""
    patterns = discover_patterns()
    if not patterns:
        typer.echo("No patterns found.")
        raise typer.Exit(code=1)

    passed = 0
    failed = 0
    for p in patterns:
        typer.echo(f"  Checking {p.name}... ", nl=False)
        issues = validate_pattern(str(p))
        if not issues:
            typer.echo("PASS")
            passed += 1
        else:
            typer.echo("FAIL")
            for issue in issues:
                typer.echo(f"    - {issue}")
            failed += 1

    typer.echo(f"\n{passed + failed} pattern(s): {passed} passed, {failed} failed")
    if failed > 0:
        raise typer.Exit(code=1)


@app.command(name="mcp-validate")
def mcp_validate() -> None:
    """Validate the MCP sector/capability registry."""
    registry = CapabilityRegistry.load_default()
    registry.validate()
    sector_count = len(registry.list_sectors())
    capability_count = len(registry.list_capabilities())
    typer.echo(
        f"MCP registry valid: {sector_count} sectors, {capability_count} capabilities"
    )


@app.command(name="mcp-serve")
def mcp_serve() -> None:
    """Run the Automation Kit MCP server over stdio."""
    run_mcp_server()


if __name__ == "__main__":
    app()
