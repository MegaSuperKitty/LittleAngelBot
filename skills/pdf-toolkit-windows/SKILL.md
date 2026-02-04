---
name: pdf-toolkit-windows
description: Perform PDF operations on Windows using Python. Use for merging, splitting, rotating, extracting text, and stamping PDFs. Supports batch-safe scripts with pypdf and simple CLI inputs.
---

# Pdf Toolkit Windows

## Overview

Provide common PDF operations via small, reliable scripts based on `pypdf`.

## Tasks

- Merge PDFs
- Split by page ranges
- Rotate pages
- Extract text
- Stamp text watermark

## Quick Start

```bash
python scripts/merge_pdfs.py --out build/merged.pdf --inputs a.pdf b.pdf
```

## Scripts

- `scripts/merge_pdfs.py`
- `scripts/split_pdf.py`
- `scripts/rotate_pdf.py`
- `scripts/extract_text.py`
- `scripts/stamp_text.py`

## References

- `references/dependencies.md`
- `references/page_ranges.md`
