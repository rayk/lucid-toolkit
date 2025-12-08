---
description: Parallel hypothesis testing for diagnosis problems
argument-hint: <symptom or problem to diagnose>
allowed-tools: Task, Read, Grep, Glob, Bash
---

<objective>
Deploy multiple hypothesis agents in parallel to rapidly explore potential causes for observed symptoms.
</objective>

<workflow>

## Phase 1: Symptom Analysis

Analyze the symptom/problem:

```
Task (think-classifier, haiku):
  Analyze symptom: "$ARGUMENTS"

  Identify:
  - Observable symptoms
  - Context and timing
  - Potential domains (infrastructure, code, data, external)

  @constraints: maxTokens: 1000
```

## Phase 2: Hypothesis Generation

Generate 4-6 distinct hypotheses:

```
Task (general-purpose, sonnet):
  Generate hypotheses for: "$ARGUMENTS"

  For each hypothesis provide:
  - Clear statement of potential cause
  - What evidence would confirm it
  - What evidence would refute it
  - Investigation approach

  @output:
  @type: HypothesisList
  hypotheses[N]{id,statement,confirmingEvidence,refutingEvidence,investigation}:
    H1,{hypothesis},{what confirms},{what refutes},{how to test}
    H2,...

  @constraints: maxTokens: 2000
```

## Phase 3: Parallel Investigation

Launch investigation agent for each hypothesis (4-6 in parallel):

```
Task 1 (Explore, haiku):
  @hypothesis: H1 - {hypothesis statement}

  Investigate by: {investigation steps}
  Look for: {confirming/refuting evidence}

  Search codebase, logs, and configs for relevant evidence.

  @output:
  @type: InvestigationResult
  hypothesis: H1
  evidenceFound[N]{type,finding,location}:
    {CONFIRMING|REFUTING|NEUTRAL},{what found},{where}
  verdict: {LIKELY|UNLIKELY|INCONCLUSIVE}
  confidence: {0.0-1.0}

  @constraints: maxTokens: 1500

Task 2 (Explore, haiku):
  @hypothesis: H2 - {hypothesis}
  ... (same pattern)

Task 3-6: (parallel, same pattern)
```

All hypothesis investigations run in parallel.

## Phase 4: Synthesis

Rank hypotheses by evidence:

```
Task (think-synthesizer, sonnet):
  Rank hypotheses by evidence strength:

  Investigation results:
  - H1: {result}
  - H2: {result}
  - H3: {result}
  - H4: {result}

  @output:
  @type: DiagnosisSynthesis
  rankedHypotheses[N]{rank,hypothesis,confidence,keyEvidence}:
    1,{statement},{0.0-1.0},{key supporting finding}
    2,...

  rootCause: {most likely cause}
  nextSteps[N]: {recommended investigation or action}
  alternatives[N]: {other possibilities to keep in mind}

  @constraints: maxTokens: 1500
```

## Phase 5: Present Results

```markdown
## Diagnosis: {symptom}

---

### Hypotheses Investigated: {count}

| Rank | Hypothesis | Confidence | Key Evidence |
|------|------------|------------|--------------|
| 1 | {hypothesis} | {%} | {evidence} |
| 2 | {hypothesis} | {%} | {evidence} |
| 3 | {hypothesis} | {%} | {evidence} |

---

### Most Likely Root Cause
**{root cause statement}**

**Supporting Evidence:**
- {evidence 1} (found in {location})
- {evidence 2}

**Confidence:** {%}

---

### Recommended Next Steps
1. {step 1}
2. {step 2}

### Alternative Explanations to Consider
- {alternative 1}
- {alternative 2}

---

### Performance
- Hypotheses generated: {count}
- Parallel investigations: {count}
- Total tokens: ~{estimate}
```

</workflow>

<success_criteria>
- 4-6 hypotheses generated
- All investigations run in parallel
- Evidence clearly categorized as confirming/refuting
- Ranked output with confidence scores
</success_criteria>
