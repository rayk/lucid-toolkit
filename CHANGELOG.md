# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.7.0] - 2025-12-16

### Added
- **architect plugin** (v1.1.0 → v1.2.0) - New `adr-curator` agent
  - Audits and maintains ADR collection consistency, cross-references, and README index
  - Autonomous fixes for: README sync, bidirectional references, stale review dates, formatting
  - Interactive resolution via AskUserQuestion for: naming violations, missing sections, domain classification, orphaned ADRs
  - Fix decision matrix separates autonomous fixes from user-required decisions
  - Complements `adr-writer` (writer creates, curator maintains)

### Changed
- Marketplace version bumped to 2.7.0

## [2.6.0] - 2025-12-15

### Added
- **luc plugin** (v2.6.0 → v2.7.0) - New `/luc:fix-escape` command
  - Diagnoses IdeaVim escape key conflicts with Claude Code CLI in IntelliJ terminal
  - Automatically fixes `~/.ideavimrc` sethandler directives
  - Fixes `vim_settings.xml` enabled state across all JetBrains IDEs
  - Reports manual steps for GitHub Copilot and Focus Editor keybindings
  - Provides `Ctrl+[` fallback guidance

## [2.5.0] - 2025-12-15

### Added
- **impl-flutter plugin** (v2.1.0 → v2.2.0) - New `/impl-flutter:run` command for interactive Flutter development sessions
  - Orchestrates app lifecycle: start, monitor, restart with hot reload support
  - Delegates all code changes to specialist agents (flutter-ux, flutter-debugger, etc.) to preserve main context
  - Manages DTD (Dart Tooling Daemon) connection for hot reload capability
  - Tracks session state: device ID, shell ID, VM Service URL (which changes on restart)
  - Feedback loop protocol: classify user observation → delegate to specialist → hot reload → confirm
  - Context-efficient design: never reads implementation files in main context
  - Agent routing table maps request types to appropriate specialists

### Changed
- Marketplace version bumped to 2.5.0

## [2.3.0] - 2025-12-13

### Changed
- **architect plugin** (v1.0.0 → v1.1.0) - Enhanced skill and agent descriptions with explicit INVOKE triggers
  - `manage-architecture` skill: Added "INVOKE THIS SKILL when user:" section with 7 trigger conditions and keywords
  - `create-adr` skill: Added "INVOKE THIS SKILL when user:" section with 5 trigger conditions and keywords
  - `architecture-reviewer` agent: Added "INVOKE when user mentions:" with 5 trigger phrases
  - `component-analyzer` agent: Added "INVOKE when user mentions:" with 4 trigger phrases
  - `adr-writer` agent: Added "INVOKE when user mentions:" with 4 trigger phrases
  - `consistency-checker` agent: Added "INVOKE when user mentions:" with 4 trigger phrases
- **plan plugin** (v2.0.0 → v2.1.0) - Enhanced skill description with explicit INVOKE triggers
  - `execution-prompt-generator` skill: Added "INVOKE THIS SKILL when user:" section with 6 trigger conditions and keywords
- **impl-flutter plugin** (v2.0.0 → v2.1.0) - Enhanced all 8 agent descriptions with explicit INVOKE triggers
  - `flutter-coder`: Added triggers for feature implementation, code generation, Riverpod, fpdart
  - `flutter-tester`: Added triggers for all testing needs (unit, widget, integration, e2e, golden, coverage)
  - `flutter-debugger`: Added triggers for runtime debugging, layout issues, performance, DevTools
  - `flutter-env`: Added triggers for build failures, CI issues, signing, environment setup
  - `flutter-data`: Added triggers for database, Firebase, offline-first, sync, secure storage
  - `flutter-platform`: Added triggers for platform channels, FFI, native code, Pigeon
  - `flutter-release`: Added triggers for app store releases, pub.dev, Crashlytics, versioning
  - `flutter-ux`: Added triggers for theming, navigation, animations, i18n, accessibility
- Marketplace version bumped to 2.3.0

### Fixed
- **Plugin invocation recognition** - Session analysis revealed 0% delegation rate due to missing trigger keywords in plugin descriptions. All affected plugins now include explicit "INVOKE when:" sections with user intent phrases and trigger keywords to improve automatic invocation matching.

