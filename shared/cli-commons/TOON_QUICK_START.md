# TOON Parser Quick Start

Get started with TOON (Token-Oriented Object Notation) in 5 minutes.

## Installation

```python
from lucid_cli_commons.toon_parser import parse_toon, to_toon
```

## 1. Parse TOON → Python

```python
toon = """
@type: Action
name: test-action
actionStatus: CompletedActionStatus
x-tokens: 12500
"""

result = parse_toon(toon)
# {'@type': 'Action', 'name': 'test-action', ...}
```

## 2. Python → TOON

```python
data = {
    '@type': 'Action',
    'name': 'test',
    'items': [
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'}
    ]
}

toon = to_toon(data)
```

Output:
```toon
@type: Action
name: test
items[2]{id,name}:
1,Alice
2,Bob
```

## 3. Common Patterns

### Subagent Return Value

```python
# Return this from a subagent to save tokens
result = {
    '@type': 'Action',
    'name': 'search-results',
    'actionStatus': 'CompletedActionStatus',
    'results': [
        {'file': 'auth.py', 'line': 42, 'match': 'def authenticate'},
        {'file': 'session.py', 'line': 15, 'match': 'def create_session'}
    ]
}

return to_toon(result)
```

TOON output (saves ~50% tokens):
```toon
@type: Action
name: search-results
actionStatus: CompletedActionStatus
results[2]{file,line,match}:
auth.py,42,def authenticate
session.py,15,def create_session
```

### Status Report

```python
status = {
    '@type': 'Action',
    'name': 'health-check',
    'actionStatus': 'FailedActionStatus',
    'checks': [
        {'name': 'Database', 'status': 'ok'},
        {'name': 'Cache', 'status': 'ok'},
        {'name': 'API', 'status': 'failed'}
    ],
    'x-passed': 2,
    'x-failed': 1
}

print(to_toon(status))
```

### Validation Results

```python
validation = {
    '@type': 'Action',
    'name': 'schema-validation',
    'actionStatus': 'FailedActionStatus',
    'errors': [
        {'file': 'config.json', 'field': 'timeout', 'error': 'Required field missing'},
        {'file': 'config.json', 'field': 'port', 'error': 'Invalid type'}
    ]
}

print(to_toon(validation))
```

## 4. Syntax Cheat Sheet

| Pattern | TOON Syntax | Python Result |
|---------|-------------|---------------|
| Simple value | `name: test` | `{'name': 'test'}` |
| Number | `count: 42` | `{'count': 42}` |
| Boolean | `active: true` | `{'active': True}` |
| Null | `empty: null` | `{'empty': None}` |
| Inline array | `tags[3]: a,b,c` | `{'tags': ['a', 'b', 'c']}` |
| Tabular array | `items[2]{id,name}:\n1,Alice\n2,Bob` | `{'items': [{'id': 1, 'name': 'Alice'}, ...]}` |
| Tab-delimited | `items[1]{a,b\|tab}:\nv1\tv2` | `{'items': [{'a': 'v1', 'b': 'v2'}]}` |
| Nested object | `config:\n  port: 80` | `{'config': {'port': 80}}` |

## 5. Schema.org Types

Always include `@type` for semantic meaning:

```python
# Action types
'@type': 'Action'           # Generic operation
'@type': 'CreateAction'     # Creating something
'@type': 'UpdateAction'     # Updating something
'@type': 'AnalyzeAction'    # Analysis/classification
'@type': 'AssessAction'     # Assessment/evaluation

# Collection types
'@type': 'ItemList'         # List of items
```

## 6. Action Status

Use standard ActionStatusType values:

```python
'actionStatus': 'PotentialActionStatus'   # Queued, pending
'actionStatus': 'ActiveActionStatus'      # In progress
'actionStatus': 'CompletedActionStatus'   # Successfully done
'actionStatus': 'FailedActionStatus'      # Failed or blocked
```

## 7. Custom Properties

Prefix custom properties with `x-`:

```python
{
    '@type': 'Action',
    'name': 'test',
    'x-maturity': 75,        # ✓ Good: uses x- prefix
    'x-tokens': 12500,       # ✓ Good: uses x- prefix
    'customField': 'value'   # ✗ Warning: should be x-customField
}
```

## 8. Validation

```python
from lucid_cli_commons.toon_parser import validate_toon

data = {
    '@type': 'Action',
    'actionStatus': 'ActiveActionStatus'
}

is_valid, messages = validate_toon(data)
if not is_valid:
    for msg in messages:
        print(msg)
```

## 9. Format Detection

```python
from lucid_cli_commons.toon_parser import detect_format

fmt = detect_format(text)
# Returns: 'toon', 'json', or 'unknown'
```

## 10. JSON Conversion

```python
from lucid_cli_commons.toon_parser import (
    convert_json_to_toon,
    convert_toon_to_json
)

# JSON → TOON (save tokens)
toon = convert_json_to_toon(json_string)

# TOON → JSON (for compatibility)
json_str = convert_toon_to_json(toon_string)
```

## Token Savings

Real example from capability plugin:

| Format | Size | Savings |
|--------|------|---------|
| JSON | 996 chars | baseline |
| TOON | 435 chars | **56.3%** |

## When to Use TOON

✓ **Use TOON for:**
- Subagent return values
- Lists of uniform items
- Status/validation reports
- Cross-plugin data exchange

✗ **Don't use TOON for:**
- Human-facing final output
- Narrative content
- Single values
- Deep nesting (>3 levels)

## Full Example: Subagent Pattern

```python
from lucid_cli_commons.toon_parser import to_toon

def search_capabilities():
    """Subagent that searches and returns capabilities."""
    capabilities = [
        {'name': 'auth', 'maturity': 47, 'status': 'ActiveActionStatus'},
        {'name': 'admin', 'maturity': 100, 'status': 'CompletedActionStatus'}
    ]

    result = {
        '@type': 'ItemList',
        'name': 'capabilities',
        'actionStatus': 'CompletedActionStatus',
        'numberOfItems': len(capabilities),
        'itemListElement': capabilities,
        'x-avgMaturity': sum(c['maturity'] for c in capabilities) / len(capabilities)
    }

    # Return TOON format to save ~50% tokens
    return to_toon(result)
```

## Learn More

- Full documentation: `TOON_PARSER_README.md`
- Examples: `examples/toon_examples.py`
- Integration guide: `shared/TOON_INTEGRATION.md`
- Run tests: `pytest tests/test_toon_parser.py -v`
