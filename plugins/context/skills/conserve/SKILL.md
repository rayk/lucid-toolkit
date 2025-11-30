---
name: conserve
description: MANDATORY context conservation protocol. ALWAYS apply these techniques - use TOON format for structured output, delegate external data operations, and coordinate subagents efficiently. Triggers on ANY output generation, file listings, search results, status reports, MCP operations, or subagent coordination.
---

<when_invoked>
**This skill activates AUTOMATICALLY when:**

- Generating ANY structured output (file lists, tables, search results, status)
- Returning results from Glob, Grep, or file searches
- Producing output with 3+ similar items
- Orchestrating subagent operations
- Any operation producing >200 tokens of uniform data

**Apply TOON format and conservation techniques without prompting.**

<correct_flow>
User: "what files are in the auth directory?"

CORRECT:
1. Execute Glob/Read to get file list
2. Apply @skills conserve for output
3. Return:
```toon
files[5]{path,purpose}:
  src/auth/login.ts,User authentication
  src/auth/session.ts,Session management
  src/auth/token.ts,JWT utilities
  src/auth/middleware.ts,Auth middleware
  src/auth/types.ts,Type definitions
```
</correct_flow>

<incorrect_flow>
INCORRECT (what NOT to do):
1. Execute Glob/Read
2. Return verbose output:
   "I found 5 files in the auth directory:
    - src/auth/login.ts - This file handles user authentication...
    - src/auth/session.ts - This manages sessions...
    ..." ← WRONG: Verbose, wastes context
</incorrect_flow>

<recognition_triggers>
Apply this skill when producing:
- File listings from Glob results
- Search matches from Grep
- Step-by-step summaries
- Status or progress reports
- Any list of 3+ items with uniform structure
- Results from MCP tools or web fetches
</recognition_triggers>
</when_invoked>

<objective>
Apply context conservation techniques to EVERY response. The main context window is precious - preserve it for strategic decisions, complex reasoning, and high-level coordination by using efficient output formats and proper delegation.

**This is not optional.** Always use TOON for structured data, delegate external operations, and minimize token usage.
</objective>

<quick_start>
**ALWAYS apply these techniques:**

1. **TOON format** - Use for ALL structured output (file lists, steps, search results, status)
2. **Delegate external data** - MCP tools, web fetches → subagent + payload-store
3. **Minimal subagent context** - Goal + constraints only, strip history
4. **Parallel operations** - Independent tasks in single message

**Quick TOON reference:**
```toon
files[3]{path,purpose}:
  src/auth.ts,Login handler
  src/session.ts,Session management
  src/token.ts,JWT utilities
```
</quick_start>

<core_principle>
**Context is precious. The main agent coordinates and synthesizes, not executes routine work.**

Preserve the main context window for:
- Strategic decisions
- Complex reasoning
- High-level coordination
</core_principle>

<conservation_techniques>
<toon_format>
Token-Oriented Object Notation provides ~40% savings vs JSON:

```toon
files[3]{path,purpose,lines}:
  src/auth/login.ts,Main login handler,145
  src/auth/session.ts,Session management,89
  src/auth/token.ts,JWT utilities,67
```

Use for: file lists, process steps, config lookups, uniform data structures.
Use JSON only for non-uniform complex objects.
</toon_format>

<index_first_lookup>
For location queries, check index files first:
```
User: "where is neo4jservice?"
→ Check project_map.json first (1 op vs many greps)
```
</index_first_lookup>

<minimal_subagent_context>
Provide only: goal statement, constraints, expected output format.
Strip: full conversation history, unrelated context, verbose explanations.
</minimal_subagent_context>

<parallel_operations>
Independent operations in single message:
```
Task(search files, haiku) + Task(search patterns, haiku)
→ Parallel execution, single response aggregation
```
</parallel_operations>

<result_summarization>
Request structured summaries from subagents:
- 300-500 token responses max
- Key findings only
- Skip intermediate reasoning
</result_summarization>
</conservation_techniques>

<external_data_operations>
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
For operations producing >500 tokens, use the payload-store skill.

<when_to_use>
- Research tasks returning comprehensive reports
- MCP tools scraping documentation
- Analysis requiring full context preservation
- Any output that may need re-access later
</when_to_use>