## [2.2.0] - 2025-12-12

### Added
- **architect plugin** (v1.0.0) - New architecture design and documentation plugin based on Lucid Composite Architecture (LCA) principles
  - 3 commands: `/architect:init`, `/architect:adr`, `/architect:review`
  - 2 skills: `manage-architecture`, `create-adr`
  - 4 agents: `component-analyzer`, `architecture-reviewer`, `adr-writer`, `consistency-checker`
  - Three-tier abstraction model (Platform → Repository → Component)
  - Document type hierarchy with trust levels (ARCHITECTURE.md, architecture.md, {topic}.md, adr-NNN-*.md)
  - Platform documentation templates (overview, shared-concepts, protocols, integration-patterns, data-residency, cross-cutting-concerns)
  - Hierarchy resolution model enforcing inheritance rules (lower levels extend, never override)
  - Consistency checker validates architecture files don't violate higher-level constraints or LCA principles
  - 8 immutable LCA principles enforcement
  - ADR lifecycle management with supersession chains
  - Maturity status tracking (Draft → InProgress → Stable → Locked)
  - TOON schemas for component inventory and ADR indexing

### Removed
- **designer plugin** - Removed empty placeholder plugin (functionality now in architect plugin)

### Changed
- Updated README.md to reflect current 7 plugins
- Marketplace version bumped to 2.2.0

## [2.3.0] - 2025-12-04

### Added
- **specialize plugin** - New `architect` agent for translating requirements into implementation-ready design documents
  - Produces validated `design.md` with complete API signatures, data structures, file layouts, and dependency specifications
  - 6-phase workflow: input validation → project discovery → external contract validation → structure design → data flow design → verification
  - Input validation with failure reports for incomplete/contradictory requirements
  - LLM Decomposition Test success criteria ensuring designs are consumable by implementing models
  - Explicit EXISTS/CREATE markers for all file paths
  - Implementation discretion annotations for areas where implementer judgment is expected
  - Prompt optimized for Claude Opus 4.5: removed impossible introspection asks, concrete tool mappings, reduced template verbosity

### Changed
- **specialize plugin** bumped to v1.2.0

## [2.2.0] - 2025-12-01

### Changed
- **plan plugin** - Expanded Haiku model usage for cost efficiency
  - Phase 5 (Integration): Split into haiku (export updates) + sonnet (verification)
  - Phase 8 (Cross-Check): Split into haiku (mechanical checks: lint, coverage, style) + sonnet (reasoning checks) + opus (analysis)
  - Updated Principle 3 with detailed Haiku use cases and subtask splitting guidance
- **plan plugin** bumped to v1.1.0

## [2.1.0] - 2025-12-01

### Fixed
- **context:delegate skill** - Removed non-standard `@skills delegate` invocation syntax; clarified that skills activate automatically via model context recognition, not explicit invocation
- **context:conserve skill** - Removed `@skills conserve` pseudo-syntax; reframed correct flow to show natural activation when generating structured output
- **context plugin** bumped to v1.3.2

## [2.0.9] - 2025-11-30

### Fixed
- **context:delegate skill** - Added `<when_invoked>` section with explicit activation triggers, CORRECT/INCORRECT flow examples, and recognition patterns to ensure proactive invocation before tool calls
- **context:conserve skill** - Added `<when_invoked>` section with automatic activation conditions, TOON format examples, and recognition triggers for structured output
- **context plugin** bumped to v1.3.1

## [2.0.8] - 2025-11-30

### Changed
- **context plugin skills** - Migrated all skills to pure XML structure with mandatory invocation patterns
  - `delegate` - Added specialized agent prioritization (specialize:* agents before built-in), proactive description triggers on ALL task execution
  - `conserve` - Converted to pure XML, added success criteria, mandatory description for ALL output generation
  - `payload-store` - Fixed YAML frontmatter (`tools` → `allowed-tools`), added objective/quick_start/success_criteria
  - `toon-schema` - Full migration from hybrid markdown/XML to pure XML structure
- **context plugin** bumped to v1.3.0

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