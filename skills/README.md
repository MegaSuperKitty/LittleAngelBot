# Skills directory

This folder holds skill packages. Each skill lives in its own subfolder and should include:

- SKILL.md (required)
- scripts/ (optional)
- references/ (optional)
- assets/ (optional)

SKILL.md should start with a YAML frontmatter block, e.g.:

---
name: my-skill
description: Short summary for discovery
when_to_use: When the user asks about X
allowed_tools: [bash]
---

# Skill Instructions
...full prompt...
