---
description: Display ws plugin version and recent changelog entries
allowed-tools: []
---

Display the following version information exactly as shown:

```
ws Workspace Plugin v0.6.1

## What's New (v0.6.1 - 2025-12-03)

### Changed
- cap:create: Major efficiency overhaul
  - Read TOON schema files directly (no toon-specialist for reads)
  - Removed capability_track.json (all tracking in YAML frontmatter)
  - Added critical_constraints, anti_patterns, yaml_frontmatter_template
  - Reduced tool calls from 30+ to 10-15

- capability-checker: Tool efficiency optimization
  - Replace Bash calls with Grep/Glob/Read tools
  - Target 5-8 tool calls (was 30+)
  - Removed autofix operations (read-only validation)

### Fixed
- cap:create no longer writes TBD/TODO placeholders
- cap:create generates correct kebab-case actor IDs
- cap:create produces proper YAML frontmatter

## Previous Release (v0.6.0 - 2025-12-03)

### Added
- outcome-checker subagent for validating outcome definitions

### Changed
- capability-checker: Autofix capabilities, upgraded to sonnet
- Standardized checker output (TOON with schema.org vocabulary)
```
