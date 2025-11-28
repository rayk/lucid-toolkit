# Example: Documentation Generator Skill

This example shows a skill that generates documentation from code.

## File: skills/doc-generator/SKILL.md

```yaml
---
name: doc-generator
description: Generates comprehensive documentation from code files including API docs, README sections, and inline documentation. Use when user asks to document code, create docs, generate API documentation, or write README content. Works with TypeScript, JavaScript, Python, and more.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# Documentation Generator

Automatically generates high-quality documentation from source code.

## When to Use

- User asks: "document this code"
- User asks: "generate API documentation"
- User asks: "create README for this"
- User mentions: "add documentation"

## Documentation Types

### 1. Inline Documentation
Add JSDoc/docstrings to functions/classes

### 2. API Documentation
Generate reference docs for public APIs

### 3. README Documentation
Create usage guides and examples

### 4. Architecture Documentation
Document system design and structure

## Instructions

### Phase 1: Analyze Code

1. **Identify Files**
   - User-specified files, or
   - Use Glob to find all source files
   - Prioritize exported/public APIs

2. **Parse Structure**
   - Functions and their signatures
   - Classes and methods
   - Exported constants/types
   - Dependencies and relationships

3. **Extract Context**
   - Parameter types and purposes
   - Return types
   - Error conditions
   - Usage patterns from tests

### Phase 2: Generate Documentation

4. **Choose Format**
   Based on request:
   - Inline: JSDoc/docstrings in source files
   - API: Markdown reference files
   - README: Usage guide with examples
   - Architecture: High-level design doc

5. **Create Content**

**For Inline Documentation:**
```typescript
/**
 * Calculates the total sum of an array of numbers.
 *
 * @param items - Array of numbers to sum
 * @returns The total sum of all numbers
 * @throws {TypeError} If items is not an array
 *
 * @example
 * ```typescript
 * calculateTotal([1, 2, 3]) // Returns 6
 * ```
 */
export function calculateTotal(items: number[]): number {
  return items.reduce((sum, item) => sum + item, 0)
}
```

**For API Documentation (Markdown):**
```markdown
# API Reference

## Functions

### `calculateTotal(items: number[]): number`

Calculates the total sum of an array of numbers.

**Parameters:**
- `items` (number[]): Array of numbers to sum

**Returns:**
- `number`: The total sum of all numbers

**Throws:**
- `TypeError`: If items is not an array

**Example:**
```typescript
import { calculateTotal } from './calculator'

const total = calculateTotal([1, 2, 3])
console.log(total) // 6
```

**For README Documentation:**
```markdown
# Project Name

Brief description of what this project does.

## Installation

```bash
npm install package-name
```

## Quick Start

```typescript
import { functionName } from 'package-name'

// Basic usage
const result = functionName(params)
```

## API

See [API.md](./API.md) for complete API reference.

## Examples

### Example 1: Basic Usage
[Code example]

### Example 2: Advanced Usage
[Code example]

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)

## License

MIT
```

### Phase 3: Write Documentation

6. **Create/Update Files**
   - For inline: Use Edit to add docs to source
   - For markdown: Use Write to create .md files
   - Organize in docs/ directory structure

7. **Verify Quality**
   - All public APIs documented
   - Examples are executable
   - No broken references
   - Consistent formatting

## Documentation Standards

### JSDoc/Docstrings Must Include:
- Brief description (one line)
- Parameter descriptions with types
- Return value description
- Error conditions (throws)
- At least one usage example

### Markdown Docs Must Include:
- Clear headings hierarchy
- Code examples with syntax highlighting
- Links to related documentation
- Table of contents for long docs

### Examples Must:
- Be executable/testable
- Show realistic use cases
- Include expected output
- Cover common scenarios

## Output Structure

```
docs/
├── API.md                 # Complete API reference
├── guides/
│   ├── getting-started.md # Quick start guide
│   ├── advanced.md        # Advanced usage
│   └── examples.md        # Code examples
├── architecture/
│   ├── overview.md        # System design
│   └── decisions.md       # Architecture decisions
└── contributing.md        # Contribution guide
```

## Report Format

```
✅ Documentation Generated

Files Created/Updated:
- src/calculator.ts (added JSDoc to 3 functions)
- docs/API.md (created)
- README.md (updated Quick Start section)

Coverage:
- 15 functions documented
- 23 code examples added
- 0 undocumented public APIs

Preview: docs/API.md
```

## Examples

### Example 1: Generate Inline Docs

**User:** "Add documentation to this function"

**Before:**
```typescript
export function processUser(data) {
  return {
    id: data.id,
    name: `${data.firstName} ${data.lastName}`,
    email: data.email.toLowerCase()
  }
}
```

**After:**
```typescript
/**
 * Processes raw user data into a standardized user object.
 *
 * Combines first and last names into full name and normalizes
 * email to lowercase.
 *
 * @param data - Raw user data from API
 * @param data.id - Unique user identifier
 * @param data.firstName - User's first name
 * @param data.lastName - User's last name
 * @param data.email - User's email address
 * @returns Processed user object
 *
 * @example
 * ```typescript
 * const raw = {
 *   id: 123,
 *   firstName: 'John',
 *   lastName: 'Doe',
 *   email: 'JOHN@EXAMPLE.COM'
 * }
 * const user = processUser(raw)
 * // Returns: { id: 123, name: 'John Doe', email: 'john@example.com' }
 * ```
 */
export function processUser(data: RawUserData): ProcessedUser {
  return {
    id: data.id,
    name: `${data.firstName} ${data.lastName}`,
    email: data.email.toLowerCase()
  }
}
```

### Example 2: Generate API Docs

**User:** "Create API documentation for the auth module"

**Generated: docs/api/auth.md**
```markdown
# Authentication API

## Functions

### `login(credentials: Credentials): Promise<AuthResult>`
[Full documentation...]

### `logout(): Promise<void>`
[Full documentation...]

### `refreshToken(token: string): Promise<string>`
[Full documentation...]

## Types

### `Credentials`
[Type documentation...]

### `AuthResult`
[Type documentation...]
```

## Why This Example Works

✅ **Multiple Use Cases:** Inline docs, API docs, README docs
✅ **Smart Analysis:** Extracts info from code structure
✅ **Quality Standards:** Enforces documentation best practices
✅ **Flexible Output:** Adapts to user's needs
✅ **Complete Examples:** All examples are executable
✅ **Professional:** Follows industry documentation standards
