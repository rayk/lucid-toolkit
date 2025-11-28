# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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