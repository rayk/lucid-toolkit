# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.30.0] - 2025-12-20

### Fixed
- **impl-flutter plugin** (v2.15.4 → v2.15.5) - Complete fix for memory exhaustion in /plan command
  - **Root cause:** Nested orchestrator pattern with parallel Task spawning exhausted 16GB heap
  - **Solution:** Eliminated orchestrator layer; /plan command now orchestrates directly
  - **plan.md command:** Rewrote as direct orchestrator with sequential Task execution
    - Runs subagents ONE AT A TIME (no parallelism)
    - Each Task completes before next starts (memory released between calls)
    - Peak memory reduced from 4x to 1x (~2-4GB vs 16GB+)
  - **flutter-plan-orchestrator agent:** Deprecated with explicit error message
    - Removed all tools (`tools: []`)
    - Returns deprecation error if invoked
    - Agent file kept for reference but is non-functional
  - Previous fix (v2.15.4) was insufficient - only removed Task from one subagent
- Marketplace version bumped to 2.30.0

## [2.29.0] - 2025-12-20

### Fixed
- **impl-flutter plugin** (v2.15.3 → v2.15.4) - Fixed memory exhaustion in plan orchestrator
  - Removed `Task` tool from `plan-capability-mapper` agent to prevent subagent cascade
  - Agent was spawning pre-flight validation agents, causing 16GB memory exhaustion
  - Now uses `Read, Glob` only (no Task) - returns embedded capability matrix without spawning
  - Updated pre-flight validation section to clarify it's reference documentation, not execution instructions
- Marketplace version bumped to 2.29.0

## [2.28.0] - 2025-12-20

### Changed
- **impl-flutter plugin** (v2.15.2 → v2.15.3) - Efficiency improvements for coding agents
  - Added `<efficiency>` section to flutter-coder and flutter-ux-widget agents
  - Progress reporting: agents output single-line status before each phase
  - MCPSearch usage guidance: load MCP tools before calling them
  - Skip exploration when task includes `## Patterns to Follow` section
  - Max 3 files for pattern discovery (was unlimited)
  - One Glob+Read round max (was multiple rounds)
  - Batch operations: write all files before tests, analyze/format once at end
  - Root cause analysis: 91.7s streaming stalls + 25s slow getDiagnostics in 8-min run
- Marketplace version bumped to 2.28.0

## [2.27.0] - 2025-12-20

### Fixed
- **impl-flutter plugin** (v2.15.1 → v2.15.2) - Added MCPSearch to all agents using MCP tools
  - Root cause: Subagents don't automatically load deferred MCP tools
  - Debug logs showed "48 MCP tools deferred" in main context, "0 deferred" in subagent context
  - Subagents with `mcp__dart__*` patterns couldn't access MCP tools without MCPSearch
  - Added `MCPSearch` to 12 agents: flutter-coder, flutter-ux-widget, flutter-gen-ui,
    flutter-data, flutter-e2e-tester, flutter-release, flutter-debugger, flutter-platform,
    flutter-env, flutter-verifier, flutter-session-driver, flutter-session-recorder
- Marketplace version bumped to 2.27.0

## [2.26.0] - 2025-12-20

### Fixed
- **impl-flutter plugin** (v2.15.0 → v2.15.1) - Added missing exploration tools to coding agents
  - **flutter-coder agent**: Added `Read`, `Glob`, `Grep` tools to enable scoped exploration
    - Agent documentation described reading existing patterns before writing code
    - But tools list only had `Write, Edit` - agent literally couldn't read files
  - **flutter-ux-widget agent**: Added `Glob`, `Grep` tools (already had `Read`)
    - Aligns with flutter-coder capabilities for pattern discovery
- Marketplace version bumped to 2.26.0

## [2.25.0] - 2025-12-19

### Changed
- **impl-flutter plugin** (v2.14.0 → v2.15.0) - Pure delegation architecture for plan/do commands
  - **plan.md command**: Complete rewrite as thin dispatcher (326 → 90 lines)
    - Added `<critical_behavior>` with PROHIBITED/REQUIRED actions
    - Now takes 3 required args: spec-path, constraints-path, output-dir
    - Only uses Task tool - all work delegated to orchestrator
  - **do.md command**: Complete rewrite as thin dispatcher
    - Added `<critical_behavior>` enforcing delegate-only pattern
    - Token counting model: only subagent RETURNS count against context
    - Plans can now complete in one context window via delegation
  - **flutter-plan-orchestrator**: Removed Read/Write tools, added critical_behavior
  - **New helper agents for /do command** (6 agents):
    - `do-plan-reader` (haiku) - Reads plan, returns structured summary
    - `do-log-writer` (haiku) - Writes execution-log.toon entries
    - `do-git-ops` (haiku) - Git commit/rollback operations
    - `do-checkpoint-validator` (haiku) - Validates phase checkpoints
    - `do-resume-writer` (haiku) - Creates resume continuation points
    - `do-resume-reader` (haiku) - Reads resume points for continuation
  - Plugin now has 26 specialized agents (was 20)
