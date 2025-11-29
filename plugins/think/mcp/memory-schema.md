# Think Plugin Memory Schema

Schema for storing analysis insights using the Official MCP Memory server.

## Entity Types

| Entity Type | Purpose | Example Name |
|-------------|---------|--------------|
| `Analysis` | A completed think analysis | `analysis-2024-01-15-slow-shipping` |
| `Problem` | A problem that was analyzed | `problem-slow-shipping-cycle` |
| `RootCause` | Identified root cause | `cause-insufficient-testing-time` |
| `Model` | Mental model that was applied | `model-5-whys` |
| `Insight` | Key finding from analysis | `insight-ci-cd-reduces-cycle-time` |
| `Injection` | Solution/intervention (TOC) | `injection-automated-testing-pipeline` |
| `Conflict` | Identified conflict (Six Hats/TOC) | `conflict-speed-vs-quality` |
| `Pattern` | Recurring theme across analyses | `pattern-communication-root-causes` |

## Relation Types

| Relation | From | To | Meaning |
|----------|------|----|---------||
| `analyzed` | Analysis | Problem | "This analysis examined this problem" |
| `identified` | Analysis | RootCause | "This analysis found this root cause" |
| `used_model` | Analysis | Model | "This analysis applied this model" |
| `produced` | Analysis | Insight | "This analysis generated this insight" |
| `caused_by` | Problem | RootCause | "Problem was caused by this" |
| `resolves` | Injection | Conflict | "This injection breaks this conflict" |
| `recurs_in` | RootCause | Pattern | "This root cause is part of a pattern" |
| `similar_to` | Problem | Problem | "These problems are related" |
| `contradicts` | Insight | Insight | "These insights conflict" |
| `supports` | Insight | Insight | "These insights reinforce each other" |

## Observation Templates

### Analysis Entity
```
Observations:
- "Date: 2024-01-15"
- "Type: DIAGNOSIS"
- "Focus: root-cause"
- "Models: 5-whys, first-principles"
- "Confidence: 0.85"
- "Consensus: MAJORITY (2/3)"
- "Key insight: [one sentence summary]"
- "Action taken: [what was done]"
```

### Problem Entity
```
Observations:
- "Domain: software-engineering"
- "Symptoms: [comma-separated UDEs]"
- "First seen: 2024-01-15"
- "Times analyzed: 3"
- "Resolved: true|false"
```

### RootCause Entity
```
Observations:
- "Category: process|technical|communication|resource"
- "Depth: surface|intermediate|root"
- "Actionable: true|false"
- "Occurrences: 5"
```

### Model Entity
```
Observations:
- "Uses: 47"
- "Avg confidence: 0.78"
- "Best for: [problem types]"
- "Last used: 2024-01-15"
```

### Insight Entity
```
Observations:
- "Validated: true|false"
- "Applied: true|false"
- "Outcome: success|partial|failed|pending"
```

## Memory Operations

### After Analysis Completion (Synthesizer)

```
1. create_entities:
   - Analysis entity with full observations
   - Problem entity (if new)
   - RootCause entity (if identified)
   - Insight entity

2. create_relations:
   - Analysis -> analyzed -> Problem
   - Analysis -> identified -> RootCause
   - Analysis -> used_model -> Model (for each model)
   - Analysis -> produced -> Insight
   - Problem -> caused_by -> RootCause

3. add_observations (to existing entities):
   - Update Model entity with new usage stats
   - Update Pattern entity if root cause matches pattern
```

### Before Analysis Start (Consider Skill)

```
1. search_nodes:
   - Query: problem keywords
   - Filter: entityType = "Problem" OR "RootCause" OR "Insight"

2. open_nodes (for relevant matches):
   - Get full observations for similar problems
   - Get insights that were previously generated
   - Get root causes that recur

3. Present to user:
   - "Similar problems analyzed before: [list]"
   - "Common root causes in this area: [list]"
   - "Previous insights that may apply: [list]"
```

