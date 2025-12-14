# Explore-then-Implement Workflow

Evidence-based workflow pattern for effective multi-agent implementation.

## The Pattern

From session analysis (successful 5-agent implementations):

```
1. EXPLORE  → Delegate understanding to Explore agents
2. REVIEW   → Human reviews exploration findings
3. IMPLEMENT → Use specialized agents per phase
4. VERIFY   → Test and validate
```

## Why This Works

- Each agent has isolated context (no pollution)
- Main context reserved for coordination
- Parallel execution possible
- Clear phase boundaries for review

## Example: Feature Implementation

### Phase 1: Exploration

```
Task(Explore): "Find existing auth patterns, user model, and infrastructure"
Task(Explore): "Identify all files that will need modification"
```

Both tasks run in parallel, returning focused findings.

### Phase 2: Human Review

Review exploration results:
- Identify approach and sequence
- Confirm file list is complete
- Note any dependencies between changes

### Phase 3: Phased Implementation

For Flutter projects:
```
Task(impl-flutter:flutter-env): "Set up Firebase Auth dependencies"
Task(impl-flutter:flutter-data): "Create auth service and state providers"
Task(impl-flutter:flutter-ux): "Implement login/signup UI screens"
Task(impl-flutter:flutter-coder): "Wire auth flow and navigation"
```

For general projects:
```
Task(general-purpose): "Implement data layer changes"
Task(general-purpose): "Update API endpoints"
Task(general-purpose): "Add UI components"
```

### Phase 4: Verification

```
Task(impl-flutter:flutter-tester): "Write auth flow integration tests"
```

Or for general:
```
Task(general-purpose): "Run test suite and verify changes"
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Direct implementation without exploration | Context exhaustion, missed files | Always explore first |
| Sequential single-agent work | Slow, context-heavy | Parallelize independent work |
| Main context does all editing | Context exhaustion | Delegate edit sequences |
| Skipping review phase | Rework, missed requirements | Always pause for human review |

## When to Use This Pattern

Use explore-then-implement for:
- New feature implementation
- Cross-cutting refactoring
- Bug fixes with unclear scope
- Any task touching 3+ files

Skip for:
- Single-file changes with known location
- Simple, well-scoped edits
- Direct answers to questions

## Progress Coordination

For complex implementations, use `progress.md`:

```markdown
# Progress Log

## Phase: Implementation

### Active
- [ ] Auth service setup (flutter-data) - agent-id-123

### Completed
- [x] Exploration - found 8 files need modification
- [x] Dependencies installed - Firebase Auth 5.0

### Blocked
- [ ] OAuth provider config - waiting on API keys
```

Each agent reads/writes to this file for coordination.

## Session Evidence

This pattern emerged from analyzing successful sessions:

- **Session a4dde869**: 5 agents, clean handoffs
  ```
  Task(Explore) → Task(Explore) → flutter-env → flutter-data → flutter-ux → flutter-coder
  ```

- **Session metrics**:
  - Delegation rate: 47%
  - Context at completion: 68%
  - Zero compaction events
