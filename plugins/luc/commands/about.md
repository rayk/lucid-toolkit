---
description: Display luc plugin info, session details, and marketplace status
allowed-tools: []
---

**CRITICAL: This is a DISPLAY-ONLY command. Do NOT call any tools. All data is provided below. Just format and output it.**

# Pre-computed Data

## Session
!`find ~/.claude/plugins/cache/lucid-toolkit/luc -name "session_info.py" -exec {} \; 2>/dev/null || echo '{"session_id": "unknown", "transcript_path": null, "debug_log_path": "unknown"}'`

## Luc Plugin
@plugins/luc/plugin.json

## Marketplace
@.claude-plugin/marketplace.json

## Installed Plugins (in this project)
!`ls -d .claude/plugins/*/ 2>/dev/null | xargs -I {} basename {} 2>/dev/null || echo "none installed"`

# Instructions

Format the above data as follows and output it directly. Do NOT read files, do NOT run commands, do NOT edit anything.

```
## luc v{version from plugin.json}

**Session**
- ID: {session_id}
- Debug: {debug_log_path}
- Transcript: {transcript_path or "not found"}

**Marketplace:** lucid-toolkit v{metadata.version}

**Plugins:**
{for each plugin in marketplace.plugins, one line: "- {name} v{version} ({category}) [Installed/Available]"}

**luc includes:** {count skills} skills, {count commands} commands, {count schemas in schemas/} schemas
```

Output ONLY the formatted result. No tool calls. No explanations. No improvements.
