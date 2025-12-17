# Lucid Toolkit

A Claude Code plugin marketplace that elevates human-AI collaboration from task execution to strategic partnership.

## Philosophy

Lucid Toolkit plugins exist to create **asymmetric leverage**: Claude's computational capacity amplifies human judgment rather than replacing it.

Every plugin must satisfy this test:

> **Does this behavior help the human operate at a higher level of abstraction while ensuring Claude has sufficient context to understand intent?**

Three modes of elevation, expressed differently across plugins:

| Mode | Human Role | Claude Role | Example |
|------|------------|-------------|---------|
| **Strategic Abstraction** | Defines what and why | Handles how | analyst, architect |
| **Cognitive Offloading** | Reviews and approves | Executes mechanical work | exe, impl-* |
| **Decision Elevation** | Makes choices | Provides options with trade-offs | architect ADRs, analyst voting |

### Inclusion Test

A behavior belongs in a plugin if it:
- Pushes decisions upward (human decides, Claude executes)
- Makes implicit context explicit (Claude can reason about intent)
- Provides clear boundaries (human knows what to expect)
- Enables recovery (human can redirect, not just accept)

### Exclusion Test

A behavior should be excluded if it:
- Requires human intervention at mechanical steps (breaks flow)
- Hides reasoning from the human (black box)
- Makes assumptions Claude cannot verify (guess-prone)
- Locks the human into a path without exit (no redirection)

---

## Plugins

### architect
**Purpose**: Elevate structural decisions from code to documented constraints.

**Behavior Test**: Include if it helps the human express architectural intent that Claude can enforce at code level. Exclude if it requires the human to specify implementation details that could be derived from higher-level constraints.

| Plugin | Category | Description |
|--------|----------|-------------|
| **[architect](plugins/architect/README.md)** | Architecture | Enforces structural hierarchy where human defines principles (Platform level) and Claude ensures code-level compliance. LCA patterns, ADRs with explicit trade-offs, consistency checking that prevents lower levels from overriding higher levels. |

---

### analyst
**Purpose**: Externalize human reasoning into structured frameworks Claude can operate.

**Behavior Test**: Include if it applies a proven mental model to clarify thinking. Exclude if it produces analysis without surfacing the reasoning for human review.

| Plugin | Category | Description |
|--------|----------|-------------|
| **[analyst](plugins/analyst/README.md)** | Analysis | 14 mental models that make reasoning explicit. Voting-based classification (3 classifiers, consensus required) ensures Claude's interpretation matches human intent. Human sees the framework, not just conclusions. |

---

### luc
**Purpose**: Make session context visible so human and Claude share the same operational picture.

**Behavior Test**: Include if it surfaces information that aligns understanding. Exclude if it automates decisions the human should make about their working context.

| Plugin | Category | Description |
|--------|----------|-------------|
| **[luc](plugins/luc/README.md)** | Workflow | Status line shows token usage, git state, and focus area. Idempotent setup detects existing state. Human sees what Claude sees—no hidden context. |

---

### exe
**Purpose**: Transform tech specs into validated execution plans with iterative refinement.

**Behavior Test**: Include if it enables Claude to autonomously generate and validate execution plans. Exclude if validation is superficial or iteration doesn't converge on high-confidence plans.

| Plugin | Category | Description |
|--------|----------|-------------|
| **[exe](plugins/exe/README.md)** | Workflow | Execution planning with iterative refinement. Generates validated execution plans from tech specs, stress-tests them with 6 validation scripts, and iterates until 95% confidence. |

---

### impl-python
**Purpose**: Decompose Python implementation into specialized domains with explicit handoffs.

**Behavior Test**: Include if it enables Claude to handle a specific Python concern end-to-end. Exclude if domains overlap (causes confusion) or handoff boundaries are unclear.

