#!/usr/bin/env python3
"""Render deterministic README proof screenshots.

The visual evidence package is intentionally generated from source text rather
than one-off manual screenshots. That makes README image labels, dimensions,
and linked proof copy reviewable in git and reproducible before public updates.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - exercised only when tooling is missing
    raise SystemExit(
        "Pillow is required to render proof screenshots. Install dev dependencies with "
        "`python -m pip install -e '.[dev]'`."
    ) from exc

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_DIR = ROOT / "docs" / "screenshots"
CASE_STUDY_URLS = (
    "https://github.com/stefan-mcf/api-webhook-bridge",
    "https://github.com/stefan-mcf/automation-debugger",
)
CASE_STUDY_PANEL_TITLE = "Case Studies"
PANEL_HEADING_FONT_SIZE = 25
PANEL_HEADING_Y_OFFSET = 22
PANEL_HEADER_STRIPE_TOP_OFFSET = 66
PANEL_HEADER_BOTTOM_OFFSET = 94
PANEL_HEADING_STRIPE_CLEARANCE = 8
Bounds = tuple[int, int, int, int]
Color = tuple[int, int, int]


@dataclass(frozen=True)
class Panel:
    heading: str
    title: str
    bullets: tuple[str, ...]
    color: Color


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    system_font = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf"
    )
    library_font = "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf"
    linux_font = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )
    candidates = [system_font, library_font, linux_font]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def rounded_rect(
    draw: ImageDraw.ImageDraw,
    xy: Bounds,
    radius: int,
    fill: Color,
    outline: Color | None = None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def ensure_inside(label: str, bbox: Bounds, bounds: Bounds) -> None:
    left, top, right, bottom = bbox
    bound_left, bound_top, bound_right, bound_bottom = bounds
    if left < bound_left or top < bound_top or right > bound_right or bottom > bound_bottom:
        raise ValueError(
            f"text overflow for {label!r}: bbox={bbox}, allowed={bounds}. "
            "Shorten the copy, reduce font size, or increase the container."
        )


def text_width(draw: ImageDraw.ImageDraw, text: str, text_font: ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=text_font)
    return bbox[2] - bbox[0]


def text_height(draw: ImageDraw.ImageDraw, text: str, text_font: ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=text_font)
    return bbox[3] - bbox[1]


def wrap_to_pixels(
    draw: ImageDraw.ImageDraw,
    text: str,
    text_font: ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if text_width(draw, candidate, text_font) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
            current = word
        if text_width(draw, current, text_font) <= max_width:
            continue
        chunk = ""
        for char in current:
            candidate_chunk = f"{chunk}{char}"
            if text_width(draw, candidate_chunk, text_font) <= max_width:
                chunk = candidate_chunk
            else:
                if chunk:
                    lines.append(chunk)
                chunk = char
        current = chunk
    if current:
        lines.append(current)
    return lines


def draw_text_checked(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    *,
    fill: Color,
    text_font: ImageFont.ImageFont,
    bounds: Bounds,
    label: str,
) -> Bounds:
    bbox = draw.textbbox(xy, text, font=text_font)
    ensure_inside(label, bbox, bounds)
    draw.text(xy, text, fill=fill, font=text_font)
    return bbox


def draw_wrapped_text_checked(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    *,
    fill: Color,
    text_font: ImageFont.ImageFont,
    max_width: int,
    max_bottom: int,
    label: str,
    line_gap: int = 8,
) -> int:
    x, y = xy
    line_height = text_height(draw, "Ag", text_font) + line_gap
    lines = wrap_to_pixels(draw, text, text_font, max_width)
    bounds = (x, y, x + max_width, max_bottom)
    for index, line in enumerate(lines):
        line_y = y + index * line_height
        draw_text_checked(
            draw,
            (x, line_y),
            line,
            fill=fill,
            text_font=text_font,
            bounds=bounds,
            label=f"{label} line {index + 1}",
        )
    return y + len(lines) * line_height


def draw_grid(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    grid = (38, 55, 80)
    for x in range(0, width, 48):
        draw.line((x, 0, x, height), fill=grid, width=1)
    for y in range(0, height, 48):
        draw.line((0, y, width, y), fill=grid, width=1)


def draw_panel(draw: ImageDraw.ImageDraw, panel: Panel, xy: Bounds) -> None:
    x1, y1, x2, y2 = xy
    rounded_rect(draw, xy, 28, (17, 28, 45), outline=panel.color, width=3)
    rounded_rect(
        draw,
        (x1, y1, x2, y1 + PANEL_HEADER_BOTTOM_OFFSET),
        28,
        (24, 39, 61),
        outline=panel.color,
        width=2,
    )
    draw.rectangle(
        (x1, y1 + PANEL_HEADER_STRIPE_TOP_OFFSET, x2, y1 + PANEL_HEADER_BOTTOM_OFFSET),
        fill=panel.color,
    )
    draw_text_checked(
        draw,
        (x1 + 44, y1 + PANEL_HEADING_Y_OFFSET),
        panel.heading,
        fill=(255, 255, 255),
        text_font=font(PANEL_HEADING_FONT_SIZE, bold=True),
        bounds=(
            x1 + 44,
            y1 + 12,
            x2 - 44,
            y1 + PANEL_HEADER_STRIPE_TOP_OFFSET - PANEL_HEADING_STRIPE_CLEARANCE,
        ),
        label=f"{panel.heading} heading",
    )
    draw_text_checked(
        draw,
        (x1 + 36, y1 + 118),
        panel.title,
        fill=(232, 240, 255),
        text_font=font(28, bold=True),
        bounds=(x1 + 36, y1 + 110, x2 - 36, y1 + 160),
        label=f"{panel.heading} title",
    )

    y = y1 + 178
    body_font = font(23)
    bullet_x = x1 + 70
    max_width = x2 - bullet_x - 38
    max_bottom = y2 - 32
    for index, bullet in enumerate(panel.bullets):
        draw.ellipse((x1 + 38, y + 8, x1 + 50, y + 20), fill=panel.color)
        next_y = draw_wrapped_text_checked(
            draw,
            (bullet_x, y),
            bullet,
            fill=(178, 193, 214),
            text_font=body_font,
            max_width=max_width,
            max_bottom=max_bottom,
            label=f"{panel.heading} bullet {index + 1}",
            line_gap=7,
        )
        y = next_y + 17
    if y > max_bottom + 24:
        raise ValueError(f"bullet stack overflow in {panel.heading}: bottom={y}, max={max_bottom}")


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int]) -> None:
    sx, sy = start
    ex, ey = end
    arrow = (247, 199, 82)
    head_base = ex - 34
    shaft_start = sx + 8
    draw.line((shaft_start, sy, head_base, ey), fill=arrow, width=12)
    draw.polygon([(ex, ey), (head_base, ey - 24), (head_base, ey + 24)], fill=arrow)
    label_font = font(24, bold=True)
    top_label = "reusable"
    bottom_label = "patterns"
    top_width = text_width(draw, top_label, label_font)
    bottom_width = text_width(draw, bottom_label, label_font)
    center_x = sx + (ex - sx) // 2
    draw_text_checked(
        draw,
        (center_x - top_width // 2, sy - 72),
        top_label,
        fill=arrow,
        text_font=label_font,
        bounds=(sx - 40, sy - 90, ex + 40, sy - 40),
        label="arrow top label",
    )
    draw_text_checked(
        draw,
        (center_x - bottom_width // 2, sy + 36),
        bottom_label,
        fill=arrow,
        text_font=label_font,
        bounds=(sx - 40, sy + 24, ex + 40, sy + 78),
        label="arrow bottom label",
    )


def render_case_study_link(path: Path) -> None:
    width, height = 1600, 1000
    image = Image.new("RGB", (width, height), (9, 16, 29))
    draw = ImageDraw.Draw(image)
    draw_grid(draw, width, height)

    draw_text_checked(
        draw,
        (88, 64),
        CASE_STUDY_PANEL_TITLE,
        fill=(245, 249, 255),
        text_font=font(52, bold=True),
        bounds=(88, 58, width - 88, 140),
        label="main title",
    )
    draw_text_checked(
        draw,
        (88, 142),
        "Reusable core linked to focused public case-study repositories.",
        fill=(150, 168, 193),
        text_font=font(25),
        bounds=(88, 134, width - 88, 184),
        label="subtitle",
    )

    left = Panel(
        heading="automation-kit",
        title="Reusable framework layer",
        bullets=(
            "Pattern contracts and validation",
            "Synthetic fixtures and deterministic outputs",
            "CLI, API, and MCP control surfaces",
            "Quality gates and local screenshot evidence",
            "Live services disabled by default",
        ),
        color=(78, 156, 255),
    )
    right = Panel(
        heading="case-study spokes",
        title="Public focused repos",
        bullets=(
            "api-webhook-bridge: safe API/webhook build path",
            "automation-debugger: failed automation diagnosis path",
            "Synthetic fixtures, local APIs, tests, and screenshots",
            "Spoke evidence stays in each repository",
            "Fixture-safe; no live service calls",
        ),
        color=(61, 220, 151),
    )

    draw_panel(draw, left, (88, 220, 682, 750))
    draw_panel(draw, right, (918, 220, 1512, 750))
    draw_arrow(draw, (715, 486), (884, 486))

    footer = (88, 806, 1512, 922)
    rounded_rect(draw, footer, 24, (15, 25, 41), outline=(76, 96, 130), width=2)
    draw_text_checked(
        draw,
        (128, 834),
        "Public repositories",
        fill=(150, 168, 193),
        text_font=font(22, bold=True),
        bounds=(128, 826, 760, 860),
        label="public repository footer label",
    )
    draw_wrapped_text_checked(
        draw,
        (128, 870),
        " • ".join(CASE_STUDY_URLS),
        fill=(255, 255, 255),
        text_font=font(20, bold=True),
        max_width=690,
        max_bottom=922,
        label="public repository URLs",
        line_gap=4,
    )
    draw_text_checked(
        draw,
        (872, 834),
        "Boundary",
        fill=(150, 168, 193),
        text_font=font(22, bold=True),
        bounds=(872, 826, 1472, 860),
        label="boundary footer label",
    )
    draw_wrapped_text_checked(
        draw,
        (872, 870),
        "Synthetic data • local proof",
        fill=(255, 255, 255),
        text_font=font(22, bold=True),
        max_width=590,
        max_bottom=910,
        label="boundary footer text",
        line_gap=4,
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)


def main() -> None:
    render_case_study_link(SCREENSHOT_DIR / "05-case-study-link.png")
    print(f"rendered {SCREENSHOT_DIR / '05-case-study-link.png'}")


if __name__ == "__main__":
    main()
