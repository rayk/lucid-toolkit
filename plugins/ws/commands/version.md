---
description: Display ws plugin version and recent changelog entries
allowed-tools: []
---

Display the following version information exactly as shown:

```
ws Workspace Plugin v0.4.2

## What's New (v0.4.2 - 2025-12-02)

### Performance
- Optimized /ws:enviro scanner prompts for parallel execution
- Reduced scanner prompt size by ~75% (compact TOON templates)
- Added "Return ONLY this TOON - no prose" constraints
- All 4 Phase 2 scanners now launch in parallel (was 3)

### Changed (v0.4.1)
- Centralized TOON schema access to toon-specialist only
- toon-specialist is exclusive gateway for schema files and .toon writes

## Previous Release (v0.4.0 - 2025-12-02)

### Added
- toon-specialist subagent for centralized TOON file production
- Two-phase pattern: Explore agents return JSON, toon-specialist produces .toon files

### Changed
- /ws:enviro delegates ALL .toon file production to toon-specialist
- Main context NEVER writes .toon files directly
```
