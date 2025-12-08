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

2. **Root cause analysis** (general-purpose opus):
   Launch analytical agent:

   Task (general-purpose, opus):
     Analyze protocol violation from step 1 context.
     Output: rule violated, cognitive pattern, root cause category.
     @constraints: maxTokens: 2500

3. **Present findings** to user:
   - What happened (concise description)
   - Protocol violated (specific rule)
   - Root cause (underlying reason)
   - Failure pattern (named pattern if applicable)

4. **Confirm understanding** (AskUserQuestion):
   - "Does this analysis capture the issue correctly?"
   - If user says "partially" or "no" → incorporate feedback, return to step 2

5. **Research solutions** (parallel agents):
   Task 1 (general-purpose, sonnet): Search docs for similar violations (2000 tokens)
   Task 2 (general-purpose, sonnet): Search skills/ for patterns (1500 tokens)
   Task 3 (general-purpose, haiku): Search CLAUDE.md (1000 tokens)

6. **Design solution** (general-purpose opus):
   Task (general-purpose, opus):
     Design robust solution from research findings.
     @constraints: maxTokens: 3000

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

<output_format>
## Reflection Findings Output Format

For step 3 (presenting findings), use TOON structured format:

```toon
@type: AssessAction
name: reflection-findings
actionStatus: CompletedActionStatus

finding:
incident: [concise description of what happened]
protocolViolated: [specific protocol rule from CLAUDE.md]
rootCause: [underlying cognitive pattern that led to violation]
failurePattern: [named pattern if applicable: Specificity Trap, Momentum, Compound Request, etc.]

x-conversationTurn: [approximate turn number where violation occurred]
x-toolsUsed: [number of tool calls involved]
```

**Note:** Keep all root cause analysis reasoning, solution research, design rationale, and implementation details as markdown prose. Only use TOON for the structured reflection findings presentation.
</output_format>

<success_criteria>
- Protocol violation clearly identified with specific rule reference
- Root cause traces cognitive pattern, not just symptom
- User confirms problem understanding before solution design
- Solution backed by documentation/workspace pattern evidence
- User confirms implementation plan before execution
- Changes tested or validated where possible
</success_criteria>