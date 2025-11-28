---
name: SKILL-NAME-HERE
description: Detailed description of what this skill does, when to use it, and trigger terms. Include specific use cases and boundaries. Can use up to 1024 characters to be thorough.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
---

# SKILL NAME

Comprehensive overview of the skill's purpose and capabilities.

## When to Use

This skill should be invoked when:
- User asks to [specific action 1]
- User mentions [trigger term 1]
- User requests [specific action 2]

This skill should NOT be used when:
- [Boundary condition 1]
- [Boundary condition 2]

## Prerequisites

Before using this skill, ensure:
- [ ] Prerequisite 1
- [ ] Prerequisite 2

## Instructions

### Phase 1: Discovery

1. **Step 1.1:** Analyze the request
   - Check for X
   - Verify Y
   - Identify Z

2. **Step 1.2:** Gather context
   - Use Grep to find relevant files
   - Use Read to examine current state
   - Use Glob to locate patterns

### Phase 2: Execution

3. **Step 2.1:** Perform main action
   - Action A with tool X
   - Action B with tool Y

4. **Step 2.2:** Validate results
   - Check that output meets criteria
   - Verify no errors occurred

### Phase 3: Finalization

5. **Step 3.1:** Clean up
   - Remove temporary artifacts
   - Update related files

6. **Step 3.2:** Report results
   - Summarize what was done
   - Note any issues or warnings

## Reference Materials

See supporting files in this skill directory:

- `checklists/quality-checklist.md` - Quality standards
- `templates/output-template.md` - Output format
- `examples/usage-examples.md` - Common scenarios

## Output Format

Results should be structured as:

```
[Standard output format here]
```

## Error Handling

If errors occur:

1. **Error Type A:** Do X
2. **Error Type B:** Do Y
3. **Unknown errors:** Ask user for guidance using AskUserQuestion

## Examples

### Example 1: Simple Case

**User Request:** "Can you [trigger phrase]?"

**Execution:**
1. Claude discovers this skill based on trigger phrase
2. Follows Phase 1 → Phase 2 → Phase 3
3. Produces output in standard format

**Output:**
```
[Expected output example]
```

### Example 2: Complex Case

**User Request:** "I need to [complex trigger phrase]"

**Execution:**
1. Skill activated with additional context
2. Uses reference materials from checklists/
3. Handles edge cases appropriately

**Output:**
```
[Expected complex output example]
```

## Best Practices

- Always verify prerequisites before execution
- Use reference materials for consistency
- Report issues clearly to the user
- Ask for clarification when ambiguous

## Notes

- This skill works best when [condition]
- Consider using with [complementary skill] for [use case]
- Avoid using when [anti-pattern situation]
