<overview>
Patterns for complex workflows, validation loops, and quality assurance in agent skills.
</overview>

<complex_workflow_patterns>
<linear_workflow>
**When:** Sequential steps, each depends on the previous

```xml
<workflow>
1. **Gather requirements**: Ask user for input
2. **Design structure**: Based on requirements
3. **Create files**: Implement the design
4. **Validate**: Check against requirements
5. **Deliver**: Present to user
</workflow>
```

**Characteristics:**
- Clear sequence A → B → C
- Each step prerequisite for next
- No branching or loops
- Best for straightforward tasks
</linear_workflow>

<branching_workflow>
**When:** Different paths based on conditions

```xml
<workflow>
1. **Analyze input**: Determine input type

2. **Branch by type**:
   - If PDF → Extract with pdfplumber
   - If Word → Extract with python-docx
   - If HTML → Extract with BeautifulSoup
   - If plain text → Read directly

3. **Validate extraction**: Check output quality

4. **Return results**: Standardized format
</workflow>
```

**Characteristics:**
- Decision points create branches
- Different tools/approaches per branch
- Converges at validation/output
- Best for multi-format or multi-method tasks
</branching_workflow>

<iterative_workflow>
**When:** Quality improvements through loops

```xml
<workflow>
1. **Generate initial draft**: First attempt

2. **Validate against criteria**: Check requirements

3. **If validation fails**:
   - Identify specific issues
   - Refine draft addressing issues
   - Return to step 2 (max 3 iterations)

4. **If validation passes**: Deliver final version
</workflow>
```

**Characteristics:**
- Explicit feedback loop
- Quality gates with criteria
- Maximum iteration limit (prevent infinite loops)
- Best for creative or complex output
</iterative_workflow>

<parallel_workflow>
**When:** Multiple independent tasks can run simultaneously

```xml
<workflow>
1. **Identify components**: Break into independent parts

2. **Execute in parallel**:
   ```
   [Task A: Generate documentation]
   [Task B: Write tests]
   [Task C: Create examples]
   ```
   (Use multiple tool calls in single message)

3. **Integrate results**: Combine outputs

4. **Validate integration**: Check combined result
</workflow>
```

**Characteristics:**
- Tasks have no dependencies
- Can execute simultaneously
- Requires integration step
- Best for composite deliverables
</parallel_workflow>

<phased_workflow>
**When:** Distinct phases with different focuses

```xml
<workflow>
**Phase 1: Discovery**
1. Analyze codebase
2. Identify patterns
3. Document findings

**Phase 2: Planning**
1. Design approach based on findings
2. Get user approval
3. Refine plan if needed

**Phase 3: Execution**
1. Implement changes
2. Run tests
3. Fix issues

**Phase 4: Validation**
1. Comprehensive testing
2. Documentation update
3. User review
</workflow>
```

**Characteristics:**
- Clear phase boundaries
- Phase completion checkpoints
- May include user gates (approvals)
- Best for large, complex projects
</phased_workflow>
</complex_workflow_patterns>

<validation_patterns>
<checklist_validation>
**When:** Multiple specific criteria to verify

```xml
<validation>
<checklist>
Validate the skill against these criteria:

**Structure:**
- [ ] Directory name matches pattern `^[a-z0-9]+(-[a-z0-9]+)*$`
- [ ] SKILL.md exists with valid YAML frontmatter
- [ ] Name field matches directory name
- [ ] Description ≤1024 characters, third person

**XML:**
- [ ] No markdown headings in body
- [ ] Required tags present (objective, quick_start, success_criteria)
- [ ] All XML tags properly closed
- [ ] Semantic tag names (not generic)

**Content:**
- [ ] Clear trigger terms in description
- [ ] Focused on one capability
- [ ] Progressive disclosure (SKILL.md < 500 lines)
- [ ] References use correct relative paths

**Security:**
- [ ] allowed-tools appropriate for task
- [ ] No credentials in files
- [ ] Scripts audited if included
</checklist>

If ANY item fails, address it before proceeding.
</validation>
```
</checklist_validation>

<schema_validation>
**When:** Structured data must match specific format

```xml
<validation>
<schema_validation>
Validate YAML frontmatter against schema:

**Required fields:**
```yaml
name: string (lowercase, hyphens, max 64 chars)
description: string (max 1024 chars)
```

**Optional fields:**
```yaml
allowed-tools: string[] (valid tool names)
model: "haiku" | "sonnet" | "opus"
```

**Validation script:**
```bash
# Check YAML is parseable
python -c "import yaml; yaml.safe_load(open('SKILL.md'))"

