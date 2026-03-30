#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "segno>=1.6",
#   "pillow>=10.0",
# ]
# ///
"""Fancy on-brand QR code generator for Cascading Labs, QScrape, Yosoi, and VoidCrawl.

Renders QR codes with:
  - Circle/dot data modules with spacing
  - Rounded squircle finder patterns with circular inners
  - Concentric circle alignment patterns
  - Logo overlay at center

Usage:
    uv run gen_qr.py
"""

import base64
import io
import re
import subprocess
from pathlib import Path

import segno
from PIL import Image

SCRIPT_DIR = Path(__file__).parent
LOGOS_DIR  = SCRIPT_DIR.parent
OUT        = SCRIPT_DIR

# --- Brand color schemes per variant ---

BRAND_VARIANTS: dict[str, dict[str, dict[str, str]]] = {
    "cascading-labs": {
        "dark":       {"bg": "#0c2340", "fg": "#5ba4cf", "icon_bg": "#0c2340", "icon_fg": "#5ba4cf", "border": "#3d7eb5"},
        "light":      {"bg": "#e8f0f8", "fg": "#2a5f8a", "icon_bg": "#e8f0f8", "icon_fg": "#1a4a72", "border": "#2a5f8a"},
        "mono-dark":  {"bg": "#141414", "fg": "#ffffff", "icon_bg": "#141414", "icon_fg": "#ffffff", "border": "#ffffff"},
        "mono-light": {"bg": "#f5f5f5", "fg": "#000000", "icon_bg": "#f5f5f5", "icon_fg": "#000000", "border": "#000000"},
    },
    "qscrape": {
        "dark":       {"bg": "#1a0808", "fg": "#ef6464", "icon_bg": "#1a0808", "icon_fg": "#ef6464", "border": "#c94040"},
        "light":      {"bg": "#faf0f0", "fg": "#8b1a1a", "icon_bg": "#faf0f0", "icon_fg": "#a52a2a", "border": "#c94040"},
        "mono-dark":  {"bg": "#141414", "fg": "#ffffff", "icon_bg": "#141414", "icon_fg": "#ffffff", "border": "#ffffff"},
        "mono-light": {"bg": "#f5f5f5", "fg": "#000000", "icon_bg": "#f5f5f5", "icon_fg": "#000000", "border": "#000000"},
    },
    "yosoi": {
        "dark":       {"bg": "#2e3742", "fg": "#c4d4df", "icon_bg": "#2e3742", "icon_fg": "#c4d4df", "border": "#8fa3b3"},
        "light":      {"bg": "#e8ecf0", "fg": "#3a4855", "icon_bg": "#e8ecf0", "icon_fg": "#3a4855", "border": "#5a6e7e"},
        "mono-dark":  {"bg": "#141414", "fg": "#ffffff", "icon_bg": "#141414", "icon_fg": "#ffffff", "border": "#ffffff"},
        "mono-light": {"bg": "#f5f5f5", "fg": "#000000", "icon_bg": "#f5f5f5", "icon_fg": "#000000", "border": "#000000"},
    },
    "voidcrawl": {
        "dark":       {"bg": "#120a24", "fg": "#b07adf", "icon_bg": "#120a24", "icon_fg": "#b07adf", "border": "#7c4dbd"},
        "light":      {"bg": "#f0eaf8", "fg": "#4a2080", "icon_bg": "#f0eaf8", "icon_fg": "#4a2080", "border": "#6b3fa0"},
        "mono-dark":  {"bg": "#141414", "fg": "#ffffff", "icon_bg": "#141414", "icon_fg": "#ffffff", "border": "#ffffff"},
        "mono-light": {"bg": "#f5f5f5", "fg": "#000000", "icon_bg": "#f5f5f5", "icon_fg": "#000000", "border": "#000000"},
    },
}

VARIANTS = ["dark", "light", "mono-dark", "mono-light"]

# (output_dir, filename, URL, brand key, icon SVG relative to LOGOS_DIR or None → use brand logo)
TARGETS: list[tuple[str, str, str, str, str | None]] = [
    # Cascading Labs
    ("cascadinglabs",         "cascadinglabs", "https://cascadinglabs.com",                "cascading-labs", None),
    ("cascadinglabs/github",  "github",        "https://github.com/CascadingLabs",         "cascading-labs", "third-party/github.svg"),
    ("cascadinglabs/discord", "discord",       "https://discord.gg/w6bVujKphH",            "cascading-labs", "third-party/discord.svg"),
    # QScrape
    ("qscrape",               "qscrape",       "https://qscrape.dev",                      "qscrape",        None),
    ("qscrape/github",        "github",        "https://github.com/CascadingLabs/QScrape", "qscrape",        "third-party/github.svg"),
    ("qscrape/discord",       "discord",       "https://discord.gg/5WZNzFZtgb",            "qscrape",        "third-party/discord.svg"),
    # Yosoi
    ("yosoi",                 "yosoi",         "https://cascadinglabs.com/yosoi",           "yosoi",          None),
    ("yosoi/github",          "github",        "https://github.com/CascadingLabs/Yosoi",   "yosoi",          "third-party/github.svg"),
    ("yosoi/discord",         "discord",       "https://discord.gg/YreV3CzxsE",            "yosoi",          "third-party/discord.svg"),
    # VoidCrawl
    ("voidcrawl",             "voidcrawl",     "https://cascadinglabs.com/voidcrawl/",         "voidcrawl",    None),
    ("voidcrawl/github",      "github",        "https://github.com/CascadingLabs/VoidCrawl",  "voidcrawl",    "third-party/github.svg"),
    ("voidcrawl/discord",     "discord",       "https://discord.gg/ftykDhmAQN",                "voidcrawl",    "third-party/discord.svg"),
]

MODULE_PX  = 20      # px per module in final PNG
SVG_SCALE  = 10      # SVG user units per module
DOT_RATIO  = 0.80    # dot diameter as fraction of module size
LOGO_RATIO = 0.25    # logo occupies 25% of QR width
ICON_SIZE  = 500     # px for rendered third-party icons
QUIET_ZONE = 4       # modules of quiet zone around QR

# Alignment pattern positions from the QR spec (version -> list of row/col positions)
ALIGNMENT_POSITIONS: dict[int, list[int]] = {
    1:  [],
    2:  [6, 18],
    3:  [6, 22],
    4:  [6, 26],
    5:  [6, 30],
    6:  [6, 34],
    7:  [6, 22, 38],
    8:  [6, 24, 42],
    9:  [6, 26, 46],
    10: [6, 28, 50],
    11: [6, 30, 54],
    12: [6, 32, 58],
    13: [6, 34, 62],
    14: [6, 26, 46, 66],
    15: [6, 26, 48, 70],
    16: [6, 26, 50, 74],
    17: [6, 30, 54, 78],
    18: [6, 30, 56, 82],
    19: [6, 30, 58, 86],
    20: [6, 34, 62, 90],
    21: [6, 28, 50, 72, 94],
    22: [6, 26, 50, 74, 98],
    23: [6, 30, 54, 78, 102],
    24: [6, 28, 54, 80, 106],
    25: [6, 32, 58, 84, 110],
    26: [6, 30, 58, 86, 114],
    27: [6, 34, 62, 90, 118],
    28: [6, 26, 50, 74, 98, 122],
    29: [6, 30, 54, 78, 102, 126],
    30: [6, 26, 52, 78, 104, 130],
    31: [6, 30, 56, 82, 108, 134],
    32: [6, 34, 60, 86, 112, 138],
    33: [6, 30, 58, 86, 114, 142],
    34: [6, 34, 62, 90, 118, 146],
    35: [6, 30, 54, 78, 102, 126, 150],
    36: [6, 24, 50, 76, 102, 128, 154],
    37: [6, 28, 54, 80, 106, 132, 158],
    38: [6, 32, 58, 84, 110, 136, 162],
    39: [6, 26, 54, 82, 110, 138, 166],
    40: [6, 30, 58, 86, 114, 142, 170],
}


def _make_qr(url: str) -> segno.QRCode:
    return segno.make(url, error="h", micro=False)


def _get_matrix(qr: segno.QRCode) -> list[list[int]]:
    """Extract the boolean module matrix from a segno QRCode."""
    return [list(row) for row in qr.matrix]


def _finder_rects(n: int) -> list[tuple[int, int]]:
    """Return (row, col) top-left origins of the three 7x7 finder patterns,
    plus the 1-module separator zone (so 8/9 module region to clear)."""
    return [(0, 0), (0, n - 7), (n - 7, 0)]


def _finder_clear_regions(n: int) -> list[tuple[int, int, int, int]]:
    """Return (r, c, h, w) rects that cover each finder + its separator.
    These are the areas we'll blank before drawing custom finders."""
    return [
        (0, 0, 8, 8),              # top-left: finder 7x7 + separator right & bottom
        (0, n - 8, 8, 8),          # top-right: finder + separator left & bottom
        (n - 8, 0, 8, 8),          # bottom-left: finder + separator right & top
    ]


def _alignment_centers(version: int, n: int) -> list[tuple[int, int]]:
    """Return (row, col) centers of alignment patterns from the spec table."""
    positions = ALIGNMENT_POSITIONS.get(version, [])
    if not positions:
        return []
    centers = []
    for r in positions:
        for c in positions:
            # Skip if overlapping with finder patterns + separators
            if r <= 8 and c <= 8:           # top-left
                continue
            if r <= 8 and c >= n - 8:       # top-right
                continue
            if r >= n - 8 and c <= 8:       # bottom-left
                continue
            centers.append((r, c))
    return centers


def _render_finder_svg(x: float, y: float, s: float, fg: str, bg: str) -> str:
    """Render a finder pattern: rounded outer rect + bg ring + circle center."""
    size = 7 * s
    rx = s * 1.0
    parts = []
    # Outer rounded rect
    parts.append(
        f'<rect x="{x}" y="{y}" width="{size}" height="{size}" '
        f'rx="{rx}" fill="{fg}"/>'
    )
    # Inner bg ring (5x5)
    inner = 5 * s
    off = s
    inner_rx = s * 0.6
    parts.append(
        f'<rect x="{x + off}" y="{y + off}" width="{inner}" height="{inner}" '
        f'rx="{inner_rx}" fill="{bg}"/>'
    )
    # Center circle (3x3)
    cr = s * 1.35
    ccx = x + size / 2
    ccy = y + size / 2
    parts.append(f'<circle cx="{ccx}" cy="{ccy}" r="{cr}" fill="{fg}"/>')
    return "\n  ".join(parts)


def _render_alignment_svg(cx: float, cy: float, s: float, fg: str, bg: str) -> str:
    """Render an alignment pattern as concentric circles."""
    parts = []
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{s * 2.0}" fill="{fg}"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{s * 1.3}" fill="{bg}"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{s * 0.65}" fill="{fg}"/>')
    return "\n  ".join(parts)


def _logo_region(n: int) -> set[tuple[int, int]]:
    """Return (row, col) cells that the center logo covers — skip dots here."""
    logo_modules = int(n * LOGO_RATIO) + 2
    half = logo_modules // 2
    center = n // 2
    coords = set()
    for r in range(center - half, center + half + 1):
        for c in range(center - half, center + half + 1):
            if 0 <= r < n and 0 <= c < n:
                coords.add((r, c))
    return coords


def _build_fancy_svg(
    qr: segno.QRCode,
    fg: str,
    bg: str,
    scale: float,
    logo_b64: str | None = None,
) -> str:
    """Build fancy SVG: all data as dots, custom finder & alignment patterns."""
    matrix = _get_matrix(qr)
    n = len(matrix)
    version = qr.version
    quiet = QUIET_ZONE
    total = (n + quiet * 2) * scale
    offset = quiet * scale
    s = scale

    dot_r = s * DOT_RATIO / 2

    # Regions to exclude from dot rendering
    finder_clear = _finder_clear_regions(n)
    finder_cells: set[tuple[int, int]] = set()
    for r0, c0, h, w in finder_clear:
        for dr in range(h):
            for dc in range(w):
                rr, cc = r0 + dr, c0 + dc
                if 0 <= rr < n and 0 <= cc < n:
                    finder_cells.add((rr, cc))

    align_centers = _alignment_centers(version, n)
    alignment_cells: set[tuple[int, int]] = set()
    for cr, cc in align_centers:
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                rr, ccol = cr + dr, cc + dc
                if 0 <= rr < n and 0 <= ccol < n:
                    alignment_cells.add((rr, ccol))

    logo_cells = _logo_region(n) if logo_b64 else set()

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="{total}" '
        f'viewBox="0 0 {total} {total}">',
        f'  <rect width="{total}" height="{total}" fill="{bg}"/>',
    ]

    # --- Data + timing modules as dots ---
    for r in range(n):
        for c in range(n):
            if (r, c) in finder_cells:
                continue
            if (r, c) in alignment_cells:
                continue
            if (r, c) in logo_cells:
                continue
            if matrix[r][c] & 1:  # dark module (check bit 0)
                cx = offset + c * s + s / 2
                cy = offset + r * s + s / 2
                parts.append(
                    f'  <circle cx="{cx}" cy="{cy}" r="{dot_r}" fill="{fg}"/>'
                )

    # --- Finder patterns: clear area then draw custom ---
    finder_origins = [(0, 0), (0, n - 7), (n - 7, 0)]
    for r0, c0 in finder_origins:
        parts.append("  " + _render_finder_svg(
            offset + c0 * s, offset + r0 * s, s, fg, bg
        ))

    # --- Alignment patterns: clear area then draw custom ---
    for cr, cc in align_centers:
        acx = offset + cc * s + s / 2
        acy = offset + cr * s + s / 2
        parts.append("  " + _render_alignment_svg(acx, acy, s, fg, bg))

    # --- Logo overlay ---
    if logo_b64:
        logo_size = n * s * LOGO_RATIO
        lx = offset + (n * s - logo_size) / 2
        ly = offset + (n * s - logo_size) / 2
        parts.append(
            f'  <image x="{lx:.2f}" y="{ly:.2f}" '
            f'width="{logo_size:.2f}" height="{logo_size:.2f}" '
            f'preserveAspectRatio="xMidYMid meet" '
            f'href="data:image/png;base64,{logo_b64}"/>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


# --- Logo loading ---

def _brand_logo_png(brand: str, variant: str) -> Image.Image | None:
    p = LOGOS_DIR / brand / variant / "logo.png"
    if not p.exists():
        p = LOGOS_DIR / brand / "dark" / "logo.png"
    return Image.open(p).convert("RGBA") if p.exists() else None


def _third_party_icon_png(svg_rel: str, brand: str, variant: str) -> Image.Image | None:
    cfg = BRAND_VARIANTS[brand][variant]
    fg, bg = cfg["icon_fg"], cfg["icon_bg"]
    border = cfg["border"]

    svg_path = LOGOS_DIR / svg_rel
    if not svg_path.exists():
        return None

    raw = svg_path.read_text()
    path_match = re.search(r'<path\b[^>]*\bd="([^"]+)"', raw)
    if not path_match:
        return None
    path_data = path_match.group(1)

    pad = 50
    area = ICON_SIZE - 2 * pad
    sc = area / 24
    border_opacity = "0.5" if variant in ("dark", "light") else "0.4"

    styled = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{ICON_SIZE}" height="{ICON_SIZE}" viewBox="0 0 {ICON_SIZE} {ICON_SIZE}">
  <rect width="{ICON_SIZE}" height="{ICON_SIZE}" rx="24" fill="{bg}"/>
  <rect x="14" y="14" width="472" height="472" rx="18" fill="none" stroke="{border}" stroke-width="4" opacity="{border_opacity}"/>
  <g transform="translate({pad}, {pad}) scale({sc:.6f})">
    <path fill="{fg}" d="{path_data}"/>
  </g>
</svg>"""

    result = subprocess.run(
        ["rsvg-convert", "-w", str(ICON_SIZE), "-h", str(ICON_SIZE)],
        input=styled.encode(),
        capture_output=True,
    )
    if result.returncode != 0:
        print(f"    WARNING: rsvg-convert failed for {svg_rel} ({variant}): {result.stderr.decode().strip()}")
        return None
    return Image.open(io.BytesIO(result.stdout)).convert("RGBA")


def _get_logo(brand: str, icon_svg: str | None, variant: str) -> Image.Image | None:
    if icon_svg:
        return _third_party_icon_png(icon_svg, brand, variant)
    return _brand_logo_png(brand, variant)


def _logo_to_b64(logo: Image.Image | None) -> str | None:
    if logo is None:
        return None
    buf = io.BytesIO()
    logo.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _variant_suffix(variant: str) -> str:
    return "" if variant == "dark" else f"-{variant}"


def _svg_to_png(svg_text: str, width: int) -> Image.Image:
    result = subprocess.run(
        ["rsvg-convert", "-w", str(width), "-h", str(width)],
        input=svg_text.encode(),
        capture_output=True,
        check=True,
    )
    return Image.open(io.BytesIO(result.stdout)).convert("RGBA")


def gen(out_path: str, filename: str, url: str, brand: str, icon_svg: str | None, variant: str) -> None:
    cfg = BRAND_VARIANTS[brand][variant]
    qr = _make_qr(url)

    out_dir = OUT / out_path
    out_dir.mkdir(parents=True, exist_ok=True)

    logo = _get_logo(brand, icon_svg, variant)
    logo_b64 = _logo_to_b64(logo)

    svg_text = _build_fancy_svg(qr, cfg["fg"], cfg["bg"], SVG_SCALE, logo_b64)

    suffix = _variant_suffix(variant)

    (out_dir / f"{filename}{suffix}.svg").write_text(svg_text, encoding="utf-8")
    print(f"    {out_path}/{filename}{suffix}.svg")

    n = len(_get_matrix(qr))
    png_width = (n + QUIET_ZONE * 2) * MODULE_PX
    img = _svg_to_png(svg_text, png_width)
    img.save(out_dir / f"{filename}{suffix}.png")
    print(f"    {out_path}/{filename}{suffix}.png")


def main() -> None:
    total = 0
    for out_path, filename, url, brand, icon_svg in TARGETS:
        label = icon_svg or "brand logo"
        print(f"[{brand}] {out_path}/{filename}  ({label})")
        for variant in VARIANTS:
            print(f"  {variant}:")
            gen(out_path, filename, url, brand, icon_svg, variant)
            total += 2
    print(f"\nDone — {total} files in {OUT}")


if __name__ == "__main__":
    main()
