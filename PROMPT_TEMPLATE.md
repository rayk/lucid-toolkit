# Structured Prompt Framework

A theoretically-grounded template for constructing effective system prompts.
Each section serves a distinct function in shaping model behavior.

---

## Template

```xml
<role>
<!--
FUNCTION: Probability Prior / Mental Model Selection
-----------------------------------------------------
Narrows the latent space from which responses are drawn.
Activates domain-specific reasoning patterns, vocabulary, and epistemic stances.

Without role: Model samples from entire capability distribution
With role: Model samples from conditioned subdistribution

Key dimensions to specify:
-->

<!-- WHO: Identity that defines the probability space -->
Primary identity: [persona, function, or archetype]

<!-- HOW: The reasoning framework this role employs -->
Mental model: [how this role thinks about problems]

<!-- WHAT MATTERS: Attention allocation -->
Priority bias: [what to notice, emphasize, or optimize for]
Blindspots: [what this role appropriately ignores]

<!-- CERTAINTY: Epistemic posture -->
Assertion style: [confident/decisive vs. exploratory/hedged]

<!-- BOUNDARIES: What this role does NOT do -->
Anti-patterns: [behaviors outside this role's scope]
</role>


<task>
<!--
FUNCTION: Objective Function / Loss Landscape
----------------------------------------------
Defines what "success" means for this interaction.
The model optimizes its output against this specification.

Poor task definition → model optimizes for wrong objective
Precise task definition → aligned optimization

Think of this as: argmax P(response | role, task) where task defines the scoring function
-->

<!-- PRIMARY: The core objective (one sentence) -->
Objective: [what must be accomplished]

<!-- DECOMPOSITION: Break complex objectives into steps -->
Sub-tasks:
1. [first required action]
2. [second required action]
3. [...]

<!-- SUCCESS CRITERIA: How to evaluate completion -->
Done when: [measurable conditions that indicate success]

<!-- SCOPE BOUNDARIES: Prevent objective drift -->
In scope: [what IS part of this task]
Out of scope: [what is NOT part of this task]

<!-- FAILURE MODES: What to actively avoid -->
Anti-goals: [outcomes that would indicate failure]
</task>


<context>
<!--
FUNCTION: Grounding Constraints / World Model
----------------------------------------------
Provides the factual substrate against which reasoning occurs.
Constrains the solution space to what's actually possible/relevant.

Context does two things:
1. GROUNDS: Connects abstract reasoning to specific reality
2. CONSTRAINS: Eliminates impossible/irrelevant solution paths

Missing context → hallucination risk (model fills gaps with priors)
Excess context → attention dilution (signal lost in noise)

Optimal context: Minimum information needed to fully constrain the problem
-->

<!-- DOMAIN: The subject matter space -->
Domain: [field, technology, industry]

<!-- SITUATION: Current state of affairs -->
Current state: [what exists now, what's true]

<!-- CONSTRAINTS: Hard boundaries on solutions -->
Constraints:
- [technical limitations]
- [resource limitations]
- [policy/rule limitations]

<!-- ASSUMPTIONS: What can be taken as given -->
Assumptions: [facts the model should accept without verification]

<!-- UNKNOWNS: Explicit uncertainty (prevents false confidence) -->
Unknown/uncertain: [what is NOT known, where to hedge]
</context>


<examples>
<!--
FUNCTION: Pattern Anchoring / Few-Shot Conditioning
----------------------------------------------------
Examples are the HIGHEST LEVERAGE section of any prompt.
They provide concrete instances that anchor abstract instructions.

Why examples dominate:
- Humans underspecify in natural language
- Examples resolve ambiguity that instructions cannot
- They demonstrate rather than describe (show > tell)
- They establish calibration for quality/length/style

Information hierarchy: Examples > Task > Role > Context
(Examples override conflicting instructions)

Design principles:
- Cover edge cases, not just happy path
- Show the reasoning process, not just final output
- Include negative examples (what NOT to do) when useful
- 2-3 examples often sufficient; diminishing returns after 5
-->

<!-- POSITIVE EXAMPLES: What good looks like -->
<example type="positive">
<input>[representative user input]</input>
<reasoning>[optional: show the thinking process]</reasoning>
<output>[desired response]</output>
</example>

<example type="positive">
<input>[edge case or complex input]</input>
<reasoning>[how to handle complexity]</reasoning>
<output>[desired response for edge case]</output>
</example>

<!-- NEGATIVE EXAMPLES: What to avoid (optional but powerful) -->
<example type="negative">
<input>[input that might trigger wrong behavior]</input>
<wrong_output>[what NOT to produce]</wrong_output>
<why_wrong>[explanation of the failure mode]</why_wrong>
<correct_output>[what to produce instead]</correct_output>
</example>
</examples>


<output>
<!--
FUNCTION: Format Constraint / Structural Prior
-----------------------------------------------
Specifies the shape of acceptable responses.
Constrains the generation to match expected structure.

This section reduces variance in output format, making responses:
- Predictable (important for programmatic consumption)
- Parseable (if structured data needed)
- Appropriately scoped (length/depth calibration)

Format spec should answer:
- What structure? (prose, list, JSON, XML, markdown)
- What length? (word count, section count)
- What must be present? (required fields)
- What must be absent? (forbidden content)
-->

<!-- STRUCTURE: The shape of the response -->
Format: [prose | markdown | JSON | XML | list | table | ...]

<!-- SCHEMA: Required structure (if applicable) -->
Schema:
```
[template or JSON schema or section headers]
```

<!-- LENGTH: Calibration for response size -->
Length: [approximate word count, or qualitative: brief/detailed/comprehensive]

<!-- REQUIRED: What MUST appear -->
Must include: [required elements, fields, or sections]

<!-- FORBIDDEN: What must NOT appear -->
Must exclude: [prohibited content, patterns, or behaviors]

<!-- STYLE: Tone and presentation -->
Style: [formal/casual, technical/accessible, assertive/hedged]
</output>
```

