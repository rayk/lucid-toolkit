# Example: Research→Action Transition - CORRECT Approach

## Scenario
[Previous turn: WebSearch about Cypher PROFILE/EXPLAIN]
User: "Add that info to the evidence directory and update the outcome"

## Correct Execution
Assistant: *recognizes research→action transition*
Assistant: "[MODE: research → action]"
Assistant: *decomposes: Write(evidence) + Read/Edit(track) + Read/Edit(statement) = 5+ ops*
Assistant: "[5 ops → delegate]: Compound request, multi-file update"
Assistant: *single Task call with full context*

## Result
Protocol followed, context preserved

## Why This Works
- Recognized research→action transition (Step 0)
- Output transition marker for visibility
- Decomposed compound request before counting
- Recognized that clear CONTENT doesn't reduce OPERATION count
- Delegated entire workflow with appropriate budget

## Key Insight
Having clear CONTENT from research does not reduce OPERATION count.
The transition from knowing to doing still requires evaluation.
