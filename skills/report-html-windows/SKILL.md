---
name: report-html-windows
description: Create report-style HTML on Windows using Python. Use when the user asks to draft a report, generate HTML from an outline/markdown, or produce a shareable report with sections, headings, and citations. Default output is HTML.
---

# Report Html Windows

## Overview

Generate report HTML from an outline or Markdown. Default output is HTML using `markdown` + Jinja2 template.

## Workflow

1. **Collect inputs**
Ask for:
- Topic, audience, and tone
- Sections and bullet points
- Branding assets (logo, colors) and page size
- Sources to cite (URLs or bibliographic entries)

2. **Draft the content**
Write the report in Markdown using headings and lists.
Always include citations in the body and a references section.
Use a simple, consistent format so the model won’t “forget” how to cite:

- **Inline numeric citations** after claims: `……事实陈述[1]`
- **References section** at the end:
  - `## 参考资料`
  - `[1] 标题 - URL`
  - `[2] 标题 - URL`

Example:

```markdown
年画在清代达到鼎盛。[1]

## 参考资料
[1] 滩头年画的故事 - https://www.ihchina.cn/news_1_details/10963.html
```

3. **Render to HTML**
Use `scripts/report_from_md.py` to convert Markdown to styled HTML.

4. **Review and iterate**
Adjust sections, styling, and assets as needed.

## Citation Rules

Use numeric inline citations and a references section (see example above). Do not omit citations for factual claims.

## Quick Start

```bash
python scripts/report_from_md.py --md reports/draft.md --out build/report.html --title "Quarterly Report"
```

## Scripts

- `scripts/report_from_md.py`:
  - Markdown -> HTML
  - Uses a Jinja2 HTML template in `assets/report_template.html`

## References

- `references/report_format.md`: Suggested structure and content outline.
- `references/dependencies.md`: Required and optional dependencies.
