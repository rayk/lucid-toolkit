# Session Manager Plugin

Automatic session lifecycle tracking for Claude Code workspaces, enabling work resumption, zombie session detection, and performance analytics.

## Overview

The Session Manager plugin tracks every Claude Code session from startup to exit, maintaining a comprehensive history in `status/sessions_summary.json`. It provides automatic session lifecycle management through hooks, manual reconciliation via commands, and diagnostic access to Claude Code debug logs.

## Architecture

```
session-manager/
├── commands/         # Slash commands for manual operations
│   ├── info.md      # Display current session info and recent activity
│   ├── update.md    # Reconcile sessions from transcripts/logs
│   └── validate.md  # Validate session data integrity
├── skills/
│   └── get-claude-logs/  # Access Claude Code debug logs for diagnostics
├── hooks/
│   └── session_summary/  # Automatic lifecycle tracking
│       ├── hooks/
│       │   ├── session_start.py  # Initialize session on startup
│       │   └── session_end.py    # Finalize session on exit
│       ├── lib/                  # Core session management
│       │   ├── session_manager.py      # CRUD operations on sessions_summary.json
│       │   ├── session_tracking.py     # Session entry creation/updates
│       │   ├── session_validator.py    # Schema validation
│       │   ├── stale_detector.py       # Zombie session detection
│       │   ├── reconciliator.py        # Backfill from transcripts
│       │   ├── accomplishments.py      # Git commit parsing
│       │   ├── transcript_parser.py    # Parse conversation JSON
│       │   └── config.py               # Configuration management
│       ├── tests/                      # Comprehensive test suite
│       │   ├── unit/              # 10 unit tests
│       │   └── integration/       # 4 integration tests
│       └── reconcile_cli.py       # Standalone reconciliation tool
├── scripts/
│   ├── status_line.py        # Generate session status for CLI prompt
│   └── status_line_debug.py  # Debug version with verbose output
└── schemas/
    └── session_summary_schema.json  # JSON Schema v1.1.0

31 Python modules | 14 test files
```

## Session Lifecycle

### Automatic Tracking

**SessionStart Hook** (runs on Claude Code startup):
1. Creates new session entry in `activeSessions`
2. Captures environment (git branch, commit, permission mode)
3. Detects session source (startup/resume/clear)
4. Initializes statistics counters
5. Updates summary aggregates

**SessionEnd Hook** (runs on Claude Code exit):
1. Parses conversation transcript for accomplishments
2. Extracts tool usage, files modified, git commits
3. Moves session from `activeSessions` to `recentHistory`
4. Updates indexes by outcome and branch
5. Prunes history older than 72 hours
6. Validates final schema compliance

### Session States

| State | Location | Meaning | Duration |
|-------|----------|---------|----------|
| **Active** | `activeSessions[]` | Currently running | Until exit |
| **Recent** | `recentHistory[]` | Completed sessions | 72 hours |
| **Stale** | `activeSessions[]` | No activity >1h | Until reconciliation |
| **Archived** | Pruned | Older than 72h | Deleted |

### Zombie Session Detection

Stale sessions indicate crashes or improper exits:
- Detected if `lastActivityAt` is >1 hour old
- Flagged in `/session:info` output
- Cleaned up by `/session:update` reconciliation
- Preserved in logs for crash analysis

## Commands

### `/session:info`
Display comprehensive session information:
- Current session ID, duration, git context
- Statistics (events, files, tasks, commits, subagents)
- Top 5 tool usage counts
- Focused outcomes (if any)
- Last session summary
- Recent activity (last 3-5 sessions)
- Stale session warnings

**Use when:**
- Resuming work to see what was accomplished
- Checking current session context
- Debugging session tracking issues

### `/session:update`
Run reconciliation to fix session data:
- Detect and cleanup stale sessions
- Backfill missing statistics from transcripts
- Move ended sessions to history
- Validate data integrity

**Use when:**
- Zombie sessions detected
- After Claude Code crash
- Session data appears inconsistent
- As part of `/up` workspace update

**Invokes:** `reconcile_cli.py --verbose`

### `/session:validate`
Validate session data health:
- Schema compliance check
- Cross-reference integrity
- Stale session detection
- Orphaned session cleanup

**Use when:**
- After manual edits to sessions_summary.json
- Debugging reconciliation failures
- Before committing session tracking changes

## Skills

### `get-claude-logs`
Access and analyze Claude Code debug logs efficiently.

**Capabilities:**
- Read structured debug logs
- Filter by session ID, timestamp, severity
- Parse error messages and stack traces
- Correlate logs with session events

**Use when:**
- Hook execution failures
- Session tracking anomalies
- MCP integration issues
- Performance debugging

