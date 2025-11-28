# Delegation Protocol Plugin

Context-preserving delegation framework for Claude Code agents.

## Overview

This plugin implements a rigorous protocol for deciding when to execute operations directly vs. delegating to subagents. It prevents context bloat by enforcing operation counting and token budget management.

## Core Principle

**Count operations before classifying. Delegate by default.**

If a request requires 3+ tool calls, delegate to a subagent with an appropriate token budget. This preserves the main context window for high-level coordination.

## Components

### Prompts

| Prompt | Purpose |
|--------|---------|
| `pre-response-protocol.md` | 4-step mandatory protocol executed before ANY response |
| `token-budget-enforcement.md` | Token budget allocation by operation type |
| `specificity-trap.md` | How specific input creates false confidence |

### Examples

10 paired examples (wrong/correct) demonstrating:
- Specificity trap scenarios
- Exploration vs. direct execution
- Multi-step workflow delegation
- Index-first lookup patterns
- Research→Action transitions

### Skills

| Skill | Purpose |
|-------|---------|
| `coordinate-subagents/` | Advanced subagent coordination patterns, voting, error handling |

## The Protocol (Summary)

### Step 0: Transition Check
Detect research→action transitions (highest-risk moment)

### Step 1: Decompose Compound Requests
Split "AND", "then", multiple verbs into atomic operations

### Step 2: Count Operations
- Find = Grep + Read (2+ ops)
- Fix = Find + Read + Edit (3+ ops)
- Unknown count = "?" = delegate

### Step 3: Verify Simplicity
Direct execution requires ALL:
- Single known file path
- Count certain (not estimated)
- No exploration component
- Output <500 tokens

### Step 4: Visible Checkpoint
```
[N ops → direct|delegate]: rationale
```

## Token Budgets

| Operation Type | Budget | Model |
|----------------|--------|-------|
| File search, pattern matching | 1500 | haiku |
| Yes/no validation | 800 | haiku |
| Code analysis, flow tracing | 2000 | sonnet |
| Multi-file fix + commit | 2500 | sonnet |
| Synthesis, complex reasoning | 3000 | opus |

## Common Patterns

### Delegate If ANY Apply
- Location unknown (need to find where)
- Open-ended question
- Multiple files/directories to check
- Synthesis required
- 3+ tool calls
- MCP tools or external operations
- Unpredictable result size

### Direct Execution ONLY When
- Reading specific known file path
- Searching known pattern in known location
- Listing files with exact glob
- Running command with known output

## The Specificity Trap

**CRITICAL**: Specific user input creates FALSE confidence.

When user provides exact error messages, paths, or variable names:
- You know WHAT to search for
- You do NOT know WHERE or HOW MANY locations
- Specific problem ≠ simple solution
- This is EXPLORATION, not LOOKUP

Count operations assuming multiple locations until proven otherwise.

## Integration

This protocol integrates with:
- **maker-toolkit**: Subagent builder for creating specialized agents
- **thinking-tools**: Mental models for complex decision evaluation
- **session-manager**: Token budget tracking across sessions

## Usage

The protocol is designed to be injected into CLAUDE.md or agent system prompts. It provides:

1. A clear decision framework
2. Visible checkpoints for auditing
3. Token budget guidelines
4. Examples for training correct behavior

## Philosophy

Context is precious. The main agent should coordinate, not execute. Delegate routine work to focused subagents, preserving context for strategic decisions and complex synthesis.
