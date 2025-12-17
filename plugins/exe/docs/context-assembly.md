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

## Codebase Inputs (existing code)

| Source | Example | Why Needed |
|--------|---------|------------|
| Pattern examples | `lib/domain/entities/user.dart` | How this codebase does things |
| Failure types | `lib/core/failures/` | Existing failure hierarchy |
| Base classes | `lib/domain/repositories/base_repository.dart` | What to extend |

## Validation Rule

A task's inputs are complete when the agent can answer:
- "What am I building?" → from spec section
- "How should I build it?" → from agent docs + patterns
- "What already exists?" → from codebase inputs
- "What did prior tasks produce?" → from dynamic inputs

## Example taskInputs

```toon
taskInputs[5,]{taskId,source,ref}:
  task-auth-001,static,plugins/impl-flutter/agents/flutter-coder.md
  task-auth-001,static,specs/auth-system.toon#components.AuthRepository
  task-auth-001,static,specs/auth-system.toon#contracts
  task-auth-001,static,lib/domain/repositories/base_repository.dart
  task-auth-001,output,task-infra-001.outputs.lib/core/failures/auth_failure.dart
```
