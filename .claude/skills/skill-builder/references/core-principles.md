<overview>
Fundamental principles that make skills effective, efficient, and maintainable.
</overview>

<progressive_disclosure>
<description>
Progressive disclosure is the **core design principle** that makes Agent Skills flexible and scalable. It operates on three levels:
</description>

<level_1_metadata>
**What:** Name + Description (~100 tokens)
**When:** At startup, loaded into system prompt
**Purpose:** Claude knows ALL skills exist and when to use them

```yaml
---
name: process-pdfs
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---
```

This lightweight metadata enables skill discovery without consuming significant context.
</level_1_metadata>

<level_2_full_instructions>
**What:** Complete SKILL.md content (<5k tokens recommended)
**When:** When Claude determines the skill is relevant
**Purpose:** Full workflow, examples, validation

Claude loads SKILL.md only when needed based on the description's trigger terms matching the user's request.
</level_2_full_instructions>

<level_3_additional_resources>
**What:** Reference files, templates, scripts, checklists
**When:** When Claude references them in SKILL.md
**Purpose:** Deep-dive content, API docs, extensive examples

```markdown
See [references/api-details.md](references/api-details.md) for complete API reference.
```

Claude navigates to these files **only when necessary** for the specific task.
</level_3_additional_resources>

<why_this_matters>
**Without progressive disclosure:**
- All content loaded upfront → context window bloat
- Limited skill complexity → can't include comprehensive docs
- One-size-fits-all → inefficient for simple tasks

