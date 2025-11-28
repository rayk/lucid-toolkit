---
name: delegate
description: Systematic delegation decisions to preserve main context window. Use before executing any operation that may require 3+ tool calls, when location is unknown, or when scope is uncertain.
---

<skill_definition>
<purpose>Systematic delegation decisions to preserve main context window</purpose>
<trigger>Before executing any operation that may require 3+ tool calls</trigger>
</skill_definition>

<core_principle>
**Count operations before classifying. Delegate by default.**

If a request requires 3 or more tool calls, delegate to a subagent with an appropriate token budget.
</core_principle>

<pre_response_protocol>
## The 4-Step Pre-Response Protocol (MANDATORY)

### STEP 0: TRANSITION CHECK
Detect if moving from research to action:
- Research: WebSearch, WebFetch, exploratory Read
- Action: Write, Edit, Bash for git

If transitioning → Output `[MODE: research → action]`

### STEP 1: DECOMPOSE COMPOUND REQUESTS
Split requests containing:
- "AND" connectors
- "then" sequences
- Multiple action verbs

Count each component separately.

### STEP 2: COUNT OPERATIONS
| Pattern | Minimum Operations |
|---------|-------------------|
| Find where X is | Grep/Glob + Read = 2+ |
| Fix X | Find + Read + Edit = 3+ |
| Unknown locations | Assume multiple reads |
| File in context | 0 ops to read |

**Uncertainty Rule**: Cannot state count with certainty? Write "?" → "?" ALWAYS means delegate

### STEP 3: VERIFY SIMPLICITY (only if count < 3)
ALL must be true:
- [ ] Single known file path
- [ ] Operation count certain (not estimated)
- [ ] No exploration/search component
- [ ] Output size <500 tokens

### STEP 4: VISIBLE CHECKPOINT
Before FIRST tool call, output:
```
[N ops → direct|delegate]: rationale
```
</pre_response_protocol>

<delegation_rules>
## Delegate If ANY Apply

- Location unknown (need to find where)
- Open-ended question
- Multiple files/directories to check
- Synthesis required
- 3+ tool calls
- MCP tools or external operations
- Unpredictable result size

## Direct Execution ONLY When ALL Apply

- Reading specific known file path
- Operation count exactly 1-2 with certainty
- No exploration/search component
- Single known location
</delegation_rules>

<token_budgets>
## Token Budget Guidelines

| Operation Type | Budget | Model | Storage |
|----------------|--------|-------|---------|
| File search, pattern matching | 1500 | haiku | inline |
| Yes/no validation | 800 | haiku | inline |
| Code analysis, flow tracing | 2000 | sonnet | inline |
| Multi-file fix + commit | 2500 | sonnet | inline |
| Synthesis, complex reasoning | 3000 | opus | inline |
| Research, documentation | 300 summary | opus | payload-store |
| MCP scrape, web fetch | 300 summary | sonnet | payload-store |

**payload-store**: Full output saved externally, summary returned to main context.
</token_budgets>

<store_and_summarize>
## Store-and-Summarize Pattern

For tasks that generate large outputs (research, documentation, analysis):

**Use when:**
- Research requiring comprehensive results
- MCP tools returning page content
- Documentation gathering
- Any task where full context may be needed later

**Delegation template:**
```
Task({agent}, {model}):
  "{task description}

   Use payload-store protocol:
   - Store full output to shared/payloads/ (or {explicit-path} if provided)
   - Return TOON summary with @stored path
   - Summary max 300 tokens

   @constraints: summary_only: true"
```

**With explicit path:**
```
Task(research, opus):
  "Research authentication best practices.

   Store full report to: docs/research/auth-practices.md
   Return TOON summary with @stored path"
```

**Main agent receives:**
```toon
@stored: shared/payloads/sess-abc/20251128-auth-practices.md

summary[4]{aspect,finding}:
  OAuth2,Recommended for third-party integration
  JWT,Use RS256 with short expiry
  Sessions,Server-side with secure cookies
  MFA,TOTP preferred over SMS

keyFindings: OAuth2 + JWT + server sessions with MFA provides layered security
confidence: High
tokens_stored: 3500
```

**Main agent can:**
- Use summary for immediate response
- Read full payload: `Read(shared/payloads/sess-abc/...)`
- Pass path to follow-up subagents
</store_and_summarize>

<specificity_trap>
## The Specificity Trap (Critical Anti-Pattern)

**Problem**: Specific user input creates FALSE confidence.

When user provides exact error messages, variable names, or paths:
- You know WHAT to search for
- You do NOT know WHERE or HOW MANY locations

**Example**:
```
User: "I got error 'path /Users/foo/luon not found'"
False: "I know exactly what to search for, this is simple"
Reality: Grep + Read + Edit = 3+ ops → DELEGATE
```

**Rule**: Count operations assuming multiple locations until proven otherwise.
</specificity_trap>

<checkpoint_examples>
## Visible Checkpoint Examples

```
[1 op → direct]: Reading known file path
[2 ops → direct]: Grep + Read, single known file
[3 ops → delegate]: Multi-file exploration
[5 ops → delegate]: Compound request with multiple edits
[? ops → delegate]: Unknown scope, location unknown
[MODE: research → action]: Transition marker
```
</checkpoint_examples>

<model_selection>
## Model Selection Guide

### Haiku (1500-2000 tokens)
- File search and pattern matching
- Yes/no validation
- Simple lookups
- High-volume parallel calls

### Sonnet (2000-2500 tokens)
- Code analysis and flow tracing
- Multi-file fixes with commits
- Architecture decisions

### Opus (3000+ tokens)
- Strategic synthesis
- Complex reasoning
- Novel architecture proposals
</model_selection>
