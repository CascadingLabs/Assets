# Assets Agent Guide

## Project overview

Assets is the Cascading Labs brand-assets repository: canonical logos, design tokens, QR codes, and reusable repo templates for the ecosystem.

## Read first

- this file
- `README.md`
- relevant assets or template directories before editing

## Working rules

- Preserve canonical brand consistency across projects and variants.
- Prefer editing source SVG/template files before regenerated raster derivatives.
- Keep project-specific asset trees and naming conventions aligned with the README.
- Do not hand-edit generated PNG/JPG/ICO/QR outputs when the documented generator flow should be used instead.

## Key commands

- Follow the reproduction commands in `README.md` for SVG rasterization and QR generation.
- Use `uv` for Python tooling in this repo.

## Repository map

- `global.css` — canonical design tokens
- project asset directories — logos and variants
- `qr-codes/` — QR generator and generated outputs
- `templates/` — reusable contribution/config templates
- `third-party/` — external source assets

## Architecture and constraints

This repo is a source-of-truth asset library. Source assets, generated derivatives, and shared templates should stay clearly separated so downstream repos can reproduce outputs consistently.

## Validation

For asset changes, validate the relevant reproduction flow from `README.md` and inspect generated outputs. For template changes, review the affected template files directly and keep them generic.
