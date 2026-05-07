# Screenshots and Visual Evidence

The committed visual assets are PNG proof panels generated from local repository outputs. They are safe to inspect without real n8n accounts, ComfyUI servers, product photos, credentials, customer data, cloud resources, or paid calls.

| Asset | What it proves |
|-------|----------------|
| [`01-cli-validation.png`](01-cli-validation.png) | The `auto-kit` command set covers discovery, validation, and representative runs. |
| [`02-pattern-output.png`](02-pattern-output.png) | Pattern outputs are deterministic and reviewable. |
| [`03-architecture.png`](03-architecture.png) | The package separates workflow contracts, Python equivalents, fixtures, mock clients, local API, MCP controls, and gated live clients. |
| [`04-quality-gates.png`](04-quality-gates.png) | The project has passing test, lint, type, pattern-validation, Docker, and CI-style gates. |
| [`05-case-study-link.png`](05-case-study-link.png) | Automation Kit is the framework layer and [`api-webhook-bridge`](https://github.com/stefan-mcf/api-webhook-bridge) is the public case-study repository; the full spoke screenshot package stays in the spoke repo. |

## Regeneration

The case-study panel is generated from `../../scripts/render_proof_screenshots.py` so the image title, repository URL, boundary copy, text bounds, and dimensions are reviewable in git instead of being a one-off manual capture. The renderer raises a `text overflow` error if any text falls outside its container; visually inspect generated images before publishing or attaching them. Regenerate after copy changes with:

```bash
python scripts/render_proof_screenshots.py
python -m pytest tests/test_proof_package.py -q
```

## Current textual evidence

The freshest verification numbers and Docker/Compose/API/MCP smoke results are recorded in `../../EVIDENCE.md`. Treat the PNG panels as durable visual proof and `EVIDENCE.md` as the current command transcript summary.

## Preview

![CLI validation proof](01-cli-validation.png)

![Pattern output proof](02-pattern-output.png)

![Architecture proof](03-architecture.png)

![Quality gate proof](04-quality-gates.png)

![Case study proof](05-case-study-link.png)

## Human-gated evidence

Live n8n editor screenshots, ComfyUI graph captures, generated image outputs, Make/Zapier equivalents, real external-service screenshots, cloud dashboards, and account-specific screenshots are intentionally outside the committed default package. They can be added only after explicit operator approval, synthetic inputs, credential review, and manual output review.
