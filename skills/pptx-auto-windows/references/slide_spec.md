# Slide Spec

Use a JSON (preferred) or YAML file with this shape:

```json
{
  "title": "Deck Title",
  "slides": [
    {
      "type": "title",
      "title": "Main Title",
      "subtitle": "Optional subtitle"
    },
    {
      "type": "bullets",
      "title": "Key Points",
      "bullets": [
        "First point",
        {"text": "Indented point", "level": 1},
        "Another top-level point"
      ]
    },
    {
      "type": "two_col",
      "title": "Pros / Cons",
      "left": ["Pro 1", "Pro 2"],
      "right": ["Con 1", "Con 2"]
    },
    {
      "type": "image",
      "title": "Architecture",
      "image": "assets/diagram.png",
      "caption": "Optional caption"
    }
  ]
}
```

## Notes

- `type` values: `title`, `bullets`, `two_col`, `image`.
- `bullets` supports strings or objects with `text` and `level` (indent level starts at 0).
- `image` slides place the image full-bleed. Use a 16:9 image if the deck is widescreen.
- Provide `--template path/to/template.pptx` to inherit fonts and theme.
