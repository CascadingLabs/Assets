# Cascading Labs — Brand Assets

Visual identity assets for Cascading Labs and its projects: **QScrape** and **Yosoi**.

## Design system

Every logo follows a **periodic table element tile** motif — a rounded rectangle with a double border, an element symbol at center, and metadata at the corners.

### Anatomy of a tile

```
┌──────────────────────────┐
│  ┌────────────────────┐  │  ← double border (bright outer, faint inner)
│  │ 404          310.26│  │
│  │                    │  │
│  │        Qs          │  │  ← element symbol, centered
│  │                    │  │
│  │      QScrape       │  │  ← project name, centered below symbol
│  └────────────────────┘  │
└──────────────────────────┘
```

| Position | Content | Meaning |
|---|---|---|
| Top-left | Atomic number | A project-specific identifier. QScrape uses **404** (HTTP 404 — the scraper's natural enemy). Cascading Labs uses **0** (the origin). Yosoi uses **3** (third project). |
| Top-right | Float value | A version or build signature rendered as a decimal. Cascading Labs: **24.26**, QScrape: **310.26**, Yosoi: **812.25**. These are arbitrary but stable — treat them like atomic mass. |
| Center | Symbol | One or two characters drawn from the project name, styled like a chemical symbol (leading uppercase, optional lowercase). **Qs** = QScrape, **Cl** = Cascading Labs, **Ys** = Yosoi. |
| Below center | Name | The full project name in regular weight. |

### Double border

The outer border is bright and solid (3.5 px stroke). The inner border is inset by 12 px, thinner (1 px), and drawn at 35% opacity. This creates depth without adding visual noise.

### Typography

**Font:** [Inter](https://rsms.me/inter/) — loaded via Google Fonts `@import` in SVGs. The font stack falls back to `system-ui, sans-serif` for headless rendering.

| Element | Weight | Size |
|---|---|---|
| Symbol | 800 (ExtraBold) | 200 |
| Atomic number / float | 700 (Bold) | 26 |
| Project name | 400 (Regular) | 28 |

All text is horizontally centered (`text-anchor="middle"`) except the atomic number (left-aligned) and the float (right-aligned via `text-anchor="end"`).

### Color palettes

Each project has its own background + accent pair. Borders use a mid-tone between the two.

| Project | Background | Accent | Border |
|---|---|---|---|
| Cascading Labs | `#0c2340` | `#5ba4cf` | `#3d7eb5` |
| QScrape | `#1a0808` | `#ef6464` | `#c94040` |
| Yosoi | `#2e3742` | `#c4d4df` | `#8fa3b3` |

Light-mode variants invert the relationship: a pale tinted background with dark accent text. Monochrome variants use pure black (`#141414`) or off-white (`#f5f5f5`) backgrounds with white or black foregrounds.

## File structure

```
Assets/
├── cascading-labs/
│   ├── logo.svg              ← canonical (dark)
│   ├── logo.png              ← 512×512 raster
│   ├── logo.jpg
│   ├── logo-dark.*           ← explicit dark variant (same as logo.*)
│   ├── logo-light.*          ← light background variant
│   ├── logo-mono-dark.*      ← white on black
│   └── logo-mono-light.*     ← black on white
├── qscrape/
│   └── (same structure)
├── yosoi/
│   └── (same structure)
├── qr-codes/
│   ├── gen_qr.py             ← QR code generator script
│   ├── cascadinglabs/
│   │   ├── cascadinglabs.png
│   │   └── cascadinglabs.svg
│   ├── discord/
│   ├── github/
│   ├── qscrape/
│   └── yosoi/
├── third-party/
│   ├── discord.svg           ← simple-icons source
│   └── github.svg
├── pyproject.toml
└── uv.lock
```

## Reproduction steps

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Inkscape](https://inkscape.org/) (SVG rasterizer, CLI)
- [ImageMagick](https://imagemagick.org/) (`magick` command)
- Optionally, the **Inter** font installed locally (`pacman -S inter-font` on Arch) for pixel-perfect PNG exports. Without it, Inkscape falls back to the system sans-serif.

### 1. Export logos from SVG to PNG and JPG

Each project directory contains SVG source files. To re-export all raster variants at 512x512:

```bash
cd Assets

for project in qscrape cascading-labs yosoi; do
  for variant in "" "-dark" "-light" "-mono-dark" "-mono-light"; do
    svg="$project/logo${variant}.svg"
    [ -f "$svg" ] || continue
    inkscape "$svg" \
      --export-type=png \
      --export-filename="$project/logo${variant}.png" \
      --export-width=512 --export-height=512
    magick "$project/logo${variant}.png" -quality 90 "$project/logo${variant}.jpg"
  done
done
```

### 2. Regenerate QR codes

QR codes embed the project logo at center using `segno` (error correction level H, 30% capacity) with `pillow` for the overlay. The generator uses brand colors from the palette table above.

```bash
cd Assets/qr-codes
uv run gen_qr.py
```

This produces PNG + SVG pairs in subdirectories (`cascadinglabs/`, `discord/`, `github/`, `qscrape/`, `yosoi/`).

### 3. Add or modify a logo

1. Edit the SVG source directly — all logos follow the same template structure (see `qscrape/logo.svg` as reference).
2. Re-run the export loop from step 1 for that project.
3. Re-run `gen_qr.py` from step 2 if the default logo (`logo.png`) changed, since QR codes embed it.

### SVG template

To create a new project logo, copy this template and fill in the values:

```xml
<svg width="100%" viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&amp;display=swap');
    </style>
  </defs>

  <rect x="0" y="0" width="500" height="500" fill="BACKGROUND"/>

  <rect x="22" y="22" width="456" height="456" rx="28"
    fill="none" stroke="BORDER" stroke-width="3.5"/>
  <rect x="34" y="34" width="432" height="432" rx="20"
    fill="none" stroke="BORDER" stroke-width="1" opacity="0.35"/>

  <text x="58" y="82" font-family="Inter, system-ui, sans-serif"
    font-size="26" font-weight="700" fill="ACCENT" opacity="0.8"
  >NUMBER</text>

  <text x="442" y="82" font-family="Inter, system-ui, sans-serif"
    font-size="26" font-weight="700" fill="ACCENT" opacity="0.8"
    text-anchor="end"
  >FLOAT</text>

  <text x="250" y="310" font-family="Inter, system-ui, sans-serif"
    font-size="200" font-weight="800" fill="ACCENT" opacity="0.95"
    text-anchor="middle"
  >SYMBOL</text>

  <text x="250" y="382" font-family="Inter, system-ui, sans-serif"
    font-size="28" font-weight="400" fill="ACCENT" opacity="0.75"
    text-anchor="middle" letter-spacing="3"
  >PROJECT NAME</text>
</svg>
```

Replace `BACKGROUND`, `BORDER`, `ACCENT`, `NUMBER`, `FLOAT`, `SYMBOL`, and `PROJECT NAME` with your values.
