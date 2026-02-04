#!/usr/bin/env python
"""Merge multiple PDFs into one."""

from __future__ import annotations

import argparse
import os
from pypdf import PdfWriter


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="Output PDF")
    parser.add_argument("--inputs", nargs="+", required=True, help="Input PDFs in order")
    args = parser.parse_args()

    writer = PdfWriter()
    for path in args.inputs:
        writer.append(path)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "wb") as f:
        writer.write(f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
