---
name: git-commits
description: Generates well-structured git commits with architectural scope and purpose documentation. Guides local commit squashing for clean remote history. Use when making commits, preparing to push, managing commit history, or writing commit messages.
---

<objective>
Create well-structured git commits that document WHY work was done, capture architectural scope, and maintain clean remote history through squashing. Use when making commits, preparing for push, or managing local commit history.
</objective>

<quick_start>
Basic commit with purpose:

```bash
git commit -m "feat(auth): add password reset flow

Purpose: Users cannot recover locked accounts without admin intervention.
This adds self-service password reset via email verification.

- Add /auth/reset-password endpoint
- Send reset tokens via email
- Expire tokens after 1 hour"
```

Before pushing, squash WIP commits:

```bash
git log --oneline origin/main..HEAD
git rebase -i origin/main  # Mark commits with 'squash' or 'fixup'
```
</quick_start>

<core_principle>
**Commits are documentation for future maintainers, not just version control checkpoints.**

Every commit should answer:
- WHAT changed (conventional commit type)
- WHERE in the architecture (scope)
- WHY it was done (purpose in body)
- HOW it connects to goals (context)
</core_principle>

<commit_format>
<format_template>
```
<type>(<scope>): <subject>

<purpose>

<body>

<footer>
```
</format_template>

<format_components>
| Component | Required | Description |
|-----------|----------|-------------|
| type | Yes | Conventional commit type |
| scope | Yes | Architectural area affected |
| subject | Yes | Imperative description (50 chars) |
| purpose | Yes | WHY this work was done (1-2 sentences) |
| body | Optional | Technical details, decisions made |
| footer | Optional | Breaking changes, issue refs, co-authors |
</format_components>

<format_example>
```
feat(auth/tokens): add JWT refresh token rotation

Purpose: Prevent token theft attacks by invalidating refresh tokens after
single use, addressing security audit finding SEC-2024-003.

- Implement token family tracking in Redis
- Add rotation logic to /auth/refresh endpoint
- Expire old tokens immediately on rotation
- Log rotation events for security monitoring

Closes #142
```
</format_example>
</commit_format>

<commit_types>
<types_table>
| Type | When to Use |
|------|-------------|
| feat | New feature or capability |
| fix | Bug fix |
| perf | Performance improvement |
| refactor | Code restructuring without behavior change |
| docs | Documentation only |
| test | Adding or updating tests |
| build | Build system, dependencies |
| ci | CI/CD configuration |
| chore | Maintenance tasks |
| style | Formatting, whitespace |
| revert | Reverting previous commit |
</types_table>

<type_selection>
Choose based on **intent**, not files changed:
- Fixing a bug that adds code → `fix`
- Adding tests for new feature → `feat` (include tests in feature commit)
- Performance fix → `perf` (not `fix`)
</type_selection>
</commit_types>

<architectural_scope>
The scope MUST reflect the architectural area, not just the file or directory.

<scope_hierarchy>
```
<domain>[/<component>][/<subcomponent>]
```
</scope_hierarchy>

<domain_examples>
| Domain | Description | Example Scopes |
|--------|-------------|----------------|
| auth | Authentication/authorization | auth, auth/tokens, auth/oauth |
| api | API endpoints and contracts | api/rest, api/graphql, api/webhooks |
| data | Data layer and persistence | data/models, data/migrations, data/cache |
| ui | User interface components | ui/forms, ui/navigation, ui/charts |
| core | Core business logic | core/validation, core/workflow |
| infra | Infrastructure concerns | infra/docker, infra/k8s, infra/terraform |
| cli | Command-line interface | cli/commands, cli/output |
| sdk | SDK and client libraries | sdk/python, sdk/typescript |
</domain_examples>

<scope_rules>
1. **Use architectural domain, not file path**
   - Good: `auth/tokens`
   - Bad: `src/services/auth`

2. **Include component when specific**
   - `api/users` for user endpoints
   - `api` for cross-cutting API changes

3. **Multi-area changes**: Use primary affected domain
   - If auth changes require API updates → `auth`
   - If adding new API that uses auth → `api`

4. **Cross-cutting concerns**: Use appropriate domain
   - Logging infrastructure → `infra/logging`
   - Logging in auth flow → `auth`
