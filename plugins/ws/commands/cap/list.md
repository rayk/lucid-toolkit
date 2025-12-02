---
description: List all capabilities in the workspace with status and maturity overview
argument-hint: [--filter <domain|status|maturity>] [--verbose] [--no-sync]
---

<objective>
Display a summary list of all capabilities in the workspace by reading the capabilities-info.toon index file. Automatically syncs the index if out-of-date by launching parallel subagents.
</objective>

<context>
Index file: Read capabilities-info.toon from workspace status directory
Workspace info: Read workspace-info.toon to locate capabilities.path
</context>

<process>
1. **Load Workspace Context**:
   - Read workspace-info.toon from workspace root
   - Extract `capabilities.path` for source location

2. **Check Index Freshness**:
   - Read capabilities-info.toon `dateModified` timestamp
   - List all `capability_track.json` files in capabilities directory
   - Compare index timestamp against each track file's modification time
   - Index is STALE if any track file is newer than index

3. **If Index is Stale** (and `--no-sync` not specified):
   - Inform user: "Index is out of sync. Updating capabilities-info.toon..."
   - Identify which capabilities need updating (modified since last sync)
   - Launch parallel subagents to gather data:

   ```
   # Launch one subagent per stale capability (up to 5 in parallel)
   Task(
     subagent_type="general-purpose",
     model="haiku",
     prompt="Read capability_track.json at {cap_path} and extract:
       - identifier, name, type, status, domain
       - currentMaturity, targetMaturity
       - purpose (first sentence of description)
       - coreValues.primary (as comma list)
       - actor count, prerequisite count, enables count
       Return as TOON properties for capability.{id}.*"
   )
   ```

   - Additionally launch capability-checker for validation status:
   ```
   Task(
     subagent_type="capability-checker",
     prompt="Validate capability at {cap_path}. Return only overallStatus."
   )
   ```

4. **Aggregate Subagent Results**:
   - Collect all capability data from subagents
   - Calculate summary statistics:
     - Total, active, deprecated counts
     - Atomic vs composed counts
     - Average maturity
     - Maturity distribution buckets
   - Identify alerts from validation results
   - Write updated capabilities-info.toon with current timestamp

5. **If Index is Fresh** (or `--no-sync` specified):
   - Skip sync, use cached data
   - Note if `--no-sync`: "Using cached data (--no-sync specified)"

6. **Parse Index Data**:
   - Read `summary.*` properties for totals
   - Read `capability.index{...}` table for capability list
   - Read `alerts{...}` table for any requiring attention

7. **Apply Filters** (if $ARGUMENTS provided):
   - `--filter domain:<name>` - Show only capabilities in specified domain
   - `--filter status:<active|deprecated|merged>` - Filter by status
   - `--filter maturity:<low|medium|high>` - Filter by maturity range (low=0-29, medium=30-79, high=80-100)
   - `--verbose` - Include extended details (purpose, core values, actor count)

8. **Present Results**:
   - Show sync status (if sync occurred)
   - Show summary statistics
   - Display capability table
   - Highlight any alerts
</process>

<sync_strategy>
**Parallel Subagent Dispatch:**

When sync is needed, dispatch subagents efficiently:

1. **Batch by staleness**: Only process capabilities modified since last sync
2. **Parallel limit**: Max 5 concurrent subagents to avoid overwhelming context
3. **Use haiku model**: Fast, cheap extraction for structured data
4. **Validation optional**: Only run capability-checker if `--validate` flag or capability was recently modified

**Subagent prompt template:**
```
Extract capability summary from {path}/capability_track.json:

Required fields (return as TOON):
- identifier: folderName value
- name: name value
- type: type value (atomic|composed)
- status: status value (active|deprecated|merged)
- domain: domain value
- currentMaturity: currentMaturity value
- targetMaturity: targetMaturity value
- purpose: first sentence of description
- coreValues: coreValues.primary array as comma string
- actorCount: length of actors array
- prereqCount: length of relationships.prerequisites array
- enablesCount: length of relationships.enables array

Return format:
capability.{id}.identifier: {value}
capability.{id}.name: {value}
...
```

**Aggregation:**
After all subagents complete, aggregate into capabilities-info.toon format.
</sync_strategy>

<output_format>
**When Sync Required:**
```
Index is out of sync (3 capabilities modified since last sync)
Syncing capabilities-info.toon...
  [1/3] auth-system - extracting...
  [2/3] billing-core - extracting...
  [3/3] data-isolation - extracting...
  Running validation checks...
Sync complete. Updated 3 capabilities.

Capabilities Overview (synced: 2025-12-02T10:30:00Z)
...
```

**Standard Output (fresh index):**
```
Capabilities Overview (last sync: 2025-12-02T10:30:00Z)

Summary: 12 total | 10 active | 2 deprecated | avg maturity: 54%
         8 atomic | 4 composed

Maturity Distribution:
  0-29%:   ### (3)
  30-59%:  ##### (5)
  60-79%:  ### (3)
  80-100%: # (1)

| ID                    | Name                      | Type     | Status | Maturity | Domain              |
|-----------------------|---------------------------|----------|--------|----------|---------------------|
| auth-system           | Authentication System     | atomic   | active | 47%/80%  | Security & Privacy  |
| data-isolation        | Data Isolation            | atomic   | active | 60%/80%  | Security & Privacy  |
| ...                   | ...                       | ...      | ...    | ...      | ...                 |

Alerts (2):
! auth-system: STALE_CHECK - Last validated 14 days ago
! billing-core: VALIDATION_FAILED - 2 critical issues
```

**Verbose Output (--verbose):**
Adds columns: Purpose (truncated), Core Values, Actors

**TOON Output (for subagent use):**
```toon
@type: ItemList
@id: capability-list-result
numberOfItems: 12
dateQueried: 2025-12-02T10:30:00Z
syncPerformed: true
capabilitiesSynced: 3

summary.total: 12
summary.active: 10
summary.avgMaturity: 54%

capability{id,name,type,status,current,target|tab}:
auth-system	Authentication System	atomic	active	47%	80%
...

alerts[2]: auth-system:STALE_CHECK,billing-core:VALIDATION_FAILED
```
</output_format>

<success_criteria>
- Freshness check performed against all capability_track.json files
- If stale: subagents launched in parallel (max 5) to extract capability data
- If stale: capability-checker subagents validate each updated capability
- If stale: capabilities-info.toon updated with aggregated results
- Summary statistics displayed accurately
- Capability table formatted and readable
- Alerts highlighted if any exist
- Filters applied correctly if specified
- Sync progress shown to user during update
</success_criteria>
