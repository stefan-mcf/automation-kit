"""Registry for Automation Kit factory sectors and callable capabilities."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

SAFE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_REGISTRY_ROOT = Path(__file__).resolve().parent / "registry"
REPO_REGISTRY_ROOT = REPO_ROOT / "registry"
REGISTRY_ROOT = PACKAGE_REGISTRY_ROOT if PACKAGE_REGISTRY_ROOT.exists() else REPO_REGISTRY_ROOT


class RegistryValidationError(ValueError):
    """Raised when sector/capability registry data is invalid."""


def validate_safe_id(value: str) -> str:
    """Return a registry id or raise when it contains unsafe path-like characters."""

    if not SAFE_ID_RE.fullmatch(value):
        raise ValueError(f"unsafe id: {value}")
    if ".." in value or "/" in value or "\\" in value:
        raise ValueError(f"unsafe id: {value}")
    return value


@dataclass(frozen=True)
class Sector:
    """Factory/business grouping used for routing and packaging."""

    sector_id: str
    label: str
    status: str
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Sector":
        sector_id = validate_safe_id(str(data["sector_id"]))
        return cls(
            sector_id=sector_id,
            label=str(data.get("label", sector_id)),
            status=str(data.get("status", "planned")),
            description=str(data.get("description", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sector_id": self.sector_id,
            "label": self.label,
            "status": self.status,
            "description": self.description,
        }


@dataclass(frozen=True)
class Capability:
    """Callable or inspectable factory unit backed by a pattern or spoke."""

    capability_id: str
    sector_id: str
    kind: str
    implementation: str
    runnable: bool
    fixture_safe: bool
    live_services_used: bool
    description: str = ""
    evidence: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Capability":
        capability_id = validate_safe_id(str(data["capability_id"]))
        sector_id = validate_safe_id(str(data["sector_id"]))
        return cls(
            capability_id=capability_id,
            sector_id=sector_id,
            kind=str(data.get("kind", "pattern")),
            implementation=str(data["implementation"]),
            runnable=bool(data.get("runnable", False)),
            fixture_safe=bool(data.get("fixture_safe", True)),
            live_services_used=bool(data.get("live_services_used", False)),
            description=str(data.get("description", "")),
            evidence=[str(item) for item in data.get("evidence", [])],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "sector_id": self.sector_id,
            "kind": self.kind,
            "implementation": self.implementation,
            "runnable": self.runnable,
            "fixture_safe": self.fixture_safe,
            "live_services_used": self.live_services_used,
            "description": self.description,
            "evidence": list(self.evidence),
        }

    def implementation_path(self, repo_root: Path = REPO_ROOT) -> Path:
        return (repo_root / self.implementation).resolve()


class CapabilityRegistry:
    """Loaded sector/capability registry with validation and lookup helpers."""

    def __init__(
        self,
        repo_root: Path,
        sectors_yaml: dict[str, Any],
        capabilities_yaml: dict[str, Any],
    ) -> None:
        self.repo_root = repo_root
        self._sectors = [Sector.from_dict(item) for item in sectors_yaml.get("sectors", [])]
        self._capabilities = [
            Capability.from_dict(item) for item in capabilities_yaml.get("capabilities", [])
        ]

    @classmethod
    def load_default(cls) -> "CapabilityRegistry":
        return cls.from_paths(REGISTRY_ROOT / "sectors.yaml", REGISTRY_ROOT / "capabilities.yaml")

    @classmethod
    def from_paths(cls, sectors_path: Path, capabilities_path: Path) -> "CapabilityRegistry":
        sectors_yaml = _read_yaml(sectors_path)
        capabilities_yaml = _read_yaml(capabilities_path)
        registry = cls(REPO_ROOT, sectors_yaml, capabilities_yaml)
        registry.validate()
        return registry

    def list_sectors(self) -> list[Sector]:
        return list(self._sectors)

    def get_sector(self, sector_id: str) -> Sector:
        safe_id = validate_safe_id(sector_id)
        for sector in self._sectors:
            if sector.sector_id == safe_id:
                return sector
        raise KeyError(f"unknown sector: {sector_id}")

    def list_capabilities(
        self,
        sector_id: str | None = None,
        runnable_only: bool = False,
    ) -> list[Capability]:
        if sector_id is not None:
            safe_sector_id = validate_safe_id(sector_id)
            self.get_sector(safe_sector_id)
        else:
            safe_sector_id = None

        capabilities = self._capabilities
        if safe_sector_id is not None:
            capabilities = [item for item in capabilities if item.sector_id == safe_sector_id]
        if runnable_only:
            capabilities = [item for item in capabilities if item.runnable]
        return list(capabilities)

    def get_capability(self, capability_id: str) -> Capability:
        safe_id = validate_safe_id(capability_id)
        for capability in self._capabilities:
            if capability.capability_id == safe_id:
                return capability
        raise KeyError(f"unknown capability: {capability_id}")

    def validate(self) -> None:
        sector_ids = [sector.sector_id for sector in self._sectors]
        capability_ids = [capability.capability_id for capability in self._capabilities]
        _ensure_unique(sector_ids, "sector")
        _ensure_unique(capability_ids, "capability")
        known_sectors = set(sector_ids)
        for capability in self._capabilities:
            if capability.sector_id not in known_sectors:
                raise RegistryValidationError(
                    f"capability {capability.capability_id} references unknown sector "
                    f"{capability.sector_id}"
                )
            if capability.kind == "pattern":
                path = capability.implementation_path(self.repo_root)
                patterns_root = (self.repo_root / "patterns").resolve()
                if patterns_root not in path.parents:
                    raise RegistryValidationError(
                        "pattern capability "
                        f"{capability.capability_id} resolves outside patterns root"
                    )
                if not (path / "workflow.json").exists():
                    raise RegistryValidationError(
                        f"pattern capability {capability.capability_id} missing workflow.json"
                    )
            if capability.live_services_used and capability.runnable:
                raise RegistryValidationError(
                    "live-service capability "
                    f"{capability.capability_id} cannot be runnable by default"
                )


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open() as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise RegistryValidationError(f"registry file must contain a mapping: {path}")
    return data


def _ensure_unique(values: list[str], label: str) -> None:
    seen: set[str] = set()
    for value in values:
        if value in seen:
            raise RegistryValidationError(f"duplicate {label} id: {value}")
        seen.add(value)
