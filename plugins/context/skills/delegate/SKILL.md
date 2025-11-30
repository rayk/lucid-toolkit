---
name: delegate
description: MANDATORY pre-response protocol for ALL task execution. Use BEFORE every tool call to classify operations and delegate appropriately. Triggers on any user request, task planning, code changes, file operations, or when starting work. This is NOT optional - apply the 4-step protocol before EVERY response.
---

<objective>
Apply the mandatory 4-step pre-response protocol before ANY task execution. This skill protects the main context window by systematically classifying operations and delegating multi-step work to subagents.

**This is not optional.** Every response that involves tool usage MUST run the protocol first.
</objective>

<quick_start>
**Before your first tool call, ALWAYS:**

1. **Count operations** - How many tool calls will this need?
2. **Check certainty** - Do you know the exact file paths? Write "?" if uncertain
3. **Match agent** - Check specialized agents FIRST (debugger, flutter-*, python-*, neo4j, research)
4. **Apply rule** - 3+ ops OR "?" = delegate; 1-2 ops with certainty = direct

**Output checkpoint before first tool:**
```
[N ops → direct|delegate(agent)]: rationale
```

**Quick reference:**
- `[1 op → direct]: Reading known file`
- `[3 ops → delegate(specialize:debugger)]: Bug diagnosis`
- `[? ops → delegate(specialize:research)]: Need verified sources`
- `[4 ops → delegate(Explore)]: Find where X is defined`
</quick_start>

<core_principle>
**Count operations before classifying. Delegate by default.**

If a request requires 3 or more tool calls, delegate to a subagent with an appropriate token budget.
</core_principle>

<pre_response_protocol>
<step_0_transition_check>
Detect if moving from research to action:
- Research: WebSearch, WebFetch, exploratory Read
- Action: Write, Edit, Bash for git

If transitioning → Output `[MODE: research → action]`
</step_0_transition_check>

<step_1_decompose>
Split requests containing:
- "AND" connectors
- "then" sequences
- Multiple action verbs

Count each component separately.
</step_1_decompose>

<step_2_count_operations>
| Pattern | Minimum Operations |
|---------|-------------------|
| Find where X is | Grep/Glob + Read = 2+ |
| Fix X | Find + Read + Edit = 3+ |
| Unknown locations | Assume multiple reads |
| File in context | 0 ops to read |

**Uncertainty Rule**: Cannot state count with certainty? Write "?" → "?" ALWAYS means delegate
</step_2_count_operations>

<step_3_verify_simplicity>
Only if count < 3, ALL must be true:
- [ ] Single known file path
- [ ] Operation count certain (not estimated)
- [ ] No exploration/search component
- [ ] Output size <500 tokens
</step_3_verify_simplicity>

<step_4_checkpoint>
Before FIRST tool call, output:
```
[N ops → direct|delegate]: rationale
```
</step_4_checkpoint>
</pre_response_protocol>

<delegation_rules>
<delegate_when_any_apply>
- Location unknown (need to find where)
- Open-ended question
- Multiple files/directories to check
- Synthesis required
- 3+ tool calls
- MCP tools or external operations
- Unpredictable result size
</delegate_when_any_apply>

<direct_when_all_apply>
- Reading specific known file path
- Operation count exactly 1-2 with certainty
- No exploration/search component
- Single known location
</direct_when_all_apply>
</delegation_rules>

<token_budgets>
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
For tasks that generate large outputs (research, documentation, analysis).

<use_when>
- Research requiring comprehensive results
- MCP tools returning page content
- Documentation gathering
- Any task where full context may be needed later
</use_when>

<delegation_template>
```
Task({agent}, {model}):
  "{task description}

   Use payload-store protocol:
   - Store full output to shared/payloads/ (or {explicit-path} if provided)
   - Return TOON summary with @stored path
   - Summary max 300 tokens

   @constraints: summary_only: true"
```

With explicit path:
```
Task(research, opus):
  "Research authentication best practices.

   Store full report to: docs/research/auth-practices.md
   Return TOON summary with @stored path"
```
</delegation_template>

<main_agent_receives>
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

Main agent can:
- Use summary for immediate response
- Read full payload: `Read(shared/payloads/sess-abc/...)`
- Pass path to follow-up subagents
</main_agent_receives>
</store_and_summarize>

<specificity_trap>
**Critical Anti-Pattern:** Specific user input creates FALSE confidence.

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
```
[1 op → direct]: Reading known file path
[2 ops → direct]: Grep + Read, single known file
[3 ops → delegate]: Multi-file exploration
[5 ops → delegate]: Compound request with multiple edits
[? ops → delegate]: Unknown scope, location unknown
[MODE: research → action]: Transition marker
```
</checkpoint_examples>

<agent_selection>
**PRIORITY ORDER: Specialized agents FIRST, then built-in agents.**

When delegating, check specialized agents before falling back to general-purpose:

<specialized_agents>
| Agent | Use When | Triggers |
|-------|----------|----------|
| `specialize:debugger` | Bugs, test failures, unexpected behavior | "bug", "failing test", "not working", "error", diagnosis |
| `specialize:flutter-coder` | Flutter/Dart code generation | Flutter, Riverpod, fpdart, widget, provider, Dart |
| `specialize:flutter-env` | Flutter environment issues | build fails, signing, emulator, CI, Flutter doctor |
| `specialize:neo4j` | Graph database work | Neo4j, Cypher, graph, AuraDB, nodes, relationships |
| `specialize:python-coder` | Python code generation | Python, FastAPI, Pydantic, uv, ruff, generate Python |
| `specialize:python-env` | Python environment issues | uv/pip fails, pyright, Docker, GCP, Jupyter kernel |
| `specialize:research` | Verified research, fact-checking | research, documentation, verify, authoritative sources |
</specialized_agents>

<builtin_agents>
Use only when no specialized agent matches:

| Agent | Use When |
|-------|----------|
| `Explore` | Codebase exploration, find files, understand structure |
| `general-purpose` | Multi-step tasks without domain specialization |
</builtin_agents>

<agent_checkpoint>
Include agent selection in your checkpoint:
```
[3 ops → delegate(specialize:debugger)]: Test failure diagnosis
[? ops → delegate(specialize:research)]: Need authoritative sources
[4 ops → delegate(Explore)]: Find authentication handlers
```
</agent_checkpoint>
</agent_selection>

<model_selection>
<haiku>
**1500-2000 tokens** - File search, pattern matching, yes/no validation, simple lookups, high-volume parallel calls
</haiku>

<sonnet>
**2000-2500 tokens** - Code analysis, flow tracing, multi-file fixes with commits, architecture decisions
</sonnet>

<opus>
**3000+ tokens** - Strategic synthesis, complex reasoning, novel architecture proposals
</opus>
</model_selection>

<success_criteria>
**Protocol applied correctly when:**

- Visible checkpoint `[N ops → ...]` appears before first tool call
- Operation count reflects reality (not underestimated)
- "?" used when location or scope is uncertain
- Specialized agent used when domain matches (debugger, flutter-*, python-*, neo4j, research)
- Built-in agents used only when no specialized agent fits
- Delegation used for 3+ operations OR uncertain scope
- Direct execution only when ALL simplicity criteria met
- Research → action transitions explicitly marked

**Anti-success indicators (protocol failure):**

- Tool calls without preceding checkpoint
- Using general-purpose agent when specialized agent exists for the domain
- Guessing file locations instead of delegating search
- Multiple sequential tool calls that could have been one delegation
- Context exhaustion mid-task due to undelegated work
</success_criteria>
