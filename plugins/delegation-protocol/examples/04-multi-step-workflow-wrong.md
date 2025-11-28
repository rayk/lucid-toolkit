# Example: Multi-Step Workflow - WRONG Approach

## Scenario
User: "Fix the /up command and update CLAUDE.md"

## Wrong Execution
Assistant: *uses Read on up.md*
Assistant: *uses Edit on up.md*
Assistant: *uses Read on CLAUDE.md*
Assistant: *uses Edit on CLAUDE.md*
Assistant: *uses Bash for git*

## Result
5 tools, 4800 tokens wasted

## What Went Wrong
- Failed to count operations before starting
- Executed multi-step workflow in main context
- Chained multiple Read → Edit operations
- Did not recognize compound request ("and")
- Massive context consumption for routine workflow
