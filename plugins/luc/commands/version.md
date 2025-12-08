---
description: Display luc plugin version, marketplace info, and installed plugins
allowed-tools: [Read, Glob, Bash]
---

<objective>
Display the luc plugin version, lucid-toolkit marketplace version, and list all marketplace plugins with their versions and installation status in the current project.

This helps users understand what version they're running and what plugins are available or installed.
</objective>

<context>
Marketplace info: @.claude-plugin/marketplace.json
Luc plugin: @plugins/luc/plugin.json
Installed plugins: !`ls -d .claude/plugins/*/ 2>/dev/null | xargs -I {} basename {} 2>/dev/null || echo "none"`
</context>

<process>
1. Read luc plugin.json for current version
2. Read marketplace.json for marketplace version and available plugins
3. Check .claude/plugins/ directory for installed plugins in current project
4. Display formatted output showing:
   - Luc plugin version with brief description
   - Marketplace name and version
   - Table of all plugins: name, version, category, installed status
</process>

<output_format>
Display in this format:

```
luc Plugin v{version}
Marketplace: lucid-toolkit v{marketplace.version}

## Available Plugins

| Plugin | Version | Category | Status |
|--------|---------|----------|--------|
| {name} | {version} | {category} | {Installed/Available} |
...

## luc Includes
- Schemas: {count} TOON schemas
- Skills: {list}
- Commands: {list}
```
</output_format>

<success_criteria>
- Luc version displayed correctly
- Marketplace version displayed correctly
- All plugins listed with accurate versions
- Installation status correctly detected for each plugin
- Clean, readable table format
</success_criteria>
