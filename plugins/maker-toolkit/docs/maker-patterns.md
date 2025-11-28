# MAKER Patterns for Claude Code CLI

Practical patterns from the MAKER paper (arxiv:2511.09030) for building reliable multi-step workflows.

---

## Core Insight

> Break complex tasks into tiny pieces. Verify each piece. Compose the results.

A million-step task with 1% error rate per step = guaranteed failure.
A million-step task with tiny focused steps + voting = zero errors.

---

## Pattern 1: Extreme Decomposition

### The Problem
Large tasks given to a single agent accumulate errors exponentially.

### The Solution
Split tasks into the smallest possible subtasks. Each subtask gets its own focused agent call.

### In Claude Code

**Bad - Monolithic agent call:**
```
Task: "Find all authentication code, analyze security issues, and suggest fixes"
```

**Good - Decomposed calls:**
```
Task 1: "Find files containing authentication logic"
Task 2: "For auth file X, list security concerns" (repeat per file)
Task 3: "Synthesize findings into recommendations"
```

### Implementation Rule
When using the Task tool:
- One clear objective per agent
- Include only the context needed for THAT step
- Prefer 3 small calls over 1 large call

---

## Pattern 2: Token Budgets as Red Flags

### The Problem
When an LLM is confused, it rambles. Long outputs correlate with errors.

### The Solution
Set strict token limits. If exceeded, discard and retry - don't try to salvage.

### In Claude Code

**Always include constraints in Task prompts:**
```
@constraints:
  maxTokens: 2000
  format: toon
  itemLimit: 10

If response exceeds these, the agent is confused. Retry.
```

**Practical limits by task type:**
| Task Type | Max Tokens | Max Items |
|-----------|------------|-----------|
| File search | 1500 | 10 |
| Code analysis | 2000 | 5 |
| Yes/no check | 500 | 1 |
| Summary | 1000 | - |

### Implementation Rule
If a subagent returns more than expected, don't parse it - invoke again.

---

## Pattern 3: Voting for Critical Decisions

### The Problem
Any single LLM call can be wrong. On important decisions, one error is catastrophic.

### The Solution
Run the same query multiple times independently. Trust the consensus.

### In Claude Code

**For critical searches (e.g., "where is X implemented"):**
```
1. Spawn 3 parallel Task(Explore) agents with identical query
2. Compare results
3. If 2+ agree on same file/location = high confidence
4. If all differ = task needs human review or refinement
```

**When to use voting:**
- Finding the "right" place to make a change
- Verifying a file is safe to delete
- Confirming a refactor won't break things

**When NOT to use voting:**
- Simple file reads
- Straightforward searches with unique terms
- Tasks where the answer is obvious

### Implementation Rule
For any decision that would be expensive to reverse, get a second opinion.

---

## Pattern 4: Cheap Models for Focused Tasks

### The Problem
Expensive reasoning models aren't better at tiny focused tasks - they're just slower and costlier.

### The Solution
Use the smallest model that can reliably handle each subtask.

### In Claude Code

**Model selection by task:**
| Task | Model | Why |
|------|-------|-----|
| Orchestration, synthesis | sonnet/opus | Needs broad understanding |
| Focused search | haiku | Fast, cheap, sufficient |
| Simple verification | haiku | Yes/no doesn't need reasoning |
| Complex analysis | sonnet | Benefits from deeper thought |

**In Task tool calls:**
```
Task(
  subagent_type: "Explore",
  model: "haiku",  // Use haiku for focused searches
  prompt: "Find files matching pattern X"
)
```

### Implementation Rule
Default to `haiku` for Explore agents. Only escalate to `sonnet` if task requires synthesis.

---

## Pattern 5: Strict Output Formats

### The Problem
Malformed output often indicates confused reasoning - not just formatting errors.

### The Solution
Define exact output format. If format is wrong, discard entirely.

### In Claude Code

**TOON for tabular data:**
```
@return ItemList in TOON:
results[N]{position,file,description}:
  1,src/auth.ts,Main authentication module
  2,src/login.ts,Login form handler
```

**JSON for structured non-tabular:**
```
@return Answer:
{"answer": "yes", "file": "src/auth.ts:42", "confidence": "high"}
```

**What to do with malformed responses:**
1. Do NOT try to repair/extract
2. Log the failure for debugging
3. Retry with same prompt
4. After 2 failures, escalate to user

### Implementation Rule
Treat format errors as reasoning errors. Retry, don't repair.

---

## Pattern 6: Parallel Independent Calls

### The Problem
Sequential calls are slow. Waiting for one search before starting another wastes time.

### The Solution
Identify independent operations and run them simultaneously.

### In Claude Code

**Before any multi-step task, ask:**
- Which steps depend on prior results?
- Which steps can run in parallel?

**Example - Investigating a bug:**
```
Parallel (no dependencies):
  - Task: Find error handling patterns
  - Task: Find test files for module
  - Task: Find related documentation

Sequential (depends on above):
  - Synthesize findings
  - Propose fix
```

**In practice:**
Send multiple Task tool calls in a single message for independent operations.

### Implementation Rule
If steps don't depend on each other, run them in the same message.

---

## Pattern 7: Minimal Context Per Agent

### The Problem
More context = more confusion. Agents get distracted by irrelevant information.

### The Solution
Each agent gets ONLY what it needs: goal + current state + constraints.

### In Claude Code

**Bad - Kitchen sink prompt:**
```
"We started this project 3 months ago. The user wants feature X.
We tried approach A but it failed because... Now we're trying B.
The codebase uses React. Find where to add the new component."
```

**Good - Focused prompt:**
```
"Find React component files in src/components/ that handle user settings.
Return: file paths only, max 5 results."
```

### What to include:
- The specific goal
- Current state (if relevant)
- Output constraints
- Nothing else

### Implementation Rule
If context isn't required for THIS step, don't include it.

---

## Quick Reference Card

| Situation | Pattern | Action |
|-----------|---------|--------|
| Complex task | Decompose | Split into 3+ focused subtasks |
| Long response | Red flag | Discard and retry |
| Critical decision | Vote | Run 2-3 times, trust consensus |
| Simple search | Cheap model | Use haiku |
| Malformed output | Strict format | Retry, don't repair |
| Independent steps | Parallel | Same message, multiple tools |
| Writing prompts | Minimal context | Goal + state + constraints only |

---

## Anti-Patterns to Avoid

1. **The Mega-Prompt**: Asking one agent to do 5 things
2. **The Repair Shop**: Trying to fix malformed outputs
3. **The Overthinker**: Using opus for simple searches
4. **The Historian**: Including full conversation history in subagent prompts
5. **The Waiter**: Running independent searches sequentially
6. **The Optimist**: Trusting a single agent on critical decisions

---

## Summary

The MAKER paper proved that reliable multi-step execution comes from:

1. **Tiny tasks** - Each agent does one thing
2. **Strict formats** - Wrong format = wrong thinking
3. **Consensus** - Vote on critical decisions
4. **Right-sized models** - Cheap for simple, powerful for complex
5. **Parallelism** - Don't wait unnecessarily
6. **Minimal context** - Less is more

Apply these patterns and your Claude Code workflows will be more reliable, faster, and cheaper.
