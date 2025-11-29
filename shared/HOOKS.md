# Hook Execution Order

This document defines the execution order and behavior of all hooks in the lucid-toolkit plugin system.

## Overview

Claude Code hooks allow plugins to execute code in response to lifecycle events. When multiple plugins register hooks for the same event, execution order matters for maintaining data consistency and avoiding conflicts.

## Execution Order Rules

1. **Priority-based ordering**: Hooks with explicit `order` field execute first, sorted by ascending order value (1, 2, 3...)
2. **Alphabetical fallback**: Hooks without `order` execute alphabetically by plugin name
3. **Within-plugin ordering**: Multiple hooks in the same plugin execute in declaration order
4. **Failure behavior**: If a hook fails (non-zero exit), subsequent hooks may not execute

## Hook Inventory

### SessionStart Hooks

Execute when a new Claude Code session begins.

| Order | Plugin | Hook Script | Purpose | Files Modified |
|-------|--------|-------------|---------|----------------|
| 1 | context | `hooks/context_start.py` | Initialize session tracking | `.lucid/context_tracking.json` |

**Files Modified:**
- `.lucid/context_tracking.json` - Created/reset with new session data

**Execution Flow:**
1. Creates `.lucid/` directory if it doesn't exist
2. Initializes tracking with session metadata, metrics counters, and empty violations list
3. Sets status to "active"

**Conflicts:** None - operates on isolated file

---

### SessionEnd Hooks

Execute when a Claude Code session terminates.

| Order | Plugin | Hook Script | Purpose | Files Modified |
|-------|--------|-------------|---------|----------------|
| 1 | context | `hooks/context_end.py` | Finalize session tracking | `.lucid/context_tracking.json` |

**Files Modified:**
- `.lucid/context_tracking.json` - Updated with end time and final metrics

**Execution Flow:**
1. Reads existing tracking data
2. Sets endTime and status="completed"
3. Prints session summary to stderr

**Conflicts:** None - operates on isolated file

---

### PreToolUse Hooks

Execute before a tool is invoked by Claude Code.

| Order | Plugin | Hook Script | Trigger Condition | Purpose | Files Read |
|-------|--------|-------------|-------------------|---------|------------|
| 1 | workspace | `hooks/pre-commit-validation.py` | Tool=Bash AND command matches `git commit` | Validate workspace integrity before commits | `.lucid/workspace.json` |

**Files Read:**
- `.lucid/workspace.json` - Workspace configuration validation

**Execution Flow:**
1. Detects if running in a workspace (looks for `.lucid/` directory)
2. Validates workspace.json schema (required fields, project structure)
3. Validates cross-references (project dependencies)
4. Returns exit code 1 on failure, blocking the git commit

**Conflicts:** None - read-only validation

**Exit Code Behavior:**
- 0: Validation passed, commit proceeds
- 1: Validation failed, commit blocked

---

### PostToolUse Hooks

Execute after a tool completes successfully.

| Order | Plugin | Hook Script | Trigger Condition | Purpose | Files Modified |
|-------|--------|-------------|-------------------|---------|----------------|
| 1 | capability | `hooks/hooks/regenerate_snapshot.py` | Tool=Write/Edit AND file_path matches `capability_summary.json` | Regenerate markdown snapshot | `capabilities/SNAPSHOT.md` |

**Files Read:**
- `status/capability_summary.json` - Source data for snapshot generation

**Files Modified:**
- `capabilities/SNAPSHOT.md` - Human-readable capability snapshot

**Execution Flow:**
1. Reads updated capability_summary.json
2. Generates formatted markdown with:
   - Summary metrics (total capabilities, average maturity, activity states)
   - By-domain breakdown
   - Maturity distribution histogram
   - Blocked capabilities list
   - At-risk capabilities (top 5)
   - Health assessment with recommendations
3. Writes atomically to SNAPSHOT.md

**Conflicts:** None - operates on isolated file

---

## Adding New Hooks

Follow these guidelines when adding hooks to plugins:

### 1. Choose Event Type

- **SessionStart**: Initialization, setup, baseline establishment
- **SessionEnd**: Cleanup, finalization, summary generation
- **PreToolUse**: Validation, pre-flight checks, blocking operations
- **PostToolUse**: Side effects, derived data generation, notifications

### 2. Determine Execution Order

Consider these factors:

**Dependencies:**
- Does your hook depend on data created by another hook?
- If yes, ensure your hook runs AFTER the dependency

**Data Safety:**
- If multiple hooks modify related data, coordinate through:
  - File locking (use `lucid_cli_commons.locking.atomic_write`)
  - Separate files
  - Explicit ordering

**Performance:**
- Expensive operations should run later (higher order number)
- Fast validations should run early to fail fast

### 3. Add Order Field to settings.json

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 hooks/your_hook.py",
            "condition": "toolInput.file_path matches 'pattern'",
            "order": 2
          }
        ]
      }
    ]
  }
}
```

**Order Values:**
- 1: Critical early operations (initialization, validation)
- 2: Secondary operations (derived data generation)
- 3+: Optional operations (notifications, external integrations)

### 4. Document Dependencies

In your hook script, add a docstring header:

```python
#!/usr/bin/env python3
"""
Hook description.

Event: PostToolUse
Order: 2
Trigger: Tool=Write AND file_path matches 'summary.json'
Dependencies: Requires capability_track.json to exist
Modifies: status/reports/snapshot.md
"""
```

### 5. Handle Failures Gracefully

```python
def main() -> int:
    try:
        # Hook logic
        return 0  # Success
    except Exception as e:
        print(f"Hook failed: {e}", file=sys.stderr)
        return 1  # Failure
