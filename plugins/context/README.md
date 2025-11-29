# Context Manager Plugin

Session lifecycle tracking with context window conservation and systematic delegation protocols for Claude Code.

## Overview

The Context Manager plugin helps preserve Claude's finite context window by combining:

1. **Session Lifecycle Tracking** - Automatic session management with work resumption context
2. **Delegation Protocol** - Systematic rules for when to delegate work to subagents
3. **Context Conservation** - Token budget monitoring and optimization techniques

**Core Principle:** "Count operations before classifying. Delegate by default."

## Installation

```bash
# Add the marketplace (one-time setup)
/plugin marketplace add rayk/lucid-toolkit

# Install the context plugin
/plugin install context@lucid-toolkit

# Install required dependencies
cd shared/cli-commons && pip install -e .
```

**Prerequisites:**
- Python >=3.11
- Claude Code >=1.0.0
- The `cli-commons` shared library must be installed for hooks to function

## Commands

### `/context:info [--verbose]`
Display current session context and status including session ID, duration, statistics (events, files, tasks, tokens), context health indicators, focused outcomes, and stale session warnings.

### `/context:checkpoint [accomplishment summary]`
Create a manual checkpoint to preserve session state including accomplishments, key decisions, next steps, and statistics snapshot. Use before risky operations, after milestones, when context is large, or before switching focus.

### `/context:compact [--aggressive]`
Reduce context window usage by summarizing conversation segments, archiving intermediate results, and preserving only essential context. Use when token usage exceeds 60%, after multiple large file reads, or before complex tasks.

### `/context:budget [--forecast N]`
Display token budget status, consumption breakdown by category, delegation thresholds, and model selection recommendations. Optionally forecast token usage for N planned operations.

### `/context:update`
Reconcile context tracking data by detecting and cleaning up stale sessions, backfilling statistics from transcripts, and moving ended sessions to history. Supports `--strict`, `--dry-run`, and `--verbose` flags.

### `/context:validate`
Validate context tracking health by checking for missing transcripts, zombie sessions (>24h inactive), stale sessions (>12h), and data discrepancies. Provides remediation recommendations.

## Skills

### `delegate`
Systematic delegation decisions using the 4-step pre-response protocol:
1. **Transition Check** - Detect research → action mode shifts
2. **Decompose** - Split compound requests with "AND"/"then"
3. **Count Operations** - Determine exact tool call count (? = delegate)
4. **Visible Checkpoint** - Output `[N ops → direct|delegate]: rationale`

**Delegate when ANY apply:** location unknown, 3+ operations, multiple files, synthesis needed, unpredictable scope.

**Direct execution ONLY when ALL apply:** known file path, 1-2 operations certain, no exploration, single location.

### `conserve`
Context window optimization techniques:
- **TOON Format** - Token-Oriented Object Notation (~40% savings vs JSON)
- **Index-First Lookup** - Check index files before grepping
- **Minimal Subagent Context** - Goal + constraints only
- **Parallel Operations** - Batch independent tasks
- **Result Summarization** - Request 300-500 token responses

### `checkpoint`
Session tracking and work resumption:
- Automatic lifecycle hooks (start/end)
- 72-hour recent history window
- Stale session detection (>1h inactivity)
- Work resumption data (`lastWorked` with outcomes, decisions, next steps)
- Statistics parsed from conversation transcripts

### `get-claude-logs`
Efficient access to Claude Code debug logs for diagnosing hook failures, MCP issues, and session problems. Uses `tail` and `grep` (never Read tool). Recommends single comprehensive reads over incremental searches.

**Golden rule:** `tail -2000 ~/.claude/debug/latest` for most diagnostics.

## Token Budget Guidelines

| Operation Type | Budget | Model |
|----------------|--------|-------|
| File search, pattern matching | 1500 | haiku |
| Yes/no validation | 800 | haiku |
| Code analysis, flow tracing | 2000 | sonnet |
| Multi-file fix + commit | 2500 | sonnet |
| Synthesis, complex reasoning | 3000 | opus |

## Context Health Thresholds

| Usage | Status | Action |
|-------|--------|--------|
| <60% | HEALTHY | Normal operation |
| 60-80% | WARNING | Delegate 2+ operations |
| >80% | CRITICAL | Delegate all, run /context:compact |

## The Specificity Trap

**Critical anti-pattern:** Specific user input (error messages, function names) creates false confidence.

```
User: "Fix error 'ConfigError: path not found'"

❌ WRONG: "I know exactly what to search for, simple!"
✓ RIGHT: Grep + Read(s) + Edit = 3+ ops → DELEGATE
```

