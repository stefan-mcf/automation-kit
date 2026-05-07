# Product Creative Pack

Product Creative Pack is a mock-first ecommerce creative automation pattern. It shows how a low-code workflow can accept a product brief, normalize the request, generate a prompt pack, prepare a ComfyUI-style job manifest, create deterministic mock asset records, and stop at a human review packet.

The default path does not generate images. Visual asset generation requires an approved GPT image generation path in HD mode or an explicitly approved live ComfyUI path. The committed pattern remains fixture-only and deterministic.

## What it proves

- Product brief validation with required fields and source-image placeholders.
- Prompt generation for multiple ecommerce aspect ratios.
- Product-safety guardrails through negative prompt constraints.
- A ComfyUI API placeholder that documents live-run controllable parameters.
- Mock asset records that prove orchestration without creating files or calling a GPU/API.
- A manual approval stop before publishing, delivery, or live image generation.

## Inputs

`fixtures/input.json` contains synthetic data only:

- `product_name`
- `category`
- `target_audience`
- `campaign_goal`
- `brand_voice`
- `source_images` using `placeholder://` references
- `required_aspect_ratios`
- `negative_prompt_constraints`
- `manual_approval_target`

## Outputs

`auto-kit run patterns/product-creative-pack` returns:

- `normalized_brief`
- `prompt_pack`
- `comfyui_job_manifest`
- `mock_assets`
- `review_packet`
- `approval_required=true`
- `publish_action=blocked_until_human_approval`
- `delivery_action=none`
- `live_service_used=false`

The expected output is locked in `fixtures/expected_output.json` so the Python equivalent and workflow artifact can be checked like the other patterns.

## Low-code vs Python tradeoff

Use low-code when the client needs a visible operations workflow: a brief intake trigger, validation node, prompt-generation step, mock asset collection, and a review handoff that non-developers can understand.

Use Python when prompt construction, deterministic asset IDs, fixture tests, safety checks, or repeatable output comparisons matter. The Python version is easier to test and version-control, while the low-code JSON is easier to inspect with clients.

## ComfyUI mock/live boundary

Mock mode is mandatory for the default default workflow. The included `comfyui_workflow_api.json` is a non-executed placeholder. It records live-run parameters such as prompt text, negative prompt text, aspect ratio, seed, sampler, scheduler, and source image references.

The shared `auto_kit.comfyui_client.ComfyUIClient` boundary is disabled by default. It raises before any network call unless `AUTO_KIT_USE_LIVE_SERVICES=true` and `COMFYUI_BASE_URL` are explicitly supplied. `COMFY_CLOUD_API_KEY` may be set only in a local `.env` or shell for an approved Comfy Cloud test; never commit a key.

Do not connect this pattern to a live ComfyUI server, Comfy Cloud, downloaded models, real product photos, generated client assets, publishing tools, or paid services without a separate human-approved evidence pass. Live local and cloud modes are human-gated modes only.

## No-auto-publish policy

This pattern always stops at human review. It must not publish, send, upload, advertise, message, or deliver generated assets automatically. The review owner must approve, revise, or reject the packet before any live generation or client-facing use.

## Import notes

`workflow.json` is an n8n-style workflow artifact for review. Before importing into a live n8n instance, validate node compatibility and keep all live credentials disabled. Fixture-backed Python validation is the source of truth.

## Run locally

```bash
PYTHONPATH=src python -m pytest patterns/product-creative-pack/python/test_product_creative_pack.py -q
PYTHONPATH=src python -m auto_kit.cli run patterns/product-creative-pack
PYTHONPATH=src python -m auto_kit.cli validate patterns/product-creative-pack
```

## External automation fit

This pattern fits ecommerce automation, AI creative ops, n8n/Make/Zapier workflow planning, prompt-pack generation, review-packet automation, and Python equivalents for teams that need deterministic tests before they risk live generation.
