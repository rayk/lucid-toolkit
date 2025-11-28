# Example: Index-First Lookup - OPTIMAL Approach

## Scenario
User: "where is neo4jservice"

## Optimal Execution
Assistant: *recognizes module name pattern*
Assistant: *checks project_map.json modules[] (in context or 1 Read)*
Assistant: "Neo4j Service is at luon/neo4j_service/ with entry points
           at cypher_loader/loader.py, executor.py, cli.py"

## Result
0-1 tools, answer from index

## Why This Works
- Recognized LOOKUP query pattern
- Checked index file first (project_map.json)
- Avoided grepping entire codebase
- Used 0 operations if index already in context
- Fast, efficient, context-preserving

## Note
If project_map.json is already in context (via system-reminder),
use it directly without a Read call.
