# Coordinate Subagents Skill

## Overview

Apply MAKER research patterns for reliable, token-efficient subagent coordination via the Task tool.

## Purpose

Prevents common subagent failures:
- **Token waste**: 10-50k tokens when 2-5k suffice
- **Unreliable outputs**: Single calls returning wrong answers
- **Sequential bottlenecks**: Waiting for independent operations

## The 7 Patterns (from MAKER research)

1. **Extreme Decomposition** - One task per agent, split on "and"
2. **Token Budgets** - Set limits, retry on overflow (don't salvage)
3. **Voting** - 2-3 parallel calls for critical decisions
4. **Right-Sized Models** - haiku for search, sonnet for analysis
5. **Strict Formats** - TOON for lists, JSON for objects
6. **Parallel Calls** - Independent operations in one message
7. **Minimal Context** - Goal + constraints only

## Quick Example

**Inefficient** (40k tokens, unreliable):
```
Explore the authentication system and tell me how it works.
```

**Efficient** (~1.5k tokens, reliable):
```toon
@type: SearchAction
query: "authentication handlers"

@return ItemList in TOON:
results[5]{position,codeRepository,description}:
  1,src/auth/login.ts,Main login handler

@constraints[2]{key,value}:
  maxTokens,1500
  itemLimit,8

Return ONLY the TOON structure.
```

## Files

- **SKILL.md**: Main skill with patterns, examples, checklist
- **references/toon-format.md**: TOON syntax reference

## Token + Reliability Gains

| Metric | Before | After |
|--------|--------|-------|
| Tokens | 40k | 4k (90% reduction) |
| Format | Varies | Consistent |
| Reliability | ~95% | >99% (with voting) |
| Speed | Sequential | Parallel |

## When to Use

- Invoking Task with Explore or general-purpose agents
- Subagent responses too verbose or unreliable
- Need structured data, not prose
- Critical decisions requiring consensus

## Source

"Solving a Million-Step LLM Task with Zero Errors" (arxiv:2511.09030)
