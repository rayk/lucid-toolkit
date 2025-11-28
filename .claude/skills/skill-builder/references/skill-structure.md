<overview>
Comprehensive guide to skill organization, naming, and structure.
</overview>

<xml_structure_requirements>
<pure_xml_in_body>
**CRITICAL RULE**: Remove ALL markdown headings (#, ##, ###) from skill body content. Replace with semantic XML tags.

**Keep markdown formatting WITHIN content:**
- Bold: `**text**`
- Italic: `*text*`
- Lists: `- item` or `1. item`
- Code blocks: ` ```language ``` `
- Links: `[text](url)`
- Inline code: `` `code` ``

**Convert headings to XML tags:**

```markdown
<!-- ❌ WRONG - markdown headings -->
## Instructions
### Step 1: Setup
- Do something

<!-- ✅ CORRECT - XML tags -->
<instructions>
<step_1_setup>
- Do something
</step_1_setup>
</instructions>
```
</pure_xml_in_body>

<required_xml_tags>
Every skill MUST have these three tags:

1. **`<objective>`** - What the skill does and why it matters
   - First thing Claude reads
   - Should be 1-3 sentences
   - Focus on the goal, not the steps

2. **`<quick_start>`** - Immediate, actionable guidance
   - The "just show me how" section
   - Can include `<workflow>` for step-by-step
   - Can include `<example_skill>` for templates

3. **`<success_criteria>`** or **`<when_successful>`** - How to know it worked
   - Observable outcomes
   - Validation checks
   - Expected artifacts
</required_xml_tags>

<conditional_xml_tags>
Add these based on complexity (see intelligence rules):

- **`<context>`** - Background/situational information
- **`<workflow>` or `<process>`** - Step-by-step procedures
- **`<advanced_features>`** - Deep-dive topics (progressive disclosure)
- **`<validation>`** - How to verify outputs
- **`<examples>`** - Multi-shot learning
- **`<anti_patterns>`** - Common mistakes to avoid
- **`<security_checklist>`** - Non-negotiable security patterns
- **`<testing>`** - Testing workflows
- **`<common_patterns>`** - Code examples and recipes
- **`<reference_guides>` or `<detailed_references>`** - Links to reference files
</conditional_xml_tags>

<xml_best_practices>
**Semantic Naming:**
```xml
<!-- ✅ GOOD - describes purpose -->
<generation_protocol>
<adaptive_intake>
<research_trigger>

<!-- ❌ BAD - generic or unclear -->
<section_1>
<misc>
<stuff>
```

**Proper Nesting:**
```xml
<!-- ✅ GOOD - clear hierarchy -->
<generation_protocol>
  <step_0>
    <critical_first_action>
      Content here
    </critical_first_action>
  </step_0>
</generation_protocol>

<!-- ❌ BAD - flat structure -->
<generation_protocol></generation_protocol>
<step_0></step_0>
<critical_first_action></critical_first_action>
```

**Closing Tags:**
```xml
<!-- ✅ GOOD - properly closed -->
<objective>
Content here
</objective>

<!-- ❌ BAD - missing close tag -->
<objective>
Content here
```
</xml_best_practices>
</xml_structure_requirements>

<naming_conventions>
<skill_directory_name>
**Pattern:** `^[a-z0-9]+(-[a-z0-9]+)*$`

**Conventions:**
- Lowercase letters, numbers, hyphens only
- Max 64 characters
- Verb-noun pattern preferred: `create-*`, `manage-*`, `setup-*`, `generate-*`, `analyze-*`, `process-*`
- Descriptive and unique

**Examples:**
- ✅ `create-agent-skills`
- ✅ `process-pdfs`
- ✅ `manage-stripe-subscriptions`
- ✅ `generate-natal-chart`
- ❌ `CreateSkills` (uppercase)
- ❌ `create_skills` (underscores)
- ❌ `skill` (too vague)
</skill_directory_name>

<skill_name_field>
**Must match directory name exactly:**

```yaml
# Directory: skills/create-agent-skills/
---
name: create-agent-skills  # ✅ Matches directory
---
```
</skill_name_field>

<supporting_file_organization>
```
skills/skill-name/
├── SKILL.md              # Required: Main skill file
├── references/           # Optional: Progressive disclosure
│   ├── topic-1.md
│   ├── topic-2.md
│   └── topic-3.md
├── templates/            # Optional: Template files
│   ├── template-1.ext
│   └── template-2.ext
├── checklists/           # Optional: Reference checklists
│   └── checklist-1.md
├── scripts/              # Optional: Executable scripts
│   ├── script-1.sh
│   └── script-2.py
└── examples/             # Optional: Example files
    ├── before.ext
    └── after.ext
```
</supporting_file_organization>
</naming_conventions>

<writing_effective_descriptions>
<description_field_requirements>
**Validation:**
- Max 1024 characters
- Third person voice
- Include WHAT it does
- Include WHEN to use it (trigger terms)
- Include WHEN NOT to use it (if ambiguous)
</description_field_requirements>

<description_formula>
```
[What it does]. Use when [trigger scenarios]. [Optional: DO NOT use for [exclusions]].
```
</description_formula>

<good_description_examples>
✅ **Specific with clear triggers:**
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

✅ **Clear boundaries:**
```yaml
description: Expert guidance for creating, writing, building, and refining Claude Code Skills. Use when working with SKILL.md files, authoring new skills, improving existing skills, or understanding skill structure, progressive disclosure, workflows, validation patterns, and XML formatting.
```

✅ **Domain-specific with exclusions:**
```yaml
description: Manage Stripe subscriptions, customers, and billing. Use when user mentions Stripe, subscriptions, payments, or billing. DO NOT use for other payment providers (PayPal, Square).
```
</good_description_examples>

<bad_description_examples>
❌ **Too vague:**
```yaml
description: Reviews code
```

❌ **Too broad:**
```yaml
description: Handles all git operations including status, diff, commit, push, pull, merge, rebase, and branch management. Use for any git task.
```

❌ **Missing triggers:**
```yaml
description: This skill helps with PDF processing tasks.
```

❌ **First person voice:**
```yaml
description: I will help you create agent skills.
```
</bad_description_examples>
</writing_effective_descriptions>

<progressive_disclosure_patterns>
<keep_skill_md_focused>
**Target: < 500 lines for main SKILL.md**

**Strategy:**
1. **Core instructions in SKILL.md**
   - Required tags (objective, quick_start, success_criteria)
   - Essential workflow
   - Common use cases

2. **Detailed content in reference files**
   - Deep-dive explanations
   - Extensive examples
   - API references
   - Advanced patterns
   - Troubleshooting guides

3. **Link from SKILL.md to references**
   ```xml
   <reference_guides>
   For detailed validation patterns, see [references/validation.md](references/validation.md)
   For API reference, see [references/api.md](references/api.md)
   </reference_guides>
   ```
</keep_skill_md_focused>

<reference_file_organization>
**By topic (recommended):**
```
references/
├── skill-structure.md      # One topic per file
├── core-principles.md
├── workflows-validation.md
└── common-patterns.md
```

**By type:**
```
references/
├── api/
│   ├── endpoint-1.md
│   └── endpoint-2.md
└── guides/
    ├── quickstart.md
    └── advanced.md
```
</reference_file_organization>

<when_to_split_content>
**Keep in SKILL.md:**
- Core workflow (step-by-step)
- Essential context
- Quick examples
- Common patterns

**Move to references/**:
- Detailed explanations (>100 lines)
- Comprehensive API docs
- Extensive code examples
- Troubleshooting matrices
- Advanced topics
</when_to_split_content>
</progressive_disclosure_patterns>

<file_organization_best_practices>
<directory_structure_by_complexity>
**Simple skill (single file):**
```
skill-name/
└── SKILL.md
```

**Medium skill (with templates):**
```
skill-name/
├── SKILL.md
└── templates/
    ├── template-1.md
    └── template-2.md
```

**Complex skill (full structure):**
```
skill-name/
├── SKILL.md
├── references/
│   ├── topic-1.md
│   ├── topic-2.md
│   └── topic-3.md
├── templates/
│   └── template-1.md
├── checklists/
│   └── checklist-1.md
└── scripts/
    └── utility-1.sh
```
</directory_structure_by_complexity>

<relative_path_references>
**From SKILL.md to supporting files:**

```markdown
See [references/api.md](references/api.md) for API details.
See [templates/component.tsx](templates/component.tsx) for template.
See [checklists/security.md](checklists/security.md) for checklist.
Run `scripts/validate.sh` to validate.
```

**Claude loads these files on-demand** - they don't consume context until referenced.
</relative_path_references>
</file_organization_best_practices>

<validation_checklist>
Before finalizing a skill:

- [ ] **Directory name**: Matches pattern, verb-noun, max 64 chars
- [ ] **YAML frontmatter**: Valid syntax, name matches directory
- [ ] **Description**: ≤1024 chars, third person, includes triggers
- [ ] **XML structure**: No markdown headings in body
- [ ] **Required tags**: Has objective, quick_start, success_criteria
- [ ] **Conditional tags**: Appropriate for complexity level
- [ ] **XML validity**: All tags properly closed, semantic names
- [ ] **Progressive disclosure**: SKILL.md < 500 lines, details in references
- [ ] **File organization**: Supporting files in correct directories
- [ ] **Relative paths**: References use correct relative paths
- [ ] **Focus**: One capability, not swiss army knife
- [ ] **Security**: allowed-tools restricted appropriately
</validation_checklist>

<common_skill_patterns>
<pattern_1_review_audit>
**Purpose:** Analyze code/docs/configs for quality

**Characteristics:**
- Read-only operations
- Structured evaluation
- Checklist-driven

**Structure:**
```
skill-name/
├── SKILL.md
└── checklists/
    ├── security-checklist.md
    └── quality-checklist.md
```

**Example tools:**
```yaml
allowed-tools:
  - Read
  - Grep
  - Glob
  # No Write/Edit
```
</pattern_1_review_audit>

<pattern_2_generation>
**Purpose:** Create new files/content

**Characteristics:**
- Template-based
- Write operations
- Structured output

**Structure:**
```
skill-name/
├── SKILL.md
└── templates/
    ├── template-1.md
    └── template-2.md
```

**Example tools:**
```yaml
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
  - Bash
```
</pattern_2_generation>

<pattern_3_transformation>
**Purpose:** Modify existing files

**Characteristics:**
- Edit operations
- Before/after examples
- Validation steps

**Structure:**
```
skill-name/
├── SKILL.md
└── examples/
    ├── before.ts
    └── after.ts
```

**Example tools:**
```yaml
allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
```
</pattern_3_transformation>

<pattern_4_analysis>
**Purpose:** Extract insights from codebase

**Characteristics:**
- Search operations
- Data aggregation
- Report generation

**Structure:**
```
skill-name/
├── SKILL.md
├── references/
│   └── metrics.md
└── scripts/
    └── analyze.sh
```

**Example tools:**
```yaml
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
```
</pattern_4_analysis>
</common_skill_patterns>

<installation_locations>
<project_skills>
**Location:** `skills/<skill-name>/`

**Characteristics:**
- Committed to version control
- Shared across team
- Team standards and workflows
- Project-specific patterns

**Usage:**
```bash
git add skills/skill-name
git commit -m "feat(skills): add skill-name skill"
git push
```
</project_skills>

<personal_skills>
**Location:** `~/skills/<skill-name>/`

**Characteristics:**
- NOT committed to version control
- Personal workflows
- Experimental skills
- Individual preferences

**Usage:**
- Simply create in `~/skills/`
- Available only to you
- Can be copied to other machines manually
</personal_skills>
</installation_locations>
