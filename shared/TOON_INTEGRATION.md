# TOON Integration Guide

Cross-plugin Token-Optimized Object Notation (TOON) standards for the Lucid Toolkit.

**Estimated Savings:** 40-55% token reduction on structured data exchanges.

---

## Quick Reference

### TOON Syntax

```toon
# Simple values
name: authentication-service
status: active

# Primitive arrays (inline)
tags[3]: security,auth,core

# Tabular arrays (most efficient)
items[3]{name,status,count}:
widget-a,active,5
widget-b,pending,3
widget-c,done,10

# Tab delimiter for fields with commas
items[2]{name,description|tab}:
widget-a	Handles authentication flow
widget-b	Manages session tokens
```

### Schema.org Integration

| Type | Usage |
|------|-------|
| `@type: Action` | General operations, validations, health checks |
| `@type: CreateAction` | Artifact creation (outcomes, checkpoints, files) |
| `@type: UpdateAction` | State transitions, maturity updates |
| `@type: AnalyzeAction` | Problem classification, gap analysis |
| `@type: ChooseAction` | Model/framework selection |
| `@type: AssessAction` | Evaluations, verdicts, reflections |
| `@type: ItemList` | Collections (capabilities, projects, phases) |

### ActionStatusType Mapping

| Domain State | Schema.org Status |
|--------------|-------------------|
| queued, ready, pending | `PotentialActionStatus` |
| in-progress, active, current | `ActiveActionStatus` |
| completed, success, done | `CompletedActionStatus` |
| blocked, failed, error | `FailedActionStatus` |

---

## Lucid Extensions (x- prefix)

Standard custom properties across all plugins:

| Extension | Type | Used By |
|-----------|------|---------|
| `x-maturity` | number (0-100) | capability, outcome |
| `x-target` | number (0-100) | capability |
| `x-gap` | number | capability |
| `x-contribution` | number | outcome |
| `x-tokens` | number | session, budget, payload, plan |
| `x-capabilityId` | string | outcome |
| `x-domain` | string | capability |
| `x-workspaceName` | string | workspace |
| `x-confidence` | number (0-100) | think, research |
| `x-phase` | string | plan |
| `x-duration` | number (seconds) | plan, session |
| `x-costUSD` | number | plan |

---

## Plugin-Specific Patterns

### Capability Plugin

**Capability List (subagent return)**
```toon
@type: ItemList
name: capabilities
numberOfItems: 5
x-avgMaturity: 52

itemListElement[5]{name,x-maturity,x-target,actionStatus,x-domain|tab}:
authentication-system	47	80	ActiveActionStatus	Data Security & Privacy
tenant-isolation	35	90	ActiveActionStatus	Data Security & Privacy
admin-portal	100	80	CompletedActionStatus	Product Lifecycle
```

**Validation Results**
```toon
@type: Action
name: schema-validation
actionStatus: FailedActionStatus

errors[2]{file,field,error}:
capability_track.json,purpose,Required field missing
capability_track.json,coreValues.primary,Must have 1-3 items

warnings[1]{file,field,warning}:
capability_track.json,scope.excluded,Empty array
```

**Circular Dependency Error**
```toon
@type: Action
name: dependency-validation
actionStatus: FailedActionStatus
error: Circular dependency detected

chain[4]{name,requires,minMaturity}:
auth-system,user-management,50
user-management,role-based-access,30
role-based-access,auth-system,60
auth-system,-,-

x-cycleStart: auth-system
```

---

### Outcome Plugin

**Focus Command Return**
```toon
@type: Action
actionStatus: CompletedActionStatus
name: focus
object: 005-authentication
result: outcomes/2-in-progress/005-authentication
```

**Create Command Return**
```toon
@type: CreateAction
actionStatus: CompletedActionStatus
@id: 005-ontology-sync
result: Created ontology sync outcome for Neo4J integration

filesCreated[2]: outcome_track.json,outcome-statement.md
crossRefsUpdated[2]: capability_track.json,outcome_summary.json
```

**Move Command Output**
```toon
@type: UpdateAction
actionStatus: CompletedActionStatus
name: move-outcomes
result: Moved 2 outcomes to in-progress

transitions[2]{@id,fromStatus,toStatus}:
001-jwt-auth,PotentialActionStatus,ActiveActionStatus
002-session-mgmt,PotentialActionStatus,ActiveActionStatus

maturity[1]{capability,from,to,delta}:
authentication-system,45,47,+2
```

**Observable Effects Status**
```toon
@type: ItemList
name: observable-effects
x-verified: 2
x-pending: 1

itemListElement[3]{position,verified,actor|tab}:
1	true	lot-owner
2	true	lot-owner
3	false	security-team
```

**Parent-Child Tree**
```toon
@type: ItemList
name: children
x-parent: 010-security-vulnerabilities

itemListElement[3]{@id,actionStatus,x-contribution}:
010.1-sql-injection,CompletedActionStatus,33
010.2-xss-prevention,PotentialActionStatus,33
010.3-auth-bypass,PotentialActionStatus,34
```

