---
description: Display ws plugin version and recent changelog entries
allowed-tools: []
---

Display the following version information exactly as shown:

```
ws Workspace Plugin v0.2.1

## What's New (v0.2.1 - 2025-12-02)

### Changed
- All subagent tasks now use model="haiku" for cost efficiency
- Scanning, migration, and repair don't require sophisticated reasoning

## Previous Release (v0.2.0 - 2025-12-02)

### Changed
- /ws:enviro uses parallel subagent delegation pattern
- SETUP launches 4 parallel scanners (directories, projects, IDE, git)
- MIGRATE and REPAIR delegate to general-purpose subagent
- Minimal main context pollution
```
