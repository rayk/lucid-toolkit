# Lucid Toolkit

A Claude Code plugin marketplace providing development, analysis, and architecture tools.

## Plugins

| Plugin | Category | Description |
|--------|----------|-------------|
| **[architect](plugins/architect/README.md)** | Architecture | Architecture design and documentation following Lucid Composite Architecture (LCA) principles with hierarchy consistency checking, ADRs, and platform documentation |
| **[analyst](plugins/analyst/README.md)** | Analysis | Analysis, research, and structured thinking tools with 14 mental models, multi-agent problem solving, and rigorous fact-checking |
| **[luc](plugins/luc/README.md)** | Workflow | Core tools with status line, TOON schemas, output rendering, and workspace utilities |
| **[plan](plugins/plan/README.md)** | Development | TDD execution prompt generator with cost-efficient model delegation |
| **[impl-python](plugins/impl-python/README.md)** | Development | Python implementation specialist with 8 specialized agents for code generation, testing, debugging, and API development |
| **[impl-flutter](plugins/impl-flutter/README.md)** | Development | Flutter implementation specialist with 8 specialized agents for mobile development with Riverpod and fpdart |
| **[impl-neo4j](plugins/impl-neo4j/README.md)** | Development | Neo4j graph database specialist with 6 specialized agents for graph modeling, Cypher, and performance tuning |

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
