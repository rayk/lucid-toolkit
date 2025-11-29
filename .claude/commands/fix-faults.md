---
description: Analyze all fault reports, diagnose root causes using debug logs, research fixes, implement in parallel, and commit
argument-hint: [--dry-run]
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, Task, AskUserQuestion, WebFetch, WebSearch]
---

<objective>
Automated fault remediation workflow that:
1. Reads all fault reports from ~/.claude/fault/
2. Analyzes each fault using specialized agents to diagnose root causes
3. Researches fixes using Claude Code documentation
4. Clarifies ambiguities with user
5. Implements all fixes in parallel
6. Cleans up fault reports, bumps versions, updates changelog, commits and pushes
</objective>

<context>
Fault reports: !`ls ~/.claude/fault/*.json 2>/dev/null | wc -l | tr -d ' '` reports found
Report files: !`ls ~/.claude/fault/*.json 2>/dev/null || echo "No fault reports found"`
</context>

<process>
## Phase 1: Discovery and Triage

1. **Read all fault reports** from `~/.claude/fault/`:
   ```bash
   ls ~/.claude/fault/*.json 2>/dev/null
   ```

2. If no fault reports found:
   - Display: "No fault reports found in ~/.claude/fault/"
   - Exit early

3. **Parse each fault report** to extract:
   - Fault ID
   - Component (plugin, type, name)
   - Problem description (expected vs actual)
   - Session debug log path
   - Any suggested fixes already in the report

4. **Display triage summary**:
   ```
   ## Fault Triage

   | ID | Component | Problem Summary |
   |----|-----------|-----------------|
   | fault-YYYYMMDD-HHMMSS | plugin/type/name | Brief description |
   ```

5. **Ask user to confirm** which faults to fix:
   - Use AskUserQuestion with options:
     - "Fix all faults"
     - "Select specific faults"
     - "Cancel"

## Phase 2: Deep Analysis (Parallel Agents)

For EACH fault to fix, launch a **plugin-debugger** agent in PARALLEL:

```
Task(subagent_type="plugin-debugger", prompt="""
Analyze this fault report and diagnose the root cause:

Fault ID: {fault-id}
Component: {plugin}/{type}/{name}
Problem: {description}
Expected: {expected}
Actual: {actual}
Debug Log: {log-path}

Instructions:
1. Read the debug log at {log-path} to understand what happened
2. Read the component source file to understand expected behavior
3. Compare actual vs expected behavior
4. Identify the root cause with evidence
5. Develop 2-3 solution options
6. Verify solutions against Claude Code best practices

Return your analysis in the standard debug analysis format.
""")
```

Wait for ALL parallel analyses to complete.

## Phase 3: Research and Validation

For each proposed fix, launch a **claude-code-guide** agent to validate:

```
Task(subagent_type="claude-code-guide", prompt="""
Validate this proposed fix against Claude Code plugin best practices:

Component Type: {command|skill|hook|agent}
Proposed Change: {description of fix}

Questions to answer:
1. Does this fix follow Claude Code plugin conventions?
2. Are there better patterns in the official documentation?
3. What edge cases should be considered?
4. Is the fix complete or are there related changes needed?

Return validation status and any recommended improvements.
""")
```

## Phase 4: Clarification

If ANY analysis reveals ambiguity or multiple valid approaches:

1. **Consolidate questions** across all faults
2. Use AskUserQuestion ONCE with:
   - Grouped questions by fault
   - Clear options for each decision point
   - Option to accept recommended approach for all

Example:
```
Question: "How should we handle these implementation choices?"
Options:
- "Use recommended approach for all"
- "Let me review each one"
```

## Phase 5: Fix Plan Presentation

1. **Generate consolidated fix plan**:
   ```
   ## Fix Plan

   ### Fault 1: {fault-id}
   **Root Cause**: {diagnosis}
   **Fix**: {selected approach}
   **Files**: {list of files to modify}
   **Changes**: {summary of changes}

   ### Fault 2: {fault-id}
   ...

   ### Version Updates
   - {plugin-name}: {old-version} → {new-version}

   ### Changelog Entry
   {draft changelog content}
   ```

