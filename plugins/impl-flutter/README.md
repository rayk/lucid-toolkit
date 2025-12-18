# Flutter Implementation Plugin

A specialized implementation plugin for Flutter/Dart development with 8 domain-specific agents optimized for Claude Code CLI (Opus 4.5).

## Installation

```bash
/plugin install impl-flutter@lucid-toolkit
```

## Philosophy

This plugin provides **deep Flutter expertise** through specialized agents that don't overlap. Each agent owns a specific domain and knows when to hand off to another specialist.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Flutter Implementation                        │
├─────────────┬─────────────┬─────────────┬─────────────────────────┤
│   CREATE    │    TEST     │   DEBUG     │        DEPLOY          │
├─────────────┼─────────────┼─────────────┼─────────────────────────┤
│ flutter-    │ flutter-    │ flutter-    │ flutter-env            │
│ coder       │ tester      │ debugger    │ flutter-release        │
├─────────────┼─────────────┼─────────────┼─────────────────────────┤
│        SPECIALIZE         │         INTEGRATE                    │
├─────────────┬─────────────┼─────────────┬─────────────────────────┤
│ flutter-    │ flutter-    │ flutter-    │                        │
│ data        │ ux-widget   │ platform    │                        │
└─────────────┴─────────────┴─────────────┴─────────────────────────┘
```

## Agents

### Core Development

| Agent | Domain | When to Use |
|-------|--------|-------------|
| **flutter-coder** | Code generation | NEW features with fpdart, Riverpod 3.0, Clean Architecture, inline TDD |
| **flutter-tester** | Testing (PRIMARY) | Integration tests, e2e tests, golden tests, test infrastructure, coverage |
| **flutter-debugger** | Runtime debugging | App IS RUNNING—runtime errors, layout issues, hot reload failures |

### Infrastructure

| Agent | Domain | When to Use |
|-------|--------|-------------|
| **flutter-env** | Environment repair | Builds FAIL, tools MISSING, CI BROKEN, signing FAILS |
| **flutter-release** | Distribution | App store setup, pub.dev publishing, Crashlytics, analytics |

### Specializations

| Agent | Domain | When to Use |
|-------|--------|-------------|
| **flutter-data** | Data persistence | Isar, Firebase, offline-first, sync strategies, secure storage |
| **flutter-ux-widget** | Visual widgets | Layout, animations, theming (Material 3), accessibility, responsive design, assets |
| **flutter-platform** | Native integration | Platform channels, Pigeon, FFI, web interop, desktop features |

## Agent Selection Guide

### "I need to..."

| Task | Agent |
|------|-------|
| Implement a new feature with TDD | `flutter-coder` |
| Write integration or e2e tests | `flutter-tester` |
| Add tests to existing code | `flutter-tester` |
| Debug a runtime crash | `flutter-debugger` |
| Fix a build failure | `flutter-env` |
| Fix CI pipeline | `flutter-env` |
| Configure app store release | `flutter-release` |
| Set up Crashlytics | `flutter-release` |
| Implement offline sync | `flutter-data` |
| Set up Isar database | `flutter-data` |
| Add animations | `flutter-ux-widget` |
| Implement dark mode | `flutter-ux-widget` |
| Fix layout overflow | `flutter-ux-widget` |
| Write a platform channel | `flutter-platform` |
| Add FFI bindings | `flutter-platform` |

## Key Design Decisions

### 1. flutter-tester is the Testing Authority

`flutter-coder` includes inline TDD for new feature development, but `flutter-tester` owns ALL other testing:

- Integration tests
- E2E tests (Patrol)
- Golden tests
- Test infrastructure (mocks, fixtures, helpers)
- Coverage optimization
- Debugging failing tests

### 2. flutter-env vs flutter-release

| Scenario | Agent |
|----------|-------|
| Build fails with Gradle error | `flutter-env` (FIX) |
| CI pipeline is broken | `flutter-env` (FIX) |
| Need to configure Play Store release | `flutter-release` (CONFIGURE) |
| Setting up Fastlane | `flutter-release` (CONFIGURE) |

**Rule**: `flutter-env` FIXES broken things. `flutter-release` CONFIGURES new things.

### 3. Handoff Protocol

Each agent includes a `<handoffs>` section that explicitly lists when to defer to another specialist. This prevents overlap and ensures the right expert handles each task.

## Technology Stack

All agents are optimized for:

- **Dart 3.x** with records, patterns, sealed classes
- **Flutter 3.24+** with Material 3
- **fpdart** for functional programming (Either, TaskEither, Option)
- **Riverpod 3.0** with code generation (@riverpod)
- **Freezed** for immutable state
- **GoRouter** for navigation
- **Isar** for local persistence
- **Firebase** (Firestore, RTDB, Crashlytics, Analytics)

## Skills

### `dart-flutter-mcp`

Expert guidance for using Dart and Flutter MCP server tools.

**Invoke when working with:**
- `dart_analyzer`, `dart_run_tests`, `dart_format`, `dart_fix`
- `dart_resolve_symbol`, `pub_dev_search`
- `get_runtime_errors`, `get_widget_tree`, `hot_reload`, `hot_restart`
- IDE MCP tools (`mcp__ide__*`)

**Covers:**
- TDD workflow with MCP tools
- Runtime debugging protocol
- Code quality workflows
- Tool order and best practices

## Commands

### `/impl-flutter:planner`

Generate high-confidence autonomous implementation prompts for Flutter projects.

```bash
/impl-flutter:planner <spec-path> [--dry-run] [--target-confidence <percent>]
```

See command documentation for details on confidence scoring and validation.

## Prompt Optimization

All agents are optimized for Claude Code CLI with Opus 4.5:

- **`<assume_base_knowledge>`** - Reduces token usage by not explaining fundamentals
- **`<handoffs>`** - Clear boundaries prevent overlap confusion
- **`<constraints>`** - Hard rules the model won't violate
- **`<output_format>`** - Consistent, parseable output structure
- **MCP tool integration** - `mcp__dart__*` and `mcp__ide__*` for IDE/Dart operations

## Example Workflow

```
User: "Add offline support for user profiles"

1. flutter-data → Implements Isar schema, sync queue, offline-first repository
2. flutter-coder → Generates Riverpod providers with fpdart error handling
3. flutter-tester → Writes integration tests for offline scenarios
4. flutter-ux-widget → Adds connectivity indicator UI
```

Each agent hands off to the next when it reaches the boundary of its domain.
