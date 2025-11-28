# Maker Toolkit Plugin

**Build Claude Code extensions with expert guidance and quality assurance.**

The Maker Toolkit provides skills, commands, agents, and patterns for creating, auditing, and refining Claude Code slash commands, skills, and subagents.

---

## 📦 Contents

### Skills (4)

Interactive expert guidance for building Claude Code extensions:

| Skill | Purpose | Use When |
|-------|---------|----------|
| **skill-builder** | Create and refine Claude Code skills | Building SKILL.md files, implementing progressive disclosure, XML formatting |
| **command-builder** | Create slash commands | Building command YAML, argument parsing, dynamic context |
| **sub-agent-builder** | Create and use subagents | Setting up agent configs, understanding Task tool patterns |
| **coordinate-subagents** | Advanced subagent patterns | Troubleshooting subagents, implementing voting, managing token budgets |

**Usage:**
```bash
# Invoke skills in conversation
/skill skill-builder
/skill command-builder
/skill sub-agent-builder
/skill coordinate-subagents
```

### Commands (5)

Executable workflows for quality assurance and creation:

| Command | Purpose | Arguments |
|---------|---------|-----------|
| `/tools:skills:audit` | Audit skill for YAML, XML structure, progressive disclosure | `<skill-path>` |
| `/tools:skills:check` | Apply corrections from execution feedback | `[specific-issue]` |
| `/tools:cmds:build-command` | Create new slash command | Interactive prompts |
| `/tools:cmds:audit` | Audit slash command for YAML, arguments, content quality | `<command-path>` |
| `/coordinate` | Guide efficient subagent invocation | `[context]` |

**Usage:**
```bash
# Audit a skill
/tools:skills:audit /path/to/SKILL.md

# Create a new command
/tools:cmds:build-command

# Audit a command
/tools:cmds:audit /path/to/command.md
```

### Agents (3)

Specialized subagents for automated quality checks:

| Agent | Model | Purpose |
|-------|-------|---------|
| **skill-auditor** | haiku | Fast skill validation (YAML, XML, structure) |
| **slash-command-auditor** | haiku | Command validation (YAML, arguments, restrictions) |
| **subagent-auditor** | haiku | Subagent config validation |

**Usage (via Task tool or coordinate skill):**
```python
# Invoked automatically by audit commands
# Or manually via Task tool with agent specification
```

### Documentation (1)

| Document | Purpose |
|----------|---------|
| **maker-patterns.md** | Design patterns, anti-patterns, and best practices for builder skills |

---

## 🎯 Common Workflows

### Creating a New Skill

1. **Start with guidance:**
   ```bash
   /skill skill-builder
   ```

2. **Follow the interactive workflow:**
   - Skill purpose and scope
   - Progressive disclosure design
   - XML structure patterns
   - Validation and testing

3. **Audit before shipping:**
   ```bash
   /tools:skills:audit skills/my-skill/SKILL.md
   ```

### Creating a New Slash Command

1. **Invoke builder:**
   ```bash
   /tools:cmds:build-command
   ```

2. **Define command:**
   - Command name and path
   - Arguments (optional/required)
   - Dynamic context needs
   - Tool restrictions

3. **Audit for quality:**
   ```bash
   /tools:cmds:audit commands/my-command.md
   ```

### Working with Subagents

1. **Learn patterns:**
   ```bash
   /skill sub-agent-builder
   ```

2. **Get coordination help:**
   ```bash
   /coordinate "need to search multiple codebases and synthesize results"
   ```

3. **Advanced troubleshooting:**
   ```bash
   /skill coordinate-subagents
   ```

---

## 🔍 Quality Assurance

### Skill Auditing

**Checks performed by `/tools:skills:audit`:**
- ✓ Valid YAML frontmatter
- ✓ Pure XML structure (no markdown in XML blocks)
- ✓ Progressive disclosure pattern compliance
- ✓ Required sections present (purpose, workflow, validation)
- ✓ Proper XML nesting and closing tags
- ✓ No anti-patterns (monolithic blocks, missing gates)

### Command Auditing

**Checks performed by `/tools:cmds:audit`:**
- ✓ Valid YAML frontmatter with required fields
- ✓ Proper argument specification (type, required, description)
- ✓ Dynamic context configuration
- ✓ Tool restrictions when needed
- ✓ Content quality and clarity
- ✓ No security issues (command injection risks)

### Automated Correction

**Skill feedback loop:**
```bash
# After running a skill and finding issues:
/tools:skills:check "XML structure violations in workflow section"
```

This applies learnings from execution to improve skill quality.

---

## 📋 Best Practices

### From `maker-patterns.md`:

**Progressive Disclosure:**
- Start with clear purpose statement
- Use XML gates (`<workflow>`, `<validation>`, `<troubleshooting>`)
- Load heavy content only when needed
- Keep initial response under 500 tokens

**XML Structure:**
- Pure XML in skill content (no markdown inside XML blocks)
- Proper nesting and closing tags
- Use CDATA for code examples: `<![CDATA[...]]>`
- Semantic tag names that describe purpose

**Subagent Coordination:**
- Set explicit token budgets
- Choose appropriate model (haiku/sonnet/opus)
- Specify output format (TOON, JSON)
- Parallel execution when independent
- Voting for critical decisions

**Anti-Patterns to Avoid:**
- ❌ Monolithic skills without progressive disclosure
- ❌ Markdown mixed with XML structure
- ❌ Missing validation sections
- ❌ Unclear skill scope or purpose
- ❌ No error handling guidance
- ❌ Unbounded subagent token usage

---

## 🔗 Integration

### Plugin Structure
```
maker-toolkit/
├── commands/          # Executable workflows
├── skills/           # Interactive guidance
├── agents/           # Quality assurance subagents
├── docs/            # Patterns and best practices
└── README.md        # This file
```

### Dependencies

**Required:**
- Claude Code CLI
- Access to `.claude/` directory structure

**Optional:**
- Schema validation tools (for advanced checks)
- Git (for version tracking)

### Configuration

Place in Claude Code plugin directory:
```
.claude-plugin/
plugins/
  maker-toolkit/
    commands/
    skills/
    agents/
    docs/
```

Enable in `.claude/config.yaml` (if using plugin system).

---

## 📚 Learn More

1. **Start here:** Read `docs/maker-patterns.md` for design philosophy
2. **Hands-on:** Try `/tools:cmds:build-command` to create your first command
3. **Deep dive:** Invoke `/skill skill-builder` for comprehensive skill creation guidance
4. **Advanced:** Study `/skill coordinate-subagents` for multi-agent patterns

---

## 🤝 Contributing

When improving maker-toolkit:

1. **Follow your own guidance:** Use the builder skills to improve themselves
2. **Audit everything:** Run audit commands before committing
3. **Document patterns:** Add learnings to `maker-patterns.md`
4. **Test workflows:** Verify end-to-end creation → audit → correction cycles

---

## 📄 License

Part of lucid-toolkit. See repository root for license information.

---

**Build better builder tools. Use maker-toolkit.**
