---
description: Publish ws plugin to marketplace with version bump, changelog update, and git sync
allowed-tools: [Read, Edit, Write, Bash, Glob, Grep, AskUserQuestion]
---

<objective>
Publish the ws plugin by committing changes, bumping version, updating changelog, and pushing to remote.

This command ensures clean, documented releases with proper versioning and git synchronization.
</objective>

<context>
Plugin version: @plugins/ws/plugin.json
Changelog: @plugins/ws/CHANGELOG.md
Git status: !`git status --porcelain plugins/ws/`
Git remote status: !`git fetch origin && git status -sb`
Current branch: !`git branch --show-current`
Last commit: !`git log -1 --oneline`
Today: !`date +%Y-%m-%d`
</context>

<process>
## Phase 1: Pre-flight Checks

1. **Verify clean state outside ws plugin**:
   ```bash
   git status --porcelain | grep -v "plugins/ws/" | head -5
   ```
   - If other changes exist, warn user and ask to proceed or abort

2. **Check remote sync**:
   ```bash
   git fetch origin
   git status -sb
   ```
   - If behind remote: abort and advise pull first
   - If diverged: abort and advise manual resolution

3. **Verify on correct branch**:
   - Should be on `main` or a release branch
   - Warn if on feature branch

## Phase 2: Analyze Changes

4. **Gather ws plugin changes since last release**:
   ```bash
   git diff HEAD -- plugins/ws/
   git log --oneline -- plugins/ws/ | head -10
   ```

5. **Categorize changes**:
   - **Added**: New files, commands, skills, features
   - **Changed**: Modified behavior, updated logic
   - **Fixed**: Bug fixes, corrections
   - **Removed**: Deleted functionality

6. **Generate detailed commit message**:
   - Summary line: `feat(ws): <brief description>`
   - Body: List all changes with context
   - Why: Explain the purpose/benefit

## Phase 3: Initial Commit

7. **Stage ws plugin changes**:
   ```bash
   git add plugins/ws/
   ```

8. **Create detailed commit**:
   ```bash
   git commit -m "$(cat <<'EOF'
   feat(ws): <summary of changes>

   Changes:
   - <change 1 with context>
   - <change 2 with context>
   ...

   Why:
   <explanation of purpose and benefit>

   🤖 Generated with [Claude Code](https://claude.ai/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   EOF
   )"
   ```

## Phase 4: Version Bump

9. **Determine version bump type**:
   - **patch** (0.0.X): Bug fixes, minor changes
   - **minor** (0.X.0): New features, commands, non-breaking
   - **major** (X.0.0): Breaking changes, major overhaul

   Ask user if not obvious from changes.

10. **Read current version from plugin.json**:
    ```bash
    grep '"version"' plugins/ws/plugin.json
    ```

11. **Calculate new version** and update plugin.json

## Phase 5: Update Changelog

12. **Prepend new release entry to CHANGELOG.md**:
    ```markdown
    ## [X.Y.Z] - YYYY-MM-DD

    ### Added
    - <new features>

    ### Changed
    - <modifications>

    ### Fixed
    - <bug fixes>

    ### Removed
    - <deletions>
    ```

13. **Include detailed explanations** for each change

## Phase 6: Release Commit

14. **Stage version and changelog**:
    ```bash
    git add plugins/ws/plugin.json plugins/ws/CHANGELOG.md
    ```

15. **Create release commit**:
    ```bash
    git commit -m "$(cat <<'EOF'
    release(ws): v{new-version}

    Bump version {old} → {new}
    Update CHANGELOG.md with release notes

    🤖 Generated with [Claude Code](https://claude.ai/claude-code)

    Co-Authored-By: Claude <noreply@anthropic.com>
    EOF
    )"
    ```

## Phase 7: Push and Verify

16. **Final sync check**:
    ```bash
    git fetch origin
    git status -sb
    ```

17. **Push to remote**:
    ```bash
    git push origin $(git branch --show-current)
    ```

18. **Verify push succeeded**:
    ```bash
    git status -sb
    ```
    - Confirm local and remote are in sync
    - No commits ahead or behind
</process>

<version_bump_rules>
Determine bump type from changes:

| Change Type | Examples | Bump |
|-------------|----------|------|
| Bug fix | Fix typo, correct logic error | patch |
| Documentation | Update README, comments | patch |
| New command | Add /ws:enviro | minor |
| New skill | Add delegate skill | minor |
| New feature | Add scanning capability | minor |
| Schema change (compatible) | Add optional field | minor |
| Breaking change | Rename command, remove feature | major |
| Schema change (incompatible) | Change required fields | major |
</version_bump_rules>

<output_format>
```
## ws Plugin Published

### Changes Committed
{commit-hash} feat(ws): {summary}

### Version Bump
{old-version} → {new-version} ({bump-type})

### Changelog Updated
Added {n} entries for v{new-version}

### Git Status
✓ Committed: 2 commits
✓ Pushed: origin/{branch}
✓ Synced: local = remote

### Release Summary
- Commands: {count}
- Skills: {count}
- Version: {new-version}
- Date: {today}
```
</output_format>

<error_handling>
| Condition | Action |
|-----------|--------|
| Uncommitted changes outside ws/ | Warn, ask to proceed |
| Behind remote | Abort, advise `git pull` |
| Diverged from remote | Abort, advise manual merge |
| Push fails | Show error, advise resolution |
| No ws changes to commit | Skip Phase 3, proceed to version bump if requested |
</error_handling>

<success_criteria>
- All ws plugin changes committed with detailed message
- Version bumped appropriately in plugin.json
- CHANGELOG.md updated with categorized changes
- Release commit created
- Successfully pushed to remote
- Local and remote branches in sync
- No uncommitted changes remaining
</success_criteria>

<verification>
After completion, verify:
1. `git status` shows clean working tree
2. `git log -2 --oneline` shows both commits
3. `git status -sb` shows sync with remote
4. `plugins/ws/plugin.json` has new version
5. `plugins/ws/CHANGELOG.md` has new entry dated today
</verification>
