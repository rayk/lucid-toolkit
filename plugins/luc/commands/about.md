---
description: Display luc plugin info, session details, marketplace info, and installed plugins
allowed-tools: [Read, Glob, Bash]
---

<objective>
Display the luc plugin version, lucid-toolkit marketplace version, and list all marketplace plugins with their versions and installation status in the current project.

This helps users understand what version they're running and what plugins are available or installed.
</objective>

<constraints>
- This is a READ-ONLY command - do NOT modify any files
- Do NOT use Edit, Write, or any file modification tools
- Only gather information and display output
- Complete quickly - this should take 2-3 tool calls maximum
</constraints>

<context>
Marketplace info: @.claude-plugin/marketplace.json
Luc plugin: @plugins/luc/plugin.json
Installed plugins: !`ls -d .claude/plugins/*/ 2>/dev/null | xargs -I {} basename {} 2>/dev/null || echo "none"`
Session info: !`find ~/.claude/plugins/cache/lucid-toolkit/luc -name "session_info.py" -exec {} \; 2>/dev/null || echo '{"session_id": "unknown"}'`
</context>

<process>
1. Run session_info.py script to get session ID and transcript path
2. Read luc plugin.json for current version
3. Read marketplace.json for marketplace version and available plugins
4. Check .claude/plugins/ directory for installed plugins in current project
5. Display formatted output
</process>

<output_format>
Display in this format:

```
luc Plugin v{version}
Marketplace: lucid-toolkit v{marketplace.version}

## Session
- ID: {session_id}
- Transcript: {transcript_path or "not found"}
- Debug Log: {debug_log_path}

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
- Session ID and paths displayed
- Luc version displayed correctly
- Marketplace version displayed correctly
- All plugins listed with accurate versions
- Installation status correctly detected for each plugin
- Clean, readable table format
</success_criteria>
