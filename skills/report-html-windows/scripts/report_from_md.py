#!/usr/bin/env python
"""Render a report HTML from Markdown using a Jinja2 template."""

from __future__ import annotations

import argparse
import os

import markdown
from jinja2 import Environment, FileSystemLoader


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--md", required=True, help="Input Markdown file")
    parser.add_argument("--out", required=True, help="Output HTML path")
    parser.add_argument("--title", default="Report", help="Report title")
    parser.add_argument("--accent", default="#0b5fff", help="Accent color")
    parser.add_argument("--logo", help="Optional logo image path")
    args = parser.parse_args()

    md_path = os.path.abspath(args.md)
    out_path = os.path.abspath(args.out)

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    body_html = markdown.markdown(md_text, extensions=["tables", "fenced_code", "footnotes"])

    template_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report_template.html")

    html = template.render(
        title=args.title,
        body=body_html,
        accent=args.accent,
        logo_path=os.path.abspath(args.logo) if args.logo else "",
    )

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