- Marketplace version bumped to 2.25.0

## [2.24.0] - 2025-12-19

### Changed
- **impl-flutter plugin** (v2.13.0 → v2.14.0) - Plan/Do integration overhaul for reliable execution
  - **execution-plan.toon template**: Added `projectRoot`, `architectureRef` at plan level
  - **execution-plan.toon template**: Added `agentInputs` section for agent-specific required inputs per task
  - **plan.md command**: Updated with fully-qualified agent names (`impl-flutter:flutter-coder`)
  - **plan.md command**: Added agentInputs requirements documentation for all Flutter agents
  - **do.md command**: Now reads `agentInputs` from plan to construct prompts
  - **do.md command**: Added context protection (85% threshold) with resume-continuation-point.md
  - **do.md command**: Added `impl-flutter:flutter-ux-widget` prompt template
  - **flutter-plan-orchestrator**: Updated with fully-qualified agent names and agentInputs generation
  - **plan-writer**: Now generates plans with fully-qualified names and agentInputs
  - **plan-simulator**: Validates agent names (fully-qualified) and agentInputs completeness
  - **plan-coverage-validator**: Cross-checks agent validity and agentInputs presence
  - **plan-capability-mapper**: All references now use fully-qualified agent names
  - Plans now self-describing: executor dispatches directly without implicit knowledge
- Marketplace version bumped to 2.24.0

## [2.23.0] - 2025-12-19

### Changed
- **impl-flutter plugin** (v2.12.0 → v2.13.0) - Agent autonomy and TDD enforcement improvements
  - **flutter-coder agent**: Added architecture reference requirement in pre-flight check
  - **flutter-coder agent**: Added capabilities query response in TOON format (schema.org)
  - **flutter-coder agent**: Added dry run mode for deep verification before execution
  - **flutter-coder agent**: Added "no handoffs after acceptance" rule - once accepted, agent owns completion
  - **flutter-ux-widget agent**: Complete rewrite to align with flutter-coder behavior patterns
  - **flutter-ux-widget agent**: Added 10 non-negotiable behaviors including theme-aware and accessible
  - **flutter-ux-widget agent**: Added design spec requirement in pre-flight check
  - **flutter-ux-widget agent**: Clarified visual specialization preference (complex animations, custom paint)
  - **flutter-ux-widget agent**: Renamed `<handoffs>` → `<rejection_guidance>` (pre-flight only, not mid-task)
  - **plan-context-builder agent**: Added flutter-coder specific context format (paths only, no code blocks)
  - **plan-context-builder agent**: Added architectureRef discovery guidance
  - **do command**: Added flutter-coder task template with required inputs (projectRoot, targetPaths, architectureRef)
  - **do command**: Added codegen field and architecture reference requirement
  - Both coding agents now: REJECT at pre-flight OR complete/fail (no mid-task handoffs)
- Marketplace version bumped to 2.23.0

## [2.22.0] - 2025-12-19

### Changed
- **impl-flutter plugin** (v2.11.0 → v2.12.0) - Split monolithic planner into orchestrator + subagents
  - **Architecture overhaul**: Replaced 1100-line `flutter-impl-planner` with modular system
  - New `flutter-plan-orchestrator` (350 lines) - Lightweight coordinator that delegates all heavy work
  - New `plan-spec-analyzer` (haiku) - Reads specs, returns structured summaries
  - New `plan-constraint-analyzer` (haiku) - Reads constraints, returns architectural rules
  - New `plan-capability-mapper` (haiku) - Queries agents, builds capability matrix
  - New `plan-context-builder` (haiku) - Creates consolidated context files with source links
  - New `plan-coverage-validator` (sonnet) - Validates 100% spec coverage
  - New `plan-simulator` (opus) - Runs mental simulation for probability assessment
  - New `plan-writer` (sonnet) - Generates execution-plan.toon
  - **Benefits**: Max context load reduced from 1100 lines to ~200 lines per agent
  - **Benefits**: Right-sized models (haiku for analysis, sonnet for validation, opus for simulation)
  - Plugin now has 20 specialized agents (was 13)
- Marketplace version bumped to 2.22.0

## [2.21.0] - 2025-12-19

