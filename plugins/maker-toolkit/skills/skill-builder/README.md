# Skill Builder

A meta-skill that helps create new Claude Code agent skills following best practices.

## What It Does

The skill-builder assists in designing and creating well-structured agent skills that Claude can discover and use automatically. It guides you through the entire process from requirements gathering to testing.

## When Claude Uses This Skill

Claude will automatically use skill-builder when you:
- Ask to "create a skill"
- Say "build a skill" or "make a new skill"
- Request "help designing a skill"
- Mention "skill builder"

## What's Included

### Main Skill File
- `SKILL.md` - Complete instructions for building skills

### Templates
- `templates/simple-skill.md` - Basic skill template
- `templates/complex-skill.md` - Advanced skill with multiple phases
- `templates/read-only-skill.md` - Analysis/review skill (no modifications)

### Examples
- `examples/code-review-skill-example.md` - Complete code review skill
- `examples/test-generator-skill-example.md` - Test generation skill
- `examples/doc-generator-skill-example.md` - Documentation skill

## Usage

Just ask naturally:

```
"Can you help me create a skill for code reviews?"
"Build a skill that generates commit messages"
"I want to make a skill for security audits"
```

Claude will:
1. Ask clarifying questions about your requirements
2. Design the skill structure
3. Create the SKILL.md file with proper frontmatter
4. Add supporting files if needed
5. Provide testing instructions
6. Explain how to install and use it

## Skill Design Principles

The skill-builder follows these principles:

- **Focus:** One skill = one capability
- **Discoverability:** Clear descriptions with trigger terms
- **Security:** Restrict tools appropriately
- **Context Efficiency:** Progressive disclosure via lazy loading
- **Quality:** Follow official Claude Code best practices

## Directory Structure

```
skill-builder/
├── SKILL.md                                    # Main skill instructions
├── README.md                                   # This file
├── templates/                                  # Starter templates
│   ├── simple-skill.md                        # Basic skill
│   ├── complex-skill.md                       # Advanced skill
│   └── read-only-skill.md                     # Analysis skill
└── examples/                                   # Complete examples
    ├── code-review-skill-example.md           # Review skill
    ├── test-generator-skill-example.md        # Generator skill
    └── doc-generator-skill-example.md         # Documentation skill
```

## Testing the Skill

After creating skill-builder, test it by asking:

```
"Can you create a skill for formatting SQL queries?"
```

Claude should:
1. Activate the skill-builder automatically
2. Ask clarifying questions
3. Design and create the skill
4. Provide installation instructions

## Notes

- This is a **project skill** (team-shared via git)
- Located in `skills/skill-builder/`
- Uses progressive disclosure for efficiency
- Includes comprehensive examples and templates

## Learn More

See the examples in `examples/` directory for:
- How to structure different types of skills
- Best practices for descriptions
- Tool permission patterns
- Testing and validation approaches
