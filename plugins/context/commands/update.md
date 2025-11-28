---
description: Reconcile context tracking data from transcripts and logs
---

Run comprehensive context reconciliation to:
- Detect and cleanup stale sessions
- Backfill missing statistics from transcripts
- Move ended sessions to history
- Validate data integrity

<process>
1. **Scan Active Sessions**
   - Load `status/context_summary.json`
   - For each active session, verify transcript exists
   - Calculate actual token usage from transcript

2. **Detect Stale Sessions**
   - Flag sessions with no activity > threshold
   - Default threshold: 24 hours (zombie)
   - Strict threshold: 2 hours

3. **Reconcile Statistics**
   - Parse transcript files for token counts
   - Update session statistics
   - Recalculate summary totals

4. **Archive Ended Sessions**
   - Move sessions without active transcripts to history
   - Update session state to "archived"
</process>

<options>
**--strict**: Use aggressive 2-hour threshold for zombie detection
**--dry-run**: Preview changes without applying
**--verbose**: Show detailed reconciliation output
</options>

<output_format>
```
Context Reconciliation Report
=============================

Scanned: 5 active sessions
Zombies detected: 2
Sessions updated: 3
Sessions archived: 1

Changes Applied:
- session-abc123: Updated token count (1.2k → 1.5k)
- session-def456: Marked as zombie (36h inactive)
- session-ghi789: Archived (transcript missing)

Summary updated: status/context_summary.json
```
</output_format>

<success_criteria>
- All active sessions verified
- Stale sessions identified
- Statistics reconciled with transcripts
- Summary file updated
</success_criteria>
