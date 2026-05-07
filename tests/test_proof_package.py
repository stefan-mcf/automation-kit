"""Tests for public proof package documentation and readiness guardrails."""

from __future__ import annotations

import re
import struct
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw
from scripts.render_proof_screenshots import (
    PANEL_HEADER_STRIPE_TOP_OFFSET,
    PANEL_HEADING_FONT_SIZE,
    PANEL_HEADING_STRIPE_CLEARANCE,
    PANEL_HEADING_Y_OFFSET,
    font,
)

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DOCS = [
    ROOT / "docs" / "pattern-index.md",
    ROOT / "docs" / "architecture.md",
    ROOT / "docs" / "screenshots" / "README.md",
    ROOT / "docs" / "public-readiness.md",
    ROOT / "docs" / "proof-spoke-architecture.md",
    ROOT / "docs" / "api.md",
    ROOT / "docs" / "mcp.md",
    ROOT / "docs" / "deployment.md",
    ROOT / "docs" / "case-studies" / "api-webhook-bridge.md",
    ROOT / "docs" / "case-studies" / "automation-debugger.md",
    ROOT / ".github" / "workflows" / "ci.yml",
    ROOT / "LICENSE",
]
REQUIRED_SCREENSHOT_ASSETS = [
    ROOT / "docs" / "screenshots" / "01-cli-validation.png",
    ROOT / "docs" / "screenshots" / "02-pattern-output.png",
    ROOT / "docs" / "screenshots" / "03-architecture.png",
    ROOT / "docs" / "screenshots" / "04-quality-gates.png",
    ROOT / "docs" / "screenshots" / "05-case-study-link.png",
]
BANNED_PUBLIC_WORDING = re.compile(
    r"\b(wip|work in progress|coming soon|prototype|alpha|beta|tbd|under construction)\b",
    re.IGNORECASE,
)
PRIVATE_SURFACE_WORDING = re.compile(
    "|".join(
        [
            "U" + "pwork",
            "pro" + "posal",
            "proof[- ]of[- ]work",
            "/Users/" + "stefan",
            "docs/" + "upwork",
            "port" + "folio",
        ]
    ),
    re.IGNORECASE,
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_required_proof_package_docs_exist() -> None:
    for path in REQUIRED_DOCS:
        assert path.is_file(), f"missing required proof package file: {path.relative_to(ROOT)}"


def test_required_visual_evidence_assets_exist() -> None:
    for path in REQUIRED_SCREENSHOT_ASSETS:
        assert path.is_file(), f"missing required visual evidence asset: {path.relative_to(ROOT)}"
        assert path.stat().st_size > 20_000, (
            f"{path.relative_to(ROOT)} is too small to be useful proof"
        )
        with path.open("rb") as handle:
            signature = handle.read(24)
        assert signature.startswith(b"\x89PNG\r\n\x1a\n"), (
            f"{path.relative_to(ROOT)} is not a valid PNG asset"
        )
        width, height = struct.unpack(">II", signature[16:24])
        assert width >= 1200 and height >= 800, (
            f"{path.relative_to(ROOT)} is too small for README readability: {width}x{height}"
        )


def test_readme_image_links_resolve_to_committed_png_assets() -> None:
    readme = read(ROOT / "README.md")
    for image_path in re.findall(r"!\[[^\]]*\]\(([^)]+\.png)\)", readme):
        path = ROOT / image_path
        assert path.is_file(), f"README references missing image: {image_path}"
        assert path in REQUIRED_SCREENSHOT_ASSETS, f"unexpected README image path: {image_path}"


def test_case_study_visual_title_is_professional_and_reproducible() -> None:
    readme = read(ROOT / "README.md")
    screenshots = read(ROOT / "docs" / "screenshots" / "README.md")
    renderer = read(ROOT / "scripts" / "render_proof_screenshots.py")

    assert "Public case-study link" not in readme
    assert "Case-study link proof" not in readme
    assert "### Case study" not in readme
    assert "Case study proof" in readme
    assert "Case study proof" in screenshots
    assert "CASE_STUDY_PANEL_TITLE = \"Case Studies\"" in renderer
    assert "05-case-study-link.png" in renderer
    assert "draw_text_checked" in renderer
    assert "text overflow" in renderer


def test_screenshot_renderer_blocks_text_overflow(tmp_path: Path) -> None:
    output_path = tmp_path / "case-study.png"
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from pathlib import Path; "
                "from scripts.render_proof_screenshots import render_case_study_link; "
                f"render_case_study_link(Path({str(output_path)!r}))"
            ),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert output_path.is_file()


def test_case_study_card_headings_clear_the_colored_header_stripe() -> None:
    draw = ImageDraw.Draw(Image.new("RGB", (1600, 1000)))
    heading_font = font(PANEL_HEADING_FONT_SIZE, bold=True)
    panel_top = 220
    stripe_top = panel_top + PANEL_HEADER_STRIPE_TOP_OFFSET
    allowed_bottom = stripe_top - PANEL_HEADING_STRIPE_CLEARANCE
    text_y = panel_top + PANEL_HEADING_Y_OFFSET

    for heading in ["automation-kit", "case-study spokes"]:
        bbox = draw.textbbox((132, text_y), heading, font=heading_font)
        assert bbox[3] <= allowed_bottom, (
            f"{heading!r} descends into the colored header stripe: "
            f"bbox={bbox}, allowed_bottom={allowed_bottom}"
        )


