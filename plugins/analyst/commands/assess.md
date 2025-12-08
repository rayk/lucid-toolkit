---
description: Four-phase rigorous assessment with parallel stress testing
argument-hint: [solution or problem description to assess]
allowed-tools: Task, Read, AskUserQuestion
---

<objective>
Assess $ARGUMENTS through rigorous four-phase protocol with parallel stress testing:
1. Gap Analysis (identify assumptions, constraints, black boxes)
2. Framework Selection (match domain to evaluation frameworks)
3. Parallel Stress Testing (4 agents test simultaneously)
4. Verdict and Recommendation
</objective>

<phase_1_gap_analysis>
## Phase 1: Gap Analysis

Analyze the solution for gaps:

1. **Implicit Assumptions**: List everything taken for granted
2. **Missing Constraints**: Budget, performance, regulatory, timeline
3. **Black Boxes**: Vaguely described components

```
Task (general-purpose, haiku):
  Analyze for gaps: "$ARGUMENTS"

  Identify:
  - All implicit assumptions
  - Missing constraints (budget, latency, compliance, etc.)
  - Black box components with vague descriptions

  @output TOON format:
  @type: GapAnalysis
  assumptions[N]{assumption,riskLevel}
  missingConstraints[N]{constraint,category}
  blackBoxes[N]{component,issue}

  @constraints: maxTokens: 1500
```
</phase_1_gap_analysis>

<phase_2_framework_selection>
## Phase 2: Framework Selection

Based on solution domain, select evaluation frameworks:

| Domain | Frameworks |
|--------|------------|
| Distributed Systems | CAP Theorem, PACELC, Fallacies |
| Security | STRIDE, Zero Trust, OWASP Top 10 |
| Architecture | SOLID, 12-Factor, DDD |
| Reliability | Chaos Engineering, SRE Golden Signals |
| Data | ACID vs BASE, Data Mesh |
| Scalability | Little's Law, Amdahl's Law |

State which framework(s) apply and why.
</phase_2_framework_selection>

<phase_3_parallel_stress_testing>
## Phase 3: Parallel Stress Testing

Launch 4 stress test agents simultaneously:

```
Task 1 (general-purpose, haiku):
  @role: Edge Case Analyst
  Analyze solution for edge cases:
  - 10x/100x load scenarios
  - Malicious input handling
  - Hardware failure modes
  - Partial failures (degraded mode)

  @output: edgeCases[N]{scenario,impact,severity}
  @constraints: maxTokens: 1500

Task 2 (general-purpose, haiku):
  @role: Second-Order Analyst
  Analyze solution for second-order effects:
  - Vendor lock-in implications
  - Technical debt accumulation
  - Team cognitive load changes
  - Cost scaling patterns

  @output: secondOrderEffects[N]{effect,timeline,severity}
  @constraints: maxTokens: 1500

Task 3 (general-purpose, haiku):
  @role: SPOF Analyst
  Identify single points of failure:
  - Infrastructure dependencies
  - Data flow bottlenecks
  - Human process dependencies
  - Key person risks

  @output: spofs[N]{component,impact,mitigation}
  @constraints: maxTokens: 1500

Task 4 (model-inversion, sonnet):
  @role: Adversarial Analyst
  Apply inversion: "How would this solution fail catastrophically?"

  @output: failureModes[N]{mode,mechanism,avoidance}
  @constraints: maxTokens: 1800
```

All 4 agents execute in parallel (single message).
</phase_3_parallel_stress_testing>

<phase_4_verdict>
## Phase 4: Verdict and Recommendation

Synthesize all stress test results:

```
Task (think-synthesizer, sonnet):
  Synthesize stress test findings:
  - Edge cases: {output 1}
  - Second-order: {output 2}
  - SPOFs: {output 3}
  - Failure modes: {output 4}

  Calculate:
  - Critical flaws count
  - Minor concerns count
  - Aggregate confidence (0.0-1.0)

  @constraints: maxTokens: 1500
```

**Confidence Scoring:**
- 0.0-0.25: Critical gaps prevent assessment
- 0.26-0.50: Major concerns require resolution
- 0.51-0.75: Viable with improvements
- 0.76-1.0: Sound with minor refinements

Output verdict:

```toon
@type: AssessmentVerdict
solution: {solution being assessed}
actionStatus: CompletedActionStatus

x-confidence: {0.0-1.0}

verdict:
  status: {viable-with-improvements|major-concerns|critical-gaps|sound-approach}
  criticalFlaws: {count}
  minorConcerns: {count}

improvements[N]{area,recommendation}:
  {area 1},{specific improvement}

nextSteps[N]: {action 1},{action 2},{action 3}
```
</phase_4_verdict>

<output_format>
## Assessment Complete

**Solution:** {restated solution}
**Confidence:** {%} - {status}

---

### Gap Analysis
- **Assumptions:** {count identified}
- **Missing Constraints:** {list}
- **Black Boxes:** {components needing detail}

### Frameworks Applied
- {framework 1}: {key findings}
- {framework 2}: {key findings}

### Stress Test Results

**Edge Cases:**
- {scenario}: {impact} - {severity}

**Second-Order Effects:**
- {effect}: {timeline}

**Single Points of Failure:**
- {component}: {mitigation}

**Failure Modes:**
- {mode}: {avoidance strategy}

---

### Verdict: {status}

**Critical Flaws:** {count}
**Minor Concerns:** {count}

### Recommended Improvements
1. {improvement 1}
2. {improvement 2}

### Next Steps
- {step 1}
- {step 2}

---

### Performance Metrics
- Stress test agents: 4 (parallel)
- Total tokens: ~{estimate}
</output_format>

<success_criteria>
- All 4 phases completed in order
- Phase 3 executes 4 agents in parallel
- Confidence score reflects actual findings
- Improvements are specific and actionable
</success_criteria>
