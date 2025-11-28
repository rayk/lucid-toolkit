# Cross-Check Protocol Reference

## Parallel Cross-Check Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 PARALLEL CROSS-CHECK PHASE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │   LINT      │ │  COVERAGE   │ │   STYLE     │               │
│  │  (sonnet)   │ │  (sonnet)   │ │  (sonnet)   │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
│                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ ARCHITECTURE│ │ REQUIREMENTS│ │    DOCS     │               │
│  │  (sonnet)   │ │  (sonnet)   │ │  (sonnet)   │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
│                                                                 │
│  ┌─────────────┐ ┌─────────────┐                               │
│  │ ACCEPTANCE  │ │   CUSTOM    │  ← From input docs            │
│  │  (sonnet)   │ │  (sonnet)   │                               │
│  └─────────────┘ └─────────────┘                               │
│                                                                 │
│         ↓ All results collected ↓                               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              ANALYSIS & FIX COORDINATION                 │   │
│  │                      (opus)                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Check Specifications

### Check 1: Lint Validation

- **Model**: sonnet
- **Timeout**: 5 minutes
- **Command**: Language-specific linter
- **Requirements**: ALL errors and warnings MUST be fixed
- **INFO messages**: Categorize and explain

### Check 2: Code Coverage

- **Model**: sonnet
- **Timeout**: 5 minutes
- **Threshold**: 80% minimum line coverage
- **Requirements**: If below threshold, identify uncovered lines, write tests

### Check 3: Style Compliance

- **Model**: sonnet
- **Timeout**: 3 minutes
- **Source**: Extract style requirements from input documents
- **Check**: Naming conventions, file organization, imports

### Check 4: Architecture Compliance

- **Model**: sonnet
- **Timeout**: 3 minutes
- **Source**: Extract patterns from design documents
- **Verify**: Required patterns used, prohibited patterns NOT used

### Check 5: Requirements Verification

- **Model**: sonnet
- **Timeout**: 5 minutes
- **Source**: Extract requirements from requirements.md
- **Verify**: Each FR-*, NFR-* has implementation and test

### Check 6: Acceptance Criteria

- **Model**: sonnet
- **Timeout**: 3 minutes
- **Behavior**: Skip if no AC defined in input documents

### Check 7: Documentation Completeness

- **Model**: sonnet
- **Timeout**: 3 minutes
- **Verify**: Every public symbol has LLM-optimized documentation

### Check 8: Custom Exit Criteria

- **Model**: sonnet
- **Timeout**: 3 minutes
- **Source**: Extract from "Exit Criteria", "Definition of Done", etc.

## Fix Attempt Protocol

When a check fails:

**Attempts 1-2**: sonnet tries to fix
```python
Task(
    model="sonnet",
    prompt="Fix: {check_name}, Failure: {details}, Location: {file}:{line}"
)
```

**Attempt 3**: opus with extended thinking
```python
Task(
    model="opus",
    prompt="""
    [EXTENDED THINKING REQUIRED]
    Previous fix attempts failed. Analyze deeply.
    Check: {check_name}
    Previous attempts: {attempt_1}, {attempt_2}
    Root cause analysis required.
    """
)
```

**After 3 failures**: Mark check as FAILED, continue other checks
**After all checks**: If ANY check FAILED, plan FAILS

## Timeout Handling

- Individual check timeout: 5 minutes max
- Fix attempt timeout: 3 minutes max
- Total Phase 8 timeout: 30 minutes max
- If timeout exceeded: Mark as TIMED_OUT, include in failure report

Use Bash tool's timeout parameter:
```python
Bash(command="pytest --cov=...", timeout=300000)  # 5 minutes in ms
```

## Parallel Execution with Fallback

### Primary: Parallel Agent Spawn

```python
# Spawn all checks in single message for parallel execution
checks = [
    Task(model="sonnet", prompt="LINT CHECK: ..."),
    Task(model="sonnet", prompt="COVERAGE CHECK: ..."),
    Task(model="sonnet", prompt="STYLE CHECK: ..."),
    Task(model="sonnet", prompt="ARCHITECTURE CHECK: ..."),
    Task(model="sonnet", prompt="REQUIREMENTS CHECK: ..."),
    Task(model="sonnet", prompt="ACCEPTANCE CHECK: ..."),
    Task(model="sonnet", prompt="DOCS CHECK: ..."),
    Task(model="sonnet", prompt="CUSTOM CHECK: ...")
]
# All spawned in single message = parallel execution
```

### Fallback: Sequential Execution

If parallel spawn fails:

```python
def execute_checks_sequential():
    """Fallback to sequential execution if parallel fails."""
    results = []
    for check in CHECKS:
        try:
            result = Task(
                model="sonnet",
                prompt=check.prompt,
                timeout=check.timeout * 2  # Extended timeout
            )
            results.append(result)
        except TimeoutError:
            results.append({"status": "TIMED_OUT", "check": check.name})
    return results
```

### Fallback Detection

```python
def execute_crosschecks():
    try:
        results = parallel_spawn(checks)
        return results
    except (SpawnError, TimeoutError) as e:
        log_warning(f"Parallel execution failed: {e}. Falling back to sequential.")
        audit_trail["notes"].append("Degraded to sequential execution")
        return execute_checks_sequential()
```
