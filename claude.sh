#!/bin/bash
# Run Claude Code with custom settings
# Usage: ./run-claude.sh [additional args...]

export TERM=xterm-256color
export FORCE_COLOR=1
export CLICOLOR=1
export CLICOLOR_FORCE=1

# UTF-8 support (prevents unicode corruption)
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export NODE_OPTIONS="--max-old-space-size=8192"
# Python encoding
export PYTHONIOENCODING=utf-8

echo -ne "\033]0;Claude Code\007"

claude --dangerously-skip-permissions "$@"
