---
description: Analyze problems using parallel multi-agent mental models with voting
argument-hint: [problem, decision, or question to analyze]
allowed-tools: Task, Read, AskUserQuestion
---

<objective>
Analyze $ARGUMENTS using parallel multi-agent reasoning:
1. Classify problem type with voting (3 parallel classifiers)
2. Select optimal models based on classification
3. Execute models in parallel
4. Synthesize with consensus scoring
5. Validate high-stakes decisions

Reference: @skills/consider/SKILL.md for selection matrix.
</objective>

<phase_1_classification_with_voting>
## Step 1: Parallel Classification (Voting)

Launch 3 classifier agents simultaneously to classify the problem:

```
Task 1 (think-classifier, haiku):
  Classify problem: "$ARGUMENTS"
  @constraints: maxTokens: 800

Task 2 (think-classifier, haiku):
  Classify problem: "$ARGUMENTS"
  @constraints: maxTokens: 800

Task 3 (think-classifier, haiku):
  Classify problem: "$ARGUMENTS"
  @constraints: maxTokens: 800
```

**Voting Rules:**
- 3/3 agree → High confidence, proceed with consensus type
- 2/3 agree → Medium confidence, proceed with majority
- All differ → Ask user to confirm type

**Output:**
```toon
@type: ClassificationConsensus
votes[3]{classifier,primaryType,confidence}:
  1,{type},{confidence}
  2,{type},{confidence}
  3,{type},{confidence}
consensus: {UNANIMOUS|MAJORITY|SPLIT}
finalType: {agreed type}
```
</phase_1_classification_with_voting>

<phase_2_user_confirmation>
## Step 2: Confirm Focus with User

Use AskUserQuestion:

**Question 1: Confirm Classification**
"Based on analysis, this appears to be a {type} problem. Is this correct?"
Options: Confirm, Change to [alternatives]

**Question 2: Focus Area** (if applicable)
Present relevant aspects based on confirmed type.

**Question 3: Depth**
- Quick (1 model): Fast insight
- Thorough (2-3 models): Multiple perspectives
- Deep (3+ with validation): High-stakes decision
</phase_2_user_confirmation>

<phase_3_orchestration>
## Step 3: Model Selection

Launch orchestrator agent:

```
Task (think-orchestrator, sonnet):
  Given classification: {consensus classification}
  User preferences: {focus, depth}
  Select models and execution pattern
  @constraints: maxTokens: 1200
```

Receive OrchestrationPlan with:
- Primary, supporting, adversarial models
- Execution pattern
- Token budgets per model
</phase_3_orchestration>

<phase_4_parallel_model_execution>
## Step 4: Execute Models in Parallel

Based on OrchestrationPlan, launch model agents.

### Template Variable Interpolation

**Extract values from OrchestrationPlan TOON output:**

Given this OrchestrationPlan:
```toon
@type: OrchestrationPlan
pattern: PARALLEL_TRIANGULATION
models[3]{role,name,tier,budget}:
  primary,5-whys,haiku,1000
  supporting,first-principles,haiku,1000
  adversarial,inversion,haiku,800
```

**Interpolate into Task calls:**

```
{primary} → "5-whys"
{supporting} → "first-principles"
{adversarial} → "inversion"
{tier} → "haiku"
{budget} → token value from budget column
```

### Execution Patterns

**For PARALLEL_TRIANGULATION:**

**Example with concrete values:**
```
Task 1 (model-5-whys, haiku):
  Apply 5-whys model to: "Why is our deployment failing intermittently?"
  Context: Production system with microservices architecture
  @constraints: maxTokens: 1000

Task 2 (model-first-principles, haiku):
  Apply first-principles model to: "Why is our deployment failing intermittently?"
  Context: Production system with microservices architecture
  @constraints: maxTokens: 1000

Task 3 (model-inversion, haiku):
  Apply inversion model to: "Why is our deployment failing intermittently?"
  Context: Production system with microservices architecture
  @constraints: maxTokens: 800
```

**Template form:**
```
Task 1 (model-{primary}, {tier}):
  Apply {primary} model to: "$ARGUMENTS"
  Context: {any gathered context}
  @constraints: maxTokens: {budget}

Task 2 (model-{supporting}, {tier}):
  Apply {supporting} model to: "$ARGUMENTS"
  Context: {any gathered context}
  @constraints: maxTokens: {budget}

Task 3 (model-{adversarial}, {tier}):
  Apply {adversarial} model to: "$ARGUMENTS"
  Context: {any gathered context}
  @constraints: maxTokens: {budget}
```

All three execute in parallel (single message with 3 Task calls).

**For SERIAL_CHAIN:**
Execute sequentially, passing output forward.

**For ADVERSARIAL_PAIR:**
Run primary + adversarial in parallel (2 Task calls in single message).
</phase_4_parallel_model_execution>

<phase_5_synthesis>
## Step 5: Synthesize Results

Launch synthesizer agent:

```
Task (think-synthesizer, sonnet):
  Synthesize outputs:
  - Model 1 output: {output}
  - Model 2 output: {output}
  - Model 3 output: {output}
  Apply voting rules for conflicts
  @constraints: maxTokens: 1500
```

Receive SynthesizedInsight with:
- Unified key insight
- Recommended action
- Aggregate confidence
- Minority views
</phase_5_synthesis>

<phase_6_validation>
## Step 6: Validation (For High-Stakes)

**Trigger validation when:**
- User selected "Deep" depth
- emotionalLoading == HIGH
- type == RISK
- confidence < 0.7

```
Task (think-validator, opus):
  Validate synthesis: {synthesis output}
  Check for blind spots, edge cases, counter-evidence
  @constraints: maxTokens: 2000
```

Receive ValidationResult with:
- Challenges to assumptions
- Edge cases
- Robustness score
- Final recommendation
</phase_6_validation>

<phase_7_output>
## Step 7: Present Results

```markdown
## Analysis Complete

**Problem:** {restated problem}
**Classification:** {type} (confidence: {%})
**Models Applied:** {list}

---

### Key Insight
{unified insight from synthesis}

### Recommended Action
{specific next step}

### Confidence: {HIGH|MEDIUM|LOW} ({%})
{reasoning for confidence level}

---

### What This Analysis Reveals
- {bullet 1}
- {bullet 2}

### Minority Views (if any)
- {model}: {different perspective}

### Validation Notes (if validated)
- Robustness: {score}
- Cautions: {any conditionals}

---

### Performance Metrics
- Agents used: {count}
- Parallel batches: {count}
- Total tokens: ~{estimate}
- Model distribution: {haiku}h / {sonnet}s / {opus}o
```
</phase_7_output>

<success_criteria>
- Classification voted with 3 parallel agents
- User confirmed type and depth
- Models executed in parallel where possible
- Synthesis applied voting for conflicts
- Validation triggered for high-stakes
- Output includes performance metrics
</success_criteria>