# Check name pattern
grep -E '^name: [a-z0-9]+(-[a-z0-9]+)*$' SKILL.md

# Check description length
python -c "import yaml; d=yaml.safe_load(open('SKILL.md')); assert len(d['description']) <= 1024"
```
</schema_validation>
</validation>
```
</schema_validation>

<functional_validation>
**When:** Testing actual behavior/output

```xml
<validation>
<functional_testing>
Test the skill with real usage:

**Setup:**
1. Create test skill in temporary directory
2. Load Claude with skill available
3. Prepare test scenarios

**Test cases:**
1. **Discovery test**: Use trigger terms without mentioning skill name
   - Expected: Claude loads the skill automatically
   - Verify: Skill mentioned in Claude's response

2. **Workflow test**: Complete a full task
   - Expected: Follows skill instructions
   - Verify: Output matches success criteria

3. **Edge case test**: Unusual or boundary conditions
   - Expected: Graceful handling
   - Verify: No errors, appropriate response

**Pass criteria:**
- All test cases pass
- No tool permission errors
- References load correctly
- Output quality acceptable
</functional_testing>
</validation>
```
</functional_validation>
</validation_patterns>

<plan_validate_execute_pattern>
<description>
Structured approach for high-stakes tasks.
</description>

<pattern_structure>
```xml
<plan_validate_execute>
**Phase 1: PLAN**
1. Analyze requirements thoroughly
2. Design complete approach
3. Identify risks and edge cases
4. Create execution checklist

**Phase 2: VALIDATE PLAN**
1. Review plan against requirements
2. Check for missing elements
3. Get user confirmation if needed
4. Refine plan based on feedback

**Phase 3: EXECUTE**
1. Follow plan step-by-step
2. Mark items as complete
3. Handle unexpected issues
4. Document any deviations

**Phase 4: VALIDATE EXECUTION**
1. Check output against success criteria
2. Run functional tests
3. Verify no regressions
4. Get user approval if required

If validation fails at any phase, return to previous phase.
</plan_validate_execute>
```
</pattern_structure>

<when_to_use>
**High-stakes scenarios:**
- Security implementations
- Data migrations
- System architecture changes
- Production deployments
- Financial transactions

**Complex scenarios:**
- Multiple file modifications
- Cross-reference updates
- API integrations
- Workflow automations

**Learning scenarios:**
- Novel problems
- Unfamiliar domains
- Exploratory tasks
- Research-heavy work
</when_to_use>

<example_implementation>
```xml
<security_review_workflow>
<phase_1_plan>
1. **Identify scope**:
   - Which files/components to review
   - What security standards apply (OWASP, CWE)
   - Any specific concerns mentioned

2. **Design checklist**:
   - Input validation points
   - Authentication/authorization checks
   - Data handling (encryption, sanitization)
   - External dependencies
   - Error handling security

3. **Plan evidence collection**:
   - What to document
   - How to present findings
   - Severity classification
</phase_1_plan>

<phase_2_validate_plan>
**Verify plan completeness:**
- [ ] All security categories covered
- [ ] Appropriate depth for risk level
- [ ] Evidence collection defined
- [ ] User agrees with scope

If incomplete, refine plan.
</phase_2_validate_plan>

<phase_3_execute>
**Conduct review:**
1. Systematically check each item on checklist
2. Document findings with file:line references
3. Classify severity (Critical/High/Medium/Low)
4. Note false positives and why
5. Suggest remediation for each issue
</phase_3_execute>

<phase_4_validate_execution>
**Verify review quality:**
- [ ] All checklist items completed
- [ ] Every finding documented with location
- [ ] Severity justified
- [ ] Remediation actionable
- [ ] No missed obvious issues

If quality insufficient, return to execution.
</phase_4_validate_execution>
</security_review_workflow>
```
</example_implementation>
</plan_validate_execute_pattern>

<feedback_loop_patterns>
<simple_feedback_loop>
**When:** Single validation criterion

```xml
<simple_loop>
```python
max_attempts = 3
for attempt in range(max_attempts):
    output = generate()
    if validate(output):
        return output
    else:
        refine_based_on_issues()
return best_effort_output
```

**Instructions:**
1. Generate output
2. Validate against criteria
3. If valid → done
4. If invalid → identify issues, refine, retry (max 3 attempts)
5. If max attempts → return best effort with caveat
</simple_loop>
```
</simple_feedback_loop>

<multi_criteria_feedback_loop>
**When:** Multiple validation dimensions

```xml
<multi_criteria_loop>
**Validation criteria:**
1. **Functional**: Does it work?
2. **Quality**: Is it well-written?
3. **Complete**: All requirements met?
4. **Secure**: No vulnerabilities?

**Loop logic:**
```
For each criterion:
    If fails → address specifically
    Track which criteria passing

