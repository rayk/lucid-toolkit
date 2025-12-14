---
description: Show installed plugins, their triggers, and available commands/agents
allowed_tools: Read, Glob, Grep
---

<task>
Display a comprehensive list of installed plugins with their trigger phrases, commands, skills, and agents to help users discover available functionality.
</task>

<instructions>
1. **Find all installed plugins**:
   - Search for `plugin.json` files in `plugins/` directory
   - Read each plugin.json to get metadata

2. **For each plugin, gather**:
   - Name and version from plugin.json
   - Commands: List files in `commands/` subdirectory
   - Skills: List SKILL.md files and read descriptions
   - Agents: List agent .md files and read descriptions

3. **Extract trigger information**:
   - From skill descriptions: Look for "Triggers when", "MUST BE USED", keywords
   - From agent descriptions: Look for "Use PROACTIVELY", "MUST BE USED"

4. **Present in organized format** by plugin
</instructions>

<output_format>
# Installed Plugins

## {Plugin Name} (v{version})

**Trigger phrases**: {extracted trigger keywords}

**Commands**:
- `/{command}` - {brief description}

**Skills**:
- `{skill-name}` - {when to use}

**Agents**:
- `{agent-name}` - {when to use}

---

[Repeat for each plugin]

## Quick Reference

| Trigger Phrase | Plugin | Component |
|---------------|--------|-----------|
| "research", "investigate" | analyst | research agent |
| "consider", "analyze" | analyst | consider skill |
| "architect review" | architect | architecture-reviewer |
| "build failed" | impl-flutter | flutter-env |
| "execute plan" | plan | execution-prompt-generator |

## Usage Examples

```
/consider "Should we use Redux or Context for state?"
Task(analyst:research): "Find best practices for React state management"
Task(architect:architecture-reviewer): "Review the current system design"
```
</output_format>