| Plugin | Category | Description |
|--------|----------|-------------|
| **[impl-python](plugins/impl-python/README.md)** | Development | 8 agents with non-overlapping domains (coder, tester, debugger, env, data, platform, release, api). Each knows when to hand off. Human directs which concern; Claude handles execution within boundaries. |

---

### impl-flutter
**Purpose**: Decompose Flutter implementation into specialized domains with explicit handoffs.

**Behavior Test**: Include if it enables Claude to handle a specific Flutter concern end-to-end. Exclude if domains overlap or handoff boundaries are unclear.

| Plugin | Category | Description |
|--------|----------|-------------|
| **[impl-flutter](plugins/impl-flutter/README.md)** | Development | 8 agents mirroring Python structure (coder, tester, debugger, env, release, data, ux, platform). Functional patterns (fpdart), state management (Riverpod). Human specifies concern; agent handles scope. |

---

### impl-neo4j
**Purpose**: Decompose graph development into specialized domains with explicit handoffs.

**Behavior Test**: Include if it enables Claude to handle a specific Neo4j concern end-to-end. Exclude if domains overlap or handoff boundaries are unclear.

| Plugin | Category | Description |
|--------|----------|-------------|
| **[impl-neo4j](plugins/impl-neo4j/README.md)** | Development | 6 agents for graph-specific domains (modeler, query, data, perf, driver, env). Schema design separate from query writing. Human defines what to model; Claude handles graph-specific how. |

---

## Quick Start

### Install from Marketplace

```bash
# Add the Lucid Toolkit marketplace
/plugin marketplace add rayk/lucid-toolkit

# Install plugins interactively
/plugin

# Or install specific plugins
/plugin install architect@lucid-toolkit
/plugin install analyst@lucid-toolkit
/plugin install luc@lucid-toolkit
```

### Install Shared Library (Required for Hooks)

```bash
cd shared/cli-commons && pip install -e .
```

## Key Features

### Architecture (architect plugin)

- **Lucid Composite Architecture (LCA)** - Structural hierarchy with Atoms, Composites, Conduits, Deployable Units
- **Three-tier abstraction** - Platform → Repository → Component documentation hierarchy
- **Consistency checking** - Lower levels can extend but never override higher levels
- **ADR management** - Architecture Decision Records with lifecycle tracking
- **Platform templates** - Complete documentation structure for platform-level architecture

### Analysis (analyst plugin)

- **14 mental models** - 5-Whys, First Principles, SWOT, Eisenhower, Pareto, and more
- **Multi-agent problem solving** - Parallel analysis with voting and synthesis
- **Research integration** - Rigorous fact-checking with source attribution

### Implementation Specialists

- **Python** - FastAPI, Pydantic, SQLAlchemy patterns with TDD
- **Flutter** - Riverpod, fpdart, mobile-specific patterns
- **Neo4j** - Graph modeling, Cypher optimization, APOC/GDS integration

## CLAUDE.md Template

For optimal plugin behavior, copy the template to your project:

```bash
# From your project root
curl -O https://raw.githubusercontent.com/rayk/lucid-toolkit/main/templates/CLAUDE.md.template
mv CLAUDE.md.template CLAUDE.md
```

The template includes:
- **Context preservation** - Delegation patterns that prevent context exhaustion
- **Plugin triggers** - Pattern recognition table that enables automatic plugin invocation
- **Compaction strategy** - Proactive context management at 70-75%
- **Parallel execution** - Multi-agent coordination patterns

Customize the "Project-Specific" section and remove plugins you haven't installed.

---

## Plugin Structure

```
plugins/{name}/
├── plugin.json          # Plugin manifest
├── commands/            # Slash commands (*.md)
├── skills/              # Skills (SKILL.md + references/)
├── agents/              # Specialized subagents (*.md)
├── schemas/             # TOON schemas (*.toon)
└── templates/           # File templates
```

## Requirements

- Claude Code CLI (latest)
- Python 3.11+ (for hooks)
- Git

## License

MIT License - See LICENSE file for details

## Author

rayk - https://github.com/rayk
