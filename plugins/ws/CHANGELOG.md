# Changelog

All notable changes to the ws plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2025-12-03

### Added

- `outcome-checker` subagent for validating outcome definitions
  - Parent/child/standalone outcome type detection from outcome_track.json
  - Decomposition adequacy checks (contribution math = 100%, scope coverage)
  - Capability alignment validation with proportionality checks
  - Behavioral observable effects validation (Given-When-Then format required)
  - Full cross-reference graph integrity validation (bidirectional links)
  - Creates `outcome-check_failure_report.md` on INVALID status
  - Updates statement footer with validation metadata

### Changed

- `capability-checker`: Major overhaul with autofix capabilities
  - Upgraded model from haiku to sonnet (complex reasoning required)
  - Added Write/Edit tools for applying safe corrections
  - Autofix operations: spelling, grammar, markdown lint, broken links, formatting
  - Removed toon-specialist dependency (self-contained validation)
  - Creates `capability-check_failure_report.md` on INVALID status
  - Updates statement footer with validation metadata
- Standardized checker output behavior across both agents:
  - VALID/NEEDS_ATTENTION: Concise TOON with autofix counts
  - INVALID: TOON with issues summary + detailed failure report file
  - Both use schema.org vocabulary (`schema:CapabilityValidationReport`, `schema:OutcomeValidationReport`)

## [0.5.0] - 2025-12-03

### Added

- `git-commits` skill for extended semantic commit workflow
  - Commit format with mandatory purpose section explaining WHY
  - Architectural scope hierarchy (domain/component/subcomponent)
  - Local commit squashing guidance for clean remote history
  - Pre-push checklist and validation rules

### Changed

- Consolidated capability tracking to YAML frontmatter in capability-statement.md
  - Single source of truth (no separate capability_track.json)
  - Machine-parseable frontmatter with human-readable body
  - Scanners now extract from YAML instead of JSON
- `capability-checker`: Validates YAML frontmatter instead of JSON schema
- `cap:create`: Generates single file with embedded tracking data
- `cap:list`: Extracts capability data from YAML frontmatter
- `enviro.md`: Updated scanners to read capability-statement.md frontmatter
- `capabilities-info-schema.toon`: Removed trackPath field

### Removed

- `capability_track_schema.json` from plugin schemas (tracking now in frontmatter)
- `plans/toon-specialist-design.md` (design complete)

## [0.4.2] - 2025-12-02

### Performance

- Optimized `/ws:enviro` scanner prompts for parallel execution
- Reduced scanner prompt size by ~75% (verbose → compact TOON templates)
- Added explicit "Return ONLY this TOON - no prose" constraints to prevent context pollution
- Changed Phase 4 scanners from JSON to compact TOON format
- Added execution summary table showing parallel launch requirements
- Added "Parallel Launch Instruction" reminders after scanner definitions
- Simplified toon-specialist invocations (verbatim pass-through, no reformatting)

### Fixed

- Ensured all 4 Phase 2 scanners launch in parallel (was only launching 3)

## [0.4.1] - 2025-12-02

### Changed

- Centralized TOON schema access to toon-specialist only
- `toon-specialist.md`: Added `<architecture>` section with TOON access control table
- `toon-specialist.md`: Added constraint preventing schema paths in instance files
- `capability-checker.md`: Added Task tool for delegating TOON data retrieval
- `capability-checker.md`: Removed direct schema file references
- `cap/create.md`: Reference schemas by name, delegate to toon-specialist
- `cap/list.md`: Delegate .toon file writes to toon-specialist instead of direct writes
- `enviro.md`: Removed all explicit schema paths, reference by name only

### Architecture

Access control now enforced:
- Any command/agent: Read instance .toon files, use TOON in messages
- toon-specialist ONLY: Read *-schema.toon files, write .toon files, know schema locations

## [0.4.0] - 2025-12-02

### Added

- `toon-specialist` subagent for centralized schema.org/TOON file production
- Two-phase pattern for file generation: Explore agents return JSON, toon-specialist produces .toon files
- `plans/toon-specialist-design.md` architecture document

### Changed

- `/ws:enviro` now delegates ALL .toon file production to toon-specialist
- Phase 3 invokes toon-specialist to produce workspace-info.toon (no direct writes)
- Phase 4 uses coordinator pattern: scanners return structured data, toon-specialist writes files
- Phase 6 changed from "Generate Output Files" to "Verify Output Files"
- Replaced `workspace_info_template` with `schema_reference` (toon-specialist reads schemas directly)
- `migrate_mode` and `repair_mode` updated to use toon-specialist
- Removed `Write` from enviro.md allowed-tools (toon-specialist handles all writes)
- Main context NEVER writes .toon files directly - all production via specialist
- `toon_parser.py`: support arrays without count prefix, dots in key names

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
