# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.7] - 2025-11-29

### Added
- **TOC (Theory of Constraints) mental model** - Three-phase analysis (CRT → EC → FRT) for systemic problems with multiple symptoms, hidden conflicts, or when obvious fixes keep failing
- **CLR Validator agent** - Adversarial logic validator using Goldratt's 8 Categories of Legitimate Reservation for rigorous causal chain validation
- **SYSTEMIC problem type** - New classifier category for complex system diagnosis with keywords: symptoms, causes, constraint, bottleneck, systemic, root cause, chain
- **TOC memory schema extensions** - 4 new entity types (UDE, CausalLink, Assumption, NegativeBranch), 8 new relation types, observation templates, and memory operations for cross-session TOC learning

### Changed
- **think plugin** bumped to v2.2.0 (13 → 14 mental models, 17 → 19 agents)

## [2.0.6] - 2025-11-29

### Added
- **@shared/status-line/ module support** - Workspace commands now configure and validate the status-line shared module for Claude Code status line configuration utilities
  - `/workspace:init` - Automatically adds `status_line` module to project configuration during initialization
  - `/workspace:health` - Validates status-line module exists in project config and file path is accessible (Phase 4)
  - `/workspace:validate` - Checks shared module references including status-line path and entry point

### Changed
- **workspace plugin** bumped to v1.2.0

## [2.0.5] - 2025-11-29

### Fixed
- **/workspace:health** - Added delegation mandate to preserve main context window (uses Task tool with Explore subagent instead of executing directly). Strengthened interactive mode with MUST directives to ensure user prompts appear when issues are detected. Added phase validation reminders.

### Changed
- **workspace plugin** bumped to v1.1.1

## [2.0.4] - 2025-11-29

### Added
- **/fix-faults command** - Automated fault remediation workflow that reads fault reports from `~/.claude/fault/`, launches parallel agents to diagnose root causes, validates fixes against Claude Code best practices, implements fixes in parallel, then cleans up and commits

## [2.0.3] - 2025-11-29

### Fixed
- **capability:snapshot** - Added fallback generation from `capability_summary.json` when `SNAPSHOT.md` is missing, instead of showing error
- **workspace:health** - Added parallel execution strategy for independent phases (1-2 together, 5-7 together) and interactive mode with user prompts for issue resolution
- **context:report** - Changed save path from project directory to `~/.claude/fault/` for proper isolation; added `model-hint: haiku` for faster execution

### Changed
- **capability plugin** bumped to v1.0.2
- **context plugin** bumped to v1.2.1
- **workspace plugin** bumped to v1.1.0

## [2.0.2] - 2025-11-29

### Added
- **context:report command** - Report misbehavior of any plugin skill, command, or subagent. Captures session ID, debug log reference, and recent actions for later debugging. Reports saved to `~/.claude/fault/`.

## [2.0.1] - 2025-11-29

### Fixed
- **capability:snapshot command** - Optimized for instant display using declarative process pattern instead of procedural steps. Added `allowed-tools: [Read]` constraint and separated error handling for true <100ms cache performance.

## [2.0.0] - 2025-11-29

### Added
- **prompt-writer skill** - Expert guidance for writing effective prompts
- **TOON parser** - Structured output format parser in lucid-cli-commons
- **New specialized agents** - flutter-coder, flutter-env, python-coder, python-env
- **think:debate and think:swarm commands** - Advanced reasoning workflows
- **Session summary schema** - Structured session tracking

### Changed
- All plugin configurations updated with enhanced settings
- Context plugin hooks improved for better session tracking
- Status line script enhanced for richer feedback
- Outcome and capability schemas refined

### Documentation
- Added TOON implementation guides and quick start
- Schema compatibility documentation
- Hook documentation improvements

## [1.1.0] - 2025-11-28

### Added
- **payload-store skill** - Store large subagent outputs externally, returning compact TOON summaries with path references
- **shared/payloads/** - Session-scoped storage directory for large outputs with auto-cleanup
- **store-and-summarize pattern** in delegate skill for research and MCP operations

### Changed
- **context plugin** (v1.1.0) - Added payload-store skill to conserve main agent context
- **conserve skill** - Updated with payload-store protocol section and external data hazards table
- **delegate skill** - Added store-and-summarize pattern and updated token budget table with storage column
- **research agent** - Now uses payload-store protocol for comprehensive research outputs

### Restructured
- Renamed plugins for clarity: `capability-workflow` → `capability`, `outcome-workflow` → `outcome`, `thinking-tools` → `think`, `planner` → `plan`, `workspace-validator` → `workspace`
- Merged `session-manager` and `delegation-protocol` into new `context` plugin
- Moved maker-toolkit skills/commands/agents to `.claude/` directory (project-local)
- Added `specialize` plugin with technology-specialized subagents (research, neo4j, debugger)
- Created `shared/workspaces/` for cross-project workspace management

## [1.0.0] - 2025-11-28

### Added
- Initial release of Lucid Toolkit marketplace
- **capability-workflow** (v1.0.0) - Strategic capability management with maturity tracking
- **outcome-workflow** (v1.0.0) - Outcome lifecycle management (create, focus, complete)
- **session-manager** (v1.0.0) - Session lifecycle tracking with accomplishment capture
- **thinking-tools** (v1.0.0) - Structured analysis using mental models
- **maker-toolkit** (v1.0.0) - Build Claude Code skills, commands, and agents
- **workspace-validator** (v1.0.0) - Schema validation and workspace health checks
- **delegation-protocol** (v1.0.0) - Context-saving patterns for efficient Claude Code usage
- **planner** (v1.0.0) - TDD execution prompt generator with cost-efficient model delegation
- **lucid-cli-commons** (v1.0.0) - Shared Python library for plugin hooks and scripts