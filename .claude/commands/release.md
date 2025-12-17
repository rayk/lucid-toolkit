---
description: Release changed plugins with version bumps, changelog update, commit, and push
allowed-tools: [Read, Edit, Bash]
---

<objective>
Release all changed plugins: detect changes, bump versions, update changelog, commit with descriptive message, push to remote.

This standardizes the release workflow ensuring version consistency across plugin.json, marketplace.json, and CHANGELOG.md.
</objective>

<context>
Git status: !`git status --porcelain`
Recent commits: !`git log --oneline -5`
Marketplace: @.claude-plugin/marketplace.json
Changelog: @CHANGELOG.md
</context>

<version_files>
Files requiring version sync:

| File | Purpose |
|------|---------|
| `plugins/{name}/plugin.json` | Plugin version (source of truth per plugin) |
| `.claude-plugin/marketplace.json` | Marketplace version + plugin version mirror |
| `CHANGELOG.md` | Human-readable release notes |
</version_files>

<workflow>
Execute these phases:

## Phase 1: Detect Changes (2 Bash calls, parallel)
```bash
# Call 1: Get changed files
git status --porcelain

# Call 2: Check remote sync
git fetch origin && git status -sb
```

**Analyze output:**
- Identify which plugins have changes (files in `plugins/{name}/`)
- If behind/diverged from remote: WARN user, ask to proceed
- If no changes: ABORT with "Nothing to release"

## Phase 2: Determine Version Bumps
For each changed plugin, determine bump type from changes:

| Change Type | Bump | Example |
|-------------|------|---------|
| Bug fix, optimization, docs | patch | 1.0.0 → 1.0.1 |
| New command/skill/agent/feature | minor | 1.0.0 → 1.1.0 |
| Breaking change, major rewrite | major | 1.0.0 → 2.0.0 |

**Marketplace version:** Always bump minor for any plugin changes.

## Phase 3: Read Current Versions (parallel Reads)
For each changed plugin:
```
Read(plugins/{name}/plugin.json)
```

Also read marketplace.json if not already in context.

## Phase 4: Bump Plugin Versions (parallel Edits)
For each changed plugin:
```
Edit(plugins/{name}/plugin.json,
     old_string='"version": "{old}"',
     new_string='"version": "{new}"')
```

## Phase 5: Update Marketplace (2 Edits)
```
# Bump marketplace version
Edit(.claude-plugin/marketplace.json,
     old_string='"version": "{old-marketplace}"',
     new_string='"version": "{new-marketplace}"')

# Mirror each changed plugin version
Edit(.claude-plugin/marketplace.json,
     old_string='name": "{plugin}",\n      "source": "./plugins/{plugin}",\n      "description": "...",\n      "version": "{old}"',
     new_string='name": "{plugin}",\n      "source": "./plugins/{plugin}",\n      "description": "...",\n      "version": "{new}"')
```

## Phase 6: Update CHANGELOG.md
Prepend new version section:

```markdown
## [{new-marketplace-version}] - {YYYY-MM-DD}

### Changed
- **{plugin} plugin** (v{old} → v{new}) - {summary of changes}
  - {bullet point for each significant change}
- Marketplace version bumped to {new-marketplace-version}
```

Use Edit to prepend after the header:
```
Edit(CHANGELOG.md,
     old_string='## [{previous-version}]',
     new_string='## [{new}] - {date}\n\n### Changed\n- ...\n\n## [{previous-version}]')
```

## Phase 7: Stage, Commit, Push (3 Bash calls)
```bash
# Stage all changes
git add -A

# Commit with descriptive message
git commit -m "$(cat <<'EOF'
release: {plugin1} v{new1}, {plugin2} v{new2}, ...

Changes:
- {plugin1}: {summary}
- {plugin2}: {summary}

Marketplace: v{old-mp} → v{new-mp}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"

# Push to remote
git push
```

## Phase 8: Verify (1 Bash call)
```bash
git status -sb && git log -1 --oneline
```
</workflow>

<bump_rules>
| Change Pattern | Bump Type |
|----------------|-----------|
| Fix typo, correct docs | patch |
| Optimize performance | patch |
| Add new command | minor |
| Add new skill | minor |
| Add new agent | minor |
| Major rewrite of agent | minor |
| Breaking API change | major |
| Remove functionality | major |
</bump_rules>

<changelog_format>
Follow Keep a Changelog format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing functionality

### Fixed
- Bug fixes

### Removed
- Removed features
```

Most releases use **### Changed** for plugin updates.
</changelog_format>

<output>
On success, display:

```
## Release Complete

{commit-hash} release: {plugins summary}

Plugins released:
- {plugin1}: v{old} → v{new} ({bump-type})
- {plugin2}: v{old} → v{new} ({bump-type})

Marketplace: v{old-mp} → v{new-mp}

✓ Committed and pushed to origin/main
```
</output>

<error_handling>
| Condition | Action |
|-----------|--------|
| No changes detected | ABORT: "Nothing to release" |
| Behind remote | WARN: "Behind remote, pull first?" |
| Diverged from remote | ABORT: "Diverged, resolve manually" |
| Edit fails (pattern not found) | Read file, retry with correct pattern |
| Push fails | Report error, suggest manual push |
</error_handling>

<success_criteria>
- All changed plugins have bumped versions in plugin.json
- Marketplace.json mirrors all plugin versions
- Marketplace version bumped
- CHANGELOG.md has new entry with today's date
- Single commit with descriptive message
- Changes pushed to remote
- `git status` shows clean working tree
</success_criteria>
