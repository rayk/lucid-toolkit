# Usage Analysis - 2025-12-13

## Summary

| Metric | Value |
|--------|-------|
| Analysis Period | 2025-12-11 to 2025-12-13 |
| Sessions Analyzed | 30 |
| Total Tool Calls | 1,147 |
| Behaviors Invoked | 17 |
| Unique Behaviors Used | 7 |
| Total Input Tokens | 276,314 |
| Total Output Tokens | 482,393 |
| Plugins Available | 7 |
| Plugins Used | 1 (impl-flutter) |

## Plugin Inventory

| Plugin | Version | Behaviors | Sessions Used |
|--------|---------|-----------|---------------|
| architect | 1.0.0 | 9 | 0 |
| analyst | 2.0.0 | 26 | 0 |
| impl-flutter | 2.0.0 | 9 | 7 |
| impl-python | 2.0.0 | 9 | 0 |
| impl-neo4j | 1.1.0 | 7 | 0 |
| luc | 2.4.0 | 7 | 0 |
| plan | 2.0.0 | 4 | 0 |

## Tool Usage Distribution

| Tool | Invocations | % of Total |
|------|-------------|------------|
| Read | 295 | 25.7% |
| Edit | 216 | 18.8% |
| Bash | 209 | 18.2% |
| TodoWrite | 112 | 9.8% |
| Write | 94 | 8.2% |
| Glob | 44 | 3.8% |
| Task | 43 | 3.7% |
| Grep | 31 | 2.7% |
| WebSearch | 20 | 1.7% |
| AskUserQuestion | 14 | 1.2% |
| WebFetch | 12 | 1.0% |
| mcp__dart__analyze_files | 11 | 1.0% |
| TaskOutput | 10 | 0.9% |
| Other | 36 | 3.1% |

## Behaviors Invoked

| Behavior | Type | Invocations | Sessions |
|----------|------|-------------|----------|
| impl-flutter:flutter-env | agent | 3 | 3 |
| impl-flutter:flutter-coder | agent | 3 | 3 |
| impl-flutter:flutter-ux | agent | 2 | 2 |
| impl-flutter:flutter-tester | agent | 2 | 2 |
| Explore | agent | 5 | 5 |
| general-purpose | agent | 1 | 1 |
| impl-flutter:dart-flutter-mcp | skill | 1 | 1 |

## Execution Patterns

| Pattern | Count |
|---------|-------|
| Sequential | 1,147 |
| Foreground Task | 39 |
| Background Task | 4 |
| Parallel | 0 |

---

## Findings

### Category 1: Missed Invocation Opportunities

These patterns indicate manual work where plugins could provide automation or structured guidance.

#### 1.1 Planning Work Without Plan Plugin (Critical)

**Evidence:** 244 file operations involving plan/spec/execution files without `/plan` commands.

**Trigger Pattern:** Users are reading and editing execution plans, specifications, and planning documents manually instead of using the `plan:generate`, `plan:analyze`, or `plan:validate` commands.

**Impact:**
- Manual plan edits may lack validation
- Execution prompts not generated consistently
- No structured checkpoint verification

**Recommendation:**
- Add contextual hints when plan files are detected
- Document `/plan analyze` for existing plan review
- Consider auto-suggesting `/plan validate` after plan edits

#### 1.2 Python Development Without impl-python (High)

**Evidence:** 33 Python file operations with no impl-python behaviors invoked.

**Trigger Pattern:** Direct Read/Edit/Bash operations on `.py` files without leveraging python-coder, python-tester, or python-debugger agents.

**Impact:**
- No specialized Python guidance
- Missing pytest integration
- Environment setup not standardized

**Recommendation:**
- Add detection for Python project markers (pyproject.toml, requirements.txt)
- Auto-load impl-python skill when Python context detected
- Document impl-python agents in project onboarding

#### 1.3 Analysis Tasks Without Analyst Plugin (Medium)

**Evidence:** 5 Task prompts containing "analyze", "assess", "consider", or "evaluate" without analyst plugin involvement.

**Trigger Pattern:** Generic Task agents used for analysis work instead of specialized mental model agents (first-principles, SWOT, 5-whys, etc.).

**Impact:**
- Analysis may lack structured methodology
- Inconsistent evaluation frameworks
- Missing synthesis capabilities

**Recommendation:**
- Improve `/assess` command discoverability
- Add examples of mental model selection to docs
- Consider auto-classifier for analysis requests

