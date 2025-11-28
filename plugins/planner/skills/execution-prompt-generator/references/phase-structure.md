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
│  Phase 5: Integration (sonnet)                                  │
│     ↓                                                           │
│  Phase 6: Verification                                          │
│     ↓                                                           │
│  Phase 7: Debug (opus, if needed)                               │
│     ↓                                                           │
│  Phase 8: Cross-Check & Report (parallel + opus)                │
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

**Model**: sonnet
**Timeout**: 5 minutes
**Prerequisites**: Phase 4 complete

Tasks:
1. Update `__init__.py` exports
2. Verify cross-module imports
3. Run full test suite

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

**Model**: sonnet (parallel) + opus (analysis)
**Timeout**: 30 minutes

Tasks:
1. Spawn 8 parallel cross-check agents
2. Collect all results
3. Fix failures (max 3 attempts each)
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
