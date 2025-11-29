---
description: Multi-agent deliberation for complex decisions requiring adversarial exploration
argument-hint: <decision or proposal to debate>
allowed-tools: Task, Read, AskUserQuestion
---

<objective>
Conduct structured debate between advocate, critic, and analyst agents to thoroughly explore a decision from multiple perspectives, then have a judge deliver verdict.
</objective>

<workflow>

## Phase 1: Frame the Debate

Parse user input to identify:
- The decision/proposal being debated
- Key stakeholders affected
- Known constraints

Present framing to user for confirmation.

## Phase 2: Parallel Debate Agents

Launch 3 debate agents simultaneously:

```
Task 1 (general-purpose, sonnet):
  @role: ADVOCATE
  Argue FOR the proposal: "$ARGUMENTS"

  Build the strongest possible case using:
  - First Principles reasoning
  - Opportunity Cost analysis (what we miss by NOT doing this)
  - Evidence and examples

  @output:
  @type: DebatePosition
  position: FOR
  arguments[N]{point,evidence,strength}:
    {argument},{supporting evidence},{HIGH|MEDIUM|LOW}
  concessions[N]: {valid concerns acknowledged}

  @constraints: maxTokens: 2000

Task 2 (general-purpose, sonnet):
  @role: CRITIC
  Argue AGAINST the proposal: "$ARGUMENTS"

  Identify all risks and downsides using:
  - Inversion (what would guarantee failure)
  - Second-Order effects (and then what)
  - Via Negativa (what simpler alternatives exist)

  @output:
  @type: DebatePosition
  position: AGAINST
  arguments[N]{point,evidence,severity}:
    {argument},{supporting evidence},{HIGH|MEDIUM|LOW}
  concessions[N]: {valid benefits acknowledged}

  @constraints: maxTokens: 2000

Task 3 (general-purpose, sonnet):
  @role: ANALYST
  Evaluate BOTH positions objectively for: "$ARGUMENTS"

  Use:
  - SWOT analysis
  - 10-10-10 time horizon analysis

  @output:
  @type: DebateAnalysis
  forStrengths[N]: {strongest FOR arguments}
  againstStrengths[N]: {strongest AGAINST arguments}
  blindSpots[N]: {what both sides missed}
  tradeoffs[N]: {key tradeoffs identified}

  @constraints: maxTokens: 2000
```

All 3 execute in parallel.

## Phase 3: Judgment

Launch judge agent with all positions:

```
Task (general-purpose, opus):
  @role: JUDGE
  Review all debate positions and deliver reasoned verdict.

  Advocate position: {output 1}
  Critic position: {output 2}
  Analyst evaluation: {output 3}

  Weigh arguments, identify decisive factors, deliver recommendation.

  @output:
  @type: DebateVerdict
  recommendation: {PROCEED|REJECT|MODIFY}
  reasoning: {why this recommendation}
  keyFactors[N]: {decisive considerations}
  conditions[N]: {if PROCEED, conditions that must hold}
  modifications[N]: {if MODIFY, what changes needed}
  confidence: {0.0-1.0}

  @constraints: maxTokens: 2500
```

## Phase 4: Present Debate Summary

```markdown
## Debate: {proposal}

---

### FOR (Advocate)
**Strongest Arguments:**
1. {argument} (strength: {level})
2. {argument}
3. {argument}

**Concedes:** {what advocate acknowledges}

---

### AGAINST (Critic)
**Strongest Arguments:**
1. {argument} (severity: {level})
2. {argument}
3. {argument}

**Concedes:** {what critic acknowledges}

---

### Analysis
**FOR Strengths:** {summary}
**AGAINST Strengths:** {summary}
**Blind Spots Both Missed:** {list}
**Key Tradeoffs:** {list}

---

### VERDICT: {PROCEED|REJECT|MODIFY}

**Reasoning:** {judge's reasoning}

**Decisive Factors:**
- {factor 1}
- {factor 2}

**Conditions (if proceeding):**
- {condition 1}
- {condition 2}

**Confidence:** {%}

---

### Performance
- Debate agents: 3 (parallel)
- Judge: 1 (opus)
- Total tokens: ~{estimate}
```

</workflow>

<success_criteria>
- All 3 debate positions generated in parallel
- Each position uses appropriate mental models
- Judge weighs all perspectives
- Verdict includes conditions and confidence
</success_criteria>