---

## Section Interaction Model

The sections form a pipeline that progressively constrains generation:

```
┌─────────────────────────────────────────────────────────────┐
│                    Full Model Capability                     │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
                ┌─────────────────────────────┐
                │      <role>                 │
                │  Selects probability prior  │
                │  (which "expert" to be)     │
                └─────────────────────────────┘
                               │
                               ▼
                  ┌───────────────────────┐
                  │       <task>          │
                  │  Defines objective    │
                  │  (what to optimize)   │
                  └───────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     <context>       │
                    │  Grounds to reality │
                    │  (solution space)   │
                    └─────────────────────┘
                               │
                               ▼
                      ┌───────────────────┐
                      │    <examples>     │
                      │  Anchors pattern  │
                      │  (calibration)    │
                      └───────────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │  <output>   │
                        │   Format    │
                        │  (shape)    │
                        └─────────────┘
                               │
                               ▼
                          ┌─────────┐
                          │Response │
                          └─────────┘
```

Each layer narrows the possibility space further.

---

## Section Summary

| Section | Function | Failure Mode if Missing |
|---------|----------|------------------------|
| Role | Probability prior | Generic, unfocused responses |
| Task | Objective function | Optimization drift, scope creep |
| Context | Reality grounding | Hallucination, impossible solutions |
| Examples | Pattern anchoring | Miscalibrated quality/format |
| Output | Structural constraint | Unpredictable, unparseable responses |

---

## Key Principles

### Role as Probability Prior

The `<role>` section functions as a **probability prior** - it conditions the model's output distribution before any specific task is considered.

```
P(response | role, task, context) ≠ P(response | task, context)
```

The role biases toward:
- **Vocabulary** - A "senior architect" uses different terms than a "junior developer"
- **Reasoning patterns** - An "auditor" looks for risks; a "builder" looks for solutions
- **Attention weights** - A "security expert" notices vulnerabilities others skip
- **Epistemic stance** - A "researcher" hedges; an "operator" decides

### Examples as Highest Leverage

Examples provide the strongest signal for model behavior:
- They resolve ambiguity that natural language cannot
- They demonstrate rather than describe
- They establish calibration for quality, length, and style
- 2-3 well-chosen examples often outperform lengthy instructions

### Context as Grounding

Context prevents hallucination by:
- Connecting abstract reasoning to specific reality
- Eliminating impossible solution paths
- Explicitly marking unknowns (preventing false confidence)

Optimal context = minimum information needed to fully constrain the problem.
