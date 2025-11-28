# Plan Plugin

TDD execution prompt generator with cost-efficient model delegation for Claude Code.

## Overview

The Plan plugin analyzes design documents and generates **Execution Prompts** that autonomously implement systems using Test-Driven Development (TDD). It enforces five mandatory principles to ensure high-quality, cost-efficient implementation:

1. **TDD Red-Green-Refactor** - Every behavior tested first
2. **LLM-Optimized Documentation** - AI consumption first, human readability second
3. **Cost-Efficient Model Delegation** - Appropriate model selection (haiku/sonnet/opus)
4. **Dependency Validation** - All assumptions verified before and during execution
5. **Cross-Check & Reporting** - Comprehensive final validation and structured reporting

## Installation

```bash
# Add the lucid-toolkit marketplace
/plugin marketplace add rayk/lucid-toolkit

# Install the plan plugin
/plugin install plan@lucid-toolkit
```

## Requirements

- Claude Code CLI >= 1.0.0
- Python >= 3.11
- Git

## Commands

### /planner:analyze

Analyze design documents without generating an execution prompt. Useful for understanding requirements, identifying missing prerequisites, and estimating cost before execution.

```bash
/planner:analyze <design-doc-path>
```

**Output**: Detailed analysis report including:
- System identity (name, language, framework)
- Dependency analysis (external libraries, internal modules)
- Validation results (pre-existing deps, circular dependencies)
- Execution estimates (tokens, duration, model distribution, cost)
- Exit criteria (explicit and implicit)

**Example**:
```bash
/planner:analyze ./docs/design/auth-service.md
```

### /planner:generate

Generate a complete execution prompt from design documents. Validates all prerequisites and creates phased implementation instructions with tracking schemas.

```bash
/planner:generate <design-doc-path> [options]
```

**Options**:
- `--output <path>` - Output directory (default: current directory)
- `--language <lang>` - Target language (python, typescript, go, rust, java, ruby)
- `--dry-run` - Analyze only, don't generate prompt

**Output**:
- `execution-prompt.md` - Complete execution prompt with phased instructions
- `analysis-report.md` - Dependency and validation analysis

**Example**:
```bash
/planner:generate ./docs/design/auth-service.md --language python
```

### /planner:validate

Validate an execution prompt or checkpoint file to ensure correctness and completeness.

```bash
/planner:validate <path> [options]
```

**Options**:
- `--checkpoint` - Validate a checkpoint.json file for resume capability
- `--prompt` - Validate an execution prompt (default)
- `--strict` - Fail on warnings as well as errors

**Validates**:
- Checkpoint: File existence, test status, schema validity, phase consistency
- Prompt: Principle coverage, phase completeness, dependency declarations, model assignments

**Example**:
```bash
/planner:validate ./output/checkpoint.json --checkpoint
/planner:validate ./execution-prompt.md --strict
```

## Skills

### execution-prompt-generator

The core skill that orchestrates execution prompt generation:

- Extracts system identity, dependencies, and patterns from design docs
- Validates prerequisites and detects circular dependencies
- Estimates token usage, duration, and cost per phase
- Generates phased execution prompts with tracking schemas
- Enforces all five mandatory principles

**Activates when**:
- Generating execution prompts from design documents
- Planning autonomous TDD implementation
- Creating phased implementation plans with cost tracking

## Execution Phases

Generated execution prompts follow a 9-phase structure:

| Phase | Model | Purpose |
|-------|-------|---------|
| 0: Setup | - | Validation, git safety, tracking initialization |
| 1: Scaffolding | haiku | Directory structure, stubs |
| 2: Foundation | sonnet | Types, errors, config (TDD) |
| 3: Core | sonnet | Main service class (TDD) |
| 4: Features | sonnet | Feature modules (parallel TDD) |
| 5: Integration | sonnet | Exports, cross-module verification |
| 6: Verification | - | Type checker, full test suite |
| 7: Debug | opus | Deep analysis (if needed) |
| 8: Cross-Check | sonnet+opus | 8 parallel checks, reporting |

## Model Cost Guidance

| Model | Input (per 1M) | Output (per 1M) | Use For |
|-------|----------------|-----------------|---------|
| Haiku | $0.25 | $1.25 | Mechanical, templated tasks |
| Sonnet | $3.00 | $15.00 | Standard implementation |
| Opus | $15.00 | $75.00 | Complex reasoning, debugging |

## Tracking and Output

Generated execution prompts create structured tracking files:

| File | Purpose | Schema |
|------|---------|--------|
| `status.json` | Phase progress tracking | - |
| `checkpoint.json` | Resume capability | checkpoint_schema.json |
| `audit_trail.json` | Token usage and cost tracking | audit_trail_schema.json |
| `execution_result.json` | Final structured results | execution_result_schema.json |
| `implementation_report.md` | Human-readable report | - |

## Cross-Check Protocol

Phase 8 executes parallel validation checks:

1. **Lint** - All errors/warnings fixed
2. **Coverage** - 80% minimum line coverage
3. **Style** - Naming and organization compliance
4. **Architecture** - Required patterns used correctly
5. **Requirements** - Functional and non-functional requirements verified
6. **Acceptance** - Acceptance criteria met (if defined)
7. **Documentation** - All public symbols documented
8. **Custom** - Custom exit criteria from design docs

## Supported Languages

- **Python** - pytest, ruff, mypy
- **TypeScript** - jest/vitest, eslint, tsc
- **Go** - testing, golangci-lint, go vet
- **Rust** - cargo test, clippy
- **Java** - JUnit 5, checkstyle
- **Ruby** - rspec, rubocop

## Resume Capability

Executions can be resumed from checkpoints after interruption:

1. Phase completion writes `checkpoint.json`
2. On restart, validates checkpoint artifacts exist
3. Skips to `next_phase` if valid
4. Continues execution from last checkpoint

## Error Handling

Common validation errors and resolutions:

| Error | Meaning | Resolution |
|-------|---------|------------|
| DEPENDENCY_UNCLEAR | Cannot determine if dependency is pre-existing or created | Clarify timing in design documents |
| PREREQ_MISSING | Pre-existing dependency not found | Implement missing dependency first |
| CIRCULAR_DEPENDENCY | Circular dependency detected | Refactor design to break cycle |
| MISSING_LANGUAGE | No language specified | Add --language option |

## Usage Workflow

1. **Analyze** - Review design completeness and estimate cost
   ```bash
   /planner:analyze ./docs/design/service.md
   ```

2. **Generate** - Create execution prompt
   ```bash
   /planner:generate ./docs/design/service.md --language python
   ```

3. **Validate** - Verify prompt correctness
   ```bash
   /planner:validate ./execution-prompt.md --strict
   ```

4. **Execute** - Run the generated prompt in Claude Code (copy/paste or via automation)

5. **Resume** - If interrupted, validate checkpoint and continue
   ```bash
   /planner:validate ./output/checkpoint.json --checkpoint
   ```