```

**Exit Code Guidelines:**
- 0: Success, continue execution
- 1: Failure, block operation (PreToolUse) or log error (PostToolUse)

### 6. Use Atomic Operations

For file modifications, always use atomic writes:

```python
from lucid_cli_commons.locking import atomic_write

with atomic_write(path, timeout=10) as f:
    f.write(content)
```

This prevents:
- Partial writes
- Race conditions
- Data corruption

### 7. Test Execution Order

Verify your hook runs in the correct sequence:

1. Add debug output: `print(f"[YourPlugin] Hook executing", file=sys.stderr)`
2. Trigger the event (e.g., commit, tool use)
3. Check stderr output for execution order
4. Verify no conflicts with other hooks

---

## Conflict Resolution

### Scenario 1: Multiple Hooks Modify Same File

**Problem:** Two PostToolUse hooks both write to `status/summary.json`

**Solutions:**
- **Separate files**: Each hook writes to its own file
- **Explicit ordering**: Hook A runs before Hook B (orders 1, 2)
- **Merge strategy**: Later hook reads and merges, doesn't overwrite

**Best Practice:** Avoid multiple hooks modifying the same file. Use derived files or subdirectories.

### Scenario 2: Validation Dependency

**Problem:** PreToolUse hook needs data initialized by SessionStart hook

**Solution:**
- SessionStart order=1 initializes data
- PreToolUse validates data exists, fails gracefully if missing

**Best Practice:** PreToolUse hooks should be defensive - check preconditions and provide clear error messages.

### Scenario 3: Performance Bottleneck

**Problem:** Slow PostToolUse hook delays every tool invocation

**Solutions:**
- **Conditional execution**: Use specific matchers/conditions to limit triggers
- **Async processing**: Write to queue file, process in background
- **Order optimization**: Run after fast hooks complete

**Best Practice:** Keep hooks fast (<100ms). Use background processing for expensive operations.

---

## Debugging Hooks

### Enable Debug Output

Set environment variable before running Claude Code:

```bash
export CLAUDE_DEBUG_HOOKS=1
claude
```

### Check Hook Execution

View stderr output:

```bash
# During session
tail -f ~/.claude/logs/claude-code.log

# After session
grep "\[.*Hook\]" ~/.claude/logs/claude-code.log
```

### Common Issues

**Hook not executing:**
- Check matcher pattern matches tool/command
- Verify condition evaluates to true
- Ensure hook script has execute permissions: `chmod +x hooks/your_hook.py`

**Hook fails silently:**
- Check exit code: `echo $?` after manual execution
- Add stderr output: `print(f"Error: {e}", file=sys.stderr)`
- Verify Python path and imports

**Wrong execution order:**
- Add `order` field to settings.json
- Verify no typos in plugin name (affects alphabetical fallback)
- Check other plugins' order values

---

## Hook Patterns

### Pattern 1: Initialization Hook (SessionStart)

```python
def main() -> int:
    """Initialize plugin state."""
    state_path = Path(".lucid") / "plugin_state.json"

    # Create directory
    state_path.parent.mkdir(exist_ok=True)

    # Initialize state
    state = {
        "initialized": datetime.now(timezone.utc).isoformat(),
        "metrics": {}
    }

    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)

    return 0
```

### Pattern 2: Validation Hook (PreToolUse)

```python
def main() -> int:
    """Validate before operation."""
    errors = []

    # Perform checks
    if not config_valid():
        errors.append("Invalid configuration")

    if not dependencies_met():
        errors.append("Missing dependencies")

    # Report and fail
    if errors:
        for error in errors:
            print(f"Validation error: {error}", file=sys.stderr)
        return 1

    return 0
```

### Pattern 3: Derived Data Hook (PostToolUse)

```python
def main() -> int:
    """Generate derived data after tool use."""
    try:
        # Read source data
        with open(source_path) as f:
            data = json.load(f)

        # Generate derived content
        derived = generate_derived(data)

        # Write atomically
        with atomic_write(output_path, timeout=10) as f:
            f.write(derived)

        return 0
    except Exception as e:
        print(f"Failed to generate derived data: {e}", file=sys.stderr)
        return 1
```

### Pattern 4: Cleanup Hook (SessionEnd)

```python
def main() -> int:
    """Clean up and finalize."""
    try:
        # Load state
        state = load_state()

        # Finalize
        state["completed"] = datetime.now(timezone.utc).isoformat()
        state["status"] = "completed"

        # Save
        save_state(state)

        # Print summary
        print(f"Session summary: {format_summary(state)}", file=sys.stderr)

        return 0
    except Exception as e:
        # Don't fail on cleanup errors
        print(f"Cleanup warning: {e}", file=sys.stderr)
        return 0  # Return success anyway
```

---

## Version History

- v1.1.0 (2025-01-29): Initial hook execution order documentation
  - Documented 4 hooks across 3 plugins
  - Established ordering conventions
  - Added conflict resolution guidelines
