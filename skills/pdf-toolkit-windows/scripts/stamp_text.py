#!/usr/bin/env python
"""Add a simple text stamp to each page using a PDF overlay."""

from __future__ import annotations

import argparse
import os
from io import BytesIO

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def make_stamp(text: str, width: float, height: float) -> BytesIO:
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(width, height))
    c.setFont("Helvetica", 24)
    c.setFillGray(0.5, 0.5)
    c.saveState()
    c.translate(width / 2, height / 2)
    c.rotate(30)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    c.save()
    packet.seek(0)
    return packet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inp", required=True, help="Input PDF")
    parser.add_argument("--out", required=True, help="Output PDF")
    parser.add_argument("--text", required=True, help="Stamp text")
    args = parser.parse_args()

    reader = PdfReader(args.inp)
    writer = PdfWriter()

    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        stamp_pdf = PdfReader(make_stamp(args.text, width, height))
        page.merge_page(stamp_pdf.pages[0])
        writer.add_page(page)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "wb") as f:
        writer.write(f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
