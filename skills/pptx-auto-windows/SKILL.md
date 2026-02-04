---
name: pptx-auto-windows
description: Generate PPTX decks on Windows using bash and Python. Use when the user asks to auto-create slides, build a .pptx from a structured outline/spec, or convert HTML (optionally to PDF) before embedding into slides. Covers python-pptx workflows, template/theme reuse, and lightweight HTML-to-PDF rendering when available.
---

# Pptx Auto Windows

## Overview

Create .pptx decks on Windows with Python-only tooling, defaulting to `python-pptx` and a structured slide spec. Optionally render HTML to PDF first, then embed as full-bleed images if a renderer is available.

## Workflow

1. **Collect inputs**
Ask for:
- Slide outline and desired layout types (title, bullets, image, two-column)
- Theme preference and whether a template `.pptx` should be used
- Assets (images, logos) and target aspect ratio (16:9 or 4:3)
- Whether an HTML-first workflow is required

2. **Choose the build path**
- **Path A (default):** Build directly with `python-pptx` using a slide spec.
- **Path B (optional):** Generate HTML, render to PDF (if `weasyprint` is installed), then place each rendered page as a full-bleed image in PPTX. Use only if the user explicitly wants HTML-first output and accepts the renderer dependency.

3. **Generate slide spec**
Draft a JSON/YAML spec from the outline, confirm structure, then run `scripts/pptx_from_spec.py`.

4. **Build the deck**
Run the script, inspect the output, and iterate on layout or assets.

## Quick Start (Path A)

1. Create a spec (see `references/slide_spec.md`).
2. Run:

```bash
python scripts/pptx_from_spec.py --spec specs/demo.json --out output/demo.pptx --widescreen
```

## Optional HTML -> PDF -> PPTX (Path B)

1. Render HTML to PDF:

```bash
python scripts/html_to_pdf.py --html slides/index.html --out build/slides.pdf
```

2. Convert PDF pages to images using a tool the user already has (Poppler, ImageMagick, etc.).
3. Insert images into PPTX as full-bleed slides using `scripts/pptx_from_spec.py` with `type: image` slides.

## Scripts

- `scripts/pptx_from_spec.py`:
  - Build a PPTX from a JSON/YAML spec.
  - Supports `title`, `bullets`, `image`, and `two_col` slide types.
  - Optional `--template` to reuse theme layouts from an existing `.pptx`.

- `scripts/html_to_pdf.py`:
  - Render HTML to PDF with `weasyprint` if installed.
  - Fails with a clear install hint if the renderer is missing.

## References

- `references/slide_spec.md`: Spec format, examples, and layout notes.
- `references/dependencies.md`: Minimal dependency guidance for `python-pptx` and optional HTML-to-PDF rendering.
