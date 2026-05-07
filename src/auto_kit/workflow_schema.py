"""Pydantic models for minimal n8n-compatible workflow JSON validation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class WorkflowNode(BaseModel):
    """A single node in an n8n-compatible workflow."""

    name: str
    type: str
    position: list[int] = Field(default_factory=lambda: [0, 0])
    parameters: dict[str, Any] = Field(default_factory=dict)


class WorkflowConnection(BaseModel):
    """Connection between two nodes."""

    source: str
    target: str
    source_output: str = "main"
    target_input: str = "main"


class WorkflowJSON(BaseModel):
    """Validated n8n-like workflow export."""

    name: str
    description: str = ""
    nodes: list[WorkflowNode] = Field(default_factory=list, min_length=1)
    connections: list[WorkflowConnection] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def find_node(self, name: str) -> WorkflowNode | None:
        for node in self.nodes:
            if node.name == name:
                return node
        return None
