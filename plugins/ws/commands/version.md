---
description: Display ws plugin version and recent changelog entries
allowed-tools: [Read]
---

<objective>
Display the current version of the ws plugin along with recent release changes from the changelog.

This helps users understand what version they're running and what features/fixes are included.
</objective>

<context>
Plugin metadata: @plugins/ws/plugin.json
Changelog: @plugins/ws/CHANGELOG.md
</context>

<process>
1. Read the plugin.json to get the current version number
2. Read the CHANGELOG.md to get recent release notes
3. Present the information in a clean, readable format:
   - Version number prominently displayed
   - Recent changelog entries (current version and previous if available)
</process>

<output>
Display format:

```
ws Workspace Plugin v:{version}

## What's New

{changelog entries for current version}

## Previous Release

{changelog entries for previous version, if available}
```
</output>

<success_criteria>
- Version number clearly displayed
- Changelog entries shown for current version
- Output is concise and well-formatted
</success_criteria>
