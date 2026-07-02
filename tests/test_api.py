"""Tests for the local FastAPI/OpenAPI proof surface."""

from __future__ import annotations

from fastapi.testclient import TestClient

from auto_kit.api import app

client = TestClient(app)


def test_health_returns_fixture_safe_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "fixture_safe": True,
        "live_services_used": False,
    }


def test_patterns_lists_discovered_patterns() -> None:
    response = client.get("/patterns")

    assert response.status_code == 200
    body = response.json()
    names = {pattern["name"] for pattern in body["patterns"]}
    assert {"webhook-router", "csv-to-crm", "lead-enrichment", "social-listening"}.issubset(
        names
    )
    social_listening = next(
        pattern for pattern in body["patterns"] if pattern["name"] == "social-listening"
    )
    assert social_listening["api_run_enabled"] is True
    assert body["fixture_safe"] is True
    assert body["live_services_used"] is False


def test_pattern_detail_returns_workflow_metadata() -> None:
    response = client.get("/patterns/webhook-router")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "webhook-router"
    assert body["fixture_safe"] is True
    assert body["live_services_used"] is False
    assert "description" in body


def test_run_supported_pattern_returns_validated_output_shape() -> None:
    response = client.post(
        "/patterns/webhook-router/run",
        json={"fixture_name": "default"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["pattern_name"] == "webhook-router"
    assert body["status"] == "passed"
    assert body["fixture_safe"] is True
    assert body["live_services_used"] is False
    assert body["validation_summary"] == {"passed": True, "fixture_name": "default"}
    assert isinstance(body["output"], dict)
    assert body["errors"] == []
    assert body["warnings"] == []


def test_run_social_listening_returns_prioritized_mentions() -> None:
    response = client.post(
        "/patterns/social-listening/run",
        json={"fixture_name": "default"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["pattern_name"] == "social-listening"
    assert body["status"] == "passed"
    assert body["output"]["matched_count"] == 3
    assert body["output"]["priority_count"] == 2
    assert body["fixture_safe"] is True
    assert body["live_services_used"] is False


def test_run_unknown_pattern_returns_404() -> None:
    response = client.post("/patterns/not-real/run", json={"fixture_name": "default"})

    assert response.status_code == 404
    assert "Unknown pattern" in response.json()["detail"]


def test_run_unsupported_existing_pattern_returns_400() -> None:
    response = client.post("/patterns/email-parser/run", json={"fixture_name": "default"})

    assert response.status_code == 400
    assert "not enabled for API runs" in response.json()["detail"]


def test_run_rejects_non_object_payload() -> None:
    response = client.post("/patterns/webhook-router/run", json=["not", "an", "object"])

    assert response.status_code == 422
    assert "object" in response.json()["detail"].lower()


def test_run_rejects_unsafe_pattern_name() -> None:
    response = client.post("/patterns/%2E%2E/run", json={"fixture_name": "default"})

    assert response.status_code == 422
    assert "pattern_name" in response.json()["detail"]


def test_run_rejects_unsafe_fixture_name() -> None:
    response = client.post("/patterns/webhook-router/run", json={"fixture_name": "../secret"})

    assert response.status_code == 422
    assert "fixture_name" in response.json()["detail"]


def test_run_rejects_unknown_fixture_name() -> None:
    response = client.post("/patterns/webhook-router/run", json={"fixture_name": "other"})

    assert response.status_code == 404
    assert "Unknown fixture" in response.json()["detail"]


def test_run_rejects_invalid_json() -> None:
    response = client.post(
        "/patterns/webhook-router/run",
        content="not-json",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 422
    assert "valid JSON" in response.json()["detail"]


def test_run_rejects_oversized_body() -> None:
    response = client.post(
        "/patterns/webhook-router/run",
        content='{"fixture_name":"default","padding":"' + ("x" * 70_000) + '"}',
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 413
    assert "too large" in response.json()["detail"]
