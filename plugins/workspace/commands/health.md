---
description: Execute comprehensive workspace health check and reconciliation
argument-hint: [--fix | --verbose | --phase N]
---

<objective>
Perform systematic 8-phase health check on workspace structure, validate cross-references, and optionally fix issues automatically.

This command:
- Syncs directory structures with summary indexes
- Validates schema compliance
- Checks cross-reference integrity
- Detects stale and orphaned entries
- Reports issues by severity
- Optionally auto-fixes common problems
</objective>

<context>
Workspace home: @../../shared/workspaces/{workspace-id}/
Schemas: @schemas/workspace_schema.json, @schemas/project_map_schema.json
</context>

<process>
## 8-Phase Health Check

### Phase 1: Capability Directory-Summary Synchronization
- Scan `{workspace-home}/capabilities/` for directories
- Compare with `{workspace-home}/status/capability_summary.json`
- Detect missing `capability_track.json` files
- Validate schema compliance
- Detect orphaned summary entries
- **Fix**: Create skeleton track files and summary entries

### Phase 2: Outcome Directory-Summary Synchronization
- Scan `{workspace-home}/outcomes/queued|in-progress|completed/`
- Validate folder naming: `^[0-9]+-[a-z0-9-]+$`
- Check for missing `outcome_track.json` files
- Validate state consistency (location matches track file)
- Detect stale and orphaned entries
- **Fix**: Create skeleton files, recalculate summary stats

### Phase 3: Cross-Reference Integrity Validation
- Validate capability → outcome references
- Check outcome → capability references
- Validate composed capability relationships
- Verify composed weights sum to 1.0
- Detect broken references (entity doesn't exist)
- Detect stale references (entity moved state)
- **Fix**: Remove broken references, update paths

### Phase 4: Index Validation & Rebuild
- Validate and rebuild indexByType (atomic/composed)
- Validate indexByStatus (active/deprecated/merged)
- Rebuild indexByDomain from capabilities
- Rebuild indexByMaturity ranges
- Detect stale index entries
- **Fix**: Rebuild indexes from source data

### Phase 5: Temporal Health Checks
- Detect zombie sessions (>24h old)
- Flag old sessions (>12h)
- Identify stale history (>72h) for pruning
- Validate timestamps on summary files
- **Fix**: Prune old history, update timestamps

### Phase 6: Temp File Cleanup
- Clean files based on retention policy:
  - exec-report-*.md: 72 hours
  - agent-*.log: 12 hours
  - search-*.json: 6 hours
  - task-*.txt: 24 hours
- Respect preserve patterns
- **Fix**: Delete expired temp files

### Phase 7: Git Health Check
- Check uncommitted tracking files
- Validate remote tracking
- Detect merge conflicts
- **Report**: Warnings for uncommitted changes

### Phase 8: Comprehensive Health Report
- Generate severity-based report (CRITICAL/HIGH/MEDIUM/LOW/INFO)
- Show phase results with pass/fail
- Display workspace statistics
- Provide remediation recommendations
</process>

<options>
**--fix**: Automatically repair issues where possible
**--verbose**: Show detailed information during execution
**--phase N**: Run only specific phase (1-8)
**--dry-run**: Preview changes without applying
**--json**: Output report as JSON
</options>

<output_format>
## Default Output
```
/workspace:health: [HEALTHY|ISSUES] | Fixes: N | Cap: N (M%) | Out: Q/I/C | Proj: N

Phase Results:
✓ Phase 1: Capability sync (12ms)
✓ Phase 2: Outcome sync (8ms)
✗ Phase 3: Cross-refs - 2 issues found
✓ Phase 4: Indexes (5ms)
...

Issues Found: 2 (0 critical, 1 high, 1 medium)
- HIGH: Broken reference in outcome 005-auth
- MEDIUM: Stale index entry for deprecated capability

Recommendations:
- Run with --fix to repair automatically
```

## Verbose Output
Includes detailed per-file validation results and timing.

## JSON Output
```json
{
  "status": "ISSUES",
  "phases": [...],
  "issues": [...],
  "statistics": {...},
  "timestamp": "2025-01-15T10:00:00Z"
}
```
</output_format>

<success_criteria>
- All 8 phases executed
- Issues detected and categorized
- Fixes applied (if --fix)
- Report generated with actionable recommendations
- Exit code reflects health status
</success_criteria>
