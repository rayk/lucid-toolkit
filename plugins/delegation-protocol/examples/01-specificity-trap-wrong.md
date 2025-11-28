# Example: Specificity Trap - WRONG Approach

## Scenario
User: "I got these errors on startup: Path /Users/foo/luon not found"

## Wrong Execution
Assistant: *thinks "I know exactly what to search for, this is simple"*
Assistant: *uses Grep to find 'luon'*
Assistant: *uses Read on settings file*
Assistant: *uses Edit to fix*

## Result
3+ tools executed, protocol violated despite feeling confident

## What Went Wrong
- Specific error message created false confidence
- Assistant knew WHAT to search for but not WHERE or HOW MANY locations
- Did not count operations before starting
- Failed to recognize this as exploration requiring delegation
