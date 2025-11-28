---
description: Validate session tracking health and detect zombie sessions (project)
---

Run comprehensive session validation to check for:
- Sessions with missing transcript files
- Zombie sessions (old with no activity)
- Discrepancies in session state
- Recommendations for cleanup

```bash
cd /Users/rayk/Projects/lucid_stack

# Check for missing transcripts and zombies
echo "🔍 Validating Session Health..."
echo ""

# Count active sessions
ACTIVE_COUNT=$(jq '.activeSessions | length' status/sessions_summary.json)
echo "📊 Active Sessions: $ACTIVE_COUNT"
echo ""

# Check each active session for issues
echo "🔎 Checking for issues..."
echo ""

jq -r '.activeSessions[] |
  .sessionId + "|" +
  .environment.transcriptPath + "|" +
  .startedAt' status/sessions_summary.json | while IFS='|' read -r session_id transcript_path started_at; do

  # Check if transcript exists
  if [ ! -f "$transcript_path" ]; then
    echo "❌ MISSING TRANSCRIPT: $session_id"
    echo "   Path: $transcript_path"
    echo "   Started: $started_at"
    echo ""
  fi

  # Calculate age in hours
  started_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$started_at" "+%s" 2>/dev/null || echo "0")
  now_epoch=$(date "+%s")
  age_hours=$(( (now_epoch - started_epoch) / 3600 ))

  # Flag old sessions (24+ hours)
  if [ "$age_hours" -ge 24 ]; then
    echo "⚠️  ZOMBIE SESSION: $session_id"
    echo "   Age: ${age_hours} hours"
    echo "   Started: $started_at"
    echo ""
  fi
done

# Show recommendation
echo "💡 Recommendations:"
echo ""
echo "To clean up zombie sessions and missing transcripts:"
echo "  /update-sessions"
echo ""
echo "For aggressive cleanup (2h threshold):"
echo "  python3 hooks/session_summary/reconcile_cli.py --strict --verbose"
echo ""
echo "To preview changes without applying:"
echo "  python3 hooks/session_summary/reconcile_cli.py --dry-run --verbose"
```
