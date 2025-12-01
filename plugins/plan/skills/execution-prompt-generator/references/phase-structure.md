# Phase Structure Reference

## Execution Phases Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXECUTION PHASE FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 0: Setup & Validation                                    │
│     ↓                                                           │
│  Phase 1: Scaffolding (haiku)                                   │
│     ↓                                                           │
│  Phase 2: Foundation TDD (sonnet)                               │
│     ↓                                                           │
│  Phase 3: Core TDD (sonnet)                                     │
│     ↓                                                           │
│  Phase 4: Features TDD (sonnet, parallel)                       │
│     ↓                                                           │
│  Phase 5: Integration (haiku + sonnet)                          │
│     ↓                                                           │
│  Phase 6: Verification                                          │
│     ↓                                                           │
│  Phase 7: Debug (opus, if needed)                               │
│     ↓                                                           │
│  Phase 8: Cross-Check & Report (haiku + sonnet + opus)          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Phase Specifications

### Phase 0: Setup & Validation

**Model**: Orchestrator (no agent)
**Timeout**: 2 minutes

Tasks:
1. Check for checkpoint.json - resume if valid
2. Record EXECUTION_START_COMMIT
3. Run git safety checks
4. Verify external libraries
5. Verify pre-existing dependencies
6. Create status.json, audit_trail.json
7. Initialize token tracking

### Phase 1: Scaffolding

**Model**: haiku (batched)
**Timeout**: 3 minutes
**Estimated tokens**: ~5,000

Single haiku agent creates all scaffolding:
- Directory structure
- Stub implementation files
- Empty test files with imports
- `__init__.py` exports

### Phase 2: Foundation TDD

**Model**: sonnet
**Timeout**: 15 minutes
**Prerequisites**: Phase 1 complete
**Estimated tokens**: ~20,000

For each foundation type (types, errors, config):
1. RED: Write failing tests
2. GREEN: Implement minimally
3. REFACTOR: Add LLM-optimized docs

### Phase 3: Core TDD

**Model**: sonnet
**Timeout**: 20 minutes
**Prerequisites**: Phase 2 complete
**Estimated tokens**: ~30,000

TDD implementation of main service class.

### Phase 4: Features TDD

**Model**: sonnet (parallel)
**Timeout**: 15 minutes
**Prerequisites**: Phase 3 complete
**Estimated tokens**: ~25,000

Parallel agents for independent feature modules.
No cross-dependencies between feature modules.

### Phase 5: Integration

**Model**: haiku (mechanical) + sonnet (verification)
**Timeout**: 5 minutes
**Prerequisites**: Phase 4 complete

**Subtask 5a - Export Updates (haiku)**:
- Update `__init__.py` exports
- Generate re-export statements
- Mechanical file updates

**Subtask 5b - Verification (sonnet)**:
- Verify cross-module imports resolve
- Run full test suite
- Validate no circular dependencies

### Phase 6: Verification

**Model**: Orchestrator
**Timeout**: 5 minutes

Tasks:
1. Run type checker
2. Run all tests
3. Verify documentation complete
4. Write checkpoint

### Phase 7: Debug (Conditional)

**Model**: opus
**Timeout**: 10 minutes
**Trigger**: Verification fails after 3 sonnet attempts

Deep analysis of persistent failures.

### Phase 8: Cross-Check & Report

**Model**: haiku (mechanical checks) + sonnet (reasoning checks) + opus (analysis)
**Timeout**: 30 minutes

**Subtask 8a - Mechanical Checks (haiku, parallel)**:
Run command-based checks that require no reasoning:
- Lint check - execute linter, collect output
- Coverage check - run coverage tool, extract percentage
- Style check - run style checker, collect violations

**Subtask 8b - Reasoning Checks (sonnet, parallel)**:
Run checks requiring code understanding:
- Architecture check - verify patterns used correctly
- Requirements check - trace requirements to implementation
- Acceptance check - validate acceptance criteria
- Documentation check - verify completeness and accuracy
- Custom check - design-specific criteria

**Subtask 8c - Analysis & Fixes (sonnet/opus)**:
1. Collect all check results
2. Fix failures (sonnet, max 3 attempts each)
3. Escalate persistent failures to opus
4. Generate implementation_report.md
5. Generate execution_result.json
6. Git commit (if all pass)

## Checkpoint Schema

```json
{
  "checkpoint_version": "1.0",
  "system": "system_name",
  "last_completed_phase": "phase_3_core",
  "next_phase": "phase_4_features",
  "completed_phases": {
    "phase_0_setup": {"status": "completed", "completed_at": "..."},
    "phase_1_scaffolding": {"status": "completed", "completed_at": "..."},
    "phase_2_foundation": {"status": "completed", "completed_at": "..."},
    "phase_3_core": {"status": "completed", "completed_at": "..."}
  },
  "pending_phases": ["phase_4_features", "phase_5_integration", "..."],
  "created_artifacts": {
    "files": ["src/types.py", "src/service.py", "..."],
    "tests": ["tests/test_types.py", "..."]
  },
  "context_summary": "Brief summary of what was accomplished",
  "resume_instructions": "Start from Phase 4: Features TDD"
}
```

## Resume Detection

On execution start:
1. Check for `checkpoint.json` in output directory
2. If exists and valid:
   - Verify all listed artifacts exist
   - Skip to `next_phase`
   - Log: "Resuming from checkpoint: {last_completed_phase}"
3. If invalid or artifacts missing:
   - Log warning
   - Start from Phase 0

## Checkpoint Validation

```python
def validate_checkpoint(checkpoint):
    # Verify all created files exist
    for file in checkpoint["created_artifacts"]["files"]:
        if not exists(file):
            return {"valid": False, "reason": f"Missing: {file}"}

    # Verify tests pass for completed phases
    if checkpoint["last_completed_phase"] >= "phase_2":
        result = run("pytest tests/ -v --tb=short")
        if result.returncode != 0:
            return {"valid": False, "reason": "Tests failing"}

    return {"valid": True}
```
