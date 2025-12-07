# Git Safety Protocol Reference

## Pre-Commit Validation

```bash
#!/bin/bash
# Step 0: Safety checks before any git operations

CURRENT_BRANCH=$(git branch --show-current)
PROTECTED_BRANCHES="main master"

# Check not on protected branch
for branch in $PROTECTED_BRANCHES; do
    if [[ "$CURRENT_BRANCH" == "$branch" ]]; then
        echo "ERROR: Cannot commit on protected branch: $branch"
        echo "Create a feature branch first: git checkout -b feature/your-feature"
        exit 1
    fi
done

# Check for uncommitted changes that aren't ours
UNCOMMITTED=$(git status --porcelain | grep -v "^[AM]" | wc -l)
if [[ "$UNCOMMITTED" -gt 0 ]]; then
    echo "WARNING: Uncommitted changes exist that weren't created by this execution"
    git status --short
fi

# Verify we have a clean starting point recorded
if [[ -z "$EXECUTION_START_COMMIT" ]]; then
    export EXECUTION_START_COMMIT=$(git rev-parse HEAD)
    echo "Recorded start commit: $EXECUTION_START_COMMIT"
fi

echo "Git safety checks passed"
```

## Commit Protocol

```bash
# Step 1: Verify start commit still exists
if ! git rev-parse "$EXECUTION_START_COMMIT" >/dev/null 2>&1; then
    echo "ERROR: Start commit no longer exists. Cannot safely squash."
    exit 1
fi

# Step 2: Count commits to squash
COMMIT_COUNT=$(git rev-list.md --count ${EXECUTION_START_COMMIT}..HEAD)
echo "Commits to squash: $COMMIT_COUNT"

if [[ "$COMMIT_COUNT" -eq 0 ]]; then
    echo "No commits to squash - nothing was committed during execution"
    exit 0
fi

# Step 3: Squash commits
git reset --soft "$EXECUTION_START_COMMIT"
git add -A

# Step 4: Create comprehensive commit
git commit -m "$(cat <<'EOF'
[type]: Implement [system_name] via TDD

## Summary
[2-3 sentence summary]

## Components
- [component1]: [description]
- [component2]: [description]

## Testing
- Test Cases: [count]
- Coverage: [X]%

## Cross-Check Results
- Lint: PASS
- Coverage: [X]%
- Requirements: [N]/[M] verified

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## Rollback Capability

```bash
# If commit fails or needs rollback
git reset --hard "$EXECUTION_START_COMMIT"
echo "Rolled back to: $EXECUTION_START_COMMIT"
```

## Safety Rules

1. **NEVER** commit directly to `main` or `master`
2. **NEVER** force push without explicit user approval
3. **NEVER** modify commits not created during this execution
4. **ALWAYS** record the starting commit before any changes
5. **ALWAYS** verify artifacts exist before committing
6. **ALWAYS** run tests before final commit

## Branch Naming Convention

For auto-generated branches:
```
feature/{system-name}-tdd-{date}
```

Example:
```
feature/neo4j-service-tdd-2025-11-28
```

## Commit Message Template

```
[type]: [short description]

## Summary
[What was implemented and why]

## Components
- [component]: [what it does]

## Testing
- Test Cases: [N]
- Coverage: [X]%

## Cross-Check Results
- Lint: [PASS/FAIL]
- Coverage: [X]%
- Style: [PASS/FAIL]
- Architecture: [PASS/FAIL]
- Requirements: [N/M verified]
- Documentation: [PASS/FAIL]

## Notes
[Any relevant notes about the implementation]

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Type Prefixes

| Type | Usage |
|------|-------|
| `feat` | New feature implementation |
| `fix` | Bug fix |
| `refactor` | Code refactoring (no behavior change) |
| `test` | Adding or modifying tests |
| `docs` | Documentation only |
| `chore` | Build/tooling changes |
