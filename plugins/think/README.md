# Thinking Tools Plugin

Structured problem-solving and analysis using mental models and decision frameworks.

## Overview

The Thinking Tools plugin provides systematic approaches to analyzing problems, making decisions, and evaluating solutions. It includes 13 proven mental models accessible through 5 commands, with intelligent model selection based on problem type and context.

## Installation

```bash
/plugin install think@lucid-toolkit
```

## Commands

### `/think:consider [problem statement]`
Analyzes problems, decisions, and questions using proven mental frameworks. The command:
1. Classifies the problem by type and characteristics
2. Confirms focus areas with the user
3. Selects optimal mental model(s)
4. Executes the model with full rigor
5. Synthesizes actionable insights

**Use for**: Problem diagnosis, decision-making, prioritization, strategic analysis

### `/think:assess [solution or problem description]`
Rigorous four-phase assessment protocol for evaluating solutions:
- **Gap Analysis**: Identifies missing information and assumptions
- **Framework Selection**: Chooses appropriate evaluation criteria (CAP Theorem, STRIDE, SOLID, etc.)
- **Stress Testing**: Tests edge cases, failure modes, and second-order effects
- **Verdict**: Provides confidence score and specific recommendations

**Use for**: Solution validation, risk assessment, design review

### `/think:reflect [optional: specific issue]`
Structured reflection on recent behavior and decisions. Analyzes protocol violations, identifies root causes, and designs robust solutions.

**Use for**: Post-action analysis, learning from mistakes, improving workflows

## Available Skills

### `consider`
Core skill for applying mental models to problems. Features:
- Automatic problem classification (9 types: diagnosis, decision, prioritization, innovation, risk, focus, optimization, strategy, deliberation)
- Interactive focus area selection
- Intelligent model selection using a 24-row selection matrix
- Efficient information gathering (local/web/user)
- Structured synthesis with actionable insights

See `/think:consider` command for access.

## Mental Models

The plugin includes 13 mental models organized by category:

### Root Cause & Diagnosis
- **5-Whys**: Iterative root cause drilling ("Why did this happen?" × 5)
- **First Principles**: Break down to fundamental truths and rebuild
- **Occam's Razor**: Prefer simplest explanation with fewest assumptions

### Decision Making
- **10-10-10**: Evaluate across time horizons (10 minutes/months/years)
- **Opportunity Cost**: Analyze what you give up by choosing
- **Second-Order**: Map consequence chains ("And then what?")

### Prioritization & Focus
- **Eisenhower Matrix**: Categorize by urgency × importance
- **Pareto (80/20)**: Find the vital 20% driving 80% of results
- **One Thing**: Identify highest leverage action

### Risk & Innovation
- **Inversion**: "What would guarantee failure?" then avoid it
- **Via Negativa**: Improve by removing rather than adding

### Strategic Analysis
- **SWOT**: Map strengths, weaknesses, opportunities, threats

### Deliberation & Group Thinking
- **Six Hats**: Parallel perspectives (facts, feelings, risks, benefits, alternatives, process)

Each model includes a complete execution template in `skills/consider/references/`.

## Usage Examples

### Root Cause Analysis
```bash
/think:consider I keep getting authentication failures in production, but they don't appear in staging. Why?
```
System will likely apply: 5-Whys → First Principles

### Strategic Decision
```bash
/think:consider Should we migrate our monolith to microservices?
```
System will likely apply: Opportunity Cost + Second-Order + 10-10-10

### Prioritization
```bash
/think:consider We have 15 features requested and limited engineering time. What should we focus on first?
```
System will likely apply: Pareto + One Thing + Eisenhower

### Solution Validation
```bash
/think:assess We'll cache all API responses in Redis with 5-minute TTL to improve performance
```
Assessment will analyze: assumptions, edge cases, failure modes, and provide confidence score

### Workflow Reflection
```bash
/think:reflect I completed the task but violated context conservation protocols
```
Reflection will: identify root cause, propose solutions, and implement if approved

## Templates

The plugin includes two template files:

- **`mental-models.md`**: Quick reference guide for all 12 models with selection tips
- **`assessment-framework.md`**: Structured template for situation/decision/risk/strategic assessments

## How It Works

### Model Selection Process
1. User provides problem statement
2. System classifies problem type and characteristics
3. User confirms focus areas (interactive)
4. System selects optimal model(s) from 24-row selection matrix
5. System gathers required information (local files, web research, user input)
6. Model(s) executed with full rigor using reference templates
7. Actionable synthesis delivered with confidence level

### Information Gathering
The skill coordinates information from three sources:
- **Local**: Codebase, logs, documentation (via Read/Task)
- **Web**: Market data, benchmarks, industry trends (via WebSearch)
- **User**: Preferences, constraints, success criteria (via AskUserQuestion)

Gathering is parallelized when possible to minimize token usage.

## Dependencies

- Claude Code >= 1.0.0
- No shared libraries required

## Related Plugins

- **outcome**: Use think commands to analyze and validate outcomes before implementation
- **capability**: Apply strategic analysis (SWOT) to capability planning
- **plan**: Validate execution plans with `/think:assess` before proceeding
