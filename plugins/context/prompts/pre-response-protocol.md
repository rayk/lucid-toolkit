# Pre-Response Protocol

Execute this protocol BEFORE responding to any user request that may involve tool calls.

## The 4-Step Protocol

### STEP 0: TRANSITION CHECK

Detect if moving from research to action:

**Research Operations:**
- WebSearch
- WebFetch
- Exploratory Read (browsing, not specific lookup)
- Grep/Glob for discovery

**Action Operations:**
- Write
- Edit
- Bash (especially git commands)
- NotebookEdit

**If transitioning from research → action:**
Output: `[MODE: research → action]`

This is the highest-risk moment for protocol violation. Apply extra scrutiny.

---

### STEP 1: DECOMPOSE COMPOUND REQUESTS

Split requests containing:
- "AND" connectors
- "then" sequences
- Multiple action verbs (fix, add, update, create)

**Example:**
```
"Fix the auth bug AND update the tests"
→ Fix auth bug (3+ ops) + Update tests (2+ ops) = 5+ total
```

Count each component separately before summing.

---

### STEP 2: COUNT OPERATIONS

Use these patterns:

| Request Pattern | Operation Count |
|-----------------|-----------------|
| "Find where X is" | Grep + Read = 2+ minimum |
| "Fix X" | Find + Read + Edit = 3+ minimum |
| "Unknown location" | Assume multiple reads needed |
| "File already in context" | 0 ops to read |
| "Update multiple files" | N × (Read + Edit) |

**Uncertainty Rule:**
Cannot state count with certainty? Write "?"

"?" ALWAYS means delegate.

---

### STEP 3: VERIFY SIMPLICITY

Only if count < 3 with certainty, verify ALL are true:

- [ ] Single known file path (not "find where X is")
- [ ] Operation count certain (not estimated)
- [ ] No exploration/search component
- [ ] Output size predictable and <500 tokens

If ANY is false → delegate.

---

### STEP 4: VISIBLE CHECKPOINT

Before your FIRST tool call, output:

```
[N ops → direct|delegate]: rationale
```

**Examples:**
```
[1 op → direct]: Reading known file path
[2 ops → direct]: Grep + Read, single known location
[3 ops → delegate]: Multi-file exploration needed
[5 ops → delegate]: Compound request, multiple edits
[? ops → delegate]: Unknown scope, need exploration first
```

---

## Quick Reference

### Delegate If ANY Apply
- Location unknown
- Open-ended question
- Multiple files to check
- Synthesis required
- 3+ tool calls
- External operations (web, MCP)
- Unpredictable output size

### Direct ONLY When ALL Apply
- Specific known file path
- Count is exactly 1-2 with certainty
- No exploration needed
- Single known location
