---
description: Display ws plugin version and recent changelog entries
allowed-tools: []
---

Display the following version information exactly as shown:

```
ws Workspace Plugin v0.1.1

## What's New (v0.1.1 - 2025-12-02)

### Fixed
- /ws:version command now works in installed plugins by embedding version info directly
- Removed dependency on @path dynamic context that only resolves in source repo

### Changed
- /pub-ws command now syncs version.md during releases (Phase 5.5)

## Previous Release (v0.1.0 - 2025-12-02)

### Added
- Initial plugin structure with plugin.json metadata
- Five key areas: Capabilities (cap), Outcomes (out), Designs (des), Plans (pln), Execution (exe)
- /ws:version command - display version and recent changelog entries
- /ws:report command - capture fault reports for debugging with session context
- /ws:enviro command - idempotent workspace environment management
- workspace-info.toon template using schema.org vocabulary
```
