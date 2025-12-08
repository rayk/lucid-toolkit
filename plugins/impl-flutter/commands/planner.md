---
description: Generate high-confidence autonomous implementation prompts (>90% success probability) from specifications
argument-hint: <spec-path> [--dry-run] [--target-confidence <percent>]
allowed-tools: [Read, Write, Glob, Grep, Bash, Task, WebSearch, WebFetch, AskUserQuestion]
---

<objective>
Analyze requirements and produce a Claude Code CLI (Opus 4.5) execution prompt that has greater than 90% probability of autonomously implementing the specified code with tests.

If success probability falls below 90%, stop and report specific blockers preventing autonomous execution.

This command produces prompts, not implementations. The output prompt is designed to execute from an empty context window and complete within 75% of the available context budget.
</objective>

<preconditions>
Before generating an execution prompt, ALL preconditions must be verified:

| Precondition | Validation | Failure Action |
|--------------|------------|----------------|
| **Clear verification criteria** | Spec contains executable test criteria | STOP: "Spec lacks testable acceptance criteria" |
| **Zero ambiguity** | No questions needed during implementation | STOP: "Ambiguity detected: {specific issues}" |
| **Dependencies identified** | All imports/libs/services listed | STOP: "Unresolved dependencies: {list}" |
| **Dependencies confirmed** | Pre-existing deps exist in codebase | STOP: "Missing dependencies: {list}" |
| **Project alignment** | Approach matches CLAUDE.md constraints | STOP: "Constraint violation: {detail}" |
| **Context budget** | Estimated tokens < 75% of window | STOP: "Scope too large: {estimate} tokens" |
| **Decomposable** | Can split into parallel subagent tasks | STOP: "Cannot decompose: {reason}" |
</preconditions>

<confidence_model>
<description>
Estimate probability of autonomous success based on specification quality.
</description>

<scoring>
Start at 100% and subtract for each risk factor:

| Risk Factor | Deduction | Detection |
|-------------|-----------|-----------|
| Vague acceptance criteria | -15% | No testable assertions |
| Missing dependency versions | -10% | Libraries without versions |
| Unclear API contracts | -15% | Method signatures undefined |
| No error handling spec | -10% | Silent on failure modes |
| Ambiguous scope boundaries | -10% | "and more" or "etc." language |
| Missing examples | -5% | No concrete input/output examples |
| Conflicting requirements | -20% | Contradictory statements |
| External service dependency | -5% each | APIs, databases, services |
| Novel/unfamiliar patterns | -10% | Unusual architecture |
| Large scope (>50 files) | -15% | High file count estimate |

**Threshold**: Proceed only if confidence >= 90% (or user-specified target)
</scoring>

<confidence_report>
```
Confidence Assessment: {final_percentage}%

Deductions:
- {factor}: -{deduction}% ({reason})
- ...

{IF confidence < 90%}
BLOCKED: Cannot generate prompt with sufficient confidence.

Remediation required:
1. {specific action to address factor}
2. ...
{/IF}
```
</confidence_report>
</confidence_model>

<process>
<phase_0 name="Parse Arguments">
Parse $ARGUMENTS into components:

1. **spec_path** = First argument (required)
   - If empty: STOP with "Usage: /impl:planner <spec-path> [--dry-run] [--target-confidence <percent>]"
   - Verify file exists or STOP with "Specification file not found: {path}"

2. **dry_run** = true if $ARGUMENTS contains "--dry-run"
   - When true: analyze only, do not write output files

3. **target_confidence** = Extract value after "--target-confidence" or default to 90
   - Must be integer between 50-100
   - Example: `--target-confidence 95` sets threshold to 95%

Store these values for use in subsequent phases.
</phase_0>

<phase_1 name="Load Context">
1. Read the specification file at spec_path

2. Load project context (check existence first):
   - If `.claude/workspace-info.toon` exists → read for workspace structure
   - Else if `.claude/project-info.toon` exists → read for project metadata
   - Else → note "No project context file found, using spec-only mode"

3. Load project constraints:
   - If `CLAUDE.md` exists → read for constraints and conventions
   - Else → note "No CLAUDE.md found, using default constraints"

4. Identify target language and framework from:
   - Project context files (if loaded)
   - Specification content
   - Package files (package.json, pyproject.toml, etc.)
</phase_1>

<phase_2 name="Validate Preconditions">
Run precondition checks in parallel:

