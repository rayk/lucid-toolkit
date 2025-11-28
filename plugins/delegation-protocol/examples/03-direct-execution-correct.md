# Example: Appropriate Direct Execution

## Scenario
User: "What's in .claude/settings.json?"

## Correct Execution
Assistant: *applies pre_response_protocol*
Assistant: *counts: Read(known path) = 1 tool*
Assistant: "Executing directly: single file read of known path"
Assistant: *uses Read*

## Result
Appropriate direct execution

## Why This Works
- Single operation with known file path
- Operation count certain (exactly 1)
- No exploration or search component
- Output size predictable
- Meets ALL criteria for direct execution
