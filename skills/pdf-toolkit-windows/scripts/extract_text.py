#!/usr/bin/env python
"""Extract text from a PDF to a .txt file."""

from __future__ import annotations

import argparse
import os

from pypdf import PdfReader


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inp", required=True, help="Input PDF")
    parser.add_argument("--out", required=True, help="Output text file")
    args = parser.parse_args()

    reader = PdfReader(args.inp)
    parts = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        parts.append(f"\n--- Page {i} ---\n")
        parts.append(text)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