See `skills/get-claude-logs/SKILL.md` for detailed usage.

## Hook Implementation

### Core Modules

**session_manager.py** - CRUD operations:
- `load()` - Read sessions_summary.json with locking
- `save()` - Atomic write with schema validation
- `get_session()` - Retrieve session by ID
- `update_session()` - Modify session fields
- `delete_session()` - Remove from tracking

**session_tracking.py** - Session lifecycle:
- `create_session_entry()` - Initialize new session
- `calculate_summary_stats()` - Aggregate metrics
- `update_indexes()` - Maintain outcome/branch indexes
- `prune_old_history()` - Remove >72h entries

**reconciliator.py** - Backfill engine:
- `reconcile_sessions()` - Main reconciliation workflow
- `backfill_from_transcript()` - Parse conversation JSON
- `detect_stale_sessions()` - Find zombies
- `cleanup_orphaned_sessions()` - Remove invalid entries

**stale_detector.py** - Zombie detection:
- `is_stale(session)` - Check if inactive >1h
- `get_stale_sessions()` - Find all zombies
- `stale_to_history()` - Convert to completed session

### Integration Points

**Common dependencies** (from workspace):
- `common.paths.WorkspacePaths` - Path resolution
- `common.locking.atomic_write` - Safe file operations
- `common.validation.SchemaValidator` - Schema enforcement
- `common.git_utils.GitInfo` - Git metadata capture

**Transcript parsing:**
- Conversation JSON from `~/.claudeCode/conversations/{sessionId}.json`
- Tool usage extraction via regex patterns
- File modification tracking from Edit/Write tools
- Git commit detection from Bash tool output

**Schema validation:**
- All writes validated against `session_summary_schema.json`
- Required fields enforced
- Type checking for dates, integers, enums
- Version compatibility checks

## Scripts

### status_line.py
Generate session status for CLI prompt display.

**Output format:**
```
[Session 4m | 12 events | 2 outcomes]
```

**Usage:**
```bash
python3 scripts/status_line.py
```

**Integration:**
Add to shell prompt (e.g., Starship, PS1) for real-time session awareness.

### status_line_debug.py
Debug version with verbose output for troubleshooting.

**Shows:**
- Full session data structure
- Parsing logic steps
- Error messages with context

## Data Model

### sessions_summary.json Structure

```json
{
  "summary": {
    "activeSessionsCount": 1,
    "totalSessionsCompletedLast72Hours": 15,
    "currentFocusedOutcome": "005-ontology-workflow",
    "totalTokensConsumedLast72Hours": 450000,
    "totalDurationMinutesLast72Hours": 120,
    "lastUpdated": "2025-11-28T16:30:00Z"
  },
  "activeSessions": [
    {
      "sessionId": "abc123...",
      "sessionSource": "startup",
      "startedAt": "2025-11-28T14:00:00Z",
      "lastActivityAt": "2025-11-28T16:30:00Z",
      "environment": {
        "gitBranch": "master",
        "gitCommit": "6d6cc68",
        "permissionMode": "default"
      },
      "focusedOutcomes": ["005-ontology-workflow"],
      "events": [...],
      "statistics": {
        "filesModified": 12,
        "tasksCompleted": 3,
        "tasksFailed": 0,
        "gitCommits": 2,
        "subagentsLaunched": 1,
        "toolUsageCounts": {"Read": 45, "Edit": 23}
      }
    }
  ],
  "lastWorked": {
    "accomplishments": "feat(session): add lifecycle tracking",
    "nextSteps": "Test reconciliation workflow",
    "durationMinutes": 30
  },
  "recentHistory": [...],
  "indexByOutcome": {...},
  "indexByBranch": {...}
}
```

### Key Fields

**summary** - Aggregated metrics:
- `activeSessionsCount` - Running sessions
- `currentFocusedOutcome` - Active work context
- `totalTokensConsumedLast72Hours` - Resource usage
- `totalDurationMinutesLast72Hours` - Time investment

**activeSessions** - Ephemeral session data:
- Created by SessionStart hook
- Updated on every tool call
- Moved to history by SessionEnd hook
- Stale if `lastActivityAt` >1h old

**recentHistory** - Completed sessions (72h):
- Enables work resumption context
- Powers `/session:info` recent activity
- Indexed by outcome and branch
- Pruned automatically

**Indexes** - Fast lookups:
- `indexByOutcome` - Sessions per outcome ID
- `indexByBranch` - Sessions per git branch

## Testing

### Test Coverage

