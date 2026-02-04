#!/usr/bin/env python
"""Render HTML to PDF using WeasyPrint if available."""

from __future__ import annotations

import argparse
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", required=True, help="Input HTML file")
    parser.add_argument("--out", required=True, help="Output PDF file")
    args = parser.parse_args()

    try:
        from weasyprint import HTML  # type: ignore
    except Exception:
        print(
            "WeasyPrint is not installed. Install with: python -m pip install weasyprint",
            file=sys.stderr,
        )
        return 1

    html_path = os.path.abspath(args.html)
    out_path = os.path.abspath(args.out)

    with open(html_path, "r", encoding="utf-8") as f:
        html_text = f.read()

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    HTML(string=html_text, base_url=os.path.dirname(html_path)).write_pdf(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
