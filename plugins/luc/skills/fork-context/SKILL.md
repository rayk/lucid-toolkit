---
name: fork-context
description: Fork current conversation context to a new Claude instance in a separate terminal tab. Use when you need to delegate work to another Claude session, spawn parallel workflows, or hand off context to continue work independently.
---

<objective>
Summarize the current conversation context and spawn a new Claude instance in a fresh terminal tab with that context as the starting prompt. This enables parallel workflows, task delegation, and context handoff without losing the current session's state.

Key principle: The summary should capture enough context for the new Claude instance to continue work independently without needing to ask clarifying questions.
</objective>

<quick_start>
<workflow>
1. **Analyze current context**: Review recent conversation, tasks, and working state
2. **Generate summary**: Create concise context summary (what, why, current state, next steps)
3. **Derive tab name**: Short descriptor of the forked task (max 20 chars)
4. **Open terminal**: Use open_terminal.py script to spawn Warp tab
5. **Launch Claude**: Pass summary as initial prompt to claude CLI
</workflow>

<example_invocation>
```bash
# The skill generates and executes:
@plugins/luc/scripts/open_terminal.py \
  -n "Auth Tests" \
  -d /Users/rayk/Projects/my-app \
  -c "claude --print 'Context: Implementing auth system...'"
```
</example_invocation>
</quick_start>

<context_summary_template>
Generate a summary using this structure:

```
## Context
[1-2 sentences: What project/codebase, what broader goal]

## Current Task
[1-2 sentences: What specific work was being done]

## State
[Bullet points: Key decisions made, files modified, current progress]

## Next Steps
[Numbered list: What the new Claude instance should do]

## Key Files
[List: Important file paths relevant to the task]
```

<summary_principles>
- Be specific: Include exact file paths, function names, variable names
- Be concise: Target 200-400 words total
- Be actionable: Next steps should be clear enough to execute immediately
- Include failures: If something didn't work, say what and why
- Skip obvious context: Don't explain what Claude Code is or how it works
</summary_principles>
</context_summary_template>

<tab_naming>
Derive tab name from the forked task:

<rules>
- Maximum 20 characters
- Use Title Case
- Focus on the task, not the project
- Avoid generic names like "Task" or "Work"
</rules>

<examples>
| Task Being Forked | Tab Name |
|-------------------|----------|
| Writing unit tests for auth | Auth Tests |
| Fixing database migration | DB Migration |
| Reviewing PR #123 | PR 123 Review |
| Refactoring user service | User Svc Refactor |
| Debugging memory leak | Memory Leak Debug |
</examples>
</tab_naming>

<execution>
<script_location>
The terminal script is at: `@plugins/luc/scripts/open_terminal.py`

Arguments:
- `-n NAME`: Tab name (required)
- `-d DIRECTORY`: Working directory (use current working directory)
- `-c COMMAND`: Command to execute (claude with prompt)
</script_location>

<claude_invocation>
Use the `--print` flag to pass the context summary as the initial prompt:

```bash
claude --print 'YOUR_CONTEXT_SUMMARY_HERE'
```

For multi-line summaries, use heredoc style in the command:
```bash
claude --print "$(cat <<'EOF'
## Context
Working on lucid-toolkit plugin...

## Current Task
Implementing fork-context skill...

## Next Steps
1. Test the skill
2. Validate output
EOF
)"
```
</claude_invocation>

<escaping>
The summary will be passed through shell, so escape properly:
- Single quotes in content: Replace `'` with `'\''`
- Dollar signs: Escape as `\$` or use single quotes
- Backticks: Escape as `` \` ``
</escaping>
</execution>

<process>
When fork-context is invoked:

1. **Gather context** (do not ask user):
   - What is the current working directory?
   - What files were recently read or modified?
   - What was the most recent task or request?
   - What is the current state of that task?
   - What should happen next?

2. **Generate summary** using the template above

3. **Derive tab name** from the task being forked

4. **Execute**:
   ```bash
   @plugins/luc/scripts/open_terminal.py \
     -n "[TAB_NAME]" \
     -d "[CURRENT_WORKING_DIRECTORY]" \
     -c "claude --print '[ESCAPED_SUMMARY]'"
   ```

5. **Confirm** to user what was forked and where
</process>

<success_criteria>
Fork is successful when:

- New Warp terminal tab opens with descriptive name
- Tab is set to correct working directory
- Claude instance launches with context summary
- Summary is sufficient for new Claude to continue work
- Original session remains unaffected
</success_criteria>

<anti_patterns>
Avoid these mistakes:

- **Too vague**: "Working on some code" - be specific about what code
- **Too verbose**: 1000+ word summaries - keep it focused
- **Missing next steps**: Summary without actionable direction
- **Wrong directory**: Spawning in home instead of project directory
- **Unescaped quotes**: Breaking the shell command with bad escaping
- **Generic tab names**: "Claude 2" instead of "Auth Tests"
</anti_patterns>

<examples>
<example name="fork_for_tests">
**Scenario**: User has been implementing a feature and wants to fork to write tests

**Generated Summary**:
```
## Context
Working on lucid-toolkit, a Claude Code plugin marketplace.

## Current Task
Implemented fork-context skill that spawns new Claude instances with context.

## State
- Created SKILL.md at plugins/luc/skills/fork-context/
- Script exists at plugins/luc/scripts/open_terminal.py
- Skill follows luc plugin patterns (pure XML, no markdown headings)

## Next Steps
1. Write tests for open_terminal.py script
2. Test argument parsing (-n, -d, -c flags)
3. Test shell escaping for special characters
4. Verify Warp integration works

## Key Files
- plugins/luc/scripts/open_terminal.py
- plugins/luc/skills/fork-context/SKILL.md
```

**Tab Name**: `Script Tests`

**Command**:
```bash
@plugins/luc/scripts/open_terminal.py \
  -n "Script Tests" \
  -d /Users/rayk/Projects/lucid-toolkit \
  -c "claude --print '## Context...'"
```
</example>

<example name="fork_for_debugging">
**Scenario**: User encountered an error and wants to fork for debugging

**Generated Summary**:
```
## Context
Debugging payment processing in e-commerce app.

## Current Task
Investigating why Stripe webhooks fail silently.

## State
- Error occurs in src/webhooks/stripe.ts:145
- Logs show 200 response but no database update
- Suspect async/await issue in handlePaymentSuccess()

## Next Steps
1. Add logging to handlePaymentSuccess function
2. Check if transaction is being rolled back
3. Verify webhook signature validation
4. Test with Stripe CLI webhook forwarding

## Key Files
- src/webhooks/stripe.ts
- src/services/payment.service.ts
- src/db/transactions.ts
```

**Tab Name**: `Webhook Debug`
</example>
</examples>