---

### Workspace Plugin

**Project Listing**
```toon
@type: ItemList
@id: workspace/lucid-toolkit
name: Lucid Toolkit
x-type: monorepo
numberOfItems: 6

itemListElement[6]{name,@type,x-role,path|tab}:
capability	plugin	primary	plugins/capability
outcome	plugin	primary	plugins/outcome
context	plugin	primary	plugins/context
think	plugin	supporting	plugins/think
workspace	plugin	supporting	plugins/workspace
plan	plugin	supporting	plugins/plan
```

**Health Check Results**
```toon
@type: Action
@id: health-check/2025-11-29
name: workspace-health
actionStatus: FailedActionStatus
x-fixes: 0
x-capabilities: 5
x-avgMaturity: 47

phases[8]{position,name,actionStatus,x-duration,x-issues}:
1,Capability sync,CompletedActionStatus,12,-
2,Outcome sync,CompletedActionStatus,8,-
3,Cross-refs,FailedActionStatus,15,2
4,Indexes,CompletedActionStatus,5,-
5,Temporal health,CompletedActionStatus,3,-
6,Temp cleanup,CompletedActionStatus,2,-
7,Git health,CompletedActionStatus,8,-
8,Report,CompletedActionStatus,1,-

issues[2]{x-severity,description}:
HIGH,Circular: auth-system -> user-management -> auth-system
MEDIUM,Stale index for deprecated capability
```

**Validation Results**
```toon
@type: Action
name: workspace-validation
actionStatus: FailedActionStatus

schemaResults[2]{file,actionStatus,error}:
workspaces.json,CompletedActionStatus,-
capability_track.json,FailedActionStatus,missing purpose

brokenRefs[2]{file,line,ref}:
commands/create.md,15,@templates/missing.md
skills/analyze/SKILL.md,42,@research/nonexistent.md
```

**Module Resolution**
```toon
@type: Action
@id: resolve/luon:neo4j_service
actionStatus: CompletedActionStatus
name: neo4j_service
x-project: luon
x-moduleType: service
path: /Users/dev/luon/src/neo4j_service/

entryPoints[2]{name,file}:
CypherLoader,cypher_loader.py
QueryEngine,query_engine.py
```

---

### Context Plugin

**Session Info**
```toon
@type: Action
@id: session/sess-xyz123
name: current-session
actionStatus: ActiveActionStatus
startTime: 2025-01-15T10:30:00Z
x-duration: 45min

stats{metric,value}:
eventsLogged,23
filesModified,5
tasksCompleted,8
tasksFailed,1
gitCommits,2
tokensConsumed,45000
subagentsUsed,4

health:
usage: 45
limit: 100000
status: HEALTHY
```

**Budget Status**
```toon
@type: Action
name: budget-status
actionStatus: ActiveActionStatus

summary:
current: 45000
limit: 100000
available: 55000
percent: 45
status: HEALTHY

breakdown[4]{category,tokens,percent}:
systemPrompt,8000,18
conversation,22000,49
toolResults,12000,27
currentMessage,3000,6
```

**Checkpoint**
```toon
@type: CreateAction
name: checkpoint
actionStatus: CompletedActionStatus
endTime: 2025-01-15T11:45:00Z

accomplishments[2]: Implemented JWT refresh,Added session tests
decisions[1]: Using RS256 for token signing
nextSteps[2]: Add integration tests,Update API docs

delta{metric,value}:
filesModified,3
tasksCompleted,5
tokensConsumed,12000
```

**Payload Store Return**
```toon
@stored: shared/payloads/sess-abc123/20251128-research.md

summary[3]{aspect,finding}:
Primary Source,NSW Fair Trading
Key Regulation,Strata Schemes Management Act 2015
Reform Status,5-phase reform 2023-2026

keyFindings: NSW strata governed by 2015 Act with ongoing reforms
confidence: High
tokens_stored: 4500
```

---

### Plan Plugin

**Dependency Analysis**
```toon
@type: ItemList
name: dependencies

external[2]{name,version,actionStatus}:
pytest,8.0.0,CompletedActionStatus
pydantic,2.5.0,FailedActionStatus

preExisting[2]{name,path,actionStatus}:
BaseService,src/base.py,CompletedActionStatus
AuthHandler,src/auth.py,FailedActionStatus

created[1]{name,x-phase,x-requiredBy}:
UserService,phase_3_core,phase_4_features
```

**Phase Status Tracking**
```toon
@type: Action
name: execution-progress
actionStatus: ActiveActionStatus
x-currentPhase: phase_3_core

phase[9]{name,actionStatus,x-model,x-timeout,x-tokens}:
phase_0_setup,CompletedActionStatus,orchestrator,2m,1000
phase_1_scaffolding,CompletedActionStatus,haiku,3m,5000
phase_2_foundation,CompletedActionStatus,sonnet,15m,20000
phase_3_core,ActiveActionStatus,sonnet,20m,30000
phase_4_features,PotentialActionStatus,sonnet,15m,25000
phase_5_integration,PotentialActionStatus,sonnet,5m,5000
phase_6_verification,PotentialActionStatus,orchestrator,5m,8000
phase_7_debug,PotentialActionStatus,opus,10m,-
phase_8_crosscheck,PotentialActionStatus,sonnet+opus,30m,15000
```

