---
description: List all outcomes in the workspace with stage distribution and capability contributions
argument-hint: [--filter <stage|priority|capability>] [--verbose] [--no-sync]
---

<objective>
Display a summary list of all outcomes in the workspace by reading workspace-info.toon and outcomes-info.toon index files. Automatically syncs indexes via outcome-index-sync skill if data is stale or missing.
</objective>

<context>
Workspace info: `.claude/workspace-info.toon` - contains outcomes.path and summary counts
Outcomes index: `status/outcomes-info.toon` (from relatedData.outcomesInfo) - detailed outcome index
Sync skill: `outcome-index-sync` - regenerates indexes from outcome-statement.md files
Output patterns: Follow [output-patterns.md](../../references/output-patterns.md) for consistent formatting
</context>

<process>
1. **Load Workspace Context**:
   - Read `.claude/workspace-info.toon` from workspace root
   - Extract `outcomes.path` for source location
   - Extract `relatedData.outcomesInfo` path for index file
   - Extract `outcomes.summary{...}` table for stage counts

2. **Attempt Index Read**:
   - Try to read outcomes-info.toon from `relatedData.outcomesInfo` path
   - If file exists: extract `outcome.index{...}` table
   - If file missing or read fails: proceed to sync

3. **Check Index Freshness** (if outcomes-info.toon exists):
   - Compare `dateModified` timestamp against outcome-statement.md files
   - List all `outcome-statement.md` files across all stage directories:
     - `{outcomes.path}/queued/*/outcome-statement.md`
     - `{outcomes.path}/ready/*/outcome-statement.md`
     - `{outcomes.path}/in-progress/*/outcome-statement.md`
     - `{outcomes.path}/blocked/*/outcome-statement.md`
     - `{outcomes.path}/completed/*/outcome-statement.md`
   - Include nested child outcomes: `{outcomes.path}/*/*/outcome-statement.md`
   - Index is STALE if any statement file is newer than index dateModified

4. **Sync Decision**:
   - If `--no-sync` specified: skip sync, use available data (may be incomplete)
   - If index missing OR index stale:
     - Inform user: "Outcome index is out of sync. Syncing..."
     - Invoke sync skill:
       ```
       Skill("outcome-index-sync")
       ```
     - Re-read outcomes-info.toon after sync completes

5. **Parse Index Data**:
   - From outcomes-info.toon:
     - `numberOfItems` - total outcome count
     - `stages.summary{...}` table - count per stage
     - `outcome.index{...}` table - full outcome list
     - `capability.contributions{...}` table - aggregated contributions
     - `outcome.hierarchy{...}` table - parent/child relationships
     - `focus.*` properties - current focus outcome
   - Calculate derived statistics:
     - Parent vs child outcome counts
     - Outcomes by priority (P1/P2/P3)

6. **Apply Filters** (if $ARGUMENTS provided):
   - `--filter stage:<queued|ready|in-progress|blocked|completed>` - Show only outcomes in specified stage
   - `--filter priority:<P1|P2|P3>` - Filter by priority level
   - `--filter capability:<capability-id>` - Show outcomes contributing to specified capability
   - `--verbose` - Include extended details (achievement, actors, dependencies)

7. **Present Results**:
   - Show sync status (if sync occurred)
   - Show summary statistics (totals, stage breakdown)
   - Show current focus (if any)
   - Display outcome table grouped by stage
   - Show capability contributions summary
   - Highlight blocked outcomes (if any)
</process>

<output_format>
**When Sync Required:**
```
Outcome index is out of sync.
Syncing outcomes-info.toon...
Sync complete. Found 11 outcomes across 5 stages.

Outcomes Overview (synced: 2025-12-02T10:30:00Z)
...
```

**When Index Missing:**
```
Outcome index not found at status/outcomes-info.toon
Running initial sync...
Sync complete. Found 11 outcomes.

Outcomes Overview (synced: 2025-12-02T10:30:00Z)
...
```

**Standard Output (fresh index):**
```
Outcomes Overview (last sync: 2025-12-02T10:30:00Z)

Summary: 11 total | 3 queued | 2 ready | 1 in-progress | 0 blocked | 5 completed
         9 parent | 2 child | 6 P1 | 4 P2 | 1 P3

Current Focus: 005-implement-auth (in-progress since 2025-12-02T10:00:00Z)

Stage Distribution:
  queued:      ### (3)
  ready:       ## (2)
  in-progress: # (1)
  blocked:     (0)
  completed:   ##### (5)

| ID                  | Name                    | Stage       | Priority | Capabilities        | Parent       |
|---------------------|-------------------------|-------------|----------|---------------------|--------------|
| 005-implement-auth  | Implement Auth          | in-progress | P1       | auth-system:30%     | -            |
| 005.1-session-mgmt  | Session Management      | completed   | P1       | auth-system:10%     | 005-impl...  |
| 006-user-mgmt       | User Management         | ready       | P2       | user-mgmt:25%       | -            |
| ...                 | ...                     | ...         | ...      | ...                 | ...          |

Capability Contributions:
  auth-system:     55% (3 outcomes)
  data-pipeline:   20% (1 outcome)
  infra:           40% (2 outcomes)

Blocked Outcomes: None
```

**Verbose Output (--verbose):**
Adds: Achievement summary, actor list, dependency info

**TOON Output (for subagent use):**
```toon
@type: ItemList
@id: outcome-list-result
numberOfItems: 11
dateQueried: 2025-12-02T10:30:00Z
syncPerformed: false

summary.total: 11
summary.queued: 3
summary.ready: 2
summary.inProgress: 1
summary.blocked: 0
summary.completed: 5

focus.outcome: 005-implement-auth
focus.stage: in-progress

outcome{id,name,stage,priority,capabilities,parent|tab}:
005-implement-auth	Implement Auth	in-progress	P1	auth-system:30%	null
005.1-session-mgmt	Session Management	completed	P1	auth-system:10%	005-implement-auth
...
```
</output_format>

<success_criteria>
- Workspace-info.toon read successfully to locate outcomes path
- Outcomes-info.toon attempted from relatedData.outcomesInfo path
- If missing or stale: outcome-index-sync skill invoked
- After sync: outcomes-info.toon readable with valid data
- Summary statistics displayed accurately (all 5 stages shown)
- Current focus highlighted if set
- Outcome table formatted with key columns
- Capability contributions summarized
- Blocked outcomes highlighted (if any)
- Filters applied correctly if specified
- Parent/child hierarchy displayed correctly
</success_criteria>
