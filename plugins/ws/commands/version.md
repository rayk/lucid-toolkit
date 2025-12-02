---
description: Display ws plugin version and recent changelog entries
allowed-tools: []
---

Display the following version information exactly as shown:

```
ws Workspace Plugin v0.3.0

## What's New (v0.3.0 - 2025-12-02)

### Added
- /cap:create command for guided capability creation with validation
- /cap:list command with automatic index sync via parallel subagents
- 6 TOON schema files for workspace data structures
- 4 output templates for generated documents
- capability-checker subagent for validation workflows
- Python hooks and workspace_info package

### Changed
- /ws:enviro now generates related data files in .claude/ directory
- Schema files organized in plugins/ws/templates/data/
- REPORT, MIGRATE, REPAIR modes check and regenerate missing files

## Previous Release (v0.2.2 - 2025-12-02)

### Changed
- /ws:report now reads workspace-info.toon for context
- Fault reports include ws plugin version and project path
```
