# TOON Integration Implementation Plan

## Executive Summary

Integrate Token-Optimized Object Notation (TOON) across all 6 Lucid Toolkit plugins to achieve **40-55% token reduction** on structured data exchanges while preserving all existing functionality.

**Approach:** Phased, evidence-based integration using subagent delegation with cross-check verification at each phase.

---

## Critical Findings from Validation

### Breaking Changes Identified

**12 HIGH-RISK breaking points** requiring mitigation:

| Component | Location | Impact |
|-----------|----------|--------|
| Status Line Display | `plugins/context/scripts/status_line.py:75` | Field `summary.currentFocusedOutcome` breaks |
| Capability Snapshot Hook | `plugins/capability/hooks/regenerate_snapshot.py:50-65` | 6+ `.get()` field accesses on nested structure |
| Defocus/Complete/Focus Commands | `plugins/outcome/commands/*.md` | jq queries against `activeSessions` fail |
| Move Command Cross-refs | `plugins/outcome/commands/move.md:145-242` | Array/object structure assumptions break |
| Workspace Health Check | `plugins/workspace/commands/health.md:42-56` | Circular dependency detection fails |

### Missing Commands in Original Plan

| Plugin | Commands Missing |
|--------|------------------|
| Context | `/context:compact` |
| Outcome | `/outcome:defocus`, `/outcome:design`, `/outcome:edit`, `/outcome:delete` |
| Workspace | `/workspace:add`, `/workspace:remove`, `/workspace:switch`, `/workspace:subscribe`, `/workspace:unsubscribe` |

### Test Infrastructure Gaps

- **No test files exist** - pytest configured but no tests written
- **No TOON fixtures** - `shared/test_fixtures/toon/` does not exist
- **No TOON schema** - `shared/schemas/toon_schema.json` must be created
- **6 untested Python modules** in `shared/cli-commons/`
- **3 untested hooks** (988 lines total)

### Mitigation Strategy

**Dual Format Support Required:**
1. Create TOON parsers alongside existing JSON parsers
2. Add runtime format detection in consuming scripts
3. Maintain backward compatibility during transition
4. Phase migration by dependency order

---

## Phase 0: Foundation & Standards (BLOCKING)

### 0.1 Create TOON Validation Schema
**Location:** `shared/schemas/toon_schema.json`

Create JSON Schema that validates:
- Valid schema.org @type values
- ActionStatusType mappings
- Required x- prefix on custom properties
- Tabular array syntax patterns

**Deliverable:** Schema file + validation utility in `shared/cli-commons/`

### 0.2 Create TOON Test Fixtures
**Location:** `shared/test_fixtures/toon/`

Create reference examples for each pattern:
- `action_completed.toon` - Basic action result
- `create_action.toon` - Artifact creation
- `update_action_transitions.toon` - State transitions
- `item_list_tabular.toon` - Tabular collection
- `analyze_action_gaps.toon` - Analysis results
- `assess_action_verdict.toon` - Assessment with confidence

**Deliverable:** 6 fixture files + validation tests

### 0.3 Baseline Token Measurement
**Method:** Use existing commands to generate output, measure token count

| Command | Current Format | Baseline Tokens | Target Savings |
|---------|----------------|-----------------|----------------|
| capability:snapshot | markdown | TBD | 50-66% |
| outcome:move | markdown | TBD | 35-47% |
| workspace:health | markdown | TBD | 43-53% |
| context:info | markdown | TBD | 35-45% |
| plan execution | markdown | TBD | 43-58% |
| think:assess verdict | markdown | TBD | 30-50% |

---

## Phase 1: Context Plugin (Already In Progress)

**Priority:** HIGH - Context plugin already has toon-schema skill defined
**Estimated Savings:** 35-45%

### 1.1 Inventory Existing TOON Support

Files to analyze:
- `plugins/context/skills/toon-schema/SKILL.md` - Reference implementation
- `plugins/context/skills/payload-store/SKILL.md` - Already uses TOON returns
- `plugins/context/commands/info.md` - Session statistics
- `plugins/context/commands/budget.md` - Token breakdown
- `plugins/context/commands/checkpoint.md` - Session checkpoints

