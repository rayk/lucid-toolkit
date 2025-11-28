# Lucid Toolkit

A Claude Code plugin marketplace for capability-driven development. Build strategic capabilities through tactical outcomes with context-aware workflows.

## What is Capability-Driven Development?

Capability-driven development structures work around **capabilities** (strategic goals with maturity percentages) that are built through **outcomes** (tactical work units with observable effects). This approach:

- Connects daily work to strategic objectives
- Tracks progress through measurable maturity metrics
- Preserves context across sessions for seamless work resumption
- Optimizes AI token usage through systematic delegation

## Plugins

The Lucid Toolkit provides six modular plugins that can be installed independently or together.

### Core Workflow Plugins

| Plugin | Description | Details |
|--------|-------------|---------|
| **[capability](plugins/capability/README.md)** | Strategic capability management with maturity tracking. Create, delete, and snapshot capabilities with business value mapping and actor involvement. | 3 commands, 1 hook |
| **[outcome](plugins/outcome/README.md)** | Outcome lifecycle management through queued → ready → in-progress → completed states. Supports parent-child hierarchies and capability contribution tracking. | 9 commands, 1 skill, 5 templates |
| **[context](plugins/context/README.md)** | Context window conservation with delegation protocols. Automatic session tracking, work resumption, and token budget management. | 6 commands, 4 skills, session hooks |

### Analysis & Development Plugins

| Plugin | Description | Details |
|--------|-------------|---------|
| **[think](plugins/think/README.md)** | Structured analysis using 12 mental models (5-Whys, First Principles, SWOT, etc.). Intelligent model selection based on problem type. | 3 commands, 1 skill, 12 frameworks |
| **[workspace](plugins/workspace/README.md)** | Multi-project management with shared registry, health validation, and cross-reference integrity checking. | 10 commands, pre-commit hooks |
| **[plan](plugins/plan/README.md)** | TDD execution prompt generator. Analyzes design docs and generates autonomous implementation prompts with cost-efficient model delegation. | 3 commands, 1 skill |

## Quick Start

### Install from Marketplace

```bash
# Add the Lucid Toolkit marketplace
/plugin marketplace add rayk/lucid-toolkit

# Install all plugins interactively
/plugin

# Or install specific plugins
/plugin install context@lucid-toolkit
/plugin install capability@lucid-toolkit
/plugin install outcome@lucid-toolkit
```

### Install Shared Library (Required for Hooks)

```bash
cd shared/cli-commons && pip install -e .
```

### Verify Installation

```bash
# Check context conservation is active
/context:info

# Create your first capability
/capability:create

# Start working on an outcome
/outcome:focus
```

## Core Concepts

### Capabilities

Strategic goals measured by maturity percentage (0-100%). Each capability:
- Maps to 1-3 core business values
- Has defined maturity milestones (30%, 60%, 80%, 100%)
- Is built by one or more outcomes
- Tracks actor involvement and dependencies

### Outcomes

Tactical work units that build capabilities. Each outcome:
- Describes WHAT to achieve (not HOW)
- Specifies observable behavioral effects
- Contributes a percentage to capability maturity
- Moves through lifecycle states: queued → ready → in-progress → completed

### Context Conservation

The main Claude context window is precious. The context plugin enforces:
- **Delegation by default**: 3+ tool calls → delegate to subagent
- **Token budgets**: Right-sized model selection (haiku/sonnet/opus)
- **Session tracking**: Automatic work resumption across sessions

## Installation Options

### Option 1: Marketplace (Recommended)

```bash
/plugin marketplace add rayk/lucid-toolkit
/plugin install context@lucid-toolkit
```

### Option 2: Team Configuration

Add to `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "lucid-toolkit": {
      "source": {
        "source": "github",
        "repo": "rayk/lucid-toolkit"
      }
    }
  }
}
```

### Option 3: Manual Clone

```bash
git clone https://github.com/rayk/lucid-toolkit.git ~/.claude/plugins/lucid-toolkit
cd ~/.claude/plugins && ln -s lucid-toolkit/plugins/* .
```

## Plugin Structure

Each plugin follows the official Claude Code plugin structure:

```
plugins/{name}/
├── plugin.json          # Plugin manifest
├── settings.json        # Hook configurations (if applicable)
├── commands/            # Slash commands (*.md)
├── skills/              # Skills (SKILL.md)
├── hooks/               # Python lifecycle scripts
├── templates/           # File templates
└── schemas/             # JSON validation schemas
```

## Requirements

- Claude Code CLI (latest)
- Python 3.11+
- Git

## Documentation

- [Capability Plugin](plugins/capability/README.md) - Strategic capability management
- [Outcome Plugin](plugins/outcome/README.md) - Outcome lifecycle and parent-child hierarchies
- [Context Plugin](plugins/context/README.md) - Session tracking and delegation protocols
- [Think Plugin](plugins/think/README.md) - Mental models and structured analysis
- [Workspace Plugin](plugins/workspace/README.md) - Multi-project management
- [Plan Plugin](plugins/plan/README.md) - TDD execution prompt generation

## License

MIT License - See LICENSE file for details

## Author

rayk - https://github.com/rayk
