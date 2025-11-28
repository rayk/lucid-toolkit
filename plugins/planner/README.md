# Planner Plugin

TDD execution prompt generator with cost-efficient model delegation for Claude Code.

## Overview

The Planner plugin analyzes design documents and generates **Execution Prompts** that autonomously implement systems using Test-Driven Development (TDD). It enforces five mandatory principles:

1. **TDD Red-Green-Refactor** - Every behavior tested first
2. **LLM-Optimized Documentation** - AI consumption first
3. **Cost-Efficient Model Delegation** - haiku/sonnet/opus appropriately
4. **Dependency Validation** - All assumptions verified
5. **Cross-Check & Reporting** - Comprehensive final validation

## Commands

| Command | Description |
|---------|-------------|
| `/planner:generate` | Generate execution prompt from design documents |
| `/planner:analyze` | Analyze design documents without generating |
| `/planner:validate` | Validate execution prompt or checkpoint |

## Skills

### execution-prompt-generator

The core skill that:
- Extracts system identity, dependencies, and patterns from design docs
- Validates prerequisites and detects circular dependencies
- Estimates token usage, duration, and cost
- Generates phased execution prompts with tracking

## Execution Phases

| Phase | Model | Purpose |
|-------|-------|---------|
| 0: Setup | - | Validation, git safety, tracking init |
| 1: Scaffolding | haiku | Directory structure, stubs |
| 2: Foundation | sonnet | Types, errors, config (TDD) |
| 3: Core | sonnet | Main service class (TDD) |
| 4: Features | sonnet | Feature modules (parallel TDD) |
| 5: Integration | sonnet | Exports, cross-module verification |
| 6: Verification | - | Type checker, full test suite |
| 7: Debug | opus | Deep analysis (if needed) |
| 8: Cross-Check | sonnet+opus | 8 parallel checks, reporting |

## Model Cost (November 2025)

| Model | Input (per 1M) | Output (per 1M) | Use For |
|-------|----------------|-----------------|---------|
| Haiku | $0.25 | $1.25 | Mechanical tasks |
| Sonnet | $3.00 | $15.00 | Standard implementation |
| Opus | $15.00 | $75.00 | Complex reasoning |

## Output Files

| File | Purpose |
|------|---------|
| `status.json` | Phase progress tracking |
| `checkpoint.json` | Resume capability |
| `audit_trail.json` | Token usage tracking |
| `execution_result.json` | Final structured results |
| `implementation_report.md` | Human-readable report |

## Cross-Checks

1. **Lint** - All errors/warnings fixed
2. **Coverage** - 80% minimum line coverage
3. **Style** - Naming, organization compliance
4. **Architecture** - Required patterns used
5. **Requirements** - FR/NFR verified
6. **Acceptance** - AC criteria met (if defined)
7. **Documentation** - All public symbols documented
8. **Custom** - Exit criteria from design docs

## Usage Example

```bash
# Analyze design document
/planner:analyze ./docs/design/auth-service.md

# Generate execution prompt
/planner:generate ./docs/design/auth-service.md --language python

# Validate checkpoint for resume
/planner:validate ./output/checkpoint.json --checkpoint
```

## Supported Languages

- Python (pytest, ruff, mypy)
- TypeScript (jest/vitest, eslint, tsc)
- Go (testing, golangci-lint, go vet)
- Rust (cargo test, clippy)
- Java (JUnit 5, checkstyle)
- Ruby (rspec, rubocop)

## Resume Capability

Executions can be resumed from checkpoints:

1. Phase completion writes `checkpoint.json`
2. On restart, validates checkpoint artifacts exist
3. Skips to `next_phase` if valid
4. Continues execution from last checkpoint

## Installation

```bash
# Link plugin
cd ~/.claude/plugins
ln -s lucid-toolkit/plugins/planner .
```

## Requirements

- Claude Code CLI
- Python 3.11+
- Git
