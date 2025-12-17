# Agent Registry

Reference documentation for available agents and their capabilities.

## Built-in Claude Code Agents

| Agent | Use For | Token Budget |
|-------|---------|--------------|
| `general-purpose` | Multi-step tasks, exploration, research | ~100k |
| `Explore` | Codebase exploration, finding files/patterns | ~50k |
| `Plan` | Architecture design, implementation planning | ~80k |

## impl-flutter Agents

| Agent | Use For | Token Budget | Notes |
|-------|---------|--------------|-------|
| `impl-flutter:flutter-coder` | Dart/Flutter code generation | ~50k | TDD, max 3 files, has spec validation |
| `impl-flutter:flutter-tester` | Integration/e2e tests | ~40k | |
| `impl-flutter:flutter-ux` | UI/UX design, widgets | ~30k | |
| `impl-flutter:flutter-debugger` | Runtime errors, debugging | ~20k | |
| `impl-flutter:flutter-data` | Data layer, persistence | ~30k | |
| `impl-flutter:flutter-platform` | Platform-specific code | ~25k | |
| `impl-flutter:flutter-env` | Build, dependencies, CI | ~20k | |
| `impl-flutter:flutter-release` | Release preparation | ~15k | |

## impl-python Agents

| Agent | Use For | Token Budget |
|-------|---------|--------------|
| `impl-python:python-coder` | Python code generation | ~50k |
| `impl-python:python-tester` | Integration tests | ~40k |
| `impl-python:python-api` | API endpoint design | ~30k |
| `impl-python:python-data` | Database, persistence | ~30k |
| `impl-python:python-debugger` | Runtime debugging | ~20k |
| `impl-python:python-env` | Build, dependencies | ~20k |
| `impl-python:python-platform` | Platform integration | ~25k |
| `impl-python:python-release` | Release preparation | ~15k |

## impl-neo4j Agents

| Agent | Use For | Token Budget |
|-------|---------|--------------|
| `impl-neo4j:neo4j-modeler` | Graph schema design | ~30k |
| `impl-neo4j:neo4j-query` | Cypher query writing | ~25k |
| `impl-neo4j:neo4j-data` | Data import/export | ~30k |
| `impl-neo4j:neo4j-driver` | Driver integration | ~25k |
| `impl-neo4j:neo4j-perf` | Performance tuning | ~20k |
| `impl-neo4j:neo4j-env` | Deployment, config | ~15k |

## Agent Selection Rules

1. Match task type to agent specialty
2. Prefer specialized agent over general-purpose
3. Check agent's tools vs task requirements
4. Use "Handoffs" section in agent docs to chain agents
5. Fall back to general-purpose if no match