### 1.2 Commands to Update

#### 1.2.1 `/context:info` Command
**Current:** Markdown tables for session stats
**Target TOON Format:**
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
tokensConsumed,45000

health:
usage: 45
limit: 100000
status: HEALTHY
```

**Changes:**
1. Add `output_format: toon` to command metadata
2. Update output template in command body
3. Preserve markdown narrative for context description

#### 1.2.2 `/context:budget` Command
**Current:** Markdown consumption table
**Target TOON Format:**
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

**Changes:**
1. Convert breakdown table to TOON tabular array
2. Add summary section with status
3. Keep recommendation text as markdown

#### 1.2.3 `/context:checkpoint` Command
**Current:** Mixed format
**Target TOON Format:**
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

### 1.3 Verification
- Run each command before/after
- Measure token reduction
- Verify all data preserved
- Test with payload-store for large outputs

---

## Phase 2: Outcome Plugin (Highest Value)

**Priority:** VERY HIGH - Most data-rich, highest savings potential
**Estimated Savings:** 35-47%

### 2.1 Commands to Update

#### 2.1.1 `/outcome:move` Command
**Current:** Markdown transition log
**Target TOON Format:**
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

**Changes:**
1. Convert transitions list to TOON tabular
2. Add maturity delta tracking
3. Map outcome states to ActionStatusType
4. Keep summary message as prose

#### 2.1.2 `/outcome:create` Command
**Target TOON Format:**
```toon
@type: CreateAction
actionStatus: CompletedActionStatus
@id: 005-ontology-sync
result: Created ontology sync outcome for Neo4J integration

filesCreated[2]: outcome_track.json,outcome-statement.md
crossRefsUpdated[2]: capability_track.json,outcome_summary.json
```

#### 2.1.3 `/outcome:complete` Command
**Target TOON Format:**
```toon
@type: UpdateAction
actionStatus: CompletedActionStatus
@id: 005-authentication
result: Outcome completed, capability maturity updated

transition:
fromStatus: ActiveActionStatus
toStatus: CompletedActionStatus

maturityUpdate{capability,from,to,delta}:
authentication-system,45,55,+10
```

#### 2.1.4 `/outcome:decompose` Command
**Target TOON Format:**
```toon
@type: CreateAction
actionStatus: CompletedActionStatus
@id: 010-security-vulnerabilities
result: Decomposed into 3 child outcomes

children[3]{@id,x-contribution,actionStatus}:
010.1-sql-injection,33,PotentialActionStatus
010.2-xss-prevention,33,PotentialActionStatus
010.3-auth-bypass,34,PotentialActionStatus
```

### 2.2 Skills to Update

#### 2.2.1 `focus` Skill
**Return format (subagent):**
```toon
@type: Action
actionStatus: CompletedActionStatus
name: focus
object: 005-authentication
result: outcomes/2-in-progress/005-authentication
```

### 2.3 Subagent Returns
All outcome-related subagent returns should use TOON:
- Observable effects status lists
- Parent-child hierarchies
- Capability contribution summaries

---

## Phase 3: Workspace Plugin

**Priority:** HIGH - Health checks generate large structured output
**Estimated Savings:** 43-53%

### 3.1 Commands to Update

#### 3.1.1 `/workspace:list` Command
**Target TOON Format:**
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

#### 3.1.2 `/workspace:health` Command
**Target TOON Format:**
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

#### 3.1.3 `/workspace:validate` Command
**Target TOON Format:**
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

#### 3.1.4 `/workspace:resolve` Command
**Target TOON Format:**
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

## Phase 4: Plan Plugin

**Priority:** HIGH - Execution tracking is token-intensive
**Estimated Savings:** 43-58%

### 4.1 Skills to Update

#### 4.1.1 `execution-prompt-generator` Skill
**Dependency Analysis Return:**
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

**Phase Status Tracking:**
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

**Model Usage Report:**
```toon
@type: ItemList
name: model-usage

