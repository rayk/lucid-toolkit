---
description: Debug plugin issues by analyzing session transcripts, comparing expected vs actual behavior, and developing verified solutions
argument-hint: <run> in <project> using <command|skill|hook> <problem-description>
---

<objective>
Invoke the plugin-debugger subagent to debug a plugin issue by analyzing what happened versus what should have happened.

Parse $ARGUMENTS to extract:
- **run**: Session/run identifier (e.g., "last run", "this morning's session")
- **project**: Project where the issue occurred
- **component**: Type (command/skill/hook/agent) and name
- **problem**: Description of unexpected behavior
</objective>

<context>
Debug logs: !`ls -t ~/.claude/debug/ | head -3`
</context>

<process>
1. Parse $ARGUMENTS to extract run, project, component, and problem
2. If critical information missing, use AskUserQuestion ONCE to clarify:
   - Which session had the problem?
   - What component type and name?
   - What was expected vs what happened?
3. Invoke plugin-debugger subagent with extracted parameters
4. Subagent will:
   - Extract and analyze debug logs
   - Compare actual vs expected behavior
   - Identify root cause with evidence
   - Develop multiple solution options
   - Verify solutions against Claude Code best practices
5. Present findings and solution options to user
6. Use AskUserQuestion to confirm which solution to implement
7. Implement selected solution (delegate if multi-file)
</process>

<success_criteria>
- Subagent invoked successfully with all required parameters
- Root cause identified with log evidence
- At least 2 solution options presented
- User-selected solution implemented
</success_criteria>
