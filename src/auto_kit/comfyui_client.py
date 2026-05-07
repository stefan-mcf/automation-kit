"""Disabled-by-default ComfyUI client boundary for human-approved live runs.

The repository must remain deterministic and safe by default. This module
therefore refuses every network operation unless live services are explicitly
enabled and a base URL is supplied. Tests monkeypatch the HTTP boundary; no real
ComfyUI server, cloud key, GPU, model download, or paid service is required.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


class DisabledLiveServicesError(RuntimeError):
    """Raised before any network call when live services are disabled."""


class UnsafeOutputPathError(ValueError):
    """Raised when a server-supplied filename would escape the output directory."""


def env_flag(value: str | None) -> bool:
    """Parse common truthy environment flag values."""
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def safe_output_path(output_dir: str | Path, filename: str) -> Path:
    """Return a safe output path for a ComfyUI-view filename.

    The filename must be a plain basename. This rejects absolute paths,
    `../` traversal, and nested paths before any file is written.
    """
    if not filename or Path(filename).name != filename or Path(filename).is_absolute():
        raise UnsafeOutputPathError(f"Unsafe output filename: {filename!r}")

    base = Path(output_dir).resolve()
    candidate = (base / filename).resolve()
    if candidate.parent != base:
        raise UnsafeOutputPathError(f"Unsafe output filename: {filename!r}")
    return candidate


class ComfyUIClient:
    """Thin ComfyUI REST client with an explicit disabled-by-default guard."""

    def __init__(
        self,
        *,
        enabled: bool | None = None,
        base_url: str | None = None,
        cloud_api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        if enabled is None:
            self.enabled = env_flag(os.getenv("AUTO_KIT_USE_LIVE_SERVICES"))
        else:
            self.enabled = enabled

        if base_url is not None:
            configured_base_url = base_url
        else:
            configured_base_url = os.getenv("COMFYUI_BASE_URL", "")
        self.base_url = configured_base_url.strip()
        configured_cloud_key = (
            cloud_api_key if cloud_api_key is not None else os.getenv("COMFY_CLOUD_API_KEY", "")
        )
        self.cloud_api_key = configured_cloud_key.strip()
        self.timeout = timeout

    @property
    def is_cloud(self) -> bool:
        """Whether this client targets Comfy Cloud rather than local ComfyUI."""
        return "cloud.comfy.org" in self.base_url.lower()

    def submit_prompt(
        self,
        workflow: dict[str, Any],
        *,
        client_id: str | None = None,
    ) -> dict[str, Any]:
        """POST a workflow to `/prompt` after explicit live-service checks."""
        payload: dict[str, Any] = {"prompt": workflow}
        if client_id:
            payload["client_id"] = client_id
        return self._request_json("POST", "/prompt", payload=payload)

    def get_history(self, prompt_id: str) -> dict[str, Any]:
        """GET prompt history for a local or cloud ComfyUI prompt id."""
        if not prompt_id.strip():
            raise ValueError("prompt_id is required")
        return self._request_json("GET", f"/history/{prompt_id.strip()}")

    def download_view(
        self,
        *,
        filename: str,
        output_dir: str | Path,
        subfolder: str = "",
        file_type: str = "output",
    ) -> Path:
        """Download a `/view` output to a path-traversal-safe local filename."""
        target = safe_output_path(output_dir, filename)
        query = urlencode({"filename": filename, "subfolder": subfolder, "type": file_type})
        content = self._request_bytes("GET", f"/view?{query}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return target

    def _assert_enabled(self) -> None:
        if not self.enabled:
            raise DisabledLiveServicesError(
                "Live ComfyUI calls are disabled. Set AUTO_KIT_USE_LIVE_SERVICES=true "
                "and COMFYUI_BASE_URL before using ComfyUIClient."
            )
        if not self.base_url:
            raise ValueError("COMFYUI_BASE_URL is required when live services are enabled")

    def _url(self, path: str) -> str:
        base = self.base_url.rstrip("/") + "/"
        relative = path.lstrip("/")
        if self.is_cloud and not relative.startswith("api/"):
            relative = "api/" + relative
        return urljoin(base, relative)

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.is_cloud and self.cloud_api_key:
            headers["X-API-Key"] = self.cloud_api_key
        return headers

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        data = self._request_bytes(method, path, payload=payload)
        decoded = json.loads(data.decode("utf-8"))
        if not isinstance(decoded, dict):
            raise RuntimeError("ComfyUI response was not a JSON object")
        return decoded

    def _request_bytes(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
    ) -> bytes:
        self._assert_enabled()
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            self._url(path),
            data=body,
            headers=self._headers(),
            method=method,
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                data = response.read()
                if not isinstance(data, bytes):
                    raise RuntimeError("ComfyUI response body was not bytes")
                return data
        except HTTPError as exc:
            raise RuntimeError(f"ComfyUI request failed: {exc.code} {exc.reason}") from exc
        except URLError as exc:
            raise RuntimeError(f"ComfyUI request failed: {exc.reason}") from exc