model[3]{name,x-inputTokens,x-outputTokens,x-calls,x-costUSD}:
haiku,5000,2000,3,0.0038
sonnet,80000,25000,15,0.615
opus,15000,5000,2,0.60
```

**Cross-Check Results:**
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

---

## Phase 5: Capability Plugin

**Priority:** MEDIUM-HIGH
**Estimated Savings:** 50-66%

### 5.1 Commands to Update

#### 5.1.1 `/capability:snapshot` Command
**Target TOON Format:**
```toon
@type: ItemList
name: capabilities
numberOfItems: 5
x-avgMaturity: 52

itemListElement[5]{name,x-maturity,x-target,actionStatus,x-domain|tab}:
authentication-system	47	80	ActiveActionStatus	Data Security & Privacy
tenant-isolation	35	90	ActiveActionStatus	Data Security & Privacy
admin-portal	100	80	CompletedActionStatus	Product Lifecycle
api-gateway	60	75	ActiveActionStatus	Integration
logging-system	75	90	ActiveActionStatus	Operations
```

#### 5.1.2 `/capability:create` Command
**Return TOON Format:**
```toon
@type: CreateAction
actionStatus: CompletedActionStatus
@id: authentication-system
result: Created capability with initial maturity 0%

filesCreated[2]: capability_track.json,capability-statement.md
crossRefsUpdated[1]: capability_summary.json
```

#### 5.1.3 `/capability:delete` Command
**Return TOON Format:**
```toon
@type: Action
actionStatus: CompletedActionStatus
@id: deprecated-feature
result: Deleted capability and cleaned up references

filesRemoved[2]: capability_track.json,capability-statement.md
crossRefsUpdated[3]: capability_summary.json,outcome_1.json,outcome_2.json
```

### 5.2 Subagent Returns
Capability list queries from subagents:
```toon
@type: ItemList
name: capabilities
numberOfItems: 5
x-avgMaturity: 52

