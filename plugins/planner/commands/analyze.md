# /planner:analyze

Analyze design documents without generating an execution prompt.

## Usage

```
/planner:analyze <design-doc-path>
```

## Arguments

- `<design-doc-path>` - Path to the design document(s) to analyze

## Output

Produces an analysis report containing:

### 1. System Identity

- System/module name
- Primary language and version
- Framework(s)
- Target runtime

### 2. Dependency Analysis

**External Libraries**
| Library | Version | Status |
|---------|---------|--------|
| [lib] | [ver] | Installed/Missing |

**Pre-existing Internal**
| Class/Module | Path | Status |
|--------------|------|--------|
| [class] | [path] | Found/Missing |

**Created During Execution**
| Class/Module | Created In | Required By |
|--------------|------------|-------------|
| [class] | Phase N | Phase N+1 |

### 3. Validation Results

- Pre-existing deps: PASS/FAIL
- Unclear deps: PASS/FAIL
- Circular deps: PASS/FAIL

### 4. Execution Estimates

- Total estimated tokens
- Estimated duration
- Model distribution (haiku/sonnet/opus calls)
- Estimated cost

### 5. Exit Criteria

- Explicit criteria found
- Implicit criteria derived

## Example

```
/planner:analyze ./docs/design/auth-service.md
```

## Behavior

When invoked:

1. Read the specified design document(s)
2. Extract all information per the analysis checklist
3. Validate dependencies (but don't fail on missing)
4. Calculate estimates
5. Output formatted analysis report

This command is useful for:
- Understanding what an execution will require
- Identifying missing prerequisites
- Estimating cost before running
- Reviewing design completeness
