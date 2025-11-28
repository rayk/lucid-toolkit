# CLAUDE.md

Project instructions for Claude Code working in this repository.

<critical_behavior>
## Context Preservation

Primary goal: Preserve main context by delegating exploration and multi-step work to sub-agents.

Claude's context window is finite. When exhausted mid-task, work is lost. Sub-agents (Task tool) operate in isolated contexts—use them to protect the main conversation.

### Decision Principle

Delegate by default. Execute directly only for simple, certain operations.

**Delegate when (any apply):**
- Location unknown: "find where X happens" → Task(Explore)
- Multi-file operation: "fix X across codebase" → Task(general-purpose)
- Uncertain scope: tool count unclear → Task
- Exploration needed: understanding before acting → Task(Explore)

**Execute directly when (ALL must apply):**
- Single, specific file path already known
- 1-2 tool calls, certain
- No search/exploration component

### Specificity Trap

Specific user input (error messages, function names) without file paths creates false confidence. You know WHAT to find, not WHERE or HOW MANY. Treat specific mutation requests as exploration until locations are confirmed.

Exception: User provides exact file path.

### Transition Awareness

After research (WebSearch, exploratory Read), the next request often asks to ACT on findings. This is the highest-risk moment. Default to delegation when transitioning from research to action.

### Trade-off

False positives (unnecessary delegation) acceptable. Context exhaustion is not.
</critical_behavior>

## Request → Action Matrix

| Request | Action | Rationale |
|---------|--------|-----------|
| "Where is auth configured?" | Task(Explore) | Unknown location |
| "Fix getUserById" | Task(general-purpose) | Find + analyze + edit |
| "Error: 'path not found' in config" | Task(general-purpose) | Specificity trap |
| "Add import to src/utils.ts" | Direct Edit | Known file, single op |
| "What does this file do?" [in context] | Direct answer | Already read |
| "Fix the performance issue" | Ask → Task | Ambiguous, then delegate |
| "Change timeout to 5000 in config.ts" | Direct Edit | Specific + location given |

## Constraints

DO NOT:
- Execute multi-file operations directly in main context
- Assume file locations without confirmation
- Guess values, paths, or behaviors when ambiguous
- Add features, refactoring, or "improvements" beyond what was requested

DO:
- Clarify ambiguous requests before acting (AskUserQuestion)
- Use Task(Explore) for any "find where" operations
- Keep solutions minimal and focused on the request
- State conclusions directly without hedging

## Clarification Protocol

**Clarify when:**
- Request has multiple valid interpretations
- Success criteria are undefined
- Technical approach requires choosing between alternatives

**Do not clarify when:**
- Request is clear and actionable
- Standard conventions apply unambiguously

**Precedence:** Ask → Delegate → Direct

---

## Repository Overview

Lucid Toolkit is a Claude Code plugin marketplace implementing capability-driven development workflows.

## Commands

```bash
# Add marketplace
/plugin marketplace add rayk/lucid-toolkit

# Install plugin
/plugin install capability@lucid-toolkit

# Install shared CLI library (required for hooks/scripts)
cd shared/cli-commons && pip install -e .

# Run tests
cd shared/cli-commons && pytest
```

## Structure

```
lucid-toolkit/
├── .claude/                 # Local commands, skills, agents
│   ├── commands/           # Slash commands for this repo
│   ├── skills/             # Skills for this repo
│   └── agents/             # Subagent definitions
├── .claude-plugin/         # Marketplace configuration
│   └── marketplace.json
├── plugins/                # Installable plugins
│   ├── capability/         # Strategic capability management
│   ├── outcome/            # Outcome lifecycle management
│   ├── context/            # Context window conservation
│   ├── think/              # Mental models (consider, assess)
│   ├── workspace/          # Multi-project management
│   └── plan/               # TDD execution prompts
└── shared/
    └── cli-commons/        # Python utilities for hooks
```

### Plugin Structure

```
plugins/{name}/
├── plugin.json          # Metadata and declarations
├── commands/            # Slash commands (*.md)
├── skills/              # Skills (SKILL.md)
├── hooks/               # Python lifecycle scripts
├── schemas/             # JSON schemas
└── templates/           # File templates
```

## Key Concepts

**Capability-Driven Development:**
- Capabilities = strategic goals with maturity percentage
- Outcomes = tactical work units that build capabilities
- Outcome completion → capability maturity increases

**Outcome Hierarchy:**
- Parent outcomes aggregate children (`005-parent/005.1-child/`)
- Children have `parentContribution` %, parent owns `capabilityContributions`

## Naming Conventions

| Entity | Pattern | Example |
|--------|---------|---------|
| Capability ID | `^[a-z0-9]+(-[a-z0-9]+)*$` | `auth-system` |
| Outcome Dir | `^[0-9]+-[a-z0-9-]+$` | `005-ontology` |
| Child Outcome | `^[0-9]+\.[0-9]+-[a-z0-9-]+$` | `005.1-testing` |

## Cross-Reference Integrity

When modifying tracking files, maintain referential integrity:
- `capabilities/*/capability_track.json` - Individual capability state
- `outcomes/*/outcome_track.json` - Outcome state and links
- `status/capability_summary.json` - Central capability index
- `status/outcome_summary.json` - Central outcome index
