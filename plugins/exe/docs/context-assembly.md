# Context Assembly

How to build taskInputs - the complete context each agent needs to succeed.

## What taskInputs Must Provide

Each task's `taskInputs` is the **complete context** the agent needs to succeed. If an agent would need to search for something, it should already be in taskInputs.

## Static Inputs (from files)

| Source | Ref Pattern | Why Needed |
|--------|-------------|------------|
| Agent docs | `plugins/{impl}/agents/{agent}.md` | Agent's patterns, constraints, tools |
| Spec section | `{spec-path}#{anchor}` | Requirements for this task |
| Patterns | `{spec-path}#quickReference` | Code patterns to follow |
| Contracts | `{spec-path}#contracts` (filtered) | Acceptance criteria |

## Dynamic Inputs (from prior tasks)

| Source | Ref Pattern | Why Needed |
|--------|-------------|------------|
| Output file | `{task-id}.outputs.{path}` | File created by prior task |
| Return value | `{task-id}.returns.{key}` | Value returned by prior task |

## Architecture Inputs (discovered)

Discovered via `find_files_by_glob` before drafting the plan.

| Source | Discovery Pattern | Why Needed |
|--------|-------------------|------------|
| Architecture overview | `**/architecture/**/*.md`, `**/ARCHITECTURE.md` | System-wide constraints and patterns |
| Component architecture | `**/architecture/{component}/*.md` | Component-specific decisions |
| ADRs | `**/adr/*.md`, `**/decisions/*.md` | Historical decisions affecting implementation |

## Codebase Inputs (discovered)

Discovered via `find_files_by_glob` and `search_in_files_by_text` before drafting.

| Source | Discovery Pattern | Why Needed |
|--------|-------------------|------------|
| Base classes | `search_in_files_by_text("abstract class")` | What to extend |
| Interfaces | `search_in_files_by_text("interface ")` | Contracts to implement |
| Pattern examples | `**/domain/**/*.dart`, `**/core/**/*.dart` | How this codebase does things |
| Utilities | `**/utils/**/*`, `**/helpers/**/*` | Available helper functions |
| Failure types | `**/failures/*`, `**/errors/*` | Existing error hierarchy |

## Validation Rule

A task's inputs are complete when the agent can answer **WITHOUT searching**:
- "What am I building?" → from spec section
- "What architectural constraints apply?" → from architecture inputs
- "What base class/interface do I extend?" → from codebase inputs
- "How do similar components look?" → from pattern examples
- "What utilities are available?" → from discovered helpers
- "How should I build it?" → from agent docs + patterns
- "What did prior tasks produce?" → from dynamic inputs

**If any answer requires the agent to search → add the missing context to taskInputs.**

## Example taskInputs

```toon
taskInputs[8,]{taskId,source,ref}:
  task-auth-001,static,plugins/impl-flutter/agents/flutter-coder.md
  task-auth-001,static,specs/auth-system.toon#components.AuthRepository
  task-auth-001,static,specs/auth-system.toon#contracts
  task-auth-001,static,docs/architecture/auth-architecture.md
  task-auth-001,static,docs/architecture/adr/001-repository-pattern.md
  task-auth-001,static,lib/domain/repositories/base_repository.dart
  task-auth-001,static,lib/domain/repositories/user_repository.dart
  task-auth-001,output,task-infra-001.outputs.lib/core/failures/auth_failure.dart
```

**Note:** Architecture docs and similar implementations (`user_repository.dart`) were discovered during context discovery and included so the agent doesn't need to search.