</scope_rules>
</architectural_scope>

<purpose_section>
The purpose section explains WHY this work was done. It appears after the subject line, before the technical body.

<purpose_answers>
- What problem does this solve?
- What goal does this advance?
- What prompted this change?
</purpose_answers>

<purpose_patterns>
| Pattern | Template |
|---------|----------|
| Problem-Solution | "Fixes [problem] by [approach]" |
| Feature-Benefit | "Enables [capability] for [users/system]" |
| Audit-Response | "Addresses [finding] from [source]" |
| Refactor-Reason | "Improves [quality] to enable [future work]" |
| Debt-Payment | "Resolves technical debt in [area] accumulated from [cause]" |
</purpose_patterns>

<purpose_examples>
```
Purpose: Users were experiencing 5-second delays on dashboard load due to
N+1 queries. This optimization reduces load time to under 200ms.
```

```
Purpose: The current token implementation doesn't support multi-device login.
This adds device tracking to enable per-device token revocation.
```

```
Purpose: Preparing for the React 19 upgrade by removing deprecated lifecycle
methods that will break in the new version.
```
</purpose_examples>
</purpose_section>

<squashing>
Before pushing to remote, related local commits should be squashed into cohesive, well-documented commits.

<squash_scenarios>
| Scenario | Action |
|----------|--------|
| WIP commits | Always squash |
| Fix-up commits | Squash into original |
| Iterative refinements | Squash into feature commit |
| Distinct features | Keep separate |
| Breaking change + migration | Keep separate |
</squash_scenarios>

<squash_workflow>
1. **Identify squash candidates**
   ```bash
   git log --oneline origin/main..HEAD
   ```

2. **Interactive rebase**
   ```bash
   git rebase -i origin/main
   ```

3. **Mark commits for squashing**
   - `pick` - Keep commit as-is
   - `squash` (or `s`) - Combine with previous, merge messages
   - `fixup` (or `f`) - Combine with previous, discard message

4. **Write consolidated message**
   Use the extended semantic format with comprehensive purpose.
</squash_workflow>

<squash_patterns>
**Pattern: Feature Development**
```
pick abc1234 feat(auth): add login endpoint
squash def5678 wip: login validation
squash ghi9012 fix typo
squash jkl3456 add tests for login
```
Result: Single `feat(auth): add login endpoint` with complete implementation.

**Pattern: Bug Investigation**
```
pick abc1234 fix(data): resolve connection pool exhaustion
fixup def5678 add logging
fixup ghi9012 found the issue
fixup jkl3456 actual fix
```
Result: Clean `fix` commit with final solution only.

**Pattern: Refactor Steps**
```
pick abc1234 refactor(core): extract validation service
pick def5678 refactor(api): use validation service
```
Result: Keep separate - distinct logical changes that reviewers need to see independently.
</squash_patterns>

<pre_push_checklist>
Before pushing, verify:

1. [ ] Each commit is a complete, logical unit
2. [ ] No WIP or fixup commits remain
3. [ ] Commit messages follow extended semantic format
4. [ ] Purpose sections explain WHY
5. [ ] Scopes reflect architecture
6. [ ] Tests pass at each commit (bisect-safe)
</pre_push_checklist>

<squash_commands>
```bash
# View commits to squash
git log --oneline origin/main..HEAD

# Squash all local commits into one
git reset --soft origin/main
git commit

# Interactive squash with control
git rebase -i origin/main

# Squash last N commits
git reset --soft HEAD~N
git commit

# Abort if something goes wrong
git rebase --abort
```
</squash_commands>
</squashing>

<workflow>
<during_development>
1. **Commit frequently** with WIP messages
   - `wip: trying approach A`
   - `wip: validation working`

2. **Use fixup commits** for corrections
   - `fixup! feat(auth): add login`
</during_development>

<before_push>
1. **Review local history**
   ```bash
   git log --oneline origin/main..HEAD
   ```

2. **Identify logical groupings**
   - What distinct features/fixes exist?
   - What should reviewers see separately?

3. **Squash WIP and fixups**
   ```bash
   git rebase -i origin/main
   ```

