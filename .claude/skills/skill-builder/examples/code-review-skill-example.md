# Example: Code Review Skill

This is a complete example of a well-designed skill for code review.

## File: skills/code-review/SKILL.md

```yaml
---
name: code-review
description: Reviews code for quality, security, performance, and best practices following team standards. Use when user asks to review code, audit code quality, check for issues, or perform code review. Supports all programming languages with language-specific checks.
allowed-tools:
  - Read
  - Grep
  - Glob
---

# Code Review

Comprehensive code review following industry best practices and team standards.

## When to Use

- User asks: "review this code"
- User asks: "can you check this for issues?"
- User asks: "audit code quality"
- User mentions: "code review"

## Review Checklist

### 1. Security
- [ ] No hardcoded credentials or API keys
- [ ] Input validation on user inputs
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection where applicable
- [ ] Secure authentication/authorization

### 2. Performance
- [ ] No N+1 query problems
- [ ] Efficient algorithms (time complexity)
- [ ] Memory usage is reasonable
- [ ] No unnecessary re-renders (React/Vue)
- [ ] Database queries are optimized
- [ ] Caching where appropriate

### 3. Code Quality
- [ ] Clear variable/function names
- [ ] Functions are focused and single-purpose
- [ ] DRY - no unnecessary duplication
- [ ] Proper error handling
- [ ] Appropriate logging
- [ ] Comments where needed (complex logic)

### 4. Testing
- [ ] Critical paths have tests
- [ ] Edge cases covered
- [ ] Test names are descriptive
- [ ] No test interdependencies
- [ ] Mocks used appropriately

### 5. Best Practices
- [ ] Follows language idioms
- [ ] Consistent style
- [ ] No deprecated APIs
- [ ] Dependencies are up to date
- [ ] No console.log/print debugging left in

## Instructions

1. **Identify Files to Review**
   - If user specified files, review those
   - Otherwise, use `git status` to find modified files
   - Use Grep to find recently changed code

2. **Read Each File**
   - Use Read tool to examine contents
   - Note line numbers for issues

3. **Apply Checklist**
   - Go through each category systematically
   - Note severity: 🔴 Critical, 🟡 Medium, 🟢 Minor

4. **Generate Report**
   - Structured format (see below)
   - Specific line numbers
   - Actionable recommendations

## Output Format

```
## Code Review Report

### Summary
Reviewed X files, found Y issues (Z critical, W medium, V minor)

### Critical Issues 🔴
1. **[Issue]** - file.ts:42
   - Problem: [description]
   - Risk: [security/performance/correctness]
   - Fix: [specific recommendation]

### Medium Issues 🟡
1. **[Issue]** - file.ts:108
   - Problem: [description]
   - Improvement: [recommendation]

### Minor Issues 🟢
1. **[Issue]** - file.ts:200
   - Suggestion: [recommendation]

### Positive Highlights ✅
- [Good practice 1]
- [Good practice 2]

### Overall Assessment
[Summary paragraph with quality score]
```

## Examples

**User:** "Can you review this authentication code?"

**Action:**
1. Find auth-related files
2. Review for security issues
3. Check for common auth vulnerabilities
4. Provide detailed report

**User:** "Review the changes in my last commit"

**Action:**
1. Run `git diff HEAD~1`
2. Identify changed files
3. Focus review on modifications
4. Report on new code only
```

## Why This Example Works

✅ **Clear Description:** Specific trigger terms ("review code", "audit", "check for issues")
✅ **Focused Purpose:** One capability - code review
✅ **Read-Only:** Uses Read, Grep, Glob (no modifications)
✅ **Comprehensive:** Covers security, performance, quality, testing
✅ **Actionable:** Structured report with line numbers and fixes
✅ **Flexible:** Works for any programming language
✅ **Examples:** Shows how it responds to different requests
