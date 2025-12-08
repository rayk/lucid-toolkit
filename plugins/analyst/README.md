# Analyst Plugin

Analysis, research, and structured thinking tools for Claude Code.

## Overview

The Analyst plugin provides two complementary capabilities:

1. **Research & Fact-Checking**: Rigorous investigation using authoritative sources via Firecrawl MCP
2. **Structured Thinking**: 14 mental models for problem-solving, decisions, and analysis

## Installation

```bash
/plugin install analyst@lucid-toolkit
```

## Commands

### Thinking Commands

#### `/think:consider [problem statement]`
Analyzes problems using proven mental frameworks:
1. Classifies problem type and characteristics
2. Confirms focus areas with user
3. Selects optimal mental model(s)
4. Executes with full rigor
5. Synthesizes actionable insights

**Use for**: Problem diagnosis, decision-making, prioritization, strategic analysis

#### `/think:assess [solution or problem description]`
Four-phase assessment protocol:
- **Gap Analysis**: Missing information and assumptions
- **Framework Selection**: CAP Theorem, STRIDE, SOLID, etc.
- **Stress Testing**: Edge cases, failure modes, second-order effects
- **Verdict**: Confidence score and recommendations

**Use for**: Solution validation, risk assessment, design review

#### `/think:reflect [optional: specific issue]`
Structured reflection on recent behavior. Analyzes protocol violations, identifies root causes, designs solutions.

**Use for**: Post-action analysis, learning from mistakes

#### `/think:debate [decision or proposal]`
Multi-agent adversarial deliberation for complex decisions.

**Use for**: Decisions requiring multiple perspectives

#### `/think:swarm [symptom or problem]`
Parallel hypothesis testing for diagnosis problems.

**Use for**: Debugging, root cause analysis with multiple possibilities

## Agents

### Research Agent
- **research**: Senior Research Analyst using Firecrawl MCP for fact-checking with authoritative source evaluation

### Mental Model Agents (14)
- **model-5-whys**: Iterative root cause drilling
- **model-10-10-10**: Time horizon analysis (10 min/months/years)
- **model-eisenhower**: Urgency × importance matrix
- **model-first-principles**: Break down to fundamentals and rebuild
- **model-inversion**: "What would guarantee failure?"
- **model-occams-razor**: Simplest explanation with fewest assumptions
- **model-one-thing**: Highest leverage action
- **model-opportunity-cost**: What you give up by choosing
- **model-pareto**: 80/20 - vital few vs trivial many
- **model-second-order**: Consequence chains ("And then what?")
- **model-six-hats**: Parallel perspectives (facts, feelings, risks, benefits)
- **model-swot**: Strengths, weaknesses, opportunities, threats
- **model-toc**: Theory of Constraints (CRT → EC → FRT)
- **model-via-negativa**: Improve by removing, not adding

### Orchestrator Agents (5)
- **think-classifier**: Problem type classification
- **think-clr-validator**: Categories of Legitimate Reservation validation
- **think-orchestrator**: Model selection and coordination
- **think-synthesizer**: Result synthesis with voting
- **think-validator**: Adversarial validation of conclusions

## Skills

### `consider`
Core skill for mental model application:
- Automatic problem classification (9 types)
- Interactive focus area selection
- 24-row model selection matrix
- Multi-source information gathering
- Structured synthesis

## Usage Examples

### Root Cause Analysis
```bash
/think:consider Authentication failures in production but not staging. Why?
```

### Strategic Decision
```bash
/think:consider Should we migrate our monolith to microservices?
```

### Solution Validation
```bash
/think:assess We'll cache all API responses in Redis with 5-minute TTL
```

### Research Task
Use the `research` agent for fact-checking and documentation gathering with rigorous source evaluation.

## Optional MCP Servers

### Memory Server (for persistent insights)
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

### Firecrawl Server (for research)
```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "@anthropic/firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "your-key"
      }
    }
  }
}
```

## Dependencies

- Claude Code >= 1.0.0
- Optional: MCP memory server (cross-session learning)
- Optional: Firecrawl MCP (web research)
