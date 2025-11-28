# Example: Test Generator Skill

This example shows a skill that generates test files.

## File: skills/test-generator/SKILL.md

```yaml
---
name: test-generator
description: Generates unit tests for code files following testing best practices. Use when user asks to create tests, write tests, generate test cases, or add test coverage. Supports Jest, Vitest, Pytest, and other frameworks.
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
---

# Test Generator

Automatically generates comprehensive unit tests for code files.

## When to Use

- User asks: "write tests for this"
- User asks: "generate test cases"
- User asks: "create unit tests"
- User mentions: "test coverage"

## Instructions

### 1. Identify Target Code

- User specifies file, or
- Use current open file, or
- Ask user which file to test

### 2. Analyze Code Structure

Read the target file and identify:
- Exported functions/classes
- Input parameters and types
- Return types
- Dependencies (imports)
- Edge cases and error conditions

### 3. Detect Test Framework

Look for existing tests to determine framework:
- Check package.json for jest/vitest/mocha
- Check imports in existing test files
- Default to Jest if unclear

### 4. Generate Test File

Create test file following patterns:

**File Naming:**
- `src/utils/math.ts` → `src/utils/math.test.ts`
- `lib/parser.js` → `lib/parser.spec.js`

**Test Structure:**
```typescript
import { functionName } from './source-file'

describe('functionName', () => {
  it('should handle normal case', () => {
    // Arrange
    const input = validInput

    // Act
    const result = functionName(input)

    // Assert
    expect(result).toBe(expectedOutput)
  })

  it('should handle edge case', () => {
    // Test edge case
  })

  it('should throw error for invalid input', () => {
    expect(() => functionName(invalidInput)).toThrow()
  })
})
```

### 5. Generate Test Cases

For each function, create tests for:
- ✅ **Happy path** - normal, expected usage
- ✅ **Edge cases** - boundary conditions, empty inputs, nulls
- ✅ **Error cases** - invalid inputs, error handling
- ✅ **Integration** - interaction with dependencies (use mocks)

### 6. Write the Test File

Use Write tool to create the test file with:
- Proper imports
- Describe blocks for organization
- Clear test names
- AAA pattern (Arrange, Act, Assert)
- Mocks for dependencies
- Coverage of all exported functions

## Test Quality Standards

Tests should be:
- **Independent:** No reliance on other tests
- **Repeatable:** Same result every time
- **Descriptive:** Clear what's being tested
- **Fast:** No unnecessary delays
- **Isolated:** Mocked external dependencies

## Output Format

After generating tests:

```
✅ Generated test file: path/to/file.test.ts

Test coverage includes:
- functionA: 3 test cases (happy path, edge cases, errors)
- functionB: 4 test cases (normal, boundary, null, invalid)
- ClassC: 5 test cases (constructor, methods, edge cases)

Total: 12 test cases created

Run tests with: npm test
```

## Examples

**Example 1: Simple Function**

User: "Create tests for the calculateTotal function"

```typescript
// Original: src/utils/calculator.ts
export function calculateTotal(items: number[]): number {
  return items.reduce((sum, item) => sum + item, 0)
}

// Generated: src/utils/calculator.test.ts
import { calculateTotal } from './calculator'

describe('calculateTotal', () => {
  it('should sum array of numbers', () => {
    expect(calculateTotal([1, 2, 3])).toBe(6)
  })

  it('should return 0 for empty array', () => {
    expect(calculateTotal([])).toBe(0)
  })

  it('should handle negative numbers', () => {
    expect(calculateTotal([-1, -2, -3])).toBe(-6)
  })

  it('should handle mixed positive and negative', () => {
    expect(calculateTotal([10, -5, 3])).toBe(8)
  })
})
```

**Example 2: Class with Dependencies**

User: "Generate tests for the UserService class"

```typescript
// Generates tests with:
// - Constructor tests
// - Method tests with mocked dependencies
// - Error handling tests
// - Async operation tests
```
```

## Supporting Files

### File: templates/jest-template.ts

```typescript
import { FUNCTION_NAME } from './SOURCE_FILE'

describe('FUNCTION_NAME', () => {
  it('should EXPECTED_BEHAVIOR', () => {
    // Arrange
    const input = INPUT_VALUE

    // Act
    const result = FUNCTION_NAME(input)

    // Assert
    expect(result).toBe(EXPECTED_OUTPUT)
  })
})
```

### File: templates/vitest-template.ts

```typescript
import { describe, it, expect } from 'vitest'
import { FUNCTION_NAME } from './SOURCE_FILE'

describe('FUNCTION_NAME', () => {
  it('should EXPECTED_BEHAVIOR', () => {
    expect(FUNCTION_NAME(INPUT_VALUE)).toBe(EXPECTED_OUTPUT)
  })
})
```

## Why This Example Works

✅ **Clear Purpose:** Generate unit tests
✅ **Multiple Tools:** Read (source), Write (tests), Grep (find files)
✅ **Template-Based:** Uses templates for consistency
✅ **Framework-Aware:** Adapts to project's test framework
✅ **Best Practices:** AAA pattern, clear naming, good coverage
✅ **Quality Focus:** Standards for test independence and clarity
