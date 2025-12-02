---
description: Display ws plugin version and recent changelog entries
allowed-tools: []
---

Display the following version information exactly as shown:

```
ws Workspace Plugin v0.5.0

## What's New (v0.5.0 - 2025-12-03)

### Added
- git-commits skill for extended semantic commit workflow
  - Mandatory purpose section explaining WHY
  - Architectural scope hierarchy (domain/component/subcomponent)
  - Local commit squashing for clean remote history

### Changed
- Consolidated capability tracking to YAML frontmatter
  - Single source of truth (no separate capability_track.json)
  - Scanners extract from YAML instead of JSON
- Updated capability-checker, cap:create, cap:list for frontmatter

### Removed
- capability_track_schema.json (tracking now in frontmatter)

## Previous Release (v0.4.2 - 2025-12-02)

### Performance
- Optimized /ws:enviro scanner prompts for parallel execution
- Reduced scanner prompt size by ~75% (compact TOON templates)
- All 4 Phase 2 scanners now launch in parallel
```