**With progressive disclosure:**
- Minimal baseline cost (~100 tokens per skill metadata)
- Effectively unbounded skill complexity (load only what's needed)
- Efficient scaling (10 skills = ~1k tokens, 100 skills = ~10k tokens)
- Task-appropriate depth (simple tasks don't load deep references)
</why_this_matters>

<design_implication>
**Keep SKILL.md < 500 lines:**
- Core workflow and essential context only
- Link to references/ for detailed content
- Balance thoroughness with token efficiency

**Split reference files by topic:**
- Mutually exclusive topics in separate files
- Claude loads only relevant topics
- Example: `api-authentication.md` vs `api-webhooks.md`
</design_implication>
</progressive_disclosure>

<pure_xml_structure>
<description>
Claude was **trained with XML tags** and has been **fine-tuned to pay special attention** to their structure.
</description>

<why_xml_over_markdown>
**Advantages of XML:**
1. **Semantic meaning**: `<validation>` is clearer than "## Validation"
2. **Parseability**: Claude can extract structured content reliably
3. **Nested hierarchy**: `<step_1><substep_a></substep_a></step_1>`
4. **Standardization**: Consistent structure across all skills
5. **Training alignment**: Claude was trained on XML-structured prompts

**Performance difference:**
- XML tags: Claude recognizes structure immediately
- Markdown headings: Generic text requiring interpretation
</why_xml_over_markdown>

<xml_tag_guidelines>
**Semantic naming:**
```xml
<!-- ✅ GOOD - describes purpose -->
<objective>
<quick_start>
<validation>
<success_criteria>

<!-- ❌ BAD - generic -->
<section_1>
<part_a>
<misc>
```

**Consistent closing:**
```xml
<!-- ✅ GOOD - properly closed -->
<workflow>
  <step_1>
    Content here
  </step_1>
</workflow>

<!-- ❌ BAD - missing close -->
<workflow>
  <step_1>
    Content here
```

**Appropriate nesting:**
```xml
<!-- ✅ GOOD - logical hierarchy -->
<generation_protocol>
  <step_0>
    <critical_first_action>
      Gate logic here
    </critical_first_action>
    <adaptive_intake>
      Questioning logic here
    </adaptive_intake>
  </step_0>
</generation_protocol>

<!-- ❌ BAD - flat when hierarchy exists -->
<generation_protocol></generation_protocol>
<step_0></step_0>
<critical_first_action></critical_first_action>
```
</xml_tag_guidelines>

<required_vs_conditional_tags>
**Required tags (every skill):**
- `<objective>` - What and why
- `<quick_start>` - Immediate actionable guidance
- `<success_criteria>` or `<when_successful>` - Observable outcomes

**Conditional tags (based on complexity):**
- `<context>` - Background information
- `<workflow>` or `<process>` - Step-by-step procedures
- `<advanced_features>` - Progressive disclosure to deep topics
- `<validation>` - Verification procedures
- `<examples>` - Multi-shot learning
- `<anti_patterns>` - Common mistakes
- `<security_checklist>` - Non-negotiable security patterns
- `<reference_guides>` - Links to reference files
</required_vs_conditional_tags>

<markdown_within_xml>
**Keep these markdown formats:**
- **Bold**: `**text**`
- *Italic*: `*text*`
- Lists: `- item` or `1. item`
- Code blocks: ` ```language ``` `
- Links: `[text](url)`
- Inline code: `` `code` ``

**Example:**
```xml
<workflow>
1. **First step**: Do something
   - Sub-point with `inline code`
   - Another sub-point
2. **Second step**: Do another thing
   ```python
   code_example()
   ```
</workflow>
```
</markdown_within_xml>
</pure_xml_structure>

<conciseness>
<description>
Every token in a skill competes with:
- Conversation history
- Other loaded skills
- User's files and context
- Tool outputs
</description>

<conciseness_strategies>
**Assume Claude is smart:**
```xml
<!-- ❌ VERBOSE - explaining obvious things -->
<instruction>
First, you need to open the file. To open a file, you use the Read tool.
The Read tool takes a file_path parameter. You must provide the absolute path.
An absolute path starts with / on Unix systems or C:\ on Windows...
</instruction>

<!-- ✅ CONCISE - Claude knows this -->
<instruction>
Read the file using the Read tool.
</instruction>
```

**Focus on domain knowledge Claude lacks:**
```xml
<!-- ✅ GOOD - domain-specific context Claude needs -->
<stripe_subscription_lifecycle>
Stripe subscriptions have three critical timestamps:
- `current_period_start`: When current billing cycle began
- `current_period_end`: When cycle ends (billing date)
- `trial_end`: When trial ends (may differ from period end)

DO NOT cancel at `current_period_end` thinking it's the trial end.
Use `trial_end` for trial cancellations.
</stripe_subscription_lifecycle>
```

**Reference, don't repeat:**
```xml
<!-- ❌ VERBOSE - repeating full API in SKILL.md -->
<stripe_api>
[500 lines of API documentation]
</stripe_api>

<!-- ✅ CONCISE - reference file -->
<stripe_api>
See [references/stripe-api.md](references/stripe-api.md) for complete API reference.

Common operations:
- Create subscription: `POST /v1/subscriptions`
- Update subscription: `POST /v1/subscriptions/:id`
- Cancel subscription: `DELETE /v1/subscriptions/:id`
</stripe_api>
```
</conciseness_strategies>
</conciseness>

<degrees_of_freedom>
<description>
The **degrees of freedom** principle: Be as specific as necessary, but no more specific than required.
</description>

<high_specificity>
**When:** Fragile tasks that MUST be done exactly right
**Examples:** Security reviews, API authentication, financial transactions, data validation

```xml
<security_checklist>
CRITICAL: Check these in order:

1. **Input validation**: ALWAYS sanitize user input
   - SQL: Use parameterized queries, NEVER string concatenation
   - XSS: Escape HTML entities in output
   - Path traversal: Validate file paths against whitelist

2. **Authentication**: MUST use established patterns
   - API keys: NEVER commit to version control
   - Passwords: MUST hash with bcrypt/scrypt (min 10 rounds)
   - Tokens: MUST expire (max 24h for sessions)

3. **Authorization**: Check before EVERY operation
   - Verify user owns resource
   - Check role permissions
   - Log access attempts
</security_checklist>
```
</high_specificity>

<low_specificity>
**When:** Creative tasks with many valid approaches
**Examples:** Documentation writing, code refactoring, exploratory analysis

```xml
<documentation_guidelines>
Write clear, helpful documentation that:
- Explains the "why" not just the "what"
- Includes practical examples
- Anticipates common questions
- Uses appropriate tone for audience

Structure and style are flexible based on context.
</documentation_guidelines>
```
</low_specificity>

<balanced_specificity>
**When:** Structured but not rigid tasks
**Examples:** Skill creation, code generation, file organization

```xml
<skill_creation_workflow>
Follow this general workflow, adapting as needed:

1. **Gather requirements**: Understand purpose, triggers, complexity
2. **Design structure**: Choose appropriate XML tags
3. **Write content**: Core instructions + references
4. **Validate**: Check naming, YAML, XML structure
5. **Test**: Real usage with trigger terms

Adjust order and depth based on skill complexity.
</skill_creation_workflow>
```
</balanced_specificity>

<decision_framework>
Ask: "What happens if Claude does this differently?"

**High stakes → Low freedom:**
- Security vulnerability
- Data loss
- Financial error
- System breakage
→ Use MUST, NEVER, ALWAYS, specific steps

**Low stakes → High freedom:**
- Stylistic preference
- Multiple valid approaches
- Exploratory work
- Creative output
→ Use should, consider, typically, guidelines
</decision_framework>
</degrees_of_freedom>

<model_selection>
<description>
Different Claude models excel at different tasks.
</description>

<model_characteristics>
**Haiku (Fast, Efficient):**
- Simple pattern matching
- Straightforward transformations
- Template filling
- Basic validation
- Cost: ~$0.25 per million tokens

**Sonnet (Balanced):**
- Moderate complexity
- Multi-step workflows
- Code generation
- Analysis tasks
- Cost: ~$3 per million tokens

**Opus (Powerful, Comprehensive):**
- Complex reasoning
- Novel problem solving
- Architecture design
- Security audits
- Cost: ~$15 per million tokens
</model_characteristics>

<testing_strategy>
**Start with Sonnet (default), then test edges:**

1. **Can Haiku handle this?**
   - Simple enough for fast model?
   - Pattern-based or template-driven?
   - If yes → save cost, improve speed

2. **Does this need Opus?**
   - Requires deep reasoning?
   - Novel or complex problem?
   - High stakes (security, architecture)?
   - If yes → use Opus for reliability
</testing_strategy>

<specifying_model_in_skills>
```yaml
---
name: simple-formatter
description: Format files according to template
model: haiku  # Simple transformation
---
```

```yaml
---
name: security-audit
description: Comprehensive security review
model: opus  # High stakes, deep reasoning
---
```

```yaml
---
name: code-generator
description: Generate code from specs
# No model specified → uses default (Sonnet)
---
```
</specifying_model_in_skills>
</model_selection>

<third_person_voice>
<description>
Skill descriptions are injected into Claude's **system prompt**, not shown to the user.
</description>

<why_third_person_matters>
**System prompt context:**
```
You are Claude. Your capabilities include:
- [Skill 1 description]
- [Skill 2 description]
- [Skill 3 description]
```

**First person breaks immersion:**
```
- I will help you create agent skills  ❌ (Claude thinks it's talking to itself)
```

**Third person maintains consistency:**
```
- Expert guidance for creating agent skills  ✅ (Claude understands this is a capability)
```
</why_third_person_matters>

<description_voice_examples>
✅ **Third person:**
```yaml
description: Extracts text from PDF files. Use when user mentions PDFs or document extraction.
description: Manages Stripe subscriptions and billing. Use when working with Stripe API.
description: Reviews code for security vulnerabilities. Use for security audits.
```

❌ **First person:**
```yaml
description: I extract text from PDF files when you ask me to.
description: I'll help you manage Stripe subscriptions.
description: I can review your code for security issues.
```
</description_voice_examples>
</third_person_voice>

<summary_checklist>
When creating a skill, ensure:

- [ ] **Progressive disclosure**: SKILL.md < 500 lines, details in references
- [ ] **Pure XML**: No markdown headings, semantic tag names, proper closing
- [ ] **Conciseness**: Only include what Claude doesn't already know
- [ ] **Appropriate freedom**: Match specificity to task fragility
- [ ] **Model consideration**: Test if Haiku/Opus would be better than Sonnet
- [ ] **Third person**: Description written as Claude's capability, not Claude's voice
</summary_checklist>
