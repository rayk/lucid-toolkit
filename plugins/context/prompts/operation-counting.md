# Operation Counting Guide

## The Specificity Trap

**Critical Anti-Pattern**: Specific user input creates FALSE confidence.

When user provides exact details (error messages, variable names, paths):
- You know WHAT to search for ✓
- You do NOT know WHERE it is ✗
- You do NOT know HOW MANY locations ✗

**This is EXPLORATION, not LOOKUP.**

### Example

```
User: "I got error 'ConfigError: path /Users/foo/luon not found'"

WRONG thinking:
"I know exactly what to search for, this is simple"

CORRECT thinking:
Grep for 'luon' → unknown locations
Read config → unknown which file
Edit fix → at least one
Total: 3+ operations → DELEGATE
```

**Rule**: Count operations assuming multiple locations until proven otherwise.

---

## Operation Count Patterns

### Search Operations

| Pattern | Count | Reason |
|---------|-------|--------|
| Grep for pattern | 1+ | May return multiple files |
| Glob for files | 1 | Single operation |
| Read search results | N | One per file found |

### Read Operations

| Pattern | Count | Reason |
|---------|-------|--------|
| Known file path | 1 | Direct read |
| "Find and read" | 2+ | Grep + Read |
| Multiple files | N | One per file |
| File in context | 0 | Already loaded |

### Write Operations

| Pattern | Count | Reason |
|---------|-------|--------|
| Edit single file | 1 | Single edit |
| Create new file | 1 | Single write |
| Multiple edits | N | One per file |
| Edit + related | 2+ | Primary + imports/tests |

### Compound Operations

| Pattern | Count | Reason |
|---------|-------|--------|
| Fix bug | 3+ | Find + Read + Edit |
| Add feature | 4+ | Read + Write + Test + Docs |
| Refactor | 5+ | Multiple reads + edits |
| Update config | 2+ | Read + Edit (often multiple) |

---

## Counting Rules

### Rule 1: Uncertainty Means Delegate
```
Can you state the exact count?
YES → Continue to verify
NO → "?" → Delegate
```

### Rule 2: "Find" Means Multiple
```
"Find where X is configured"
= Grep (unknown results) + Read (unknown count)
= 2+ minimum → Delegate
```

### Rule 3: Compounds Add Up
```
"Fix X and update Y"
= Fix X (3+) + Update Y (2+)
= 5+ total → Delegate
```

### Rule 4: Related Files Count
```
"Update the auth handler"
= Read handler + Read tests + Edit handler + Edit tests
= 4 operations → Delegate
```

### Rule 5: Context Reduces Count
```
File already read this session?
= 0 operations to read again
(But still count edits)
```

---

## Decision Tree

```
Is the exact file path known?
├─ NO → "?" → Delegate
└─ YES → Is it a single file?
         ├─ NO → Count all files → Likely 3+ → Delegate
         └─ YES → Is operation count ≤ 2?
                  ├─ NO → Delegate
                  └─ YES → Verify simplicity → Execute directly
```

---

## Examples

### Example 1: Lookup (Direct)
```
User: "What's in /src/config.json?"
Count: 1 (known path, single read)
→ [1 op → direct]: Known file path
```

### Example 2: Search (Delegate)
```
User: "Where is the database connection configured?"
Count: Grep + Read(s) = 2+ minimum
→ [2+ ops → delegate]: Unknown location
```

### Example 3: Fix (Delegate)
```
User: "Fix the login timeout error"
Count: Grep + Read(s) + Edit(s) = 3+ minimum
→ [3+ ops → delegate]: Bug fix requires exploration
```

### Example 4: Compound (Delegate)
```
User: "Update the API version and regenerate the docs"
Count: (Read + Edit) + (Bash for docs) = 3+ minimum
→ [3+ ops → delegate]: Compound request
```

### Example 5: Context Reduces (May be Direct)
```
User: "Change the timeout from 30 to 60"
(File config.json already in context)
Count: 0 (read) + 1 (edit) = 1
→ [1 op → direct]: File in context, single edit
```
