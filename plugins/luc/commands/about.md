---
description: Display luc plugin info, session details, and installed plugins
allowed-tools: []
---

**DISPLAY-ONLY: Format the data below and output. No tool calls.**

# Data
!`~/.claude/plugins/cache/lucid-toolkit/luc/*/scripts/about_info.py 2>/dev/null || echo '{"luc_version":"unknown","session":{"session_id":"unknown"},"installed_plugins":[],"project_plugins":[],"luc_contents":{"skills":[],"commands":[],"schemas":[]}}'`

# Format as:

```
## luc v{luc_version}

**Session:** {session.session_id}
- Debug: {session.debug_log_path}
- Transcript: {session.transcript_path or "not found"}

**Installed plugins:**
{for each in installed_plugins: "- {name} v{version}"}

**Project plugins:** {project_plugins joined by ", " or "none"}

**luc includes:** {len(luc_contents.skills)} skills, {len(luc_contents.commands)} commands
```

Output the formatted result only.
