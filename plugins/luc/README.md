# Luc Plugin

Base-level plugin for Claude Code providing foundational commands, skills, and status line.

## Purpose

This is the foundational plugin intended to be installed alongside all other plugins. It provides common commands and skills that are useful regardless of project type:

- Not specific to workspaces
- Not specific to monorepos
- Not specific to ontology-based projects
- Works with any project structure

## Installation

```bash
/plugin install luc@lucid-toolkit
```

Install this plugin first, then add specialized plugins based on your project needs.

## Status Line

The plugin includes a rich status line script (`scripts/status_line.py`) that displays:

**Line 1: Session & Token Info**
- Focus indicator (from project-info.toon or workspace-info.toon)
- Context window usage
- Cache stats (database size, hit rate, ROI)
- Token usage (up/down)
- Session time and efficiency

**Line 2: Git Info**
- Branch name
- Worktree name (if applicable)
- Lines changed (+added/-removed)
- Commits today

**Line 3: Location**
- Current working directory

The status line is automatically configured when running `/luc:setup`. It dynamically reads the project directory from Claude Code's stdin and looks for `.claude/project-info.toon` or `.claude/workspace-info.toon` for project context.

## Commands

| Command | Description |
|---------|-------------|
| `/luc:setup` | Idempotent project setup - generates project-info.toon and configures status line |
| `/luc:about` | Display plugin info, session details, and marketplace info |

## Features

- Common commands applicable to all projects
- Foundational skills for general development workflows
- Base utilities that other plugins can build upon
- Rich status line with session, token, and git information
