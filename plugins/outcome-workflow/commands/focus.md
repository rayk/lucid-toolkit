---
description: Focus on a queued outcome so you can commence work
argument-hint: <outcome-id or directory-label>
allowed-tools: Task, Read, AskUserQuestion
---

<objective>
Prepare context for focused work on outcome `$ARGUMENTS`. This command:
1. Validates sufficient context capacity (≥75% free)
2. Delegates file operations to a subagent (resolve, move, update tracking)
3. Loads outcome_track.json into main context for immediate work
</objective>

<context>
0-Queued: !`ls outcomes/0-queued/ 2>/dev/null | grep -E "^[0-9]+-" | tr '\n' ' ' || echo "none"`
1-Ready: !`ls outcomes/1-ready/ 2>/dev/null | grep -E "^[0-9]+-" | tr '\n' ' ' || echo "none"`
2-In-Progress: !`ls outcomes/2-in-progress/ 2>/dev/null | grep -E "^[0-9]+-" | tr '\n' ' ' || echo "none"`
3-Blocked: !`ls outcomes/3-blocked/ 2>/dev/null | grep -E "^[0-9]+-" | tr '\n' ' ' || echo "none"`
Session: !`jq -r '.activeSessions | sort_by(.startedAt) | last | .sessionId' status/sessions_summary.json 2>/dev/null || echo "unknown"`
</context>

<process>

## Step 0: Context capacity check

**CRITICAL: Do this BEFORE any other work.**

Evaluate current context usage. If the conversation has:
- Significant prior discussion
- Multiple large file reads already in context
- Complex multi-turn exchanges

Then context is likely >25% used. Use AskUserQuestion:

```
Question: "Context may be limited. Loading this outcome will add ~2-3KB. Continue?"
Options:
- "Yes, load outcome" - Proceed with focus
- "No, start fresh session" - User should /clear first
```

If context appears mostly fresh (start of session, minimal prior content), proceed directly.

## Step 1: Delegate file operations to subagent

Use Task tool with subagent_type=general-purpose:

```
@type: FocusAction
@task: Focus on outcome matching "$ARGUMENTS"

Steps:
1. Resolve outcome label from "$ARGUMENTS":
   - If numeric (1, 001): Find directory starting with that number
   - If partial (jwt): Match against outcome directories
   - If full label: Use directly
   - Search order: 1-ready → 0-queued → 2-in-progress → 3-blocked

2. Handle classification transitions:
   - ONLY outcomes in 1-ready/ can be focused (best practice)
   - If in 1-ready/: Move to 2-in-progress/
   - If in 0-queued/: Warn user outcome needs design first, move to 1-ready required
   - If in 2-in-progress/: Already focused, no move needed
   - If in 3-blocked/: Return warning, cannot focus blocked outcome
   - If parent outcome: move entire nested tree together

3. Update sessions_summary.json:
   - Set focusedOutcomes to [outcome_label]
   - Update lastActivityAt timestamp
   - Update summary.currentFocusedOutcome

4. Return ONLY this JSON (no other output):
{
  "success": true|false,
  "outcomePath": "outcomes/2-in-progress/XXX-outcome-name",
  "outcomeLabel": "XXX-outcome-name",
  "warning": "optional warning message if blocked or not ready"
}

@constraints: maxTokens: 1500, model: haiku
```

If subagent returns `success: false` or includes a warning about blocked state:
- Present the warning to user
- Use AskUserQuestion to ask if they want to unblock first
- Stop here if user declines

## Step 2: Load outcome_track.json into context

**This step MUST execute in main context, not subagent.**

Using the `outcomePath` returned by subagent:

```
Read: {outcomePath}/outcome_track.json
```

This loads the full outcome tracking data into the conversation context,
making it immediately available for work.

## Step 3: Present ready state

Extract key fields from the loaded outcome_track.json and present:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FOCUSED: [outcome.directoryLabel]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[outcome.description]

Token Budget: [effort.tokenBudget] tokens
Primary Capability: [capabilityContributions[0].capabilityId]
                    (+[maturityContribution]% on completion)
Primary Project: [projects[0].projectName] ([involvement])

What would you like to work on first?
```

</process>

<design_rationale>
**Why check context capacity first?**
Loading an outcome consumes context. If context is already constrained,
loading more data makes the session less productive. Better to warn early
and let user decide whether to /clear first.

**Why delegate file operations?**
Steps 1-3 of the old command involve: Bash(ls), Bash(grep), Bash(mv),
Bash(jq), multiple file reads/writes. This is 5+ operations that should
not consume main context. The subagent handles all this and returns just
the path needed.

**Why load outcome_track.json in main context?**
The whole point of /focus is to prepare context for work. The outcome's
tracking data (description, capabilities, projects, tasks) must be IN
the main conversation to be useful. A subagent reading it doesn't help—
that context is discarded when the subagent completes.

**Alignment with CLAUDE.md:**
- Follows delegation protocol: 5+ operations → subagent
- Preserves context: subagent does grunt work, main context gets payload
- Single Read in main context: known path from subagent return value
</design_rationale>

<important>
**File Structure Note**: Each outcome has its own `outcome_track.json` inside its directory:
- `outcomes/2-in-progress/001-jwt-authentication/outcome_track.json` ✓
- NOT `status/outcome_track.json` ✗

**Classification Rule**: Only outcomes in `1-ready/` should be focused. This ensures they have designs and dependencies met.

**Context Loading**: The Read in Step 2 is NOT optional. It is the primary purpose
of this command—to get outcome data INTO context for productive work.
</important>