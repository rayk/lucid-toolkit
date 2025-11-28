# Lucid Toolkit

Capability-driven development tools for Claude Code. A plugin marketplace for building capabilities through outcomes.

## Overview

The Lucid Toolkit provides a comprehensive suite of plugins that implement capability-driven development workflows for Claude Code. Each plugin is modular and can be installed independently.

## Plugins

### Core Workflow

- **capability-workflow** - Strategic capability management with maturity tracking
- **outcome-workflow** - Outcome lifecycle management (create, focus, complete)
- **session-manager** - Session lifecycle tracking with accomplishment capture

### Analysis & Development

- **thinking-tools** - Structured analysis using mental models (consider, assess)
- **maker-toolkit** - Build Claude Code skills, commands, and agents
- **workspace-validator** - Schema validation and workspace health checks

### Best Practices

- **delegation-protocol** - Context-saving patterns for efficient Claude Code usage

## Installation

### Full Toolkit

```bash
# Clone the repository
git clone https://github.com/rayk/lucid-toolkit.git ~/.claude/plugins/lucid-toolkit

# Link plugins to your workspace
cd ~/.claude/plugins
ln -s lucid-toolkit/plugins/* .
```

### Individual Plugin

```bash
# Clone the repository
git clone https://github.com/rayk/lucid-toolkit.git ~/.claude/plugins/lucid-toolkit

# Link specific plugin
cd ~/.claude/plugins
ln -s lucid-toolkit/plugins/capability-workflow .
```

## Shared CLI Commons

The toolkit includes `lucid-cli-commons`, a shared Python library used by plugin hooks and scripts.

### Install CLI Commons

```bash
cd ~/.claude/plugins/lucid-toolkit/shared/cli-commons
pip install -e .
```

This provides common utilities for:
- Schema validation
- JSON/YAML parsing
- Git operations
- File system utilities
- Cross-reference management

## Plugin Structure

Each plugin follows a standard structure:

```
plugins/{name}/
├── plugin.json          # Plugin metadata
├── commands/           # Slash commands (*.md)
├── skills/            # Skills (SKILL.md)
├── hooks/             # Git hooks and lifecycle scripts
├── agents/            # Subagent configurations
├── templates/         # File templates
└── schemas/           # JSON schemas
```

## Requirements

- Claude Code CLI
- Python 3.11+
- Git

## Development

See `docs/DEVELOPMENT.md` for contribution guidelines and plugin development patterns.

## License

MIT License - See LICENSE file for details

## Author

rayk - https://github.com/rayk