**Unit tests** (10 files):
- `test_session_manager.py` - CRUD operations
- `test_session_tracking.py` - Lifecycle methods
- `test_session_validator.py` - Schema validation
- `test_stale_detector.py` - Zombie detection
- `test_reconciliator.py` - Backfill logic
- `test_accomplishments.py` - Git parsing
- `test_transcript_parser.py` - JSON parsing
- `test_config.py` - Configuration loading
- `test_session_start.py` - Hook initialization
- `test_session_end.py` - Hook finalization

**Integration tests** (4 files):
- `test_full_lifecycle.py` - Start → End workflow
- `test_concurrent_sessions.py` - Multi-session handling
- `test_reconciliation_flow.py` - Backfill scenarios
- `test_session_end_transcript_integration.py` - Transcript parsing

### Running Tests

```bash
cd /Users/rayk/Projects/lucid-toolkit/plugins/session-manager

# Run all tests
pytest hooks/session_summary/tests/

# Run unit tests only
pytest hooks/session_summary/tests/unit/

# Run integration tests
pytest hooks/session_summary/tests/integration/

# Run with coverage
pytest --cov=hooks/session_summary/lib hooks/session_summary/tests/
```

## Configuration

### Workspace Integration

**Required paths:**
- `status/sessions_summary.json` - Session data file
- `schemas/session_summary_schema.json` - Validation schema
- `~/.claudeCode/conversations/{sessionId}.json` - Conversation transcripts

**Hook registration** (in `.claude-plugin/main.py`):
```python
from session_summary.hooks.session_start import session_start_hook
from session_summary.hooks.session_end import session_end_hook

HOOKS = {
    "session_start": session_start_hook,
    "session_end": session_end_hook
}
```

### Environment Variables

- `WORKSPACE_ROOT` - Override workspace path (defaults to git repo root)
- `SESSION_SUMMARY_DEBUG` - Enable verbose logging

## Troubleshooting

### Common Issues

**Stale sessions accumulate:**
- Run `/session:update` to reconcile
- Check for Claude Code crashes in logs
- Verify SessionEnd hook is executing

**Statistics missing:**
- Ensure SessionEnd hook has transcript access
- Check `~/.claudeCode/conversations/` permissions
- Run `/session:update` to backfill

**Schema validation failures:**
- Verify schema version compatibility
- Check for manual edits to sessions_summary.json
- Run `/session:validate` to identify issues

**Reconciliation timeouts:**
- Reduce transcript parsing scope
- Archive old conversation files
- Increase timeout in config

### Debug Workflow

1. Run `/session:info` to see current state
2. Check logs with `get-claude-logs` skill
3. Run `/session:validate` for integrity check
4. Execute `/session:update` to reconcile
5. Verify fix with `/session:info` again

## Performance

**SessionStart hook:** <50ms
- Minimal file I/O
- No transcript parsing
- Cached git metadata

**SessionEnd hook:** 100-500ms
- Transcript parsing (largest cost)
- Regex-based extraction
- Atomic write with validation

**Reconciliation:** 1-5 seconds
- Parses all transcripts in 72h window
- Rebuilds indexes
- Validates all sessions

**Optimization tips:**
- Archive old conversation files
- Reduce `recentHistory` retention window
- Run reconciliation during idle time
- Use status_line.py caching

## Migration

### From Manual Session Tracking

1. Install plugin in workspace
2. Run `/session:update` to backfill from existing transcripts
3. Verify with `/session:info`
4. Configure status line integration (optional)

### Schema Updates

When updating `session_summary_schema.json`:
1. Increment `schemaVersion`
2. Add migration logic to `session_manager.py`
3. Run `/session:validate` to check compatibility
4. Update tests to match new schema

## Dependencies

**Python 3.8+**

**Standard library:**
- `json`, `pathlib`, `datetime`, `typing`
- `re`, `subprocess`, `os`

**Common workspace modules:**
- `common.paths` - Path resolution
- `common.locking` - File locking
- `common.validation` - Schema validation
- `common.git_utils` - Git integration

**No external dependencies** - Pure Python implementation for portability.

## Contributing

### Adding Session Metrics

1. Update `session_summary_schema.json` with new field
2. Add field to `create_session_entry()` in `session_tracking.py`
3. Update extraction logic in `transcript_parser.py`
4. Add tests to verify metric capture
5. Update this README with field documentation

### Extending Reconciliation

1. Add new reconciliator in `lib/` (e.g., `mcp_reconciliator.py`)
2. Register in `reconcile_cli.py` workflow
3. Add integration test
4. Document in README

## License

Part of lucid-toolkit workspace. See top-level LICENSE.

## References

- **Schema:** `schemas/session_summary_schema.json`
- **Commands:** `commands/*.md`
- **Skill:** `skills/get-claude-logs/SKILL.md`
- **Tests:** `hooks/session_summary/tests/`
- **Main implementation:** `hooks/session_summary/lib/session_manager.py`
