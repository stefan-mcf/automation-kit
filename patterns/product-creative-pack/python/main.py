"""Pattern 7: Product Creative Pack — mock-first ComfyUI review packet builder.

This pattern turns a synthetic ecommerce product brief into a deterministic
prompt pack, ComfyUI job manifest, mock asset records, and human review packet.
It never calls ComfyUI, creates image files, publishes assets, or delivers
client work. Live visual generation is a separate human-gated tranche.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = [
    "product_name",
    "category",
    "target_audience",
    "campaign_goal",
    "brand_voice",
    "source_images",
    "required_aspect_ratios",
    "negative_prompt_constraints",
    "manual_approval_target",
]

SHOT_BY_RATIO = {
    "1:1": "studio hero shot on a warm neutral background",
    "4:5": "vertical social ad composition with lifestyle context",
    "16:9": "wide website banner with clean negative space for copy",
}


class ProductCreativePackPipeline:
    """Build a mock-first creative generation packet from a product brief."""

    def normalize_brief(self, brief: dict[str, Any]) -> dict[str, Any]:
        """Validate required fields and return a normalized brief."""
        missing = [field for field in REQUIRED_FIELDS if not brief.get(field)]
        if missing:
            raise ValueError(f"Missing required product brief fields: {', '.join(missing)}")

        source_images = list(brief["source_images"])
        aspect_ratios = list(brief["required_aspect_ratios"])
        negative_constraints = list(brief["negative_prompt_constraints"])
        if not source_images:
            raise ValueError("source_images must include at least one placeholder")
        if not aspect_ratios:
            raise ValueError("required_aspect_ratios must include at least one ratio")
        if not negative_constraints:
            raise ValueError("negative_prompt_constraints must include at least one guardrail")

        return {
            "product_name": str(brief["product_name"]).strip(),
            "category": str(brief["category"]).strip(),
            "target_audience": str(brief["target_audience"]).strip(),
            "campaign_goal": str(brief["campaign_goal"]).strip(),
            "brand_voice": str(brief["brand_voice"]).strip(),
            "source_images": [str(item).strip() for item in source_images],
            "required_aspect_ratios": [str(item).strip() for item in aspect_ratios],
            "negative_prompt_constraints": [str(item).strip() for item in negative_constraints],
            "manual_approval_target": str(brief["manual_approval_target"]).strip(),
        }

    def generate_prompt_pack(self, normalized: dict[str, Any]) -> list[dict[str, Any]]:
        """Create one deterministic prompt per requested aspect ratio."""
        prompts: list[dict[str, Any]] = []
        negative_prompt = ", ".join(normalized["negative_prompt_constraints"])
        for index, ratio in enumerate(normalized["required_aspect_ratios"], start=1):
            shot = SHOT_BY_RATIO.get(ratio, "commerce-safe product marketing composition")
            positive_prompt = (
                f"{normalized['product_name']} {normalized['category']}, {shot}, "
                f"for {normalized['target_audience']}, campaign goal: "
                f"{normalized['campaign_goal']}, brand voice: {normalized['brand_voice']}, "
                "photorealistic product lighting, crisp detail, ecommerce-ready"
            )
            prompts.append(
                {
                    "prompt_id": f"prompt-{index:02d}",
                    "aspect_ratio": ratio,
                    "positive_prompt": positive_prompt,
                    "negative_prompt": negative_prompt,
                    "source_image_refs": list(normalized["source_images"]),
                }
            )
        return prompts

    def build_comfyui_manifest(
        self, normalized: dict[str, Any], prompt_pack: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Build a non-executing ComfyUI job manifest for approved live mode."""
        jobs = []
        for prompt in prompt_pack:
            seed_basis = "|".join(
                [normalized["product_name"], prompt["prompt_id"], prompt["aspect_ratio"]]
            )
            seed = int(hashlib.sha256(seed_basis.encode()).hexdigest()[:8], 16)
            jobs.append(
                {
                    "job_id": f"comfyui-{prompt['prompt_id']}",
                    "prompt_id": prompt["prompt_id"],
                    "aspect_ratio": prompt["aspect_ratio"],
                    "seed": seed,
                    "steps": 28,
                    "cfg_scale": 6.5,
                    "sampler": "dpmpp_2m_sde",
                    "scheduler": "karras",
                    "source_image_refs": prompt["source_image_refs"],
                }
            )
        return {
            "mode": "mock",
            "execute_live": False,
            "requires_live_services": False,
            "workflow_template": "comfyui_workflow_api.json",
            "client_boundary": "deferred_to_tranche_9_or_later",
            "jobs": jobs,
        }

    def generate_mock_assets(self, manifest: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate deterministic asset records without creating image files."""
        assets = []
        for index, job in enumerate(manifest["jobs"], start=1):
            digest = hashlib.sha256(
                f"{job['job_id']}|{job['seed']}|{job['aspect_ratio']}".encode()
            ).hexdigest()[:12]
            assets.append(
                {
                    "asset_id": f"asset-{index:02d}-{digest}",
                    "job_id": job["job_id"],
                    "aspect_ratio": job["aspect_ratio"],
                    "asset_uri": f"mock://product-creative-pack/{digest}.png",
                    "file_created": False,
                    "approval_status": "pending_human_review",
                }
            )
        return assets

    def build_review_packet(
        self,
        normalized: dict[str, Any],
        prompt_pack: list[dict[str, Any]],
        assets: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Create the operator review packet; this is the stop boundary."""
        return {
            "review_owner": normalized["manual_approval_target"],
            "decision_required": "approve_revise_or_reject",
            "summary": (
                f"Review {len(assets)} mock creative records for "
                f"{normalized['product_name']} before any live generation or publishing."
            ),
            "items_to_review": [asset["asset_id"] for asset in assets],
            "checklist": [
                "Confirm prompts match product positioning and brand voice.",
                "Check every negative prompt constraint is present.",
                "Verify aspect ratios cover ecommerce, paid social, and web banner use.",
                "Confirm mock assets are placeholders, not generated client deliverables.",
                "Do not publish, send, or use live ComfyUI until a human approves.",
            ],
            "prompt_count": len(prompt_pack),
        }

    def process(self, brief: dict[str, Any]) -> dict[str, Any]:
        """Run the full mock-first creative-pack pipeline."""
        normalized = self.normalize_brief(brief)
        prompt_pack = self.generate_prompt_pack(normalized)
        manifest = self.build_comfyui_manifest(normalized, prompt_pack)
        assets = self.generate_mock_assets(manifest)
        review_packet = self.build_review_packet(normalized, prompt_pack, assets)
        return {
            "normalized_brief": normalized,
            "prompt_pack": prompt_pack,
            "comfyui_job_manifest": manifest,
            "mock_assets": assets,
            "review_packet": review_packet,
            "approval_required": True,
            "publish_action": "blocked_until_human_approval",
            "delivery_action": "none",
            "live_service_used": False,
        }


def run(pattern_path: str | None = None) -> dict[str, Any]:
    """Load input.json, build the mock creative review packet, and return it."""
    if pattern_path is None:
        pattern_path = str(Path(__file__).resolve().parent.parent)

    base = Path(pattern_path)
    input_path = base / "fixtures" / "input.json"
    with open(input_path) as f:
        brief: dict[str, Any] = json.load(f)

    pipeline = ProductCreativePackPipeline()
    return pipeline.process(brief)


if __name__ == "__main__":
    import sys

    result = run(sys.argv[1] if len(sys.argv) > 1 else None)
    print(json.dumps(result, indent=2))