```
Task(subagent_type="Explore", model="haiku", prompt="""
Check specification for testable acceptance criteria.
Return: {hasCriteria: bool, criteria: list, issues: list}
""")

Task(subagent_type="Explore", model="haiku", prompt="""
Extract all dependencies from specification.
Return: {external: list, internal: list, unresolved: list}
""")

Task(subagent_type="Explore", model="haiku", prompt="""
Check specification for ambiguous language.
Return: {isAmbiguous: bool, ambiguities: list}
""")
```

After parallel checks complete:
- Verify internal dependencies exist in codebase (Glob/Read)
- Verify external dependencies are available (check package.json/pyproject.toml)
- Check CLAUDE.md for constraint conflicts
</phase_2>

<phase_3 name="Calculate Confidence">
Apply confidence scoring model:

1. Score each risk factor from the scoring table
2. Calculate final confidence percentage (starting from 100%)
3. Compare against target_confidence (from Phase 0, default 90%)
4. If confidence < target_confidence:
   - Generate remediation report listing all deductions
   - Output blockers to user with specific remediation actions
   - STOP execution (do not proceed to Phase 4)
5. If confidence >= target_confidence:
   - Log "Confidence {percentage}% meets target {target_confidence}%"
   - Proceed to Phase 4
</phase_3>

<phase_4 name="Decompose Work">
Break implementation into parallel-safe units:

```
Task(subagent_type="specialize:architect", prompt="""
Decompose this specification into implementation phases:

Requirements:
1. Each phase must be independently testable
2. Phase dependencies must be explicit
3. Phases should maximize parallelism
4. No phase should exceed 20% of context budget
5. Identify which phases can use haiku vs sonnet vs opus

Return phase structure with:
- Phase name and description
- Dependencies on other phases
- Estimated token budget
- Recommended model
- Rollback strategy if phase fails
""")
```
</phase_4>

<phase_5 name="Context Budget Analysis">
Estimate total context consumption:

| Component | Estimate Method |
|-----------|-----------------|
| Spec reading | Token count of spec file |
| Project context | ~2000 tokens (CLAUDE.md, project-info) |
| Per-phase overhead | ~1000 tokens (instructions, checkpoints) |
| TDD cycles | ~3000 tokens per component |
| Cross-checks | ~5000 tokens |
| Buffer for errors | 10% of total |

**Budget constraint**: Total must be < 75% of context window (~150k tokens for Opus)

If over budget:
- Further decompose large phases
- Increase parallel subagent usage
- Externalize reference context to files
</phase_5>

<phase_6 name="Generate Execution Prompt">
Produce the autonomous execution prompt following this structure:

```markdown
# Autonomous Implementation: {system-name}

## Execution Identity
- System: {name}
- Language: {language} {version}
- Framework: {framework}
- Generated: {timestamp}
- Confidence: {percentage}%

## Pre-Execution Validation
Before starting, verify:
{dependency_checklist}

## Execution Phases

### Phase 0: Setup (haiku, 2 min)
{scaffolding_instructions}
Rollback: rm -rf {created_dirs}

### Phase 1: Foundation (sonnet, 10 min)
{foundation_instructions}
Rollback: git checkout -- {files}

### Phase N: {name} ({model}, {time})
{instructions}
Rollback: {rollback_strategy}

## Parallel Subagent Delegation
{subagent_delegation_instructions}

## Failure Contingencies
{failure_handling_matrix}

## Cross-Check Protocol
{verification_steps}

## Reporting Requirements
On completion, output:
{reporting_template}
```
</phase_6>

<phase_7 name="Output Generation">
Check dry_run flag (from Phase 0):

**If dry_run is true:**
- Output confidence report to console
- Output phase breakdown to console
- Output execution estimate to console
- Do NOT write any files
- End with: "Dry run complete. Use without --dry-run to generate files."

**If dry_run is false:**
Write output files:
1. `execution-prompt.md` - The generated prompt (ready for autonomous execution)
2. `confidence-report.md` - Detailed confidence analysis with all risk factors
3. `phase-breakdown.md` - Phase structure with token estimates and rollback strategies

After writing, output success summary with file paths and execution instructions.
</phase_7>
</process>

<execution_prompt_requirements>
The generated execution prompt MUST include:

<requirement name="Empty Context Start">
Prompt must work from a fresh Claude Code session with no prior context.
Include all necessary file paths, commands, and patterns inline.
</requirement>

