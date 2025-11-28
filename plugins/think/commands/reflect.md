---
description: Reflect on recent behavior, identify protocol violations, design robust solutions
argument-hint: [optional: specific issue to reflect on]
---

<objective>
Analyze recent assistant behavior to identify protocol violations, understand root causes, and design robust solutions that prevent recurrence.

This helps when the assistant completed a task "correctly but wrongly" — the outcome was achieved but workspace protocols were violated (context conservation, delegation rules, checkpoint requirements, etc.).
</objective>

<context>
Protocol rules: @CLAUDE.md
Skills reference: @skills/
Commands reference: @commands/
User-specified issue: $ARGUMENTS
</context>

<process>
1. **Gather context** (parallel agents, haiku, 1500 tokens each):
   - Analyze conversation for tool call patterns and potential violations
   - Extract relevant protocol rules from CLAUDE.md
   - Check if debug logs needed (only if user reports errors)

2. **Root cause analysis** (ultrathink):
   - Identify which specific protocol rule was violated
   - Trace the cognitive pattern that led to violation
   - Find root cause (momentum, specificity trap, compound request, uncertainty)
   - Connect to known failure modes in CLAUDE.md delegation_examples

3. **Present findings** to user:
   - What happened (concise description)
   - Protocol violated (specific rule)
   - Root cause (underlying reason)
   - Failure pattern (named pattern if applicable)

4. **Confirm understanding** (AskUserQuestion):
   - "Does this analysis capture the issue correctly?"
   - If user says "partially" or "no" → incorporate feedback, return to step 2

5. **Research solutions** (parallel agents):
   - claude-code-guide agent: Search official docs for relevant patterns (2000 tokens)
   - sonnet agent: Search skills/ and commands/ for existing patterns (1500 tokens)
   - haiku agent: Search CLAUDE.md for similar solutions (1000 tokens)

6. **Design solution** (ultrathink):
   - Apply criteria: robust, sustainable, long-term, evidence-based
   - Consider: protocol modifications, new commands/skills, checkpoints, examples
   - Present approach, components, implementation plan, evidence, trade-offs

7. **Confirm implementation** (AskUserQuestion):
   - "Should I implement this solution?"
   - If user says "modify" → incorporate feedback, return to step 6

8. **Implement** (delegate to appropriate agent):
   - CLAUDE.md changes → Task(general-purpose, sonnet, 2500 tokens)
   - New command → Task(general-purpose, sonnet, 2000 tokens)
   - New skill → Skill(skill-builder)
   - Multi-file → Task(general-purpose, sonnet, 3000 tokens)

9. **Verify changes** and present summary
</process>

<verification>
Before completing, verify:
- Root cause identified and confirmed by user
- Solution grounded in documentation evidence
- Implementation follows workspace conventions (skill patterns, command structure)
- All modified files pass schema validation if applicable
- User explicitly approved each phase transition (steps 4 and 7)
</verification>

<output>
Files potentially created/modified:
- `CLAUDE.md` - Protocol updates, new examples, rule modifications
- `commands/*.md` - New or updated commands
- `skills/*/SKILL.md` - New or updated skills
</output>

<success_criteria>
- Protocol violation clearly identified with specific rule reference
- Root cause traces cognitive pattern, not just symptom
- User confirms problem understanding before solution design
- Solution backed by documentation/workspace pattern evidence
- User confirms implementation plan before execution
- Changes tested or validated where possible
</success_criteria>