# Agent Color Classification Guide

This document defines the unified color system for all agents in the Lucid Toolkit marketplace. All plugins MUST follow this classification to ensure visual consistency.

## Supported Colors

Claude Code officially supports these colors for agents:

| Color | Hex (approx) | Status |
|-------|--------------|--------|
| `red` | #FF6B6B | Supported |
| `blue` | #4A90D9 | Supported |
| `green` | #7CB342 | Supported |
| `yellow` | #FDD835 | Supported |
| `purple` | #9C27B0 | Supported |
| `orange` | #FF9800 | Supported |
| `cyan` | #00BCD4 | Supported |
| `magenta` | #E91E63 | Supported |

**Note:** `gray` and `teal` have been used but are not officially documented. Prefer the 8 colors above.

## Classification System

### Category → Color Mapping

| Category | Color | Use For | Keywords |
|----------|-------|---------|----------|
| **Code Generation** | `blue` | Agents that write/generate code | coder, writer, generator, impl, driver, query |
| **Testing & Verification** | `green` | Agents that test or verify code | tester, verifier, validator, e2e |
| **Debugging** | `red` | Agents that diagnose/fix problems | debugger, fix, diagnose, troubleshoot |
| **Planning & Analysis** | `purple` | Agents that plan, analyze, orchestrate | plan, analyze, orchestrate, model, think, simulate |
| **Infrastructure & Ops** | `orange` | Agents for env, platform, deployment | env, platform, release, deploy, ops |
| **Data & Persistence** | `cyan` | Agents for data layer, databases | data, persist, store, modeler, perf |
| **Research & Interactive** | `magenta` | Agents for research, sessions, AI-gen | research, session, gen-ui, api, interactive |
| **Architecture & Docs** | `yellow` | Agents for architecture, ADRs | architect, adr, component, consistency, design |
| **Helper & Utility** | (none) | Background support agents | do-*, helper, utility, internal |

### Decision Tree

When assigning a color to a new agent:

```
1. Does it write/generate code?
   → blue (Code Generation)

2. Does it test or verify code?
   → green (Testing & Verification)

3. Does it debug or fix problems?
   → red (Debugging)

4. Does it plan, analyze, or orchestrate?
   → purple (Planning & Analysis)

5. Does it manage env, platform, or releases?
   → orange (Infrastructure & Ops)

6. Does it handle data or databases?
   → cyan (Data & Persistence)

7. Does it research or run interactive sessions?
   → magenta (Research & Interactive)

8. Does it manage architecture or documentation?
   → yellow (Architecture & Docs)

9. Is it a background helper (do-*, utility)?
   → (no color) - omit the color field
```

## Color Assignments by Plugin

### analyst

| Agent | Color | Category |
|-------|-------|----------|
| model-* (14 agents) | purple | Planning & Analysis |
| think-classifier | purple | Planning & Analysis |
| think-orchestrator | purple | Planning & Analysis |
| think-synthesizer | purple | Planning & Analysis |
| think-validator | green | Testing & Verification |
| think-clr-validator | green | Testing & Verification |
| research | magenta | Research & Interactive |

### architect

| Agent | Color | Category |
|-------|-------|----------|
| adr-curator | yellow | Architecture & Docs |
| adr-writer | yellow | Architecture & Docs |
| architecture-reviewer | yellow | Architecture & Docs |
| component-analyzer | yellow | Architecture & Docs |
| consistency-checker | yellow | Architecture & Docs |

### exe

| Agent | Color | Category |
|-------|-------|----------|
| execution-planner | purple | Planning & Analysis |

### impl-flutter

| Agent | Color | Category |
|-------|-------|----------|
| flutter-coder | blue | Code Generation |
| flutter-ux-widget | blue | Code Generation |
| flutter-e2e-tester | green | Testing & Verification |
| flutter-verifier | green | Testing & Verification |
| flutter-debugger | red | Debugging |
| flutter-env | orange | Infrastructure & Ops |
| flutter-platform | orange | Infrastructure & Ops |
| flutter-release | orange | Infrastructure & Ops |
| flutter-data | cyan | Data & Persistence |
| flutter-gen-ui | magenta | Research & Interactive |
| flutter-session-driver | magenta | Research & Interactive |
| flutter-session-recorder | magenta | Research & Interactive |
| plan-* (7 agents) | purple | Planning & Analysis |
| do-* (6 agents) | (none) | Helper & Utility |
| flutter-plan-orchestrator | (none) | Deprecated |

### impl-neo4j

| Agent | Color | Category |
|-------|-------|----------|
| neo4j-query | blue | Code Generation |
| neo4j-driver | blue | Code Generation |
| neo4j-env | orange | Infrastructure & Ops |
| neo4j-data | cyan | Data & Persistence |
| neo4j-modeler | cyan | Data & Persistence |
| neo4j-perf | cyan | Data & Persistence |

### impl-python

| Agent | Color | Category |
|-------|-------|----------|
| python-coder | blue | Code Generation |
| python-tester | green | Testing & Verification |
| python-debugger | red | Debugging |
| python-env | orange | Infrastructure & Ops |
| python-platform | orange | Infrastructure & Ops |
| python-release | orange | Infrastructure & Ops |
| python-data | cyan | Data & Persistence |
| python-api | magenta | Research & Interactive |

### luc

| Agent | Color | Category |
|-------|-------|----------|
| setup-specialist | (none) | Helper & Utility |
| fix-phase | (none) | Helper & Utility |
| output-analyzer | (none) | Helper & Utility |

## Rationale

### Why These Colors?

1. **Blue for Code Generation** - Blue is universally associated with productivity, creativity, and building. It's calm and focused, perfect for the primary creative work of writing code.

2. **Green for Testing** - Green universally means "pass" in testing contexts. All verification and testing agents use green to signal their validation role.

3. **Red for Debugging** - Red signals problems that need attention. Reserved exclusively for debugging agents to maintain its impact.

4. **Purple for Planning** - Purple connotes wisdom, strategy, and foresight. The largest category, covering all mental models, planners, and orchestrators.

5. **Orange for Infrastructure** - Orange signals caution and environment concerns. All environment, platform, and release agents get orange.

6. **Cyan for Data** - Cyan suggests flow and depth. All data layer and persistence agents get cyan.

7. **Magenta for Research/Interactive** - Magenta is unique and stands out. Research, session management, and AI-generated content agents get magenta.

8. **Yellow for Architecture** - Yellow draws attention to important structural decisions. Architecture and documentation agents get yellow.

9. **No Color for Helpers** - Background utility agents (do-*, helpers) don't need visual prominence. Omitting color keeps them invisible in the UI.

## Adding New Agents

When creating a new agent:

1. Determine its primary function using the decision tree above
2. Assign the corresponding color in the frontmatter:

```yaml
---
name: my-new-agent
description: |
  What this agent does
color: blue  # ← Use the classification color
model: sonnet
---
```

3. If the agent doesn't fit any category, ask: "Is this really a new category, or does it fit an existing one?"

4. New categories require updating this document and getting consensus.

## References

- [Claude Code Custom Subagents](https://ccforpms.com/fundamentals/custom-subagents)
- [GitHub: Agent Colors Discussion](https://github.com/anthropics/claude-code/issues/4553)
- [GitHub: Colors Feature Request](https://github.com/anthropics/claude-code/issues/5254)
