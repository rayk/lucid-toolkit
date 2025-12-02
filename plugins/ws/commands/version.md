---
description: Display ws plugin version and recent changelog entries
allowed-tools: []
---

Display the following version information exactly as shown:

```
ws Workspace Plugin v0.2.0

## What's New (v0.2.0 - 2025-12-02)

### Changed
- /ws:enviro command now uses parallel subagent delegation pattern
- Scanning operations run in isolated contexts, minimizing main context pollution
- SETUP launches 4 parallel scanners: directories, projects, IDE, git metadata
- MIGRATE and REPAIR delegate to single general-purpose subagent
- User notified immediately when scan starts, results reported on completion

## Previous Release (v0.1.1 - 2025-12-02)

### Fixed
- /ws:version command now works in installed plugins by embedding version info directly

### Changed
- /pub-ws command now syncs version.md during releases
```
