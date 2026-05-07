"""Tests for workflow JSON schema validation."""

import json

import pytest
from pydantic import ValidationError

from auto_kit.workflow_schema import WorkflowConnection, WorkflowJSON, WorkflowNode


def test_minimal_valid_workflow():
    """A workflow with just a name and one node should validate."""
    wf = WorkflowJSON(name="Test", nodes=[WorkflowNode(name="Start", type="n8n-nodes-base.noOp")])
    assert wf.name == "Test"
    assert len(wf.nodes) == 1


def test_workflow_from_dict():
    data = {
        "name": "CSV to CRM",
        "description": "Sync CSV data to CRM",
        "nodes": [
            {"name": "Read CSV", "type": "n8n-nodes-base.readBinaryFile", "position": [0, 0]},
            {"name": "Transform", "type": "n8n-nodes-base.set", "position": [300, 0]},
        ],
        "connections": [
            {"source": "Read CSV", "target": "Transform"},
        ],
    }
    wf = WorkflowJSON(**data)
    assert wf.name == "CSV to CRM"
    assert len(wf.nodes) == 2
    assert len(wf.connections) == 1
    assert wf.find_node("Transform") is not None
    assert wf.find_node("NonExistent") is None


def test_workflow_requires_at_least_one_node():
    with pytest.raises(ValidationError):
        WorkflowJSON(name="Empty", nodes=[])


def test_workflow_node_requires_name_and_type():
    with pytest.raises(ValidationError):
        WorkflowNode(name="OnlyName")  # type: ignore[call-arg]


def test_serialize_roundtrip():
    wf = WorkflowJSON(
        name="Roundtrip",
        nodes=[WorkflowNode(name="A", type="noOp")],
        connections=[WorkflowConnection(source="A", target="B")],
    )
    data = json.loads(wf.model_dump_json())
    restored = WorkflowJSON(**data)
    assert restored.name == "Roundtrip"
    assert len(restored.nodes) == 1


def test_pattern_workflow_json(tmp_path):
    """Simulate loading a workflow.json from a pattern directory."""
    pattern_dir = tmp_path / "test-pattern"
    pattern_dir.mkdir()
    wf_path = pattern_dir / "workflow.json"
    wf_data = {
        "name": "Test Pattern",
        "nodes": [{"name": "Trigger", "type": "n8n-nodes-base.manualTrigger"}],
    }
    with open(wf_path, "w") as f:
        json.dump(wf_data, f)

    with open(wf_path) as f:
        loaded = json.load(f)
    wf = WorkflowJSON(**loaded)
    assert wf.name == "Test Pattern"
