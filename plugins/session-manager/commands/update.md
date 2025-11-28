---
description: Reconcile session tracking data from transcripts and logs
---

Run comprehensive session reconciliation to:
- Detect and cleanup stale sessions
- Backfill missing statistics from transcripts
- Move ended sessions to history
- Validate data integrity

Execute the reconciliation script that analyzes all active sessions and updates `status/sessions_summary.json`.

```bash
cd /Users/rayk/Projects/lucid_stack
python3 hooks/session_summary/reconcile_cli.py --verbose
```
