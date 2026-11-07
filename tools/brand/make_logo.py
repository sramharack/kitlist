"""Generate the kitlist logo files from code, so the brand is reproducible.

The icon is a miniature equipment schedule: a title band and three rows on a
12-unit grid. Every row has a copper tag cell and ends flush right, but the
cells inside each row span different numbers of grid units, which is the
whole idea of kitlist (see ADR 0001).

Text is converted to outlines, so the SVGs look identical everywhere,
with no font installed. Font: IBM Plex Mono (SIL Open Font License).

Usage (from the repo root):
    uv run --with fonttools --with cairosvg python tools/brand/make_logo.py FONT_DIR
FONT_DIR must contain IBMPlexMono-SemiBold.ttf and IBMPlexMono-Regular.ttf.
"""

import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

OUT = Path("docs/assets")

NAVY = "#1F3A5F"
COPPER = "#D9782D"
PALE = "#E8EEF5"
BAND = "#8FA7C4"
TEXT_LIGHT = NAVY  # wordmark on light backgrounds
TEXT_DARK = "#E6EDF3"  # wordmark on GitHub dark theme
GREY = "#5B6B7F"

# Icon geometry (120 x 120 units)
UNIT, GAP, X0 = 7, 3, 18  # 12 grid units of 7 -> 84 wide, starting at x = 18
ROWS = [(42, [2, 4, 3, 3]), (62, [2, 3, 5, 2]), (82, [2, 6, 2, 2])]  # (top y, spans)
ROW_H = 14


def text_path(font_file: Path, text: str, size: float, x: float, baseline: float) -> str:
    """Return an SVG path 'd' string for text, starting at x on the given baseline."""
    font = TTFont(font_file)
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    parts, cursor = [], x
    for ch in text:
        name = cmap[ord(ch)]
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, cursor, baseline)))
        parts.append(pen.getCommands())
        cursor += glyphs[name].width * scale
    return " ".join(p for p in parts if p)


def icon_shapes(dx: float = 0, dy: float = 0, k: float = 1) -> str:
    """SVG shapes for the icon, translated by (dx, dy) and scaled by k."""

    def rect(x, y, w, h, rx, fill):
        return (
            f'<rect x="{dx + k * x:g}" y="{dy + k * y:g}" width="{k * w:g}" '
            f'height="{k * h:g}" rx="{k * rx:g}" fill="{fill}"/>'
        )

    shapes = [rect(6, 6, 108, 108, 18, NAVY)]
    shapes.append(rect(X0 + GAP / 2, 24, 12 * UNIT - GAP, 10, 2, BAND))  # title band
    for top, spans in ROWS:
        start = 0
        for i, n in enumerate(spans):
            x = X0 + start * UNIT + GAP / 2
            shapes.append(rect(x, top, n * UNIT - GAP, ROW_H, 2, COPPER if i == 0 else PALE))
            start += n
    return "\n  ".join(shapes)


def svg(width: float, height: float, body: str, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {height:g}" '
        f'width="{width:g}" height="{height:g}" role="img" aria-label="{title}">\n'
        f"  <title>{title}</title>\n  {body}\n</svg>\n"
    )


def main(font_dir: Path) -> None:
    bold = font_dir / "IBMPlexMono-SemiBold.ttf"
    regular = font_dir / "IBMPlexMono-Regular.ttf"
    OUT.mkdir(parents=True, exist_ok=True)

    # 1. Icon only (avatar, favicon)
    (OUT / "icon.svg").write_text(svg(120, 120, icon_shapes(), "kitlist"))

    # 2. Horizontal logo, one per GitHub theme
    word = text_path(bold, "kitlist", 72, 140, 88)
    for name, colour in [("logo-light.svg", TEXT_LIGHT), ("logo-dark.svg", TEXT_DARK)]:
        body = icon_shapes() + f'\n  <path d="{word}" fill="{colour}"/>'
        (OUT / name).write_text(svg(452, 120, body, "kitlist"))

    # 3. Social preview, 1280 x 640 (GitHub: Settings > Social preview)
    W, H = 1280, 640
    grid = "".join(
        f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="{BAND}" stroke-opacity="0.18"/>'
        for x in (W * i / 24 for i in range(1, 24))  # the 24-column grid
    )
    k = 1.6  # icon scale
    logo_w = k * 120 + 24 + 7 * 0.6 * 115  # icon + gap + 7 mono glyphs at size 115
    lx = (W - logo_w) / 2
    baseline = 300
    word = text_path(bold, "kitlist", 115, lx + k * 120 + 24, baseline)
    tag = "aligned equipment schedules for MEP drawings"
    tag_w = len(tag) * 0.6 * 34
    tagline = text_path(regular, tag, 34, (W - tag_w) / 2, 450)
    body = (
        f'<rect width="{W}" height="{H}" fill="#F6F8FA"/>\n  {grid}\n  '
        # centre the icon on the wordmark (its visual middle is ~0.35 em above the baseline)
        + icon_shapes(lx, baseline - 0.35 * 115 - k * 60, k)
        + f'\n  <path d="{word}" fill="{NAVY}"/>\n  <path d="{tagline}" fill="{GREY}"/>'
    )
    (OUT / "social-preview.svg").write_text(svg(W, H, body, "kitlist"))

    # PNGs for places that don't take SVG (GitHub social preview, avatars)
    import cairosvg

    cairosvg.svg2png(url=str(OUT / "social-preview.svg"), write_to=str(OUT / "social-preview.png"))
    cairosvg.svg2png(
        url=str(OUT / "icon.svg"),
        write_to=str(OUT / "icon-512.png"),
        output_width=512,
        output_height=512,
    )
    print("wrote", ", ".join(sorted(p.name for p in OUT.iterdir())))


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