### Added
- **impl-flutter plugin** (v2.10.0 → v2.11.0) - Execution planning system
  - New `flutter-impl-planner` agent for creating verified execution plans
    - Accepts technical specs + architectural constraints as inputs
    - Dynamic agent capability discovery via parallel Task queries
    - Aggressive context conservation (delegates all analysis to subagents)
    - Coverage validation: 100% spec coverage required before probability assessment
    - Mental simulation (5 rounds max) with risk identification
    - Produces execution-plan.toon with ≥95% success probability
    - Subagent context isolation model: taskReturns ≤500 tokens each
  - New `/plan` command - Invoke flutter-impl-planner with spec and constraint paths
  - New `/do` command - Execute execution-plan.toon files
    - Runs tasks phase-by-phase with parallel group support
    - Clean emoji-based progress reporting (no tree characters)
    - Orchestrator context protection via minimal taskReturns
    - Checkpoint validation between phases
  - Plugin now has 13 specialized agents

### Changed
- **exe plugin** (v1.4.0 → v1.4.1) - execution-planner agent improvements
- Marketplace version bumped to 2.21.0

## [2.20.0] - 2025-12-18

### Added
- **impl-flutter plugin** (v2.8.0 → v2.9.0) - New `flutter-gen-ui` agent for Generative UI
  - Implements LLM-generated dynamic interfaces using flutter/genui ecosystem
  - Research-first disposition: never guesses, admits uncertainty, researches when stuck
  - Knows theoretical foundations: Google Research paper, NN/g outcome-oriented design
  - Covers genui, genui_firebase_ai, genui_google_generative_ai, genui_a2ui packages
  - Collaborative pairing workflow with confidence-rated outputs
  - Plugin now has 12 specialized agents
- Marketplace version bumped to 2.20.0

## [2.19.0] - 2025-12-18

### Changed
- **impl-flutter plugin** (v2.7.0 → v2.8.0) - Renamed and optimized flutter-ux-widget agent
  - Renamed `flutter-ux` → `flutter-ux-widget` for clearer widget/rendering focus
  - Complete rewrite as TDD-first specialist (widget tests are "the sword")
  - Added proactive invocation for ANY widget implementation, not just debugging
  - Condensed from 731 → 163 lines (78% smaller) to preserve context for actual work
  - Added non-obvious gotchas table: Opacity trap, AnimatedBuilder leak, image memory, etc.
  - Added expert patterns: LeafRenderObjectWidget, Flow, CustomMultiChildLayout escalation
  - Added `<not_my_domain>` section with clear boundaries and handoff targets
  - Updated all agent handoff references across plugin
- Marketplace version bumped to 2.19.0

## [2.18.0] - 2025-12-18

### Changed
- **impl-flutter plugin** (v2.6.0 → v2.7.0) - schema.org vocabulary for project configuration
  - Updated `interact/start` command to use schema.org types for localDevelopment config
  - Updated `flutter-session-driver` agent to parse project-info.toon using Read tool
  - Config uses SoftwareApplication, ActivateAction, PropertyValue types
  - Replaced bash grep parsing with agent-based MCP workflow
- Marketplace version bumped to 2.18.0

## [2.17.0] - 2025-12-18

### Added
- **impl-flutter plugin** (v2.3.0 → v2.6.0) - Interactive session system and agent improvements
  - New `/interact/start` command - Start interactive debug or dev sessions on device
  - New `/interact/stop` command - Stop session and generate diagnostic reports
  - New `flutter-session-driver` agent - App lifecycle and DTD connection management
  - New `flutter-session-recorder` agent - Issue diagnosis with confidence-scored diagnostics
  - New `flutter-verifier` agent - Code review with categorized issues (critical/important/minor/nitpick)
  - Renamed `flutter-tester` → `flutter-e2e-tester` - Focused on E2E test execution, not code fixes
  - Updated `flutter-debugger` - Aligned methodology with philosophy (6 phases including REPRODUCE and TEST)
  - Debug sessions output `plan/sess-debug-MM-DD-HH-mm.md` with fix confidence scores
  - Dev sessions output `plan/sess-dev-MM-DD-HH-mm.md` with change logs
- Marketplace version bumped to 2.17.0

## [2.16.0] - 2025-12-17

### Added
- **exe plugin** (v1.3.0 → v1.4.0) - New `/exe:do` command for execution plan execution
  - Executes tasks from execution-plan.toon files phase-by-phase
  - Parallel task execution within parallel groups using Task tool
  - Real-time progress reporting: phase start, task completion, phase summary
  - Phase summaries show estimated vs actual tokens with variance percentage
  - TaskReturns displayed in phase summaries (testCoverage, testsPass, etc.)
  - Execution log output following execution-log.toon template
  - Checkpoint validation between phases with rollback support
  - Phase commits and final squash commit on completion
- Marketplace version bumped to 2.16.0

## [2.15.0] - 2025-12-17

