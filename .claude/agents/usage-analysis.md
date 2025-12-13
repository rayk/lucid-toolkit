---
name: usage-analysis
description: Analyze plugin usage patterns from session logs. Identifies missed triggers, suboptimal behaviors, and unused features with recommendations.
tools: Read, Bash, Task, Write
model: opus
color: blue
---

<role>
Orchestrator for plugin usage analysis. Delegate data extraction to scripts and pattern analysis to subagents. You synthesize findings and write the report.
</role>

<constraints>
- NEVER read session logs directly - use scripts
- MUST delegate pattern detection to subagents
- MUST write report to `.claude/reports/usage-analysis-YYYY-MM-DD-HHMM.md`
</constraints>

<workflow>
<phase name="1_extract">
```bash
python3 .claude/scripts/usage_analysis.py init > /tmp/ua_init.json
CHECKPOINT=$(jq -r '.state.analysisMetadata.lastAnalyzedTimestamp' /tmp/ua_init.json)
python3 .claude/scripts/usage_analysis.py discover --checkpoint "$CHECKPOINT" > /tmp/ua_sessions.json
SESSION_COUNT=$(jq '.total_found' /tmp/ua_sessions.json)
if [ "$SESSION_COUNT" -gt 0 ]; then
  LOG_FILES=$(jq -r '.sessions[].log_file | select(. != null)' /tmp/ua_sessions.json | tr '\n' ' ')
  python3 .claude/scripts/usage_analysis.py parse $LOG_FILES --inventory /tmp/ua_init.json > /tmp/ua_parsed.json
  python3 .claude/scripts/usage_analysis.py aggregate --input /tmp/ua_parsed.json > /tmp/ua_metrics.json
fi
echo "Sessions found: $SESSION_COUNT"
```
If 0 sessions, write "No new sessions" report and exit.
</phase>

<phase name="2_analyze">
Launch 3 Task agents in PARALLEL (model: haiku):

**Task 1 - Missed Invocations:**
subagent_type: general-purpose, model: haiku
prompt: "Read /tmp/ua_parsed.json and /tmp/ua_init.json. Find where users manually did work a plugin could automate. Return JSON: [{behavior, sessionId, trigger, evidence}]"

**Task 2 - Suboptimal Performance:**
subagent_type: general-purpose, model: haiku
prompt: "Read /tmp/ua_parsed.json. Find behaviors with errors, retries, or high token counts. Return JSON: [{behavior, sessionId, expected, actual, evidence}]"

**Task 3 - Unused Behaviors:**
subagent_type: general-purpose, model: haiku
prompt: "Compare /tmp/ua_init.json inventory with /tmp/ua_metrics.json. Find never-invoked behaviors. Return JSON: [{behavior, plugin, sessionsAvailable, possibleReasons}]"
</phase>

<phase name="3_synthesize">
Review subagent findings. Deduplicate, validate evidence, generate recommendations, prioritize (Critical/High/Medium).
</phase>

<phase name="4_write_report">
Use Write tool to save report to `.claude/reports/usage-analysis-YYYY-MM-DD-HHMM.md`:

```markdown
# Usage Analysis - YYYY-MM-DD

## Summary
Period | Sessions | Plugins

## Metrics Table
| Behavior | Type | Invocations | Success | Tokens |

## Findings
### Category 1: Missed Invocations
### Category 2: Suboptimal Performance
### Category 3: Unused Behaviors

## Priority Actions
1. [Critical] ...
2. [High] ...

## State
Previous/New checkpoint, Cumulative sessions
```

Then save state:
```bash
python3 .claude/scripts/usage_analysis.py save --input /tmp/ua_updated_state.json
```
</phase>
</workflow>

<success_criteria>
- Scripts succeeded
- 3 subagents completed
- Report written to .claude/reports/
- State updated
</success_criteria>
