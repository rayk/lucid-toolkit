# Example: Exploration in Main Context - WRONG Approach

## Scenario
User: "Where are auth errors handled?"

## Wrong Execution
Assistant: *uses Grep*
Assistant: *uses Read on 3 files*
Assistant: *uses Grep again*

## Result
2000+ tokens consumed

## What Went Wrong
- Open-ended exploration done in main context
- Multiple file reads without delegation
- Consumed valuable context window for exploratory work
- Did not recognize this as exploration requiring Task delegation
