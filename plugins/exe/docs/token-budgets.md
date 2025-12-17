# Token Budgets

Execution model and token budget guidance for plan execution.

## Execution Model

```
┌─────────────────────────────────────────────────────────────┐
│  Main Agent (Executor) - ~150k tokens                       │
│  - Reads execution-plan.toon                                │
│  - Orchestrates task execution                              │
│  - Calls subagents via Task tool                            │
│  - Tracks progress, handles checkpoints                     │
└─────────────────────────────────────────────────────────────┘
         │
         │ Task(agent, prompt)  ←── each call spawns isolated context
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Subagent Context (per task) - agent's budget               │
│  - Receives: task prompt + taskInputs context               │
│  - Executes: implementation work                            │
│  - Returns: outputs + returns to main agent                 │
│  - Budget: 15k-100k depending on agent                      │
└─────────────────────────────────────────────────────────────┘
```

**Key insight:** Total plan can consume millions of tokens across many subagent calls. The constraints are:
1. Main agent must stay within ~150k (reading plan + orchestration overhead)
2. Each individual task must fit within its subagent's budget

## Main Agent Budget (~150k)

The execution-plan.toon must be readable by the main agent plus leave room for:
- Reading task outputs/returns from subagents
- Checkpoint validation logic
- Error handling and recovery decisions
- Progress tracking

**Plan size guideline:** Keep plan under ~30k tokens to leave ~120k for orchestration.

## Subagent Budgets (per task)

| Agent | Budget | Typical Task Scope |
|-------|--------|-------------------|
| `general-purpose` | ~100k | Large exploration, multi-file research |
| `Plan` | ~80k | Architecture design |
| `Explore` | ~50k | Codebase exploration |
| `impl-flutter:flutter-coder` | ~50k | 1-3 files, TDD cycle |
| `impl-flutter:flutter-tester` | ~40k | Integration tests |
| `impl-python:python-coder` | ~50k | 1-3 files, TDD cycle |
| `impl-neo4j:neo4j-modeler` | ~30k | Schema design |

**Rule: Each task must complete within 85% of its subagent's budget.**

## Task Sizing Heuristics

From `flutter-coder` agent docs (50k budget):
- Test file: ~200-400 lines → ~2k-4k tokens
- Implementation file: ~100-300 lines → ~1k-3k tokens
- Analyze/fix cycle: ~500-1k tokens per iteration
- Typical iterations: 3-5
- **Safe scope:** 1-3 files, one component, ~40k total

## Signs Task Exceeds Subagent Budget (Must Split)

- Multiple unrelated features
- More than 3 new files
- Touches more than 5 existing files
- Complex refactoring + new feature combined
- Multiple failure types + providers + UI together

## Task Complexity Estimates

| Complexity | Subagent Tokens | Max Files | Suitable Agents |
|------------|-----------------|-----------|-----------------|
| `trivial` | 2,000-5,000 | 1 | Any |
| `standard` | 10,000-25,000 | 2-3 | coder, tester |
| `complex` | 30,000-80,000 | 3-5 | coder (split if >50k) |

## Decomposition Strategy

If task exceeds subagent budget:
1. Split by layer (domain → application → infrastructure → presentation)
2. Split by component (one component per task)
3. Split by concern (tests separate from implementation)
4. Create dependency chain between split tasks
5. Re-estimate each split task against its agent's budget
