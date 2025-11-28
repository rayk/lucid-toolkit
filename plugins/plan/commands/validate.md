# /planner:validate

Validate an existing execution prompt or checkpoint.

## Usage

```
/planner:validate <path> [options]
```

## Arguments

- `<path>` - Path to execution prompt or checkpoint.json

## Options

- `--checkpoint` - Validate a checkpoint file for resume capability
- `--prompt` - Validate an execution prompt (default)
- `--strict` - Fail on warnings as well as errors

## Checkpoint Validation

When validating a checkpoint:

1. **File Existence**: All listed artifacts exist
2. **Test Status**: Tests pass for completed phases
3. **Schema Validity**: Checkpoint follows required schema
4. **Consistency**: Phase ordering is valid

```
/planner:validate ./output/checkpoint.json --checkpoint
```

### Checkpoint Schema

```json
{
  "checkpoint_version": "1.0",
  "system": "string",
  "last_completed_phase": "phase_N",
  "next_phase": "phase_N+1",
  "completed_phases": {},
  "pending_phases": [],
  "created_artifacts": {
    "files": [],
    "tests": []
  },
  "context_summary": "string",
  "resume_instructions": "string"
}
```

## Prompt Validation

When validating an execution prompt:

1. **Principle Coverage**: All 5 principles included
2. **Phase Completeness**: All 9 phases defined
3. **Dependency Declaration**: Dependencies properly categorized
4. **Timeout Specification**: All phases have timeouts
5. **Model Assignment**: Appropriate model for each phase

```
/planner:validate ./execution-prompt.md --prompt
```

## Output

### Success

```
Validation: PASS

Checklist:
✓ All 5 principles specified
✓ All 9 phases defined with timeouts
✓ Dependencies extracted and classified
✓ Token estimates provided
✓ Exit criteria extracted
✓ Tracking schemas included
✓ Reporting templates complete
```

### Failure

```
Validation: FAIL

Errors:
✗ Missing phase timeout: phase_4_features
✗ Dependency unclear: AuthService (pre-existing or created?)

Warnings:
⚠ No explicit exit criteria found (using implicit)
⚠ Token estimate missing for phase_7_debug
```

## Example

```
/planner:validate ./docs/execution-prompt.md --strict
```

## Behavior

When invoked:

1. Read the specified file
2. Determine type (checkpoint or prompt)
3. Apply appropriate validation rules
4. Report all findings
5. Exit with success/failure status