#### 1.4 Architecture Decisions Without Architect Plugin (Medium)

**Evidence:** 4 operations on ADR/architecture files without architect plugin behaviors.

**Trigger Pattern:** Manual ADR file creation and architecture documentation without `/architect adr` or `/architect review` commands.

**Impact:**
- ADRs may not follow template
- Architecture consistency not validated
- Component analysis not systematic

**Recommendation:**
- Detect `adr/` or `architecture/` directories
- Suggest `/architect init` for new projects
- Auto-invoke architecture-reviewer on structure changes

---

### Category 2: Suboptimal Performance Patterns

#### 2.1 Sequential Task Execution (Medium)

**Evidence:** 1,147 sequential operations vs 0 parallel operations.

**Observation:** All tool calls are executed sequentially. While some operations require sequential execution (dependencies), independent file reads and exploration could benefit from parallelization.

**Impact:**
- Longer session times
- Higher token usage for wait states
- Reduced throughput

**Recommendation:**
- Review Explore agent for parallel file reading
- Document parallel execution patterns in skills
- Consider batch operations for multi-file edits

#### 2.2 Low Background Task Utilization (Low)

**Evidence:** Only 4 background tasks across 30 sessions.

**Observation:** Long-running operations (test suites, builds) rarely use background execution.

**Impact:**
- User waits for blocking operations
- Context consumed during idle time

**Recommendation:**
- Document background execution for test/build commands
- Add hints for long-running bash commands

---

### Category 3: Unused Behaviors

#### 3.1 Completely Unused Plugins

| Plugin | Behaviors Available | Possible Reasons |
|--------|--------------------|--------------------|
| **architect** | 9 (init, adr, review + agents) | New plugin, low awareness; manual ADR editing preferred |
| **analyst** | 26 (consider, assess, reflect, debate, swarm + 20 mental models) | Commands not discovered; `/assess` not intuitive |
| **impl-python** | 9 (skill + 8 agents) | Python work may be in non-toolkit projects |
| **impl-neo4j** | 7 (skill + 6 agents) | No Neo4j projects in analyzed sessions |
| **luc** | 7 (setup, about + 5 skills) | Base behaviors may not be tracked as invocations |
| **plan** | 4 (generate, analyze, validate + skill) | Manual plan editing preferred |

#### 3.2 Underutilized impl-flutter Behaviors

Within the only used plugin (impl-flutter), some behaviors show no usage:

| Behavior | Type | Notes |
|----------|------|-------|
| flutter-debugger | agent | No debugging sessions captured |
| flutter-data | agent | Data layer work done manually |
| flutter-platform | agent | Platform-specific work not observed |
| flutter-release | agent | No release/deployment sessions |

---

## Priority Actions

### Critical

1. **Improve Plan Plugin Discovery**
   - Add contextual suggestion when plan files detected
   - Create onboarding flow for plan-heavy projects
   - Measure: Track `/plan` command usage in next analysis

### High

2. **Enable impl-python Auto-Detection**
   - Detect pyproject.toml/requirements.txt presence
   - Auto-suggest impl-python installation
   - Measure: Python file operations with plugin usage

3. **Document Analyst Mental Models**
   - Create quick-reference for `/assess` use cases
   - Add examples to analyst plugin README
   - Measure: Analyst plugin invocation rate

### Medium

4. **Architect Plugin Awareness**
   - Add detection for architecture/ directories
   - Suggest `/architect init` for new projects
   - Measure: ADR file creation with plugin assistance

5. **Enable Parallel Execution Patterns**
   - Review Task agent parallelization opportunities
   - Document parallel read patterns
   - Measure: Parallel vs sequential ratio

---

## State

| Field | Value |
|-------|-------|
| Previous Checkpoint | 1970-01-01T00:00:00Z (initial) |
| New Checkpoint | 2025-12-13T12:18:12.307Z |
| Sessions in Analysis | 30 |
| Cumulative Sessions | 30 |

---

## Methodology

- **Data Source:** Claude Code session logs from `~/.claude/projects/`
- **Extraction:** `usage_analysis.py` script (init, discover, parse, aggregate)
- **Analysis Period:** 2025-12-11 to 2025-12-13
- **Sampling:** First 30 unique session logs from discovery (113 total available)
- **Limitations:**
  - Skills loaded via CLAUDE.md inheritance may not show as explicit invocations
  - Behavior detection relies on Task/Skill tool parameters
  - Some projects may not have plugins installed