**Model Usage**
```toon
@type: ItemList
name: model-usage

model[3]{name,x-inputTokens,x-outputTokens,x-calls,x-costUSD}:
haiku,5000,2000,3,0.0038
sonnet,80000,25000,15,0.615
opus,15000,5000,2,0.60
```

**Cross-Check Results**
```toon
@type: Action
name: cross-check-results
actionStatus: FailedActionStatus
x-passed: 5
x-failed: 2
x-skipped: 1

check[8]{name,actionStatus,x-detail}:
lint,CompletedActionStatus,-
coverage,CompletedActionStatus,85%
style,FailedActionStatus,3 errors
architecture,CompletedActionStatus,-
requirements,CompletedActionStatus,-
acceptance,PotentialActionStatus,skipped
documentation,FailedActionStatus,5 missing
custom,CompletedActionStatus,-
```

**Checkpoint**
```toon
@type: Action
name: checkpoint
x-version: 1.0
x-system: auth-service
x-lastCompleted: phase_3_core
x-nextPhase: phase_4_features

completed[4]{name,endTime}:
phase_0_setup,2025-11-29T10:00:00Z
phase_1_scaffolding,2025-11-29T10:03:00Z
phase_2_foundation,2025-11-29T10:18:00Z
phase_3_core,2025-11-29T10:38:00Z

pending[5]: phase_4_features,phase_5_integration,phase_6_verification,phase_7_debug,phase_8_crosscheck
```

---

### Think Plugin

**Problem Classification**
```toon
@type: AnalyzeAction
name: problem-classification
object: Why do production errors not appear in staging?
actionStatus: CompletedActionStatus

classification:
primaryType: DIAGNOSIS
temporalFocus: PAST
complexity: COMPLICATED
emotionalLoading: LOW

signals[3]: why,cause,root
```

**Model Selection**
```toon
@type: ChooseAction
name: model-selection
actionStatus: CompletedActionStatus

selection[2]{role,model,rationale}:
primary,5-Whys,Root cause analysis matches problem signals
supporting,First-Principles,Validates assumptions at root
```

**Assessment Verdict**
```toon
@type: AssessAction
name: solution-assessment
actionStatus: CompletedActionStatus
x-confidence: 62

verdict:
status: viable-with-improvements
criticalFlaws: 2
minorConcerns: 4

gaps[3]{type,description}:
assumption,Infinite bandwidth assumed
constraint,No latency requirements defined
blackbox,Data processing unspecified

nextSteps[3]: clarify latency,add circuit breakers,security review
```

**Gap Analysis**
```toon
@type: AnalyzeAction
name: gap-analysis
actionStatus: CompletedActionStatus

assumptions[2]{assumption,riskLevel}:
Infinite network bandwidth,high
No concurrent writes,medium

missingConstraints[3]{constraint,category}:
Budget limitations,financial
Latency SLA,performance
GDPR scope,regulatory

blackBoxes[1]{component,issue}:
Data processing,No implementation detail
```

**Reflection Findings**
```toon
@type: AssessAction
name: reflection-findings
actionStatus: CompletedActionStatus

finding:
incident: Direct edit without delegation for multi-file operation
protocolViolated: Delegate when location unknown
rootCause: Specificity trap - error message gave false confidence
failurePattern: Specificity Trap

x-conversationTurn: 15
x-toolsUsed: 7
```

---

## When to Use TOON

**Use TOON for:**
- Subagent return values (transient, machine-consumed)
- Status displays with tabular data
- Cross-plugin data exchange
- Validation result reporting
- Action/operation results
- Lists and collections

**Do NOT use TOON for:**
- Human-facing final output (use markdown)
- Narrative/analytical content (reasoning chains, explanations)
- Single-value responses
- Instructional content (process steps, workflows)
- Deeply nested structures (>2 levels)

---

## Implementation Checklist

When adding TOON support to a command/skill:

- [ ] Identify structured data in output
- [ ] Choose appropriate schema.org @type
- [ ] Map status values to ActionStatusType
- [ ] Use x- prefix for custom extensions
- [ ] Use tabular arrays for uniform collections
- [ ] Use tab delimiter for fields containing commas
- [ ] Keep human-facing output in markdown
- [ ] Test with payload-store for large outputs
- [ ] Document in command's output_format section

---

## Token Savings Summary

| Plugin | Primary Opportunity | Savings |
|--------|---------------------|---------|
| capability | Subagent list returns | 50-66% |
| outcome | State transition reports | 35-47% |
| workspace | Health/validation reports | 43-53% |
| context | Session/budget info | 35-45% |
| plan | Phase tracking, cost reports | 43-58% |
| think | Classification, verdicts | 30-50% |

**Overall expected savings: 40-55% on structured data exchanges.**