2. **Ask for approval**:
   - Use AskUserQuestion:
     - "Approve and implement all fixes"
     - "Modify plan first"
     - "Cancel"

3. If --dry-run flag: Stop here with plan display

## Phase 6: Parallel Implementation

Launch specialized agents in PARALLEL to implement fixes:

For EACH file group (by plugin), launch a **general-purpose** agent:

```
Task(subagent_type="general-purpose", model="haiku", prompt="""
Implement this fix:

File: {file-path}
Changes:
{detailed change description}

Instructions:
1. Read the current file
2. Apply the specified changes using Edit tool
3. Verify the changes are correct
4. Return summary of changes made
""")
```

Wait for ALL implementations to complete.

## Phase 7: Cleanup and Commit

1. **Delete processed fault reports**:
   ```bash
   rm ~/.claude/fault/{fault-id}.json
   ```

2. **Update plugin.json versions** for each affected plugin:
   - Patch bump for bug fixes (1.0.0 → 1.0.1)
   - Minor bump for new features (1.0.0 → 1.1.0)

3. **Update CHANGELOG.md**:
   - Add new version section at top
   - List all fixes with component names
   - Note version bumps

4. **Commit and push**:
   ```bash
   git add -A
   git commit -m "fix: Resolve N fault reports with automated remediation

   {list of fixes}

   Bumped versions:
   {list of version changes}

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"

   git push origin main
   ```

5. **Display summary**:
   ```
   ## Remediation Complete

   Faults fixed: N
   Files modified: M
   Versions bumped: {list}

   Commit: {hash}
   Pushed to: origin/main
   ```
</process>

<parallel_execution_strategy>
## Agent Parallelization

**Phase 2 - Analysis**: Launch ALL plugin-debugger agents in a SINGLE message
- Each fault gets its own agent
- Agents run concurrently, analyzing different faults

**Phase 3 - Validation**: Launch ALL claude-code-guide agents in a SINGLE message
- One per proposed fix
- Validate all fixes concurrently

**Phase 6 - Implementation**: Launch agents grouped by independence
- Group 1: All file edits that don't overlap
- If files overlap, serialize those edits

**Example parallel launch**:
```
[Task(fault-1-analysis)] + [Task(fault-2-analysis)] + [Task(fault-3-analysis)]
```
</parallel_execution_strategy>

<error_handling>
**No fault reports found**:
- Exit early with informative message

**Debug log not found**:
- Use fault report's problem/expected/actual fields
- Note: "Analysis based on fault report only (debug log unavailable)"

**Analysis fails for one fault**:
- Continue with other faults
- Report failed analysis in summary
- Ask user if they want to skip or retry

**Implementation fails**:
- Rollback changes for that fault
- Continue with other fixes
- Report failure in summary

**Git push fails**:
- Display commit hash
- Suggest manual push
- Don't fail the entire workflow
</error_handling>

<success_criteria>
- All fault reports in ~/.claude/fault/ processed
- Root cause identified for each fault with evidence
- Fixes validated against Claude Code best practices
- User approved the fix plan
- All fixes implemented successfully
- Fault report files deleted
- Plugin versions bumped appropriately
- CHANGELOG.md updated
- Changes committed with descriptive message
- Pushed to remote (or clear instructions if failed)
</success_criteria>

<output_format>
**Progress Updates** (during execution):
```
[1/7] Discovering fault reports...
[2/7] Analyzing 3 faults in parallel...
[3/7] Validating fixes against best practices...
[4/7] Presenting fix plan...
[5/7] Implementing fixes in parallel...
[6/7] Updating versions and changelog...
[7/7] Committing and pushing...
```

**Final Summary**:
```
## Fault Remediation Complete

| Fault ID | Component | Status |
|----------|-----------|--------|
| fault-... | plugin/cmd | Fixed |

Files modified: N
Versions bumped: plugin-a v1.0.1 → v1.0.2, ...
Commit: abc1234
Remote: Pushed to origin/main
```
</output_format>
