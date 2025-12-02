# workspace_info

Python library for managing workspace-info.toon files. **Hook-first design**.

## Installation

```bash
cd plugins/ws/scripts
pip install -e .
```

## Status

**Phase 1: Complete** - Hook Infrastructure
- HookContext class for parsing Claude Code hook inputs
- run_hook decorator for minimal-boilerplate hook authoring
- Response helpers (success, warn, block)
- Full test coverage (12/12 tests passing)

**Phase 2: Pending** - Core WorkspaceInfo class
**Phase 3: Pending** - Section methods
**Phase 4: Pending** - CLI implementation
**Phase 5: Pending** - Integration and examples

## Quick Start: Writing a Hook

### Pattern 1: Using the Decorator (Simplest)

```python
#!/usr/bin/env python3
from workspace_info import run_hook

@run_hook
def main(ws, ctx):
    """Update workspace info on session start."""
    if ws.exists():
        ws.update_git_info()
        ws.update_timestamp()
        ws.record_session(ctx)

if __name__ == "__main__":
    main()
```

### Pattern 2: Explicit Control (When Needed)

```python
#!/usr/bin/env python3
from workspace_info import HookContext, WorkspaceInfo

def main():
    ctx = HookContext.from_stdin()

    # Early exit on irrelevant events
    if ctx.tool_name != "Edit":
        return ctx.success()

    # Process only outcome edits
    file_path = ctx.tool_input.get("file_path", "")
    if "outcomes/" not in file_path:
        return ctx.success()

    ws = WorkspaceInfo(ctx.project_dir)
    if ws.exists():
        ws.set_focus("my-outcome", "outcomes/in-progress/005", "ActiveActionStatus")

    return ctx.success()

if __name__ == "__main__":
    exit(main())
```

## HookContext API

| Method | Exit Code | When to Use |
|--------|-----------|-------------|
| `ctx.success()` | 0 | Normal completion |
| `ctx.success(context="...")` | 0 | Add info to Claude's context (SessionStart, UserPromptSubmit only) |
| `ctx.warn("...")` | 1 | Non-blocking warning |
| `ctx.block("...")` | 2 | Stop Claude's action (use sparingly!) |

## HookContext Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `ctx.session_id` | str \| None | Claude session ID |
| `ctx.hook_event` | str \| None | Event type (SessionStart, PostToolUse, etc.) |
| `ctx.tool_name` | str \| None | Tool being used (Edit, Bash, Read, etc.) |
| `ctx.tool_input` | dict | Tool parameters |
| `ctx.project_dir` | Path | Project root (from CLAUDE_PROJECT_DIR) |
| `ctx.log` | Logger | Writes to stderr with hook prefix |

## Testing

```bash
# Run all tests
pytest tests/workspace_info/test_hook.py -v

# Run with coverage
pytest tests/workspace_info/test_hook.py --cov=workspace_info.hook --cov-report=term-missing

# Run single test
pytest tests/workspace_info/test_hook.py::test_hook_context_from_stdin_with_full_json -v
```

## Tests Implemented (12/12 passing)

- test_hook_context_from_stdin_with_full_json
- test_hook_context_from_stdin_with_empty_input
- test_hook_context_from_stdin_with_malformed_json
- test_hook_context_uses_claude_project_dir_env
- test_hook_context_falls_back_to_cwd
- test_success_returns_zero
- test_success_with_context_adds_additional_context
- test_block_returns_two
- test_warn_returns_one
- test_run_hook_decorator_catches_exceptions
- test_run_hook_decorator_returns_exit_code_from_function
- test_run_hook_decorator_defaults_to_success

## Error Handling in Hooks

**Golden Rule: Never block Claude unless explicitly intended.**

```python
@run_hook
def main(ws, ctx):
    # The decorator catches all exceptions and returns success
    # This prevents your hook from breaking Claude's workflow

    if ws.exists():
        ws.update_git_info()  # Automatically times out after 5s

if __name__ == "__main__":
    main()
```

## Dependencies

- `lucid-cli-commons` - TOON parser, atomic writes
- `click` - CLI framework
- Python 3.11+
