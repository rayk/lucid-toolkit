# Example: Specificity Trap - CORRECT Approach

## Scenario
User: "I got these errors on startup: Path /Users/foo/luon not found"

## Correct Execution
Assistant: *applies pre_response_protocol*
Assistant: *counts: Grep(unknown locations) + Read(unknown count) + Edit = 3+ minimum*
Assistant: "Delegating: 3+ operations needed to find and fix config paths, 2000 token budget"
Assistant: *single Task call*

## Result
Protocol followed, context preserved

## Why This Works
- Recognized that specific error doesn't reduce operation count
- Counted operations before starting
- Delegated to subagent with appropriate budget
- Preserved main context for higher-level work
