# Pre-Execution Investigation Prompt

**Purpose**: Systematic investigation of an execution plan before implementation to identify blockers, validate assumptions, and increase probability of success.

**Usage**: Run this prompt after creating an execution plan but before beginning implementation.

---

## Prompt

```
You are about to execute the plan in: {PLAN_PATH}

Before executing, conduct a systematic pre-execution investigation to identify potential blockers and validate assumptions. Your goal is to increase the probability of success from the current estimate to 90%+.

## Investigation Process

### 1. Read the Plan
- Read the execution plan completely
- Read the linked specification if referenced
- Note all file paths, dependencies, and assumptions mentioned

### 2. Dependency Compatibility Check
- Read the current pubspec.yaml (or equivalent package manifest)
- For each NEW dependency the plan proposes to add:
  - Run a dry-run: `fvm flutter pub add --dry-run <package>`
  - Note any version conflicts or resolution issues
- Document which versions actually resolve

### 3. Existing Code Audit
For each file the plan expects to MODIFY:
- Verify the file exists at the expected path
- Read the file and verify:
  - The interfaces/classes match what the plan expects
  - The methods to extend/modify exist
  - No unexpected changes have occurred since plan creation

For each file the plan expects to CREATE:
- Verify the parent directory exists
- Check no conflicting file already exists

### 4. Configuration Verification
Check all configuration files mentioned in the plan:
- Firebase configs (GoogleService-Info.plist, google-services.json, firebase_options.dart)
- Platform configs (Info.plist, build.gradle, AndroidManifest.xml)
- Build configs (build.yaml, analysis_options.yaml)
- Environment configs (.env, .fvmrc, pubspec.yaml SDK constraints)

For each, verify:
- File exists (or correctly noted as "to create")
- Current content is compatible with plan assumptions
- Extract any values the plan will need (API keys, client IDs, etc.)

### 5. Test Infrastructure Audit
- Check existing test directory structure
- Verify test helpers mentioned in the plan exist
- Check if mock classes need extension
- Verify test dependencies are available

### 6. Tool/Environment Verification
- Verify required SDK versions (Flutter, Dart)
- Check if FVM or similar version manager is required
- Verify external tools are installed (Firebase CLI, etc.)
- Test that basic commands work (`flutter pub get`, `flutter analyze`)

### 7. Compile Findings

Create a structured report with:

#### Findings Table
| Area | Status | Notes |
|------|--------|-------|
| ... | ✅/⚠️/❌ | ... |

#### Existing Code Inventory
Document what exists vs what needs to be added for key interfaces.

#### Known Issues
Number each issue and note:
- What the issue is
- Which work unit addresses it
- Exact solution (with code/config if applicable)

#### Verified Values
List any concrete values discovered (client IDs, paths, versions) that should be added to the plan.

#### Dependency Resolution
List the exact versions that will be installed (from dry-run output).

#### Risk Assessment
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| ... | Low/Medium/High | ... |

Estimate overall probability of success.

### 8. Update the Plan
Add your findings to the execution plan:
- Add a "Pre-Execution Investigation" section after the checklist
- Update any work units with discovered concrete values
- Add FVM/environment notes if needed
- Update dependency versions to verified ones

## Output Format

After investigation, provide:
1. Summary of findings (what you checked, what you found)
2. List of blockers (if any) - things that MUST be fixed before execution
3. List of risks with mitigations
4. Confirmation that the plan has been updated with findings
5. Updated probability of success estimate
```

---

## Example Invocation

```bash
claude "$(cat plans/01-auth-onboarding/pre-execution-investigation.prompt.md)" \
  --replace "{PLAN_PATH}" "plans/01-auth-onboarding/execution-plan.md"
```

Or simply:

```
Review the execution plan at plans/01-auth-onboarding/execution-plan.md

Before executing, investigate what could go wrong. Check:
- Do the proposed dependencies resolve?
- Do the files the plan expects to modify actually exist?
- Are the platform configs (iOS/Android) in the expected state?
- Is the test infrastructure ready?
- Are there any environment issues (SDK versions, FVM)?

Update the execution plan with your findings to increase success probability.
```

---

## Checklist Template

Use this checklist to track investigation progress:

- [ ] Read execution plan and specification
- [ ] Check dependency compatibility (dry-run `pub add`)
- [ ] Verify existing code matches plan assumptions
- [ ] Check Firebase configuration files
- [ ] Check platform configs (iOS Info.plist, Android build.gradle)
- [ ] Verify build tooling setup (build.yaml, Freezed, etc.)
- [ ] Audit test infrastructure and mocks
- [ ] Verify SDK/environment requirements
- [ ] Compile findings into structured report
- [ ] Update execution plan with findings
- [ ] Provide risk assessment and success probability
