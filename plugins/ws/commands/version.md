---
description: Display ws plugin version and recent changelog entries
allowed-tools: []
---

Display the following version information exactly as shown:

```
ws Workspace Plugin v0.7.0

## What's New (v0.7.0 - 2025-12-03)

### Added
- cap:check command for validating capability statements
- capability-index-sync skill for cross-cutting index synchronization
- capability_sync.py PostToolUse hook as safety net
- Implemented cap:edit, cap:delete, cap:merge, cap:split commands

### Changed
- All cap/* commands invoke capability-index-sync skill in epilogue
- git-commits skill migrated to pure XML structure

## Previous Release (v0.6.1 - 2025-12-03)

### Changed
- cap:create: Read TOON files directly, removed capability_track.json
- capability-checker: Replace Bash calls with Grep/Glob/Read tools

### Fixed
- cap:create no longer writes TBD/TODO placeholders
- cap:create generates correct kebab-case actor IDs
```