You know WHAT to find, not WHERE or HOW MANY locations. Treat specific mutations as exploration until locations are confirmed.

## Usage Examples

### Basic Session Info
```bash
/context:info
# Shows: session ID, duration, token usage, health status

/context:info --verbose
# Shows: full statistics, recent history, tool usage breakdown
```

### Token Budget Management
```bash
/context:budget
# Check current usage and thresholds

/context:budget --forecast 5
# Estimate tokens needed for 5 planned operations
```

### Manual Checkpoints
```bash
/context:checkpoint "Completed authentication module"
# Saves progress with custom description

/context:checkpoint
# Interactive prompt for accomplishments and next steps
```

### Context Compaction
```bash
/context:compact
# Standard summarization

/context:compact --aggressive
# Aggressive mode for >80% usage (targets 50% reduction)
```

### Session Maintenance
```bash
/context:validate
# Check for zombie/stale sessions

/context:update
# Clean up detected issues

/context:update --strict --verbose
# Aggressive cleanup with detailed output
```

## Output Formats

### TOON Format (~40% token savings)
```toon
files[3]{path,type,lines}:
  src/auth.ts,service,145
  src/token.ts,utility,89
  src/session.ts,service,234
```

### Delegation Checkpoints
```
[1 op → direct]: Reading known file path
[3 ops → delegate]: Multi-file exploration
[? ops → delegate]: Unknown scope
[MODE: research → action]: Transition marker
```

## Integration

Works seamlessly with other Lucid Toolkit plugins:

| Plugin | Integration |
|--------|-------------|
| **workspace** | Sessions track active workspace/project |
| **capability** | Sessions linked to capability work |
| **outcome** | Sessions linked to outcome progress |
| **think** | Mental models enhance delegation decisions |

## Path Structure

The context plugin uses a two-tier tracking system following workspace conventions:

| File Path | Purpose | Scope | Updated By |
|-----------|---------|-------|------------|
| `.lucid/current_session.json` | Active session state | Per-session | Hooks, commands |
| `status/sessions_summary.json` | All sessions index | Cross-session | Hooks, reconciliation |

**Current Session** (`.lucid/current_session.json`):
- Real-time tracking of the active session
- Updated throughout the session lifecycle
- Contains full metrics, checkpoints, and violations
- Preserved after session end for archival/recovery

**Sessions Summary** (`status/sessions_summary.json`):
- Central index of all sessions (active, completed, stale)
- Used for cross-session analysis and work resumption
- Enables zombie session detection
- Follows workspace `status/` pattern (like `capability_summary.json`, `outcome_summary.json`)

## Schema

Session tracking data conforms to two schemas:

- **`context_tracking_schema.json`** - Current session structure (`.lucid/current_session.json`)
  - Session metadata (ID, timestamps, status)
  - Metrics (tool calls, delegations, checkpoints, tokens saved)
  - Violations (protocol violations with severity levels)

- **`sessions_summary_schema.json`** - Sessions summary structure (`status/sessions_summary.json`)
  - activeSessions[] - Currently running sessions
  - completedSessions[] - Finalized sessions with metrics
  - staleSessions[] - Detected zombie/interrupted sessions

## File Structure

```
plugins/context/
├── plugin.json                  # Plugin metadata
├── README.md
├── commands/                    # Slash commands
│   ├── info.md
│   ├── checkpoint.md
│   ├── compact.md
│   ├── budget.md
│   ├── update.md
│   └── validate.md
├── skills/                      # Skills
│   ├── delegate/
│   ├── conserve/
│   ├── checkpoint/
│   └── get-claude-logs/
├── prompts/                     # Core protocol prompts
│   ├── pre-response-protocol.md
│   ├── operation-counting.md
│   └── token-budgets.md
├── hooks/                       # Lifecycle hooks
│   ├── context_start.py         # Initialize session tracking
│   └── context_end.py           # Finalize and archive session
└── schemas/
    ├── context_tracking_schema.json    # Current session schema
    └── sessions_summary_schema.json    # Sessions index schema
```

## Quick Reference

### Delegation Decision Matrix

| Request | Tool Count | Action |
|---------|-----------|--------|
| "Read src/auth.ts" | 1 | Direct (known path) |
| "Find where X happens" | 2+ | Delegate (unknown location) |
| "Fix getUserById" | 3+ | Delegate (find + analyze + edit) |
| "Add import to utils.ts" | 1 | Direct (known file, single op) |

### Model Selection

- **Haiku**: Searches, validations, lookups (1500 tokens)
- **Sonnet**: Analysis, multi-file fixes (2000-2500 tokens)
- **Opus**: Synthesis, strategy, novel architecture (3000+ tokens)
