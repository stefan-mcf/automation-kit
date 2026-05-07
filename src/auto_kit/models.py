"""Core data models for Automation Kit patterns."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PatternFixture(BaseModel):
    """A single test fixture for a pattern."""

    name: str
    input: dict[str, Any] = Field(default_factory=dict)
    expected_output: dict[str, Any] = Field(default_factory=dict)
    description: str = ""


class PatternResult(BaseModel):
    """Result of running a pattern against a fixture."""

    pattern_name: str
    fixture_name: str
    passed: bool = False
    actual_output: dict[str, Any] = Field(default_factory=dict)
    expected_output: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.pattern_name}/{self.fixture_name}"
