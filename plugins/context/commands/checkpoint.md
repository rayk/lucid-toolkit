---
description: Create manual checkpoint to preserve session state
argument-hint: [accomplishment summary]
---

<objective>
Create a manual checkpoint to preserve current session state, capturing accomplishments, key decisions, and next steps for work resumption.

This command:
- Saves current progress and accomplishments
- Records key decisions made in session
- Captures next steps for continuation
- Updates session statistics
</objective>

<context>
Use manual checkpoints when:
- About to attempt risky operation
- Completed significant milestone
- Context window getting large
- Before switching focus to different work
- Want to preserve specific context for resumption
</context>

<process>
1. **Gather Checkpoint Data**:
   - If $ARGUMENTS provided: Use as accomplishment summary
   - Otherwise: Prompt for accomplishment description
   - Capture current timestamp

2. **Collect Session State**:
   - Files modified since last checkpoint
   - Tasks completed/failed
   - Current focused outcomes
   - Git status (branch, uncommitted changes)

3. **Prompt for Context** (interactive):
   ```
   Key decisions made this session?
   (Enter decisions, or skip)

   Next steps to continue this work?
   (Enter next steps, or skip)
   ```

4. **Update Session Record**:
   - Add checkpoint event to session
   - Update statistics
   - Save accomplishments and next steps
   - Record checkpoint timestamp

5. **Display Confirmation**:
   ```
   ## Checkpoint Created
   Time: 2025-01-15 11:45:00

   Accomplishments:
   - [User-provided or generated summary]

   Key Decisions:
   - [Listed decisions]

   Next Steps:
   - [Listed next steps]

   Statistics since last checkpoint:
   - Files modified: 3
   - Tasks completed: 5
   - Tokens consumed: 12,000
   ```
</process>

<automatic_accomplishments>
If no accomplishments provided, generate from:
- Number of files modified
- Tasks completed
- Git commits made
- Outcomes worked on

Example:
"Modified 3 files, completed 5 tasks, made 2 commits on authentication-system outcome"
</automatic_accomplishments>

<success_criteria>
- Checkpoint data captured
- Session record updated
- Accomplishments saved
- Next steps recorded (if provided)
- Confirmation displayed
</success_criteria>

<output>
Displayed to user:
- Checkpoint timestamp
- Accomplishments captured
- Key decisions (if provided)
- Next steps (if provided)
- Statistics since last checkpoint
</output>