## Example Knowledge Graph

```
(analysis-2024-01-15-slow-shipping)
    -[analyzed]-> (problem-slow-shipping-cycle)
    -[identified]-> (cause-insufficient-testing-time)
    -[used_model]-> (model-5-whys)
    -[used_model]-> (model-toc)
    -[produced]-> (insight-ci-cd-reduces-cycle-time)

(problem-slow-shipping-cycle)
    -[caused_by]-> (cause-insufficient-testing-time)
    -[caused_by]-> (cause-developer-rushing)
    -[similar_to]-> (problem-deployment-failures)

(cause-insufficient-testing-time)
    -[recurs_in]-> (pattern-quality-speed-tradeoff)

(injection-automated-testing-pipeline)
    -[resolves]-> (conflict-speed-vs-quality)
```

## Query Patterns

### "What worked for similar problems?"
```
search_nodes: "[problem keywords]"
-> open_nodes: matching Problem entities
-> follow: produced relations to Insight entities
-> filter: observations contain "Outcome: success"
```

### "What root causes keep appearing?"
```
search_nodes: "Occurrences"
-> filter: RootCause entities with high occurrence count
-> return: name + category + linked problems
```

### "Which models work best for this type?"
```
search_nodes: "[problem type]"
-> open_nodes: Model entities
-> sort by: "Avg confidence" observation
```

## Integration Points

| Component | Memory Operation | Trigger |
|-----------|------------------|---------|
| Consider Skill (start) | `search_nodes`, `open_nodes` | Before classification |
| Synthesizer (end) | `create_entities`, `create_relations` | After synthesis complete |
| Validator (optional) | `add_observations` | Update insight validation status |

