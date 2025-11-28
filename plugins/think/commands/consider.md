---
description: Analyze problems using mental models with interactive approach selection
argument-hint: [problem, decision, or question to analyze]
---

<objective>
Analyze $ARGUMENTS using structured problem-solving frameworks. This command:
1. Examines the problem to identify its nature
2. Asks user to confirm which aspects to focus on
3. Selects and applies the optimal mental model(s)
4. Synthesizes actionable insights

Reference: @skills/consider/SKILL.md for selection matrix and model overview.
</objective>

<phase_1_problem_analysis>
## Step 1: Understand the Problem

Read the problem statement: $ARGUMENTS

Perform initial classification by examining:

**Problem Signals** (detect from language):
- "why" / "cause" / "root" → DIAGNOSIS
- "should I" / "decide" / "choose" → DECISION
- "overwhelmed" / "too many" / "prioritize" → PRIORITIZATION
- "stuck" / "nothing works" / "assume" → INNOVATION
- "fail" / "risk" / "wrong" → RISK
- "focus" / "leverage" / "most important" → FOCUS
- "simplify" / "remove" / "eliminate" → OPTIMIZATION
- "strategy" / "position" / "compete" → STRATEGY
- "consequences" / "then what" / "long-term" → CONSEQUENCES
- "tradeoff" / "cost" / "give up" → TRADEOFF

**Output your initial read:**
```
**Problem Statement:** [restate concisely]

**Initial Classification:**
- Primary Type: [type from above]
- Temporal Focus: [PAST | PRESENT | FUTURE]
- Complexity: [SIMPLE | COMPLICATED | COMPLEX]
- Emotional Loading: [HIGH | LOW]

**Key Signals Detected:** [list phrases that triggered classification]
```
</phase_1_problem_analysis>

<phase_2_user_confirmation>
## Step 2: Confirm Focus with User

Use AskUserQuestion with these questions based on detected type:

**Question 1: Problem Type Confirmation**
Confirm or correct the detected problem type. Offer 2-3 alternatives.

**Question 2: Aspect Focus** (multiSelect: true)
Present relevant aspects based on problem type:

| Type | Aspects to Offer |
|------|------------------|
| DIAGNOSIS | Root cause depth, Assumption verification, Simplest explanation |
| DECISION | Time horizon impact, Tradeoff clarity, Failure prevention |
| PRIORITIZATION | Urgency/importance, Impact ranking, Single leverage point |
| INNOVATION | Assumption challenge, Inversion thinking, Subtraction approach |
| RISK | Failure modes, Consequence chains, Defensive strategy |
| FOCUS | Highest leverage, Vital few, What to eliminate |
| OPTIMIZATION | What to remove, Efficiency gains, Simplification |
| STRATEGY | Position assessment, Competitive dynamics, Long-term consequences |

**Question 3: Depth**
- Quick (1 model): Fast insight using best-fit approach
- Thorough (2-3 models): Multiple perspectives for validation
</phase_2_user_confirmation>

<phase_3_approach_selection>
## Step 3: Select Approach(es)

Based on confirmed type and focus, use the selection matrix in SKILL.md.

**Announce selection:**
```
**Selected Approach(es):**
- Primary: [MODEL NAME] - [one-line why it fits]
- Supporting: [MODEL NAME or "None - quick analysis requested"]
```
</phase_3_approach_selection>

<phase_4_execute_models>
## Step 4: Execute Selected Model(s)

Read the full template from the appropriate reference file:
- @skills/consider/references/5-whys.md
- @skills/consider/references/10-10-10.md
- @skills/consider/references/eisenhower.md
- @skills/consider/references/first-principles.md
- @skills/consider/references/inversion.md
- @skills/consider/references/occams-razor.md
- @skills/consider/references/one-thing.md
- @skills/consider/references/opportunity-cost.md
- @skills/consider/references/pareto.md
- @skills/consider/references/second-order.md
- @skills/consider/references/swot.md
- @skills/consider/references/via-negativa.md

Apply the model with full rigor using the template from the reference file.
Do NOT abbreviate - use the complete framework.
</phase_4_execute_models>

<phase_5_synthesis>
## Step 5: Synthesize Insights

After executing model(s), provide synthesis:

```
## Synthesis

**Key Insight:** [Single most important finding from the analysis]

**Recommended Action:** [Specific, concrete next step]

**Confidence Level:** [HIGH | MEDIUM | LOW]
- Reasoning: [Why this confidence level]

**What This Analysis Reveals:**
- [Bullet 1]
- [Bullet 2]

**What This Analysis Doesn't Cover:**
- [Limitation - when to use different approach]

**If You Want to Go Deeper:**
- Consider also applying: [Other relevant model] for [what it would add]
```
</phase_5_synthesis>

<process>
1. **Analyze Problem** (Phase 1): Read $ARGUMENTS, classify problem type and signals
2. **Confirm with User** (Phase 2): Use AskUserQuestion to verify classification and get focus preferences
3. **Select Approach** (Phase 3): Map confirmed type + focus to optimal model(s) using SKILL.md matrix
4. **Execute Models** (Phase 4): Read reference file, apply model with full rigor
5. **Synthesize** (Phase 5): Distill key insight, recommended action, and confidence
</process>

<success_criteria>
- Problem clearly restated and classified
- User confirms problem type and focus areas BEFORE analysis proceeds
- Selected model(s) match confirmed problem type and focus
- Reference file read for each selected model
- Each model executed with complete framework (no abbreviated analysis)
- Synthesis provides single actionable insight
- Confidence level stated with reasoning
- Limitations acknowledged
</success_criteria>
