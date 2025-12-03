---
description: Publish ws plugin to marketplace with version bump, changelog update, and git sync
allowed-tools: [Edit, Write, Bash]
---

<objective>
Publish ws plugin: commit changes, bump version, update changelog, push to remote.
</objective>

<context>
Plugin: @plugins/ws/plugin.json
Changelog: @plugins/ws/CHANGELOG.md
</context>

<version_registry>
Files requiring version sync (old → new):

| File | Pattern | Method |
|------|---------|--------|
| `plugins/ws/plugin.json` | `"version": "X.Y.Z"` | Edit (source of truth) |
| `plugins/ws/CHANGELOG.md` | `## [X.Y.Z] - DATE` | Edit (prepend section) |
| `plugins/ws/commands/version.md` | entire file | Write (regenerate) |
| `plugins/ws/commands/enviro.md` | `object.targetVersion: X.Y.Z` | Edit |
| `plugins/ws/commands/enviro.md` | `softwareVersion to X.Y.Z` | Edit replace_all |
| `plugins/ws/commands/enviro.md` | `Plugin: ws vX.Y.Z` | Edit |
</version_registry>

<workflow>
Execute these phases with MINIMAL tool calls:

## Phase 1: Pre-flight (2 Bash calls, parallel)
```bash
# Call 1: Check for non-ws changes
git status --porcelain | grep -v "plugins/ws/" | head -5

# Call 2: Check remote sync
git fetch origin && git status -sb
```
- If behind/diverged: ABORT
- If non-ws changes: WARN, proceed

## Phase 2: Commit ws changes (2 Bash calls)
```bash
# Call 3: Stage
git add plugins/ws/

# Call 4: Commit with detailed message
git commit -m "..."
```

## Phase 3: Version bump (1 Edit)
Determine bump type from changes:
- patch: bug fixes, optimizations
- minor: new features, commands
- major: breaking changes

```
# Call 5: Edit plugin.json
Edit(old_string='"version": "{old}"', new_string='"version": "{new}"')
```

## Phase 4: Update all version files (5 tool calls, can parallelize Edits)
```
# Call 6: Edit CHANGELOG.md - prepend new section
Edit(old_string='## [{old}]', new_string='## [{new}] - {date}\n\n### Changed\n- ...\n\n## [{old}]')

# Call 7: Write version.md - full regeneration (no Read needed)
Write(file_path='plugins/ws/commands/version.md', content='...')

# Calls 8-10: Edit enviro.md (3 patterns)
Edit(old_string='object.targetVersion: {old}', new_string='object.targetVersion: {new}')
Edit(old_string='softwareVersion to {old}', new_string='softwareVersion to {new}', replace_all=true)
Edit(old_string='Plugin: ws v{old}', new_string='Plugin: ws v{new}')
```

## Phase 5: Release commit and push (4 Bash calls)
```bash
# Call 11: Stage version files
git add plugins/ws/plugin.json plugins/ws/CHANGELOG.md plugins/ws/commands/version.md plugins/ws/commands/enviro.md

# Call 12: Release commit
git commit -m "release(ws): v{new}"

# Call 13: Push
git push origin main

# Call 14: Verify
git status -sb && git log -2 --oneline
```
</workflow>

<version_md_template>
Generate this exact content for version.md (replace {new}, {date}, {changes}):

```markdown
---
description: Display ws plugin version and recent changelog entries
allowed-tools: []
---

Display the following version information exactly as shown:

\`\`\`
ws Workspace Plugin v{new}

## What's New (v{new} - {date})

{changes from this release - summarized}

## Previous Release (v{old})

{changes from previous release - summarized}
\`\`\`
```
</version_md_template>

<bump_rules>
| Change Type | Bump |
|-------------|------|
| Bug fix, optimization | patch |
| New command/skill/feature | minor |
| Breaking change | major |
</bump_rules>

<output>
```
## ws Plugin Published

{commit-hash} feat(ws): {summary}
{old} → {new} ({bump-type})

✓ Committed, pushed, synced
```
</output>

<constraints>
- Target: 14 tool calls total
- NO verification phase (we just made the edits)
- NO Read before Write for version.md
- NO grep before Edit for enviro.md
- Parallelize independent Bash/Edit calls where possible
</constraints>
