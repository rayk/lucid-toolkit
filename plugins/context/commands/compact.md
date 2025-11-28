---
description: Compact context window to reduce token usage
argument-hint: [--aggressive]
---

<objective>
Reduce context window usage by summarizing conversation history, archiving intermediate results, and preserving only essential context.

This command:
- Analyzes current context composition
- Summarizes verbose conversation segments
- Archives intermediate tool results
- Reports tokens saved
- Preserves critical context for continuation
</objective>

<context>
Use context compaction when:
- Token usage exceeds 60% of limit
- Multiple large file reads in session
- Repeated exploration patterns detected
- Before starting new complex task
- Session has accumulated verbose output
</context>

<process>
1. **Analyze Context Composition**:
   ```
   ## Context Analysis
   Total tokens: 67,000 / 100,000 (67%)

   Breakdown:
   - Conversation history: 35,000 (52%)
   - Tool results: 22,000 (33%)
   - System context: 10,000 (15%)
   ```

2. **Identify Compaction Targets**:
   - Verbose tool outputs (file reads, search results)
   - Repeated exploration attempts
   - Superseded information
   - Intermediate reasoning steps

3. **Generate Summaries**:
   - Summarize file contents to key points
   - Condense search results to findings
   - Archive intermediate steps
   - Preserve key decisions and outcomes

4. **Apply Compaction**:
   - Replace verbose segments with summaries
   - Archive full content if needed later
   - Update context pointers

5. **Preserve Essential Context**:
   - Current task and goal
   - Key decisions made
   - Files being actively edited
   - Error states and blockers
   - Next steps

6. **Report Results**:
   ```
   ## Compaction Complete

   Before: 67,000 tokens (67%)
   After: 42,000 tokens (42%)
   Saved: 25,000 tokens (37% reduction)

   Summarized:
   - 5 file reads → key excerpts
   - 3 search results → findings list
   - 12 conversation turns → summary

   Preserved:
   - Current task context
   - Key decisions (3)
   - Active file edits (2)
   - Next steps (4)
   ```
</process>

<aggressive_mode>
With `--aggressive` flag:
- More aggressive summarization
- Remove all intermediate reasoning
- Keep only final conclusions
- Target 50% reduction minimum
- May lose some context nuance

Use when:
- Token usage >80%
- Need significant headroom
- Current task is well-defined
- Don't need to backtrack
</aggressive_mode>

<preservation_rules>
## Always Preserve

1. **Current Task Context**
   - Active goal/objective
   - Constraints and requirements
   - Acceptance criteria

2. **Key Decisions**
   - Architecture choices
   - Trade-off resolutions
   - User preferences captured

3. **Active Work**
   - Files being edited
   - Uncommitted changes
   - In-progress operations

4. **Blockers and Errors**
   - Current error states
   - Unresolved issues
   - Dependencies needed

5. **Navigation Context**
   - Current workspace/project
   - Focused outcomes
   - Branch context
</preservation_rules>

<success_criteria>
- Context analysis completed
- Compaction targets identified
- Summaries generated accurately
- Essential context preserved
- Token reduction achieved
- Report displayed with savings
</success_criteria>

<output>
Displayed to user:
- Before/after token counts
- Percentage reduction
- What was summarized
- What was preserved
- Recommendations for further reduction
</output>
