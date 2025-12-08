# Python Implementation Plugin

A Claude Code plugin providing 8 specialized agents for Python development, optimized for modern Python 3.12+ with type hints, functional patterns, and TDD methodology.

## Philosophy

Deep expertise through specialized agents with clear handoffs. Each agent owns a specific domain and knows when to delegate to others.

## Agent Selection Guide

| Need | Agent | When |
|------|-------|------|
| New feature with TDD | `python-coder` | Writing new code with tests |
| Integration/E2E tests | `python-tester` | Comprehensive test suites |
| Runtime errors | `python-debugger` | App running, errors occurring |
| Build/env failures | `python-env` | uv/pip/venv/Docker issues |
| Database/persistence | `python-data` | SQLAlchemy, Redis, migrations |
| Native/FFI code | `python-platform` | C extensions, subprocess |
| PyPI/Docker releases | `python-release` | Publishing, CI/CD, versioning |
| REST/GraphQL APIs | `python-api` | FastAPI, Django, endpoints |

## Key Design Decisions

### 1. python-tester Owns ALL Testing
Except inline TDD (python-coder writes unit tests with features), python-tester owns:
- Integration tests
- E2E tests
- Property-based tests
- Snapshot tests
- Performance tests
- Test infrastructure

### 2. python-env FIXES, python-release CONFIGURES
- **python-env**: Broken builds, dependency conflicts, version issues
- **python-release**: New release configs, CI/CD setup, publishing

### 3. Handoff Protocol
Each agent explicitly declares handoffs to prevent overlap.

## Technology Stack

| Category | Tools |
|----------|-------|
| Package Management | uv, pip, poetry |
| Type Checking | pyright, mypy |
| Linting | ruff, flake8, pylint |
| Formatting | black, ruff format |
| Testing | pytest, hypothesis, pytest-asyncio |
| Web Frameworks | FastAPI, Django, Flask |
| Data | SQLAlchemy, Pydantic, Redis |
| Functional | returns, pyrsistent |
| CLI | typer, click, rich |

## Agent Architecture

```
Python Implementation Plugin
├─ CREATE LAYER
│  └─ python-coder: New features with TDD, type hints, functional patterns
├─ TEST LAYER
│  └─ python-tester: All testing (unit, integration, e2e, property-based)
├─ DEBUG LAYER
│  └─ python-debugger: Runtime issues, profiling, logging
├─ INFRASTRUCTURE LAYER
│  ├─ python-env: Fix builds, dependencies, Docker, CI
│  └─ python-release: PyPI, Docker Hub, versioning, CHANGELOG
└─ SPECIALIZATION LAYERS
   ├─ python-data: Databases, ORMs, migrations, caching
   ├─ python-platform: Native code, FFI, multiprocessing, OS integration
   └─ python-api: REST/GraphQL APIs, authentication, rate limiting
```

## Example Workflow

```
User: "Add user authentication to the FastAPI app"

1. python-coder: Implements auth with inline unit tests (TDD)
2. python-tester: Adds integration tests for auth flows
3. python-api: Configures OAuth2/JWT middleware
4. python-data: Sets up user storage, sessions
5. python-release: Updates version, CHANGELOG
```

## Installation

```bash
/plugin install impl-python@lucid-toolkit
```

## Usage

Agents are automatically available as subagent types in the Task tool:
```
Task(subagent_type="specialize:python-coder", prompt="...")
```