If all criteria pass → done
If any fail after 3 iterations → flag for manual review
```

**Advantage:** Targeted refinement per criterion, not blanket revision
</multi_criteria_loop>
```
</multi_criteria_feedback_loop>

<progressive_refinement_loop>
**When:** Quality improves incrementally

```xml
<progressive_refinement>
**Iteration 1: Core functionality**
- Focus: Does it work at all?
- Validation: Basic functional test
- If fail → fix critical issues

**Iteration 2: Quality improvement**
- Focus: Code quality, readability
- Validation: Linting, standards
- If fail → improve specific quality issues

**Iteration 3: Polish**
- Focus: Edge cases, documentation, tests
- Validation: Comprehensive review
- If fail → minor refinements

Each iteration builds on previous, no rework of passing elements.
</progressive_refinement>
```
</progressive_refinement_loop>
</feedback_loop_patterns>

<error_handling_in_workflows>
<graceful_degradation>
```xml
<error_handling>
<graceful_degradation>
When encountering errors:

1. **Attempt primary approach**
   - If succeeds → continue workflow
   - If fails → log error, try fallback

2. **Attempt fallback approach**
   - If succeeds → continue with note about fallback used
   - If fails → try minimal viable

3. **Minimal viable output**
   - Partial success if possible
   - Clear documentation of what worked/didn't
   - Actionable next steps for user

Never fail silently. Always explain what happened and why.
</graceful_degradation>
</error_handling>
```
</graceful_degradation>

<fail_fast_validation>
```xml
<error_handling>
<fail_fast>
For critical prerequisites, validate immediately:

**Before starting main workflow:**
```
1. Check required files exist
2. Verify API credentials available
3. Validate input format
4. Confirm tool permissions

If ANY prerequisite fails:
    - STOP immediately
    - Report specific failure
    - Suggest remediation
    - DO NOT proceed with main workflow
```

**Rationale:** Failing early saves tokens and time, provides clearer feedback.
</fail_fast>
</error_handling>
```
</fail_fast_validation>
</error_handling_in_workflows>

<workflow_documentation_best_practices>
<numbered_steps_with_clear_actions>
```xml
<!-- ✅ GOOD - clear, actionable -->
<workflow>
1. **Read configuration file**: Use Read tool on `config.json`
2. **Validate schema**: Check required fields present
3. **Apply defaults**: For any missing optional fields
4. **Write updated config**: Use Write tool to save
</workflow>

<!-- ❌ BAD - vague, unclear sequence -->
<workflow>
You should look at the config file and then do validation.
After that update things as needed and save it.
</workflow>
```
</numbered_steps_with_clear_actions>

<decision_points_with_clear_conditions>
```xml
<!-- ✅ GOOD - explicit conditions -->
<workflow>
3. **Check authentication type**:
   - If `auth.type === "oauth"` → Execute OAuth flow
   - If `auth.type === "api_key"` → Use API key header
   - If `auth.type === "basic"` → Use Basic Auth
   - If unrecognized → Error: unsupported auth type
</workflow>

<!-- ❌ BAD - ambiguous branching -->
<workflow>
3. Figure out what kind of auth to use and do it.
</workflow>
```
</decision_points_with_clear_conditions>

<expected_outcomes_at_each_step>
```xml
<!-- ✅ GOOD - observable outcomes -->
<workflow>
1. **Fetch user data**: API call to `/users/:id`
   - Success: JSON object with user fields
   - Failure: 404 if user not found, 401 if unauthorized

2. **Validate user active**: Check `user.status === "active"`
   - If active → proceed to step 3
   - If inactive → return error "User account inactive"
</workflow>

<!-- ❌ BAD - no outcome clarity -->
<workflow>
1. Get the user data
2. Make sure they're active
</workflow>
```
</expected_outcomes_at_each_step>
</workflow_documentation_best_practices>

<summary>
**Choose workflow pattern based on task:**
- Linear → sequential dependencies
- Branching → conditional paths
- Iterative → quality refinement
- Parallel → independent components
- Phased → complex multi-stage

**Choose validation pattern based on need:**
- Checklist → multiple specific criteria
- Schema → structured data format
- Functional → behavior/output testing

**Use plan-validate-execute for:**
- High-stakes tasks
- Complex operations
- Novel problems

**Implement feedback loops when:**
- Quality matters more than speed
- Clear validation criteria exist
- Refinement improves output

**Handle errors gracefully:**
- Fail-fast for prerequisites
- Graceful degradation for attempts
- Always explain what happened
</summary>