## MCP Server Configuration

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "~/.claude/think-memory.jsonl"
      }
    }
  }
}
```

Recommended: Use a dedicated memory file for think plugin to avoid mixing with other memory data.

---

## TOC-Specific Entity Types

| Entity Type | Purpose | Example Name |
|-------------|---------|--------------|
| `UDE` | Undesirable Effect (symptom) | `ude-slow-releases` |
| `CausalLink` | A CLR-validated cause-effect pair | `link-rushing-to-bugs` |
| `Assumption` | An EC assumption that can be attacked | `assumption-testing-slow` |
| `NegativeBranch` | Unintended consequence of injection | `negbranch-fewer-tests` |

## TOC-Specific Relation Types

| Relation | From | To | Meaning |
|----------|------|----|---------|
| `symptom_of` | UDE | Problem | "This UDE indicates this problem" |
| `leads_to` | Entity | Entity | "Forward causal link (FRT)" |
| `validated_by_clr` | CausalLink | - | (stored in observations) |
| `blocks` | Conflict | RootCause | "This conflict prevents resolution" |
| `assumes` | Conflict | Assumption | "This conflict depends on this assumption" |
| `invalidates` | Injection | Assumption | "This injection breaks this assumption" |
| `prevents` | Injection | NegativeBranch | "Trimming injection prevents this" |
| `trimmed_by` | NegativeBranch | Injection | "This side effect is handled by" |

## TOC-Specific Observation Templates

### UDE Entity
Observations:
- "Symptom: [observable behavior]"
- "Evidence: [how we know]"
- "Severity: h|m|l"
- "First seen: {date}"
- "Linked to problem: {problem-name}"

### CausalLink Entity
Observations:
- "From: {cause entity name}"
- "To: {effect entity name}"
- "CLR Status: VALID|INVALID|PENDING"
- "CLR Checks: clarity:pass, entity:pass, causality:pass, sufficiency:fail"
- "Failed reservation: {if any}"
- "Revision: {if revised}"
- "Validator confidence: 0.0-1.0"

### Assumption Entity
Observations:
- "Arrow: {from} -> {to}"
- "Statement: [the assumption text]"
- "Type: necessity|conflict"
- "Attacked: true|false"
- "Attack method: {injection name if attacked}"
- "Weakness score: h|m|l"

### Conflict Entity
Observations:
- "Objective (A): [common goal]"
- "Requirement B: [need 1]"
- "Requirement C: [need 2]"
- "Prerequisite D: [action 1]"
- "Prerequisite D': [action 2, conflicts with D]"
- "Core tension: [D] vs [D']"
- "Resolved: true|false"
- "Resolution: {injection name}"

### NegativeBranch Entity
Observations:
- "Injection: {source injection}"
- "Consequence: [what goes wrong]"
- "Severity: h|m|l"
- "Likelihood: h|m|l"
- "Trimmed: true|false"
- "Trimming injection: {name}"

### Injection Entity (extended)
Observations:
- "Type: primary|trimming"
- "Attacks assumption: {assumption name}"
- "Resolves conflict: {conflict name}"
- "Outcome: pending|success|partial|failed"
- "Implementation date: {date}"
- "Side effects prevented: {count}"

## TOC Memory Operations

### Phase 1 Storage (After CRT)

1. Create UDE entities for each symptom:
```
create_entities([
  { name: "ude-{slug}", entityType: "UDE", observations: [...] }
])
```

2. Create CausalLink entities for each validated link:
```
create_entities([
  { name: "link-{from}-{to}", entityType: "CausalLink", observations: [
    "From: cause-{from}",
    "To: cause-{to}",
    "CLR Status: VALID",
    "CLR Checks: clarity:pass, entity:pass, causality:pass, sufficiency:pass"
  ]}
])
```

3. Create RootCause entity:
```
create_entities([
  { name: "cause-{slug}", entityType: "RootCause", observations: [...] }
])
```

4. Create relations:
```
create_relations([
  { from: "ude-X", to: "problem-Y", relationType: "symptom_of" },
  { from: "link-A-B", to: "link-B-C", relationType: "leads_to" },
  { from: "problem-Y", to: "cause-Z", relationType: "caused_by" }
])
```

### Phase 2 Storage (After EC)

1. Create Conflict entity:
```
create_entities([
  { name: "conflict-{slug}", entityType: "Conflict", observations: [...] }
])
```

2. Create Assumption entities:
```
create_entities([
  { name: "assumption-{slug}", entityType: "Assumption", observations: [...] }
])
```

3. Create relations:
```
create_relations([
  { from: "conflict-X", to: "cause-Y", relationType: "blocks" },
  { from: "conflict-X", to: "assumption-Z", relationType: "assumes" }
])
```

### Phase 3 Storage (After FRT)

1. Create Injection entity:
```
create_entities([
  { name: "injection-{slug}", entityType: "Injection", observations: [...] }
])
```

2. Create NegativeBranch entities:
```
create_entities([
  { name: "negbranch-{slug}", entityType: "NegativeBranch", observations: [...] }
])
```

3. Create relations:
```
create_relations([
  { from: "injection-X", to: "conflict-Y", relationType: "resolves" },
  { from: "injection-X", to: "assumption-Z", relationType: "invalidates" },
  { from: "injection-trim", to: "negbranch-W", relationType: "prevents" }
])
```

### Recall Operations (Before Analysis)

```
search_nodes("{symptom keywords}")
→ Filter: entityType IN ["UDE", "RootCause", "Conflict", "Injection"]

For each match:
  open_nodes(["{match.name}"])
  → Extract observations
  → Build context for user

Present:
  "## Prior TOC Context

  **Similar symptoms previously analyzed:**
  - {ude-name}: {observations}

  **Root causes that recurred:**
  - {cause-name}: appeared in {N} analyses

  **Conflicts that match this pattern:**
  - {conflict-name}: resolved by {injection-name}

  **Suggested approach:**
  - Attack assumption: {assumption with high weakness score}
  - Consider injection: {injection with Outcome: success}"
```
