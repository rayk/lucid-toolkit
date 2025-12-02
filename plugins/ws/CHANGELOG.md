# Changelog

All notable changes to the ws plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-12-02

### Added

- `/cap:create` command for guided capability creation with validation workflow
- `/cap:list` command with automatic index sync via parallel subagents
- Placeholder commands: `/cap:delete`, `/cap:edit`, `/cap:merge`, `/cap:split`
- TOON schema files for workspace data structures:
  - `workspace-info-schema.toon` - main workspace snapshot structure
  - `capabilities-info-schema.toon` - capabilities index structure
  - `outcomes-info-schema.toon` - outcomes index structure
  - `execution-info-schema.toon` - execution tracking structure
  - `core-values-schema.toon` - 34-value framework reference data
  - `actor-registry-schema.toon` - actor definitions reference data
- Output templates for generated documents:
  - `capability-statement-template.md`
  - `outcome-statement-template.md`
  - `execution-plan-template.md`
  - `execution-completion-template.md`
- `capability-checker` subagent for validation workflows
- Python hooks (`session_start.py`, `focus_tracker.py`)
- `capability_track_schema.json` for JSON schema validation
- `workspace_info` Python package with CLI and hook support

### Changed

- `/ws:enviro` now generates related data files (capabilities-info, outcomes-info, execution-info)
- Added Phase 4 to `/ws:enviro` for checking and generating missing related data files
- All TOON instance files now stored in `.claude/` directory
- Schema files organized in `plugins/ws/templates/data/`
- Output templates organized in `plugins/ws/templates/outputs/`
- REPORT, MIGRATE, and REPAIR modes now check and regenerate missing related files

## [0.2.2] - 2025-12-02

### Changed

- `/ws:report` command now reads workspace-info.toon for context
- Fault reports include ws plugin version and project path
- Added `environment` section to report JSON schema

## [0.2.1] - 2025-12-02

### Changed

- All subagent tasks in `/ws:enviro` now specify `model="haiku"` for cost efficiency
- Scanning, migration, and repair tasks don't require sophisticated reasoning

## [0.2.0] - 2025-12-02

### Changed

- `/ws:enviro` command now uses parallel subagent delegation pattern
- Scanning operations run in isolated contexts, minimizing main context pollution
- State detection remains in main context (minimal reads)
- REPORT mode reads directly (no delegation needed)
- SETUP launches 4 parallel scanners: directories, projects, IDE, git metadata
- MIGRATE and REPAIR delegate to single general-purpose subagent
- User notified immediately when scan starts, results reported on completion

## [0.1.1] - 2025-12-02

### Fixed

- `/ws:version` command now works in installed plugins by embedding version info directly
- Removed dependency on @path dynamic context that only resolves in source repo

### Changed

- `/pub-ws` command now syncs version.md during releases (Phase 5.5)

## [0.1.0] - 2025-12-02

### Added

- Initial plugin structure with plugin.json metadata
- Five key areas: Capabilities (cap), Outcomes (out), Designs (des), Plans (pln), Execution (exe)
- `/ws:version` command - display version and recent changelog entries
- `/ws:report` command - capture fault reports for debugging with session context
- `/ws:enviro` command - idempotent workspace environment management (setup, repair, migrate, report)
- `workspace-info.toon` template using schema.org vocabulary for workspace snapshots
- Comprehensive scanning for IntelliJ .idea/, project-map.json, and technology indicators
- README.md documentation
