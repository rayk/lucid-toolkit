---
description: Display ws plugin version and recent changelog entries
allowed-tools: []
---

Display the following version information exactly as shown:

```
ws Workspace Plugin v0.4.0

## What's New (v0.4.0 - 2025-12-02)

### Added
- toon-specialist subagent for centralized schema.org/TOON file production
- Two-phase pattern: Explore agents return JSON, toon-specialist produces .toon files

### Changed
- /ws:enviro delegates ALL .toon file production to toon-specialist
- Main context NEVER writes .toon files directly - all via specialist
- Phase 6 changed from "Generate" to "Verify" output files
- toon_parser.py: support arrays without count, dots in key names

## Previous Release (v0.3.0 - 2025-12-02)

### Added
- /cap:create, /cap:list commands
- 6 TOON schema files, capability-checker subagent
```
