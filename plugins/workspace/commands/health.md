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

<execution_strategy>
## Parallel Execution Requirements

CRITICAL: Use parallel tool calls to maximize performance.

**Parallel Group A** (launch Phase 1 and Phase 2 simultaneously):
- Phase 1 and Phase 2 are INDEPENDENT - run them in a SINGLE message with multiple tool calls
- Use parallel Glob calls for capabilities/ and outcomes/ directories
- Use parallel Read calls for capability_summary.json and outcome_summary.json

**Sequential Group B** (wait for Group A to complete):
- Phase 3 depends on Phase 1+2 results
- Phase 4 depends on Phase 3 results
- These MUST run sequentially

**Parallel Group C** (launch Phases 5, 6, 7 simultaneously):
- These phases are INDEPENDENT of each other and of Group B
- Run in a SINGLE message with parallel tool calls:
  - Phase 5: Read sessions_summary.json, check timestamps
  - Phase 6: Glob for temp file patterns
  - Phase 7: Bash git status

**Final** (after all groups complete):
- Phase 8: Generate consolidated report

## Tool Call Pattern

Example for Group A:
```
Message 1: [Glob capabilities/**/*.json] + [Glob outcomes/**/*.json] + [Read capability_summary.json] + [Read outcome_summary.json]
```

Example for Group C:
```
Message N: [Read sessions_summary.json] + [Glob **/temp-*] + [Glob **/exec-report-*] + [Bash git status]
```
</execution_strategy>

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
- **Detect circular dependencies in capability prerequisites**:
  - For each capability, trace prerequisite chains recursively
  - Algorithm: Depth-first search with path tracking
  - If capability appears in its own prerequisite chain, report cycle
  - Show full cycle path: "A → B → C → A"
  - Report as HIGH severity issue
- Detect broken references (entity doesn't exist)
- Detect stale references (entity moved state)
- **Fix**: Remove broken references, update paths (circular dependencies require manual resolution)

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

<interactive_mode>
## User Interaction for Issues

When issues are detected during any phase (unless --batch flag is set):

1. Pause after the phase completes
2. Use AskUserQuestion with options:
   - **"Fix automatically"**: Apply the suggested fix and continue
   - **"Skip this"**: Record issue in report but don't fix, continue
   - **"Abort"**: Stop health check and show partial report

3. For CRITICAL severity issues, always prompt regardless of --batch flag

Example prompt after Phase 3 finds issues:
```
Question: "Phase 3 found 2 cross-reference issues. How should I proceed?"
Options:
- "Fix automatically" (apply fixes and continue)
- "Skip" (record issues, continue without fixing)
- "Abort" (stop and show report)
```
</interactive_mode>

<options>
**--fix**: Automatically repair issues where possible
**--verbose**: Show detailed information during execution
**--phase N**: Run only specific phase (1-8)
**--dry-run**: Preview changes without applying
**--json**: Output report as JSON
</options>

<output_format>
## TOON Format (for machine consumption)

```toon
@type: Action
@id: health-check/{ISO-date}
name: workspace-health
actionStatus: {CompletedActionStatus|FailedActionStatus}
x-fixes: {number-applied}
x-capabilities: {count}
x-avgMaturity: {0-100}

phases[8]{position,name,actionStatus,x-duration,x-issues}:
1,Capability sync,CompletedActionStatus,12,-
2,Outcome sync,CompletedActionStatus,8,-
3,Cross-refs,FailedActionStatus,15,2
4,Indexes,CompletedActionStatus,5,-
5,Temporal health,CompletedActionStatus,3,-
6,Temp cleanup,CompletedActionStatus,2,-
7,Git health,CompletedActionStatus,8,-
8,Report,CompletedActionStatus,1,-

issues[N]{x-severity,description}:
HIGH,Circular: auth-system -> user-management -> auth-system
MEDIUM,Stale index for deprecated capability
```

**Use TOON when:**
- Returning health status to subagents or orchestrators
- Providing data for automated remediation
- Integrating with monitoring systems
- Token efficiency is critical

## Default Markdown Output
```
/workspace:health: [HEALTHY|ISSUES] | Fixes: N | Cap: N (M%) | Out: Q/I/C | Proj: N

Phase Results:
✓ Phase 1: Capability sync (12ms)
✓ Phase 2: Outcome sync (8ms)
✗ Phase 3: Cross-refs - 2 issues found
✓ Phase 4: Indexes (5ms)
...

Issues Found: 3 (0 critical, 2 high, 1 medium)
- HIGH: Circular dependency detected: auth-system → user-management → role-based-access → auth-system
- HIGH: Broken reference in outcome 005-auth
- MEDIUM: Stale index entry for deprecated capability

Recommendations:
- Circular dependencies require manual resolution (remove one prerequisite link)
- Run with --fix to repair other issues automatically
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
