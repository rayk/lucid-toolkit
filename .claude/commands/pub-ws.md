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

<version_file_registry>
## Files Requiring Version Updates

| File | Field/Location | Update Method |
|------|----------------|---------------|
| `plugins/ws/plugin.json` | `"version": "X.Y.Z"` | Source of truth - bump here first |
| `plugins/ws/CHANGELOG.md` | `## [X.Y.Z] - DATE` | Add new section |
| `plugins/ws/commands/version.md` | Embedded version display | Regenerate entire content |
| `plugins/ws/commands/enviro.md` | `object.targetVersion:` | Replace all occurrences |
| `plugins/ws/commands/enviro.md` | `softwareVersion to X.Y.Z` | Replace all occurrences |
| `plugins/ws/commands/enviro.md` | `Plugin: ws vX.Y.Z` | Replace all occurrences |

**Note**: Schema files (`templates/data/*.toon`) and Python package (`scripts/`) have SEPARATE version tracks and are NOT updated during plugin releases.
</version_file_registry>

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

## Phase 5.5: Sync version.md Command

14. **Update `plugins/ws/commands/version.md`** with embedded version info:
    - The version.md command must be self-contained (no dynamic @path references)
    - This is required because installed plugins can't resolve paths to source repo
    - Replace the entire content with current version and changelog entries
    - Format:
    ```markdown
    ---
    description: Display ws plugin version and recent changelog entries
    allowed-tools: []
    ---

    Display the following version information exactly as shown:

    ```
    ws Workspace Plugin v{new-version}

    ## What's New (v{new-version} - {date})

    {current version changelog entries}

    ## Previous Release (v{old-version})

    {previous version changelog entries, if any}
    ```
    ```

## Phase 5.6: Sync enviro.md Version

15. **Update `plugins/ws/commands/enviro.md`** with current version.

    Search and replace ALL occurrences of version strings:
    ```bash
    # Find all version references in enviro.md
    grep -n "0\.[0-9]\+\.[0-9]\+" plugins/ws/commands/enviro.md
    ```

    **Locations to update (use Edit tool with replace_all where applicable):**

    | Pattern | Context | Action |
    |---------|---------|--------|
    | `object.targetVersion: X.Y.Z` | migrate_mode section | Replace with new version |
    | `softwareVersion to X.Y.Z` | migrate_mode and repair_mode | Replace with new version |
    | `Plugin: ws vX.Y.Z` | output_format section | Replace with new version |

    **Use these Edit operations:**
    ```
    Edit(file_path="plugins/ws/commands/enviro.md",
         old_string="object.targetVersion: {old}",
         new_string="object.targetVersion: {new}")

    Edit(file_path="plugins/ws/commands/enviro.md",
         old_string="softwareVersion to {old}",
         new_string="softwareVersion to {new}",
         replace_all=true)

    Edit(file_path="plugins/ws/commands/enviro.md",
         old_string="Plugin: ws v{old}",
         new_string="Plugin: ws v{new}")
    ```

## Phase 5.7: Pre-Release Verification (MANDATORY)

16. **Verify all version references are in sync** before creating release commit:
    ```bash
    # Extract expected version from plugin.json (source of truth)
    EXPECTED=$(grep '"version"' plugins/ws/plugin.json | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
    echo "Expected version: $EXPECTED"
    echo ""

    # Check all version-sensitive files
    echo "=== Checking version.md ==="
    grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' plugins/ws/commands/version.md | head -3

    echo ""
    echo "=== Checking enviro.md ==="
    grep -E "targetVersion|softwareVersion|Plugin: ws v" plugins/ws/commands/enviro.md | grep -oE '[0-9]+\.[0-9]+\.[0-9]+'

    echo ""
    echo "=== Summary ==="
    # Count mismatches
    MISMATCHES=$(grep -r "$EXPECTED" plugins/ws/commands/version.md plugins/ws/commands/enviro.md 2>/dev/null | wc -l)
    echo "Files with correct version: $MISMATCHES references found"
    ```

    **ABORT if ANY version doesn't match $EXPECTED.**

    | File | Must Show |
    |------|-----------|
    | `version.md` line 9 | `v{EXPECTED}` |
    | `version.md` line 11 | `v{EXPECTED}` |
    | `enviro.md` targetVersion | `{EXPECTED}` |
    | `enviro.md` softwareVersion (x2) | `{EXPECTED}` |
    | `enviro.md` Plugin: ws v | `{EXPECTED}` |

    **If mismatch found:**
    - version.md wrong → Go back to Phase 5.5
    - enviro.md wrong → Go back to Phase 5.6
    - Typo → Fix with Edit tool and re-verify

## Phase 6: Release Commit

17. **Stage version, changelog, version command, and enviro command**:
    ```bash
    git add plugins/ws/plugin.json plugins/ws/CHANGELOG.md plugins/ws/commands/version.md plugins/ws/commands/enviro.md
    ```

19. **Create release commit**:
    ```bash
    git commit -m "$(cat <<'EOF'
    release(ws): v{new-version}

    Bump version {old} → {new}
    Update CHANGELOG.md with release notes
    Sync version.md and enviro.md

    🤖 Generated with [Claude Code](https://claude.ai/claude-code)

    Co-Authored-By: Claude <noreply@anthropic.com>
    EOF
    )"
    ```

## Phase 7: Push and Verify

20. **Final sync check**:
    ```bash
    git fetch origin
    git status -sb
    ```

21. **Push to remote**:
    ```bash
    git push origin $(git branch --show-current)
    ```

22. **Verify push succeeded**:
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
- **version.md regenerated with new version embedded**
- **enviro.md updated with new version in ALL locations**
- **Phase 5.7 verification passed - all versions match**
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
6. `plugins/ws/commands/version.md` has embedded version matching plugin.json
7. `plugins/ws/commands/enviro.md` has softwareVersion matching plugin.json
</verification>