<how_it_works>
1. Subagent generates full output
2. Stores to `shared/payloads/{session}/` (or explicit path if provided)
3. Returns TOON summary + `@stored: path` reference
4. Main agent uses summary, can Read full payload if needed
</how_it_works>

<delegation_instruction>
```
Task(research, opus):
  "Research X comprehensively.

   Use payload-store protocol:
   - Store full output to shared/payloads/
   - Return TOON summary with @stored path
   - Summary max 300 tokens"
```
</delegation_instruction>

<return_format>
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
</return_format>
</payload_store_protocol>

<subagent_coordination>
1. **Extreme Decomposition**: One task per agent, split on "and"
2. **Token Budgets**: Set limits, retry on overflow (never salvage)
3. **Voting**: 2-3 parallel calls for critical decisions
4. **Right-Sized Models**: haiku for search, sonnet for analysis, opus for synthesis
5. **Strict Formats**: TOON for lists, JSON for objects
6. **Parallel Calls**: Independent operations in one message
7. **Minimal Context**: Goal + constraints only
</subagent_coordination>

<failure_recovery>
| Symptom | Action |
|---------|--------|
| Output exceeds budget >30% | Discard entirely, retry |
| Wrong format | Discard, retry with stricter instruction |
| 2 consecutive failures | Decompose further OR escalate model |
| Contradictory answers | Query is ambiguous, refine |

**Never**: Try to parse or repair confused output. Discard and retry.
</failure_recovery>

<context_monitoring>
<warning_signs>
- Token count >60% of limit
- Multiple large file reads in session
- Repeated search patterns (sign of exploration)
- Web fetches returning full content
</warning_signs>

<recovery_actions>
- Compact conversation history
- Delegate remaining work
- Summarize accumulated findings
- Clear intermediate results from context
</recovery_actions>
</context_monitoring>

<output_optimization>
<file_lists>
```toon
files[N]{path,type,purpose}:
  path1,type1,purpose1
  path2,type2,purpose2
```
</file_lists>

<process_steps>
```toon
steps[N]{order,action,result}:
  1,Read config,Found 3 endpoints
  2,Update auth,Added token validation
```
</process_steps>

<search_results>
```toon
matches[N]{file,line,context}:
  src/auth.ts,45,handleLogin function
  src/api.ts,123,validateToken call
```
</search_results>

<status_reports>
```toon
status{metric,value,threshold}:
  tokens,45000,100000
  files_modified,3,unlimited
  operations,7,delegate_at_3
```
</status_reports>
</output_optimization>

<success_criteria>
**Conservation applied correctly when:**

- TOON format used for ALL structured output (file lists, steps, search results, status)
- External data operations delegated with payload-store protocol
- Subagent context minimal (goal + constraints only)
- Parallel operations batched into single messages
- Token budgets enforced on all subagent calls
- Summaries requested (300-500 tokens max) instead of full output

**Anti-success indicators (conservation failure):**

- JSON used for uniform data structures (should be TOON)
- MCP/web content returned directly to main context (should be payload-stored)
- Full conversation history passed to subagents
- Sequential calls that could have been parallel
- Large outputs returned inline instead of stored externally
</success_criteria>

<self_audit>
## Post-Response Audit

After completing tool operations, verify protocol compliance:

### Checkpoint Verification
1. Did response begin with checkpoint?
   - YES → Protocol followed
   - NO → Log violation, apply checkpoint to next response

2. Did operation count match reality?
   - Within ±1 → Acceptable
   - Off by 2+ → Improve estimation next time

3. Was delegation appropriate?
   - Direct execution exhausted >500 tokens → Should have delegated
   - Delegation used for 1-op task → Acceptable (false positive OK)

### Recovery Actions
**If you realize mid-response that you skipped the checkpoint:**

Output it immediately before continuing:
```
[Late checkpoint: N ops → should have delegated]: Fixing inline
```

**If you completed a response without checkpoint:**

Acknowledge in next response:
```
[Note: Previous response missing checkpoint - correcting]
[N ops → direct|delegate]: Current task rationale
```

### Violation Patterns to Self-Monitor
- Multiple consecutive responses without checkpoints
- "Simple" tasks that consumed >500 context tokens
- Sequential tool calls that could have been parallel
- Using general-purpose agent when specialized agent exists

**Recovery is always better than pretending compliance.**
</self_audit>
