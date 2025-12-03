---
description: Create a git commit using the git-commits skill for proper semantic formatting
allowed-tools: Bash(git:*), Read, Skill
---

<objective>
Create a well-structured git commit following the workspace's extended semantic commit format with purpose documentation and architectural scoping.

This ensures all commits document WHY work was done, maintain clean history, and follow team conventions.
</objective>

<context>
Current status: !`git status`
Staged changes: !`git diff --cached --stat`
Recent commits: !`git log --oneline -5`
</context>

<process>
1. Review staged changes to understand what's being committed
2. Invoke the git-commits skill for guidance on formatting:
   ```
   Skill("ws:git-commits")
   ```
3. Determine commit type (feat/fix/refactor/etc.) based on intent
4. Identify architectural scope (domain/component, not file path)
5. Write commit with:
   - Subject line: `<type>(<scope>): <imperative description>`
   - Purpose section: WHY this change was made
   - Body: Technical details if needed
   - Footer: Issue refs, breaking changes
6. Execute the commit

If nothing is staged, stage relevant changes first using `git add`.
</process>

<success_criteria>
- Commit follows extended semantic format
- Purpose section explains WHY (not just WHAT)
- Scope reflects architecture, not file paths
- Subject is imperative and under 50 chars
- Commit created successfully
</success_criteria>