itemListElement[5]{name,x-maturity,x-target,actionStatus,x-domain|tab}:
...
```

---

## Phase 6: Think Plugin

**Priority:** MEDIUM - Mix of narrative and structured output
**Estimated Savings:** 30-50%

### 6.1 Commands to Update

#### 6.1.1 `/think:consider` Command
**Problem Classification (structured section only):**
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

**Note:** Keep reasoning/analysis as markdown prose. Only structure the classification output.

#### 6.1.2 `/think:assess` Command
**Gap Analysis:**
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

**Final Verdict:**
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

#### 6.1.3 `/think:reflect` Command
**Reflection Findings:**
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

## Cross-Check Verification Strategy

### Per-Phase Verification

1. **Syntax Validation**
   - Run TOON schema validator on all outputs
   - Check @type values against schema.org list
   - Verify ActionStatusType mappings
   - Confirm x- prefix on custom properties

2. **Functional Verification**
   - Execute command with test data
   - Compare data completeness vs baseline
   - Verify no information loss
   - Test edge cases (empty lists, long values, commas in fields)

3. **Token Measurement**
   - Count tokens in baseline output
   - Count tokens in TOON output
   - Calculate actual savings %
   - Document in phase report

4. **Integration Testing**
   - Run affected commands end-to-end
   - Verify subagent consumers can parse TOON
   - Test payload-store integration for large outputs
   - Validate cross-plugin data exchange

### Rollback Strategy

Each phase maintains:
- Git commit before changes
- Backup of original command files
- Feature flag for TOON output (optional)

If issues detected:
1. Revert to backup
2. Document failure mode
3. Adjust approach
4. Re-attempt with fixes

---

## Implementation Delegation Matrix

| Phase | Primary Agent | Verification Agent | Cross-Check |
|-------|---------------|-------------------|-------------|
| 0 (Foundation) | general-purpose | debugger | Schema validation |
| 1 (Context) | general-purpose | Explore | Before/after comparison |
| 2 (Outcome) | general-purpose | debugger | State transition testing |
| 3 (Workspace) | general-purpose | Explore | Health check validation |
| 4 (Plan) | general-purpose | debugger | Execution tracking |
| 5 (Capability) | general-purpose | Explore | Snapshot verification |
| 6 (Think) | general-purpose | Explore | Reasoning preservation |

---

## Success Criteria

### Quantitative
- [ ] Achieve 40%+ token reduction on structured outputs
- [ ] Zero data loss in any conversion
- [ ] All existing tests pass
- [ ] No functional regressions

### Qualitative
- [ ] TOON syntax consistent across all plugins
- [ ] Schema.org types used correctly
- [ ] ActionStatusType mappings accurate
- [ ] Human-readable output preserved where needed

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing functionality | Per-phase verification, git commits, rollback plan |
| Inconsistent TOON usage | Central schema + validation in Phase 0 |
| Token savings less than expected | Measure baselines first, adjust targets |
| Subagent parsing issues | Test consumers before finalizing format |
| Complex nested data | Keep to 2 levels max, use markdown for deeper |

---

## Execution Order

1. **Phase 0:** Foundation (blocks all others)
2. **Phase 1:** Context (already has toon-schema, quick win)
3. **Phase 2:** Outcome (highest value, most savings)
4. **Phase 3:** Workspace (health/validation improvements)
5. **Phase 4:** Plan (execution tracking)
6. **Phase 5:** Capability (snapshot improvements)
7. **Phase 6:** Think (selective - structured sections only)

**Parallelization:** After Phase 0, Phases 1-6 can proceed in parallel with separate subagents, merging at verification checkpoints.

---

## Appendix A: Complete File Inventory by Plugin

### Context Plugin (6 commands, 5 skills, 2 hooks)
**Commands:**
- `commands/info.md` - Session info display
- `commands/budget.md` - Token budget display
- `commands/checkpoint.md` - Checkpoint creation
- `commands/compact.md` - Context window compression *(MISSING FROM ORIGINAL PLAN)*
- `commands/update.md` - Context tracking reconciliation
- `commands/validate.md` - Health validation

**Skills:**
- `skills/toon-schema/SKILL.md` - TOON reference (existing)
- `skills/payload-store/SKILL.md` - Already uses TOON
- `skills/checkpoint/SKILL.md` - Session tracking
- `skills/conserve/SKILL.md` - Context conservation
- `skills/delegate/SKILL.md` - Delegation decisions

**Hooks (HIGH RISK):**
- `hooks/context_start.py` - Session initialization
- `hooks/context_end.py` - Session cleanup

**Scripts (HIGH RISK):**
- `scripts/status_line.py` - Status line display (336 lines)

### Outcome Plugin (9 commands, 1 skill)
**Commands:**
- `commands/create.md` - Outcome creation
- `commands/move.md` - State transitions (HIGH RISK - cross-refs)
- `commands/complete.md` - Completion handling
- `commands/decompose.md` - Child outcome creation
- `commands/focus.md` - Focus management
- `commands/defocus.md` - Remove focus *(MISSING FROM ORIGINAL PLAN)*
- `commands/design.md` - Design documents *(MISSING FROM ORIGINAL PLAN)*
- `commands/edit.md` - Edit properties *(MISSING FROM ORIGINAL PLAN)*
- `commands/delete.md` - Delete outcome *(MISSING FROM ORIGINAL PLAN)*

**Skills:**
- `skills/focus/SKILL.md` - Focus transition workflow

### Workspace Plugin (10 commands, 1 hook)
**Commands:**
- `commands/init.md` - Initialize workspace
- `commands/list.md` - Project listing
- `commands/health.md` - Comprehensive health check (HIGH RISK)
- `commands/validate.md` - Schema/ref validation
- `commands/resolve.md` - Module resolution
- `commands/add.md` - Add project *(MISSING FROM ORIGINAL PLAN)*
- `commands/remove.md` - Remove project *(MISSING FROM ORIGINAL PLAN)*
- `commands/switch.md` - Switch context *(MISSING FROM ORIGINAL PLAN)*
- `commands/subscribe.md` - Subscribe to workspace *(MISSING FROM ORIGINAL PLAN)*
- `commands/unsubscribe.md` - Unsubscribe *(MISSING FROM ORIGINAL PLAN)*

**Hooks:**
- `hooks/pre-commit-validation.py` - Pre-commit validation (125 lines)

### Plan Plugin (1 skill)
**Skills:**
- `skills/execution-prompt-generator/SKILL.md` - TDD execution prompts

**Schemas:**
- `schemas/audit_trail_schema.json`
- `schemas/checkpoint_schema.json`
- `schemas/execution_result_schema.json`

### Capability Plugin (3 commands, 1 hook)
**Commands:**
- `commands/create.md` - Capability creation
- `commands/snapshot.md` - Capability display
- `commands/delete.md` - Capability deletion

**Hooks (HIGH RISK):**
- `hooks/regenerate_snapshot.py` - Snapshot generation (258 lines)

### Think Plugin (3 commands, 1 skill)
**Commands:**
- `commands/consider.md` - Problem analysis
- `commands/assess.md` - Solution assessment
- `commands/reflect.md` - Behavior reflection

**Skills:**
- `skills/consider/SKILL.md` - Mental models

---

## Appendix B: High-Risk File Dependencies

### JSON Summary Files (Breaking Change Sources)

| File | Consumers | Risk Level |
|------|-----------|------------|
| `sessions_summary.json` | status_line.py, context hooks, outcome commands | CRITICAL |
| `capability_summary.json` | snapshot hook, workspace health, outcome move | CRITICAL |
| `outcome_summary.json` | move command, workspace health, capability updates | HIGH |

### Field Access Patterns Requiring Updates

```python
# status_line.py:75 - WILL BREAK
summary.get("currentFocusedOutcome")

