---
description: Display luc plugin info, session details, and marketplace status
allowed-tools: []
---

**CRITICAL: This is a DISPLAY-ONLY command. Do NOT call any tools. All data is provided below. Just format and output it.**

# Pre-computed Data

## Session
!`~/.claude/plugins/cache/lucid-toolkit/luc/*/scripts/session_info.py 2>/dev/null || python3 -c "import json; from pathlib import Path; d=Path.home()/'.claude'/'debug'; l=d/'latest'; print(json.dumps({'session_id':l.resolve().stem if l.exists() else 'unknown','debug_log_path':str(l.resolve()) if l.exists() else 'unknown','transcript_path':None}))" 2>/dev/null || echo '{"session_id":"unknown"}'`

## Installed Plugins Registry
!`cat ~/.claude/plugins/installed_plugins.json 2>/dev/null || echo '{"plugins":{}}'`

## Installed Plugins (in this project)
!`ls -d .claude/plugins/*/ 2>/dev/null | xargs -I {} basename {} 2>/dev/null || echo "none installed"`

# Instructions

Format the above data as follows and output it directly. Do NOT read files, do NOT run commands, do NOT edit anything.

```
## luc v{version from installed_plugins.json for luc@lucid-toolkit}

**Session**
- ID: {session_id}
- Debug: {debug_log_path}
- Transcript: {transcript_path or "not found"}

**Installed from lucid-toolkit:**
{for each plugin in installed_plugins.json.plugins where key contains "@lucid-toolkit":
  "- {plugin name} v{version}"}

**Project plugins:** {list from "Installed Plugins (in this project)" or "none"}
```

Output ONLY the formatted result. No tool calls. No explanations. No improvements.