### Changed
- **exe plugin** (v1.2.0 → v1.3.0) - Context discovery for execution plans
  - Added `<context-discovery>` section with mandatory discovery phase before drafting
  - Step 0: DISCOVER added to core-loop (search architecture dirs, base classes, utilities)
  - Architecture inputs: `**/architecture/**/*.md`, `**/ARCHITECTURE.md`, ADRs
  - Codebase inputs: base classes, interfaces, pattern examples, utilities
  - Task type → required context mapping table
  - Context sufficiency test: tasks must not require agent searching
  - Enhanced stress-testing with 4 context validation questions
  - New fix strategies for missing architecture/code context
  - Updated `context-assembly.md` with discovery patterns and richer examples
- Marketplace version bumped to 2.15.0

## [2.14.0] - 2025-12-17

### Changed
- **exe plugin** (v1.1.0 → v1.2.0) - Migrated to JetBrains MCP server tools
  - Replaced built-in tools (Read, Write, Edit, Glob, Grep, Bash) with JetBrains MCP equivalents
  - `get_file_text_by_path` for reading, `create_new_file` for writing, `replace_text_in_file` for editing
  - `find_files_by_glob` for file discovery, `search_in_files_by_text` for content search
  - `execute_terminal_command` for running validation scripts
  - Added tool mapping table in `<tool_efficiency>` section
  - Updated all examples and enforcement rules to reference JetBrains MCP tools
  - Updated `/exe:plan` command with JetBrains MCP tools in allowed-tools
- Marketplace version bumped to 2.14.0

## [2.13.0] - 2025-12-17

### Changed
- **exe plugin** (v1.0.0 → v1.1.0) - Token efficiency improvements for execution-planner agent
  - Added `<tool_efficiency>` section with three critical rules:
    - **File size pre-check**: Mandatory `wc -c` before Read operations; use offset/limit or Grep for files >100KB
    - **Parallel tool calls**: Batch independent Glob/Grep operations in single messages
    - **Edit vs Write**: Use Write only for initial creation; Edit for all refinements
  - Updated `<core-loop>` with file size check step and explicit "Use Edit, NOT Write" for fixes
  - Updated `<iteration-strategy>` with Edit examples for each fix type
  - Fixes MaxFileReadTokenExceededError (31564 tokens) encountered in production
  - Reduces refinement iteration token usage by ~50% (Edit vs full file rewrite)
- Marketplace version bumped to 2.13.0

## [2.12.0] - 2025-12-17

### Removed
- **plan plugin** - Removed TDD execution prompt generator plugin (functionality superseded by exe plugin)

### Changed
- Marketplace version bumped to 2.12.0

## [2.10.0] - 2025-12-17

### Changed
- **impl-flutter plugin** (v2.2.0 → v2.3.0) - Major `flutter-coder` agent rewrite
  - Cross-referenced with official docs: fpdart, Riverpod 3.0, fast_immutable_collections, mocktail
  - Fixed critical error: fpdart has NO IList—must use `fast_immutable_collections` with `.lock`
  - Fixed `ref.mounted` pattern—check BEFORE state update, not after
  - Added Do notation for TaskEither chaining (fpdart major feature)
  - Added `<clarification>` section: strict spec validation before coding
    - Code review scoped to implementation
    - CAN/CANNOT infer boundaries
    - Spec readiness check format
  - Added build_runner step: `fvm dart run build_runner build --delete-conflicting-outputs`
  - Added `registerFallbackValue` requirement for mocktail custom types
  - Added Records vs Freezed guidance
  - Zero tolerance: 0 errors, 0 warnings, 0 info
  - All code examples now lint-clean with proper class context
  - Explicit `very_good_analysis` workflow: write → analyze → fix → format → repeat
- Marketplace version bumped to 2.10.0

## [2.9.0] - 2025-12-16

### Changed
- **architect plugin** (v1.3.0 → v1.4.0) - Integrated ADR workflow
  - `adr-curator` updated with division of labor (writer creates, curator validates)
  - `adr-audit.py` aligned with `templates/adr-template.md` required sections
  - `/architect:adr` command now includes Phase 7 validation via curator
  - `adr-writer` and `adr-curator` cross-reference each other as partners
  - README updated with Hooks section documenting adr-audit.py usage
  - Fixed section detection to handle both H2 and H3 headers (for Consequences)
- Marketplace version bumped to 2.9.0

## [2.8.0] - 2025-12-16

### Added
- **architect plugin** (v1.2.0 → v1.3.0) - New `adr-audit.py` script for mechanical ADR validation
  - Naming convention validation with suggested fixes
  - Cross-reference extraction and bidirectionality checking
  - Template section presence detection
  - Review date staleness calculation
  - README index synchronization checking
  - Outputs structured JSON for agent consumption
  - Zero LLM tokens for detection phase

### Changed
- **adr-curator agent** updated to use `adr-audit.py` script
  - Replaced Glob/Grep with Bash for script execution
  - 5-phase methodology: Run script → Autonomous fixes → Batch questions → Apply decisions → Re-verify
  - Agent context preserved for judgment and editing, not scanning
- Marketplace version bumped to 2.8.0

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