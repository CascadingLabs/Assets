#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "segno>=1.6",
#   "pillow>=10.0",
# ]
# ///
"""On-brand QR code generator for Cascading Labs, QScrape, and Yosoi.

Generates QR codes in all color variants (dark, light, mono-dark, mono-light)
for each target. Brand logos embed the matching logo variant; third-party icons
(discord, github) get the color scheme applied directly.

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

SCRIPT_DIR = Path(__file__).parent   # Assets/qr-codes/
LOGOS_DIR  = SCRIPT_DIR.parent       # Assets/
OUT        = SCRIPT_DIR              # QR files live alongside this script

# Brand color schemes per variant
# Each variant has: bg (QR light modules), fg (QR dark modules), icon_bg, icon_fg
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
}

VARIANTS = ["dark", "light", "mono-dark", "mono-light"]

# (output name, URL, brand key, icon SVG relative to LOGOS_DIR or None → use brand logo)
TARGETS: list[tuple[str, str, str, str | None]] = [
    ("discord",       "https://discord.gg/7jgEzfbTWY",    "cascading-labs", "third-party/discord.svg"),
    ("github",        "https://github.com/CascadingLabs",  "cascading-labs", "third-party/github.svg"),
    ("cascadinglabs", "https://cascadinglabs.com",          "cascading-labs", None),
    ("qscrape",       "https://qscrape.dev",                "qscrape",        None),
    ("yosoi",         "https://cascadinglabs.com/yosoi",    "yosoi",          None),
]

PNG_SCALE  = 20    # px per QR module
SVG_SCALE  = 10    # user units per QR module
LOGO_RATIO = 0.25  # logo occupies 25% of QR width (within H-level 30% error capacity)
ICON_SIZE  = 500   # px for rendered third-party icons


def _make_qr(url: str) -> segno.QRCode:
    return segno.make(url, error="h", micro=False)


def _brand_logo_png(brand: str, variant: str) -> Image.Image | None:
    """Load the brand's logo PNG for the given variant."""
    p = LOGOS_DIR / brand / f"logo-{variant}.png"
    if not p.exists():
        # Fall back to default logo.png
        p = LOGOS_DIR / brand / "logo.png"
    return Image.open(p).convert("RGBA") if p.exists() else None


def _third_party_icon_png(svg_rel: str, brand: str, variant: str) -> Image.Image | None:
    """Render a simple-icon SVG with variant colors, styled to match the brand logo tiles."""
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

    # simple-icons use a 24x24 viewBox; scale to fill a padded area inside 500x500
    pad = 50
    area = ICON_SIZE - 2 * pad
    scale = area / 24

    # Border opacity: bright for color variants, subdued for mono
    border_opacity = "0.5" if variant in ("dark", "light") else "0.4"

    styled = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{ICON_SIZE}" height="{ICON_SIZE}" viewBox="0 0 {ICON_SIZE} {ICON_SIZE}">
  <rect width="{ICON_SIZE}" height="{ICON_SIZE}" rx="24" fill="{bg}"/>
  <rect x="14" y="14" width="472" height="472" rx="18" fill="none" stroke="{border}" stroke-width="4" opacity="{border_opacity}"/>
  <g transform="translate({pad}, {pad}) scale({scale:.6f})">
    <path fill="{fg}" d="{path_data}"/>
  </g>
</svg>"""

    result = subprocess.run(
        ["rsvg-convert", "-w", str(ICON_SIZE), "-h", str(ICON_SIZE)],
        input=styled.encode(),
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return Image.open(io.BytesIO(result.stdout)).convert("RGBA")


def _get_logo(brand: str, icon_svg: str | None, variant: str) -> Image.Image | None:
    if icon_svg:
        return _third_party_icon_png(icon_svg, brand, variant)
    return _brand_logo_png(brand, variant)


def _overlay_logo(base: Image.Image, logo: Image.Image) -> Image.Image:
    size = int(base.width * LOGO_RATIO)
    logo = logo.resize((size, size), Image.LANCZOS)
    x = (base.width - size) // 2
    y = (base.height - size) // 2
    out = base.copy()
    out.paste(logo, (x, y), logo)
    return out


def _variant_suffix(variant: str) -> str:
    """Return file suffix: '' for dark (default), '-light', '-mono-dark', '-mono-light'."""
    return "" if variant == "dark" else f"-{variant}"


def gen_png(name: str, url: str, brand: str, icon_svg: str | None, variant: str) -> None:
    cfg = BRAND_VARIANTS[brand][variant]
    qr = _make_qr(url)

    out_dir = OUT / name
    out_dir.mkdir(parents=True, exist_ok=True)

    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=PNG_SCALE, dark=cfg["fg"], light=cfg["bg"])
    buf.seek(0)
    img = Image.open(buf).convert("RGBA")

    logo = _get_logo(brand, icon_svg, variant)
    if logo:
        img = _overlay_logo(img, logo)

    suffix = _variant_suffix(variant)
    img.save(out_dir / f"{name}{suffix}.png")
    print(f"    {name}/{name}{suffix}.png")


def gen_svg(name: str, url: str, brand: str, icon_svg: str | None, variant: str) -> None:
    cfg = BRAND_VARIANTS[brand][variant]
    qr = _make_qr(url)

    buf = io.BytesIO()
    qr.save(buf, kind="svg", scale=SVG_SCALE, dark=cfg["fg"], light=cfg["bg"])
    svg = buf.getvalue().decode("utf-8")

    m_w = re.search(r'<svg[^>]+\bwidth="([\d.]+)"', svg)
    m_h = re.search(r'<svg[^>]+\bheight="([\d.]+)"', svg)
    if m_w and m_h:
        w, h = float(m_w.group(1)), float(m_h.group(1))
    else:
        modules = qr.symbol_size()[0]
        w = h = float(modules * SVG_SCALE)

    out_dir = OUT / name
    out_dir.mkdir(parents=True, exist_ok=True)

    logo = _get_logo(brand, icon_svg, variant)
    if logo:
        png_buf = io.BytesIO()
        logo.save(png_buf, format="PNG")
        b64 = base64.b64encode(png_buf.getvalue()).decode()

        logo_size = w * LOGO_RATIO
        lx = (w - logo_size) / 2
        ly = (h - logo_size) / 2
        img_tag = (
            f'  <image x="{lx:.2f}" y="{ly:.2f}" '
            f'width="{logo_size:.2f}" height="{logo_size:.2f}" '
            f'preserveAspectRatio="xMidYMid meet" '
            f'href="data:image/png;base64,{b64}"/>\n'
        )
        svg = svg.replace("</svg>", img_tag + "</svg>")

    suffix = _variant_suffix(variant)
    (out_dir / f"{name}{suffix}.svg").write_text(svg, encoding="utf-8")
    print(f"    {name}/{name}{suffix}.svg")


def main() -> None:
    total = 0
    for name, url, brand, icon_svg in TARGETS:
        label = icon_svg or "brand logo"
        print(f"[{brand}] {name}  ({label})")
        for variant in VARIANTS:
            print(f"  {variant}:")
            gen_png(name, url, brand, icon_svg, variant)
            gen_svg(name, url, brand, icon_svg, variant)
            total += 2
    print(f"\nDone — {total} files in {OUT}")


if __name__ == "__main__":
    main()
