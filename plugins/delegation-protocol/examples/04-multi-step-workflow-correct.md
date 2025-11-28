# Example: Multi-Step Workflow - CORRECT Approach

## Scenario
User: "Fix the /up command and update CLAUDE.md"

## Correct Execution
Assistant: *counts: Read + Edit + Read + Edit + Git = 5 tools*
Assistant: "Delegating: 5 operations needed, 2500 token budget"
Assistant: *single Task call with full workflow*

## Result
400 tokens, same outcome

## Why This Works
- Counted operations before starting
- Recognized compound request pattern
- Delegated entire workflow with appropriate budget
- Used sonnet model for multi-file fix
- Preserved main context window