4. **Write final messages**
   - Extended semantic format
   - Clear purpose sections
   - Architectural scopes

5. **Verify history**
   ```bash
   git log origin/main..HEAD
   ```

6. **Push**
   ```bash
   git push origin <branch>
   ```
</before_push>
</workflow>

<examples>
<example_feature>
```
feat(api/webhooks): add webhook signature verification

Purpose: Third-party integrations require cryptographic verification of
webhook payloads to prevent spoofing attacks and ensure data integrity.

- Add HMAC-SHA256 signature generation on send
- Add signature verification middleware for incoming webhooks
- Support both header-based and query-param signatures
- Include timestamp to prevent replay attacks (5-min window)
- Log verification failures with request metadata

Breaking: Existing webhook endpoints now require X-Signature header.
See docs/webhooks.md for integration guide.

Closes #89
```
</example_feature>

<example_bugfix>
```
fix(data/cache): prevent stale cache reads during failover

Purpose: During Redis failover, the cache client was returning stale data
from a disconnected replica instead of failing fast to the database.

- Add connection health check before cache reads
- Implement circuit breaker pattern for cache failures
- Fall back to database when circuit is open
- Add metrics for cache miss reasons

Fixes production incident INC-2024-156 where users saw outdated pricing
during the December 15th Redis maintenance window.
```
</example_bugfix>

<example_refactor>
```
refactor(core/validation): extract validation into dedicated service

Purpose: Validation logic was duplicated across 12 controllers, making
rule updates error-prone and testing difficult. Centralizing enables
consistent validation and simplifies the upcoming custom rules feature.

- Create ValidationService with fluent API
- Migrate all controllers to use service
- Add validation result caching
- Remove duplicate validation helpers

No behavior changes. All existing tests pass unchanged.
```
</example_refactor>

<example_performance>
```
perf(ui/dashboard): optimize widget rendering with virtualization

Purpose: Dashboards with 50+ widgets were causing browser freezes due to
rendering all widgets simultaneously. Users reported 10+ second load times.

- Implement react-window for widget list virtualization
- Only render visible widgets plus 2-row buffer
- Add intersection observer for lazy data fetching
- Reduce initial bundle by code-splitting widget types

Measured improvements:
- Initial render: 10.2s → 0.8s
- Memory usage: 450MB → 120MB
- Lighthouse performance: 23 → 89
```
</example_performance>
</examples>

<best_practices>
1. **Commit Purpose First**: Write the purpose before the technical body - if you can't explain why, reconsider the change

2. **Atomic Commits**: Each commit should be deployable independently where possible

3. **Bisect-Safe**: Ensure tests pass at every commit for effective `git bisect`

4. **Review Your History**: Before pushing, read commits as a reviewer would

5. **Scope Consistency**: Use consistent scope names across the project - document in CONTRIBUTING.md

6. **No Secrets**: Never commit credentials, even in "WIP" commits that will be squashed

7. **Link Context**: Reference issues, PRs, docs, or incidents that provide context

8. **Sign Commits**: Use GPG signing for audit trails in production systems
</best_practices>

<validation>
<validation_checklist>
Before committing, verify:

1. Type matches intent (feat/fix/refactor/etc.)
2. Scope reflects architecture, not file path
3. Subject is imperative, under 50 chars
4. Purpose explains WHY in 1-2 sentences
5. Body provides technical details if needed
6. Footer includes references and breaking changes
</validation_checklist>

<common_issues>
| Issue | Problem | Fix |
|-------|---------|-----|
| File-based scope | `src/auth/token.ts` | Use `auth/tokens` |
| Missing purpose | Just describes what | Add why paragraph |
| Vague subject | "update stuff" | Be specific: "add token rotation" |
| Wrong type | Using `fix` for features | Match to intent table |
| WIP in remote | "wip: trying" pushed | Squash before push |
</common_issues>
</validation>

<success_criteria>
- Commit message follows extended semantic format (type, scope, subject, purpose)
- Purpose section clearly explains WHY the change was made
- Scope reflects architectural domain, not file paths
- WIP and fixup commits squashed before push to remote
- Each commit represents complete, logical unit of work
- Tests pass at each commit (bisect-safe)
</success_criteria>
