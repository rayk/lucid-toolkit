# Example: Exploration in Main Context - CORRECT Approach

## Scenario
User: "Where are auth errors handled?"

## Correct Execution
Assistant: "Delegating: open-ended exploration, 1500 token budget"
Assistant: Task(Explore, haiku, 1500 tokens): "Find auth error handling patterns"

## Result
300 token structured response

## Why This Works
- Recognized open-ended exploration pattern
- Delegated to haiku subagent with appropriate budget
- Received structured, concise results
- Preserved main context window
