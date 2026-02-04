#!/usr/bin/env python
"""Rotate all pages in a PDF."""

from __future__ import annotations

import argparse
import os

from pypdf import PdfReader, PdfWriter


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inp", required=True, help="Input PDF")
    parser.add_argument("--out", required=True, help="Output PDF")
    parser.add_argument("--deg", type=int, default=90, help="Rotation degrees (90, 180, 270)")
    args = parser.parse_args()

    reader = PdfReader(args.inp)
    writer = PdfWriter()

    for page in reader.pages:
        page.rotate(args.deg)
        writer.add_page(page)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "wb") as f:
        writer.write(f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
