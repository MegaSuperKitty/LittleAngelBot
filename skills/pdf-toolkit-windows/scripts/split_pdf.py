#!/usr/bin/env python
"""Split a PDF into a new PDF by page ranges."""

from __future__ import annotations

import argparse
import os
from typing import Iterable

from pypdf import PdfReader, PdfWriter


def parse_ranges(ranges: str, max_pages: int) -> Iterable[int]:
    pages = set()
    for part in ranges.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start = int(start_s)
            end = int(end_s)
            for p in range(start, end + 1):
                if 1 <= p <= max_pages:
                    pages.add(p)
        else:
            p = int(part)
            if 1 <= p <= max_pages:
                pages.add(p)
    return [p - 1 for p in sorted(pages)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inp", required=True, help="Input PDF")
    parser.add_argument("--out", required=True, help="Output PDF")
    parser.add_argument("--pages", required=True, help="Page ranges, 1-based, e.g. 1-3,5")
    args = parser.parse_args()

    reader = PdfReader(args.inp)
    writer = PdfWriter()

    for idx in parse_ranges(args.pages, len(reader.pages)):
        writer.add_page(reader.pages[idx])

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "wb") as f:
        writer.write(f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
