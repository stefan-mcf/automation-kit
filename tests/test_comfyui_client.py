"""Tests for the disabled-by-default ComfyUI client boundary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError

import pytest

from auto_kit.comfyui_client import (
    ComfyUIClient,
    DisabledLiveServicesError,
    UnsafeOutputPathError,
    safe_output_path,
)


class FakeHTTPResponse:
    """Small context-manager response for monkeypatched urlopen calls."""

    def __init__(self, payload: dict[str, Any] | bytes) -> None:
        self.payload = payload

    def __enter__(self) -> FakeHTTPResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        if isinstance(self.payload, bytes):
            return self.payload
        return json.dumps(self.payload).encode("utf-8")


def test_default_client_disabled_before_network_call(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[Any] = []

    def fake_urlopen(*args: Any, **kwargs: Any) -> FakeHTTPResponse:
        calls.append((args, kwargs))
        return FakeHTTPResponse({"prompt_id": "should-not-happen"})

    monkeypatch.setattr("auto_kit.comfyui_client.urlopen", fake_urlopen)
    client = ComfyUIClient()

    with pytest.raises(DisabledLiveServicesError, match="AUTO_KIT_USE_LIVE_SERVICES=true"):
        client.submit_prompt({"1": {"class_type": "TestNode"}})

    assert calls == []


def test_enabled_client_requires_base_url() -> None:
    client = ComfyUIClient(enabled=True, base_url="")

    with pytest.raises(ValueError, match="COMFYUI_BASE_URL"):
        client.submit_prompt({"1": {"class_type": "TestNode"}})


def test_submit_prompt_constructs_local_prompt_request(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(request: Any, timeout: float) -> FakeHTTPResponse:
        captured["url"] = request.full_url
        captured["method"] = request.get_method()
        captured["content_type"] = request.headers["Content-type"]
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return FakeHTTPResponse({"prompt_id": "abc-123"})

    monkeypatch.setattr("auto_kit.comfyui_client.urlopen", fake_urlopen)
    client = ComfyUIClient(enabled=True, base_url="http://127.0.0.1:8188")

    response = client.submit_prompt(
        {"1": {"class_type": "TestNode"}},
        client_id="automation-kit-test",
    )

    assert response == {"prompt_id": "abc-123"}
    assert captured == {
        "url": "http://127.0.0.1:8188/prompt",
        "method": "POST",
        "content_type": "application/json",
        "payload": {
            "prompt": {"1": {"class_type": "TestNode"}},
            "client_id": "automation-kit-test",
        },
        "timeout": 30.0,
    }


def test_cloud_prompt_request_uses_api_prefix_and_key(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(request: Any, timeout: float) -> FakeHTTPResponse:
        captured["url"] = request.full_url
        captured["api_key"] = request.headers["X-api-key"]
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        return FakeHTTPResponse({"prompt_id": "cloud-123"})

    monkeypatch.setattr("auto_kit.comfyui_client.urlopen", fake_urlopen)
    client = ComfyUIClient(
        enabled=True,
        base_url="https://cloud.comfy.org",
        cloud_api_key="comfyui-test-key",
    )

    response = client.submit_prompt({"2": {"class_type": "CloudNode"}})

    assert response == {"prompt_id": "cloud-123"}
    assert captured["url"] == "https://cloud.comfy.org/api/prompt"
    assert captured["api_key"] == "comfyui-test-key"
    assert captured["payload"] == {"prompt": {"2": {"class_type": "CloudNode"}}}


def test_get_history_constructs_local_history_request(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(request: Any, timeout: float) -> FakeHTTPResponse:
        captured["url"] = request.full_url
        captured["method"] = request.get_method()
        return FakeHTTPResponse({"abc-123": {"status": "complete"}})

    monkeypatch.setattr("auto_kit.comfyui_client.urlopen", fake_urlopen)
    client = ComfyUIClient(enabled=True, base_url="http://127.0.0.1:8188")

    response = client.get_history("abc-123")

    assert response == {"abc-123": {"status": "complete"}}
    assert captured == {
        "url": "http://127.0.0.1:8188/history/abc-123",
        "method": "GET",
    }


def test_download_view_constructs_request_and_writes_safe_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(request: Any, timeout: float) -> FakeHTTPResponse:
        captured["url"] = request.full_url
        return FakeHTTPResponse(b"PNGDATA")

    monkeypatch.setattr("auto_kit.comfyui_client.urlopen", fake_urlopen)
    client = ComfyUIClient(enabled=True, base_url="http://127.0.0.1:8188")

    output_path = client.download_view(
        filename="product.png",
        output_dir=tmp_path,
        subfolder="review",
        file_type="output",
    )

    assert captured["url"] == (
        "http://127.0.0.1:8188/view?filename=product.png&subfolder=review&type=output"
    )
    assert output_path == tmp_path / "product.png"
    assert output_path.read_bytes() == b"PNGDATA"


def test_safe_output_path_rejects_path_traversal(tmp_path: Path) -> None:
    with pytest.raises(UnsafeOutputPathError, match="Unsafe output filename"):
        safe_output_path(tmp_path, "../secret.png")

    with pytest.raises(UnsafeOutputPathError, match="Unsafe output filename"):
        safe_output_path(tmp_path, "/tmp/secret.png")


def test_http_errors_are_reported_clearly(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: Any, timeout: float) -> FakeHTTPResponse:
        raise HTTPError(request.full_url, 403, "Forbidden", hdrs=None, fp=None)

    monkeypatch.setattr("auto_kit.comfyui_client.urlopen", fake_urlopen)
    client = ComfyUIClient(enabled=True, base_url="https://cloud.comfy.org")

    with pytest.raises(RuntimeError, match="ComfyUI request failed: 403 Forbidden"):
        client.get_history("abc-123")
