---
description: Display ws plugin version and recent changelog entries
allowed-tools: []
---

Display the following version information exactly as shown:

```
ws Workspace Plugin v0.6.0

## What's New (v0.6.0 - 2025-12-03)

### Added
- outcome-checker subagent for validating outcome definitions
  - Parent/child/standalone outcome type detection
  - Decomposition adequacy checks (contribution math = 100%)
  - Capability alignment and behavioral effects validation
  - Creates outcome-check_failure_report.md on INVALID

### Changed
- capability-checker: Major overhaul with autofix capabilities
  - Upgraded to sonnet model, added Write/Edit tools
  - Autofix: spelling, grammar, markdown lint, broken links
  - Creates capability-check_failure_report.md on INVALID
- Standardized checker output (TOON with schema.org vocabulary)

## Previous Release (v0.5.0 - 2025-12-03)

### Added
- git-commits skill for extended semantic commit workflow

### Changed
- Consolidated capability tracking to YAML frontmatter
- Updated capability-checker, cap:create, cap:list for frontmatter
```