# regenerate_snapshot.py:50-65 - WILL BREAK
capability.get("name")
capability.get("maturity")
capability.get("targetMaturity")

# outcome commands - jq queries WILL BREAK
jq '.activeSessions | keys[]'
jq '.summary.currentFocusedOutcome'
```

---

## Appendix C: Test Infrastructure Requirements

### Directory Structure to Create

```
shared/
├── schemas/
│   └── toon_schema.json              # NEW: TOON validation
├── test_fixtures/
│   └── toon/                         # NEW: Reference examples
│       ├── action_completed.toon
│       ├── create_action.toon
│       ├── update_action_transitions.toon
│       ├── item_list_tabular.toon
│       ├── analyze_action_gaps.toon
│       └── assess_action_verdict.toon
└── cli-commons/
    ├── src/lucid_cli_commons/
    │   └── toon_parser.py            # NEW: TOON parsing utility
    └── tests/                        # NEW: Test suite
        ├── conftest.py
        ├── test_validation.py
        ├── test_toon_parser.py
        └── test_schema_compliance.py

plugins/
├── context/tests/                    # NEW
├── capability/tests/                 # NEW
├── outcome/tests/                    # NEW
└── workspace/tests/                  # NEW
```

### Existing Schemas (13 files)
All require test coverage:
- `plugins/capability/schemas/capability_summary_schema.json`
- `plugins/capability/schemas/capability_track_schema.json`
- `plugins/context/schemas/context_tracking_schema.json`
- `plugins/context/schemas/sessions_summary_schema.json`
- `plugins/outcome/schemas/outcome_summary_schema.json`
- `plugins/outcome/schemas/outcome_track_schema.json`
- `plugins/plan/schemas/audit_trail_schema.json`
- `plugins/plan/schemas/checkpoint_schema.json`
- `plugins/plan/schemas/execution_result_schema.json`
- `plugins/workspace/schemas/actor_summary_schema.json`
- `plugins/workspace/schemas/project_map_schema.json`
- `plugins/workspace/schemas/workspace_schema.json`
- `shared/workspaces/workspaces_schema.json`
