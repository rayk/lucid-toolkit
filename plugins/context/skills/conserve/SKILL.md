---
name: conserve
description: Techniques to protect and optimize the context window. Use when context usage is high, operations may bloat context, or when coordinating subagents for token efficiency.
---

<skill_definition>
<purpose>Techniques to protect and optimize the context window</purpose>
<trigger>When context usage is high or operations may bloat context</trigger>
</skill_definition>

<core_principle>
**Context is precious. The main agent coordinates and synthesizes, not executes routine work.**

Preserve the main context window for:
- Strategic decisions
- Complex reasoning
- High-level coordination
</core_principle>

<conservation_techniques>
## Context Conservation Techniques

### 1. TOON Format for Structured Output
Token-Oriented Object Notation provides ~40% savings vs JSON:

```toon
files[3]{path,purpose,lines}:
  src/auth/login.ts,Main login handler,145
  src/auth/session.ts,Session management,89
  src/auth/token.ts,JWT utilities,67
```

Use for:
- File lists
- Process steps
- Config lookups
- Uniform data structures

Use JSON only for non-uniform complex objects.

### 2. Index-First Lookup Pattern
For location queries, check index files first:
```
User: "where is neo4jservice?"
→ Check project_map.json first (1 op vs many greps)
```

### 3. Minimal Context for Subagents
Provide only:
- Goal statement
- Constraints
- Expected output format

Strip:
- Full conversation history
- Unrelated context
- Verbose explanations

### 4. Parallel Operations
Independent operations in single message:
```
Task(search files, haiku) + Task(search patterns, haiku)
→ Parallel execution, single response aggregation
```

### 5. Result Summarization
Request structured summaries from subagents:
- 300-500 token responses max
- Key findings only
- Skip intermediate reasoning
</conservation_techniques>

<external_data_operations>
## External Data Hazards

MCP tools and web scrapes pollute context:

| Tool | Payload | Risk | Solution |
|------|---------|------|----------|
| firecrawl_scrape | 500-5000 | High | Delegate + payload-store |
| WebFetch | 500-3000 | High | Delegate + payload-store |
| firecrawl_search | 200-1000 | Medium | Batch into single fetch |
| Research agent | 2000-10000 | High | payload-store protocol |

**Rule**: N external fetches → delegate with payload-store, budget `min(N × 200, 2500)` for summary only
</external_data_operations>

<payload_store_protocol>
## Payload Store Protocol

For operations producing >500 tokens, use the payload-store skill:

**When to use:**
- Research tasks returning comprehensive reports
- MCP tools scraping documentation
- Analysis requiring full context preservation
- Any output that may need re-access later

**How it works:**
1. Subagent generates full output
2. Stores to `shared/payloads/{session}/` (or explicit path if provided)
3. Returns TOON summary + `@stored: path` reference
4. Main agent uses summary, can Read full payload if needed

**Delegation instruction:**
```
Task(research, opus):
  "Research X comprehensively.

   Use payload-store protocol:
   - Store full output to shared/payloads/
   - Return TOON summary with @stored path
   - Summary max 300 tokens"
```

**Return format:**
```toon
@stored: shared/payloads/sess-abc/20251128-topic.md

summary[N]{aspect,finding}:
  aspect1,finding1
  aspect2,finding2

keyFindings: Single sentence synthesis
confidence: High|Medium|Low
tokens_stored: 4500
```

See `@skills/payload-store` for full protocol details.
</payload_store_protocol>

<subagent_coordination>
## 7 Patterns for Reliable Subagent Coordination

1. **Extreme Decomposition**: One task per agent, split on "and"
2. **Token Budgets**: Set limits, retry on overflow (never salvage)
3. **Voting**: 2-3 parallel calls for critical decisions
4. **Right-Sized Models**: haiku for search, sonnet for analysis, opus for synthesis
5. **Strict Formats**: TOON for lists, JSON for objects
6. **Parallel Calls**: Independent operations in one message
7. **Minimal Context**: Goal + constraints only
</subagent_coordination>

<failure_recovery>
## Subagent Failure Recovery

| Symptom | Action |
|---------|--------|
| Output exceeds budget >30% | Discard entirely, retry |
| Wrong format | Discard, retry with stricter instruction |
| 2 consecutive failures | Decompose further OR escalate model |
| Contradictory answers | Query is ambiguous, refine |

**Never**: Try to parse or repair confused output. Discard and retry.
</failure_recovery>

<context_monitoring>
## Context Health Indicators

### Warning Signs
- Token count >60% of limit
- Multiple large file reads in session
- Repeated search patterns (sign of exploration)
- Web fetches returning full content

### Recovery Actions
- Compact conversation history
- Delegate remaining work
- Summarize accumulated findings
- Clear intermediate results from context
</context_monitoring>

<output_optimization>
## Output Format Guidelines

### For File Lists
```toon
files[N]{path,type,purpose}:
  path1,type1,purpose1
  path2,type2,purpose2
```

### For Process Steps
```toon
steps[N]{order,action,result}:
  1,Read config,Found 3 endpoints
  2,Update auth,Added token validation
```

### For Search Results
```toon
matches[N]{file,line,context}:
  src/auth.ts,45,handleLogin function
  src/api.ts,123,validateToken call
```

### For Status Reports
```toon
status{metric,value,threshold}:
  tokens,45000,100000
  files_modified,3,unlimited
  operations,7,delegate_at_3
```
</output_optimization>
