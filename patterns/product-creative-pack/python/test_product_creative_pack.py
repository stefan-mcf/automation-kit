"""Tests for Pattern 7: Product Creative Pack — mock-first ComfyUI orchestration."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "product_creative_pack_main", HERE / "python" / "main.py"
)
assert _spec is not None and _spec.loader is not None, "Could not load main.py"
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

ProductCreativePackPipeline = _mod.ProductCreativePackPipeline
run = _mod.run


def _load_json(name: str) -> dict[str, Any]:
    with open(HERE / "fixtures" / name) as f:
        return dict(json.load(f))


class TestProductCreativePackPipeline:
    """Unit tests for brief validation, prompt generation, mock assets, and approval gate."""

    def setup_method(self) -> None:
        self.pipeline = ProductCreativePackPipeline()
        self.brief = _load_json("input.json")

    def test_validate_brief_requires_core_fields(self) -> None:
        broken = dict(self.brief)
        broken.pop("product_name")

        try:
            self.pipeline.normalize_brief(broken)
        except ValueError as exc:
            assert "product_name" in str(exc)
        else:
            raise AssertionError("Missing product_name should raise ValueError")

    def test_normalize_brief_preserves_manual_approval_target(self) -> None:
        normalized = self.pipeline.normalize_brief(self.brief)

        assert normalized["product_name"] == "LumaSip Travel Bottle"
        assert normalized["manual_approval_target"] == "marketing_manager"
        assert normalized["source_images"] == ["placeholder://studio-front", "placeholder://lifestyle-side"]

    def test_generate_prompt_pack_includes_brand_and_safety_constraints(self) -> None:
        normalized = self.pipeline.normalize_brief(self.brief)
        prompt_pack = self.pipeline.generate_prompt_pack(normalized)

        assert len(prompt_pack) == 3
        assert prompt_pack[0]["aspect_ratio"] == "1:1"
        assert "premium insulated travel bottle" in prompt_pack[0]["positive_prompt"]
        assert "clean, confident, eco-conscious" in prompt_pack[0]["positive_prompt"]
        for prompt in prompt_pack:
            assert "no medical claims" in prompt["negative_prompt"]
            assert "no competitor logos" in prompt["negative_prompt"]

    def test_build_comfyui_manifest_is_mock_mode_and_non_executing(self) -> None:
        normalized = self.pipeline.normalize_brief(self.brief)
        prompt_pack = self.pipeline.generate_prompt_pack(normalized)
        manifest = self.pipeline.build_comfyui_manifest(normalized, prompt_pack)

        assert manifest["mode"] == "mock"
        assert manifest["execute_live"] is False
        assert manifest["requires_live_services"] is False
        assert manifest["workflow_template"] == "comfyui_workflow_api.json"
        assert [job["aspect_ratio"] for job in manifest["jobs"]] == ["1:1", "4:5", "16:9"]

    def test_mock_assets_are_deterministic_and_not_image_files(self) -> None:
        normalized = self.pipeline.normalize_brief(self.brief)
        prompt_pack = self.pipeline.generate_prompt_pack(normalized)
        manifest = self.pipeline.build_comfyui_manifest(normalized, prompt_pack)

        first = self.pipeline.generate_mock_assets(manifest)
        second = self.pipeline.generate_mock_assets(manifest)

        assert first == second
        assert first[0]["asset_uri"].startswith("mock://product-creative-pack/")
        assert first[0]["file_created"] is False
        assert all(asset["approval_status"] == "pending_human_review" for asset in first)

    def test_review_packet_requires_approval_and_forbids_publish_action(self) -> None:
        result = self.pipeline.process(self.brief)

        assert result["approval_required"] is True
        assert result["publish_action"] == "blocked_until_human_approval"
        assert result["live_service_used"] is False
        assert result["review_packet"]["decision_required"] == "approve_revise_or_reject"
        assert "Do not publish" in result["review_packet"]["checklist"][-1]


class TestRunOutput:
    """Integration tests for fixture parity and pattern runner compatibility."""

    def test_run_matches_expected_output(self) -> None:
        actual = run(pattern_path=str(HERE))
        expected = _load_json("expected_output.json")
        assert actual == expected, (
            f"run() output does not match expected_output.json\n"
            f"Actual:   {json.dumps(actual, indent=2)}\n"
            f"Expected: {json.dumps(expected, indent=2)}"
        )

    def test_output_contains_no_auto_publish_or_delivery(self) -> None:
        result = run(pattern_path=str(HERE))

        assert result["approval_required"] is True
        assert result["publish_action"] == "blocked_until_human_approval"
        assert result["delivery_action"] == "none"
        assert result["live_service_used"] is False
        assert result["comfyui_job_manifest"]["execute_live"] is False
