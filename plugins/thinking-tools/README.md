# Thinking Tools Plugin

Structured problem-solving and analysis capabilities for the Claude Code workspace.

## Overview

The Thinking Tools plugin provides mental models and decision frameworks for analyzing problems, making decisions, and solving complex challenges systematically. It includes three command interfaces and twelve reference frameworks for different problem types.

## Commands

### `/think:consider [problem statement]`
Analyzes problems, decisions, and questions using proven mental frameworks. The system:
1. Classifies problems by type and characteristics
2. Assesses information requirements
3. Gathers context efficiently
4. Selects and executes optimal mental model(s)
5. Synthesizes actionable insights

**Best for**: Open-ended analysis, decision-making, problem diagnosis

### `/think:assess [solution or problem description]`
Four-phase rigorous assessment protocol for evaluating solutions and problems:
- Gap analysis
- Framework selection
- Stress testing
- Verdict generation

**Best for**: Validating proposed solutions, stress testing ideas, risk assessment

### `/reflect [optional: specific issue to reflect on]`
Structured reflection on recent behavior, decisions, and code changes. Helps identify patterns and opportunities for improvement.

**Best for**: Post-action analysis, protocol review, learning from mistakes

## Mental Models Available

### Root Cause & Diagnosis
- **5-Whys** (`references/5-whys.md`) - Iterative root cause drilling
  - Core question: "Why did this happen?" (iterate 5x)
  - Best for: Understanding failure sources

- **First Principles** (`references/first-principles.md`) - Assumption challenging
  - Core question: "What is fundamentally true?"
  - Best for: Breaking through conventional thinking

- **Occam's Razor** (`references/occams-razor.md`) - Simplest explanation principle
  - Core question: "Which requires fewest assumptions?"
  - Best for: Competing hypothesis evaluation

### Decision Making
- **10-10-10** (`references/10-10-10.md`) - Time horizon analysis
  - Core question: "How will I feel in 10 minutes / 10 months / 10 years?"
  - Best for: Decisions with emotional bias

- **Opportunity Cost** (`references/opportunity-cost.md`) - Tradeoff analysis
  - Core question: "What am I giving up?"
  - Best for: Resource allocation decisions

- **Second-Order** (`references/second-order.md`) - Consequence chains
  - Core question: "And then what happens?"
  - Best for: Predicting ripple effects

### Prioritization & Focus
- **Eisenhower** (`references/eisenhower.md`) - Urgency/importance matrix
  - Core question: "Is this urgent AND important?"
  - Best for: Task and project prioritization

- **Pareto** (`references/pareto.md`) - 80/20 principle
  - Core question: "Which 20% drives 80% of results?"
  - Best for: Impact-based resource allocation

- **One Thing** (`references/one-thing.md`) - Leverage identification
  - Core question: "What makes everything else easier?"
  - Best for: Finding high-impact leverage points

### Risk & Innovation
- **Inversion** (`references/inversion.md`) - Failure mode analysis
  - Core question: "What would guarantee failure?"
  - Best for: Risk prevention and innovation breakthroughs

- **Via Negativa** (`references/via-negativa.md`) - Improvement by subtraction
  - Core question: "What should I remove?"
  - Best for: Simplification and optimization

### Strategic Analysis
- **SWOT** (`references/swot.md`) - Strengths/Weaknesses/Opportunities/Threats
  - Core question: "What is our competitive position?"
  - Best for: Strategic planning and positioning

## Problem Classification

The consider skill classifies problems by:

**Problem Type**: Diagnosis, Decision, Prioritization, Innovation, Risk, Focus, Optimization, Strategy

**Temporal Focus**: Past, Present, Future

**Complexity**: Simple, Complicated, Complex

**Information State**: Overload, Sparse, Conflicting

## Model Selection

The plugin includes an intelligent selection matrix that recommends models based on:
- Problem type (diagnosis, decision, etc.)
- Focus area (root cause, tradeoffs, leverage, etc.)
- Supporting models for triangulation

For example:
- **DIAGNOSIS + Root Cause** → Primary: 5-Whys, Support: First Principles
- **DECISION + Time Horizons** → Primary: 10-10-10, Support: Second-Order
- **PRIORITIZATION + Impact Ranking** → Primary: Pareto, Support: One Thing
- **STRATEGY + Competition** → Primary: SWOT, Support: Inversion

## Information Gathering

The skill intelligently sources information from three types:

1. **Local Sources**: Logs, codebase, project history, documentation
2. **Web Research**: Market data, competitor info, industry benchmarks
3. **User Clarification**: Values, priorities, constraints, success criteria

Each model specifies which sources are needed, and the framework coordinates parallel information gathering to minimize token usage.

## Reference Templates

Each mental model has a complete execution framework in the `references/` directory:

```
references/
├── 5-whys.md              (Root cause iteration template)
├── 10-10-10.md            (Time horizon decision matrix)
├── eisenhower.md          (Urgency/importance quadrants)
├── first-principles.md    (Assumption deconstruction)
├── inversion.md           (Failure mode prevention)
├── occams-razor.md        (Hypothesis evaluation)
├── one-thing.md           (Leverage point identification)
├── opportunity-cost.md    (Tradeoff analysis)
├── pareto.md              (80/20 vital few analysis)
├── second-order.md        (Consequence chain mapping)
├── swot.md                (Strategic position matrix)
└── via-negativa.md        (Subtraction optimization)
```

## Usage Examples

### Problem Diagnosis
```
/think:consider I keep getting authentication failures in production, but they don't appear in staging. Why?
```
Recommended: 5-Whys + First Principles

### Strategic Decision
```
/think:consider Should we migrate our monolith to microservices?
```
Recommended: Opportunity Cost + Second-Order + 10-10-10

### Prioritization Under Load
```
/think:consider We have 15 features requested, limited engineering time. What should we focus on first?
```
Recommended: Pareto + One Thing + Eisenhower

### Innovation Challenge
```
/think:consider Our API response times are stuck at 500ms. Nothing we've tried helps.
```
Recommended: Inversion + First Principles + Via Negativa

## Integration with Workspace

These tools integrate with the larger Claude Code workspace for:
- Outcome analysis and decision-making
- Capability assessment and planning
- Risk identification and mitigation
- Design validation before implementation
- Post-action reflection and learning

## Token Budget Management

The framework optimizes token usage:
- Simple lookups: 1000-2000 tokens
- Moderate analysis: 2000-3000 tokens
- Complex research: 3000-5000 tokens
- Web-heavy research: delegated to subagents

Information gathering is parallelized when possible to minimize latency and token consumption.

## Mental Model Count

**Total Models**: 12
**Categories**: Diagnosis (3), Decision (3), Prioritization (3), Risk/Innovation (2), Strategy (1)

All templates include:
- Step-by-step execution process
- Real-world examples
- Common pitfalls to avoid
- Integration with other models
- Output formats for documentation

## Related Resources

- **Skill Definition**: `skills/consider/SKILL.md`
- **Classification Matrix**: Full selection logic in SKILL.md
- **Information Requirements**: Model-specific data needs and sources
- **Combination Patterns**: Serial chains and parallel triangulation strategies