def test_readme_links_to_public_package_and_verified_commands() -> None:
    readme = read(ROOT / "README.md")

    for phrase in [
        "docs/pattern-index.md",
        "docs/architecture.md",
        "docs/screenshots/",
        "docs/proof-spoke-architecture.md",
        "docs/case-studies/api-webhook-bridge.md",
        "docs/case-studies/automation-debugger.md",
        "docs/api.md",
        "docs/mcp.md",
        "docs/deployment.md",
        "docs/public-readiness.md",
        "auto-kit validate-all",
        "auto-kit mcp-validate",
        "docker run --rm automation-kit validate-all",
    ]:
        assert phrase in readme


def test_pattern_index_covers_every_shipped_pattern() -> None:
    index = read(ROOT / "docs" / "pattern-index.md")
    for pattern_dir in sorted((ROOT / "patterns").iterdir()):
        if pattern_dir.is_dir():
            assert f"`{pattern_dir.name}`" in index


def test_public_facing_docs_avoid_unfinished_language_and_private_surface() -> None:
    docs_to_check = [
        ROOT / "README.md",
        ROOT / "EVIDENCE.md",
        ROOT / "docs" / "pattern-index.md",
        ROOT / "docs" / "architecture.md",
        ROOT / "docs" / "api.md",
        ROOT / "docs" / "mcp.md",
        ROOT / "docs" / "deployment.md",
        ROOT / "docs" / "proof-spoke-architecture.md",
        ROOT / "docs" / "public-readiness.md",
        ROOT / "docs" / "case-studies" / "api-webhook-bridge.md",
        ROOT / "docs" / "case-studies" / "automation-debugger.md",
        ROOT / "docs" / "screenshots" / "README.md",
        ROOT / "patterns" / "product-creative-pack" / "README.md",
    ]

    for path in docs_to_check:
        content = read(path)
        assert not BANNED_PUBLIC_WORDING.search(content), (
            f"unfinished public wording found in {path.relative_to(ROOT)}"
        )
        assert not PRIVATE_SURFACE_WORDING.search(content), (
            f"private/marketplace wording found in {path.relative_to(ROOT)}"
        )


def test_public_case_study_link_is_explicit_without_duplicate_screenshots() -> None:
    api_case_study = read(ROOT / "docs" / "case-studies" / "api-webhook-bridge.md")
    debugger_case_study = read(ROOT / "docs" / "case-studies" / "automation-debugger.md")
    screenshots = read(ROOT / "docs" / "screenshots" / "README.md")
    readme = read(ROOT / "README.md")

    expected = {
        "api-webhook-bridge": "https://github.com/stefan-mcf/api-webhook-bridge",
        "automation-debugger": "https://github.com/stefan-mcf/automation-debugger",
    }
    for repo, url in expected.items():
        for content in [screenshots, readme]:
            assert repo in content
            assert url in content

    assert "full spoke screenshot package stays in the spoke repo" in screenshots
    for case_study in [api_case_study, debugger_case_study]:
        assert "does not require live external-service credentials" in case_study
        assert "fixture-safe" in case_study


def test_local_deployment_proof_is_cloud_free_and_smokeable() -> None:
    deployment = read(ROOT / "docs" / "deployment.md")
    compose = read(ROOT / "docker-compose.yml")

    for phrase in [
        "local only",
        "no cloud resources",
        "healthcheck",
        "docker compose up",
        "http://127.0.0.1:8000/health",
        "uvicorn auto_kit.api:app",
    ]:
        assert phrase.lower() in deployment.lower()

    assert "automation-kit-api" in compose
    assert "8000:8000" in compose
    assert "auto_kit.api:app" in compose
    assert "healthcheck" in compose
    assert "AUTO_KIT_USE_LIVE_SERVICES=false" in compose


def test_ci_workflow_matches_local_regression_gates() -> None:
    workflow = read(ROOT / ".github" / "workflows" / "ci.yml")

    for phrase in [
        "pip install -e .[dev]",
        "python -m pytest -q",
        "python -m ruff check .",
        "python -m mypy src",
        "python -m auto_kit.cli validate-all",
        "docker build -t automation-kit .",
        "docker run --rm automation-kit validate-all",
        "PYTHONPATH: src",
    ]:
        assert phrase in workflow


def test_env_example_contains_empty_secret_placeholders() -> None:
    env_example = read(ROOT / ".env.example")

    assert re.search(r"^COMFY_CLOUD_API_KEY=$", env_example, re.MULTILINE)
    assert "***" not in env_example
    assert "AUTO_KIT_USE_LIVE_SERVICES=false" in env_example