<requirement name="75% Budget Limit">
Total execution must consume less than 75% of context window.
Reserve 25% for:
- Error handling and debugging
- TDD red-green-refactor cycles
- Cross-check verification
</requirement>

<requirement name="Parallel Decomposition">
Maximize use of parallel subagents:
- Use `Task(subagent_type="Explore")` for read-only investigation
- Use `Task(subagent_type="general-purpose")` for implementation tasks
- Use specialized agents when available (specialize:python-coder, etc.)
</requirement>

<requirement name="Context Externalization">
Prevent context pollution:
- Write intermediate results to files, not memory
- Use checkpoint files between phases
- Reference external docs by path, not inline content
</requirement>

<requirement name="Failure Contingencies">
Every phase must have:
- Clear success criteria
- Rollback strategy if failed
- Escalation path (sonnet → opus → user)
</requirement>

<requirement name="Implementation Summary">
Prompt must require final output containing:
```
## Implementation Summary

### Completed
- {list of implemented components}

### Learnings
- {insights discovered during implementation}

### Metrics
- Total tokens: {input + output}
- Execution time: {duration}
- Model distribution: haiku: {%}, sonnet: {%}, opus: {%}
- TDD cycles: {count}
- Test coverage: {percentage}%

### Checkpoint
{final state for potential continuation}
```
</requirement>
</execution_prompt_requirements>

<subagent_patterns>
<note>
These patterns show conceptual Task tool usage. When generating execution prompts, translate to natural language instructions that Claude Code will interpret as Task tool invocations.
</note>

<pattern name="Parallel Investigation">
Launch multiple Explore agents in parallel for independent data gathering:
- Use `run_in_background=true` for concurrent execution
- Wait for all results with `AgentOutputTool(block=true)` before proceeding

Conceptual structure:
```
Task(Explore, haiku, background) → scan dependencies
Task(Explore, haiku, background) → check test patterns
Task(Explore, haiku, background) → analyze imports
Wait for all → merge results
```
</pattern>

<pattern name="Phased Implementation">
Sequential phases with parallel branches where dependencies allow:

Conceptual structure:
```
Phase 1 (sonnet) → foundation code
  ↓ (must complete)
Phase 2a (sonnet, background) → feature A
Phase 2b (sonnet, background) → feature B
  ↓ (wait for both)
Phase 3 (sonnet) → integration
```

Use specialized agents when available (specialize:python-coder, specialize:flutter-coder, etc.)
</pattern>

<pattern name="Escalation on Failure">
Try cheaper/faster models first, escalate on failure:

Conceptual structure:
```
Attempt (sonnet) → implement component
  ↓ (if failed)
Debug (opus) → analyze failure, suggest fix
  ↓ (if still failed)
Escalate → report to user with context
```

Always capture error context before escalating to preserve debugging information.
</pattern>
</subagent_patterns>

<output_format>
<success_output>
```
## Execution Prompt Generated

Confidence: {percentage}%
Target: {target}%
Status: READY FOR EXECUTION

### Output Files
- execution-prompt.md ({token_count} tokens)
- confidence-report.md
- phase-breakdown.md

### Execution Estimate
- Phases: {count}
- Estimated duration: {time}
- Estimated tokens: {tokens} ({budget_percentage}% of budget)
- Model distribution: haiku {%}, sonnet {%}, opus {%}

### To Execute
```bash
claude --prompt execution-prompt.md
```
```
</success_output>

<blocked_output>
```
## Execution Prompt BLOCKED

Confidence: {percentage}%
Target: {target}%
Status: INSUFFICIENT CONFIDENCE

### Blockers
{numbered_list_of_blockers}

### Remediation Required
{specific_actions_to_resolve_each_blocker}

### After Remediation
Re-run: /impl:planner {spec-path}
```
</blocked_output>
</output_format>

<success_criteria>
Command succeeds when:
- All preconditions validated
- Confidence >= target threshold (default 90%)
- Execution prompt generated with all requirements
- Budget estimate < 75% of context window
- All phases have rollback strategies
- Implementation summary template included

Command blocks (correctly) when:
- Any precondition fails
- Confidence < target threshold
- Scope exceeds context budget
- Cannot decompose into parallel-safe phases

**Uncertainty Handling:**
- NEVER guess at solutions when evidence is insufficient. If you cannot determine the answer with confidence, explicitly state: "I don't have enough information to confidently assess this."
</success_criteria>
