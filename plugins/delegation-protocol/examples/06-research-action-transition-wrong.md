# Example: Research→Action Transition - WRONG Approach

## Scenario
[Previous turn: WebSearch about Cypher PROFILE/EXPLAIN]
User: "Add that info to the evidence directory and update the outcome"

## Wrong Execution
Assistant: *feels confident because content is clear*
Assistant: *uses Write for evidence file*
Assistant: *uses Read on outcome_track.json*
Assistant: *uses Edit on outcome_track.json*
Assistant: *uses Read on outcome-statement.md*
Assistant: *uses Edit on outcome-statement.md (multiple times)*

## Result
7+ tools executed, massive context consumption

## What Went Wrong
- Failed to recognize research→action transition (highest-risk moment)
- Clear content created false confidence
- Did not count operations before starting
- Executed compound request without decomposition
- Violated protocol at critical transition point
