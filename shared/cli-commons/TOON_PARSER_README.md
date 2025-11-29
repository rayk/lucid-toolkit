# TOON Parser Module

Python parser and serializer for TOON (Token-Oriented Object Notation) format with schema.org integration.

## Overview

TOON is a token-efficient format designed for structured data exchange with LLMs, achieving 40-55% token savings compared to JSON while maintaining readability and semantic meaning through schema.org vocabulary.

## Features

- **Parse TOON to Python dict**: Handle all TOON syntax patterns
- **Serialize Python dict to TOON**: Automatic format selection for optimal token efficiency
- **Validate TOON structure**: Check schema.org types, ActionStatusType values, and custom property naming
- **Format detection**: Automatically detect TOON, JSON, or unknown formats
- **Bidirectional conversion**: Convert between JSON and TOON formats

## Installation

The TOON parser is part of the `lucid-cli-commons` package:

```bash
cd shared/cli-commons
pip install -e .
```

## Usage

### Basic Parsing

```python
from lucid_cli_commons.toon_parser import parse_toon, to_toon

# Parse TOON string to Python dict
toon = """
@type: Action
name: authentication-check
actionStatus: CompletedActionStatus
x-tokens: 12500
"""

result = parse_toon(toon)
# {'@type': 'Action', 'name': 'authentication-check', ...}
```

### Serialization

```python
# Convert Python dict to TOON
data = {
    '@type': 'CreateAction',
    'name': 'test',
    'items': [
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'}
    ]
}

toon = to_toon(data)
# @type: CreateAction
# name: test
# items[2]{id,name}:
# 1,Alice
# 2,Bob
```

### Validation

```python
from lucid_cli_commons.toon_parser import validate_toon

data = {
    '@type': 'Action',
    'actionStatus': 'ActiveActionStatus',
    'x-maturity': 50
}

is_valid, messages = validate_toon(data)
# (True, [])
```

### Format Detection

```python
from lucid_cli_commons.toon_parser import detect_format

detect_format('{"key": "value"}')  # 'json'
detect_format('@type: Action')     # 'toon'
detect_format('plain text')        # 'unknown'
```

### JSON Conversion

```python
from lucid_cli_commons.toon_parser import convert_json_to_toon, convert_toon_to_json

# JSON -> TOON
json_str = '{"@type": "Action", "name": "test"}'
toon = convert_json_to_toon(json_str)

# TOON -> JSON
toon_str = "@type: Action\nname: test"
json_result = convert_toon_to_json(toon_str)
```

## TOON Syntax Reference

### Simple Values

```toon
name: authentication-service
count: 42
active: true
empty: null
```

### Inline Arrays

```toon
tags[3]: security,auth,core
```

### Tabular Arrays (Comma-Delimited)

```toon
items[3]{id,name,status}:
1,Alice,active
2,Bob,pending
3,Charlie,done
```

### Tabular Arrays (Tab-Delimited)

Use when fields contain commas:

```toon
items[2]{name,description|tab}:
widget-a	Handles authentication, session management
widget-b	Manages user roles, permissions
```

### Nested Objects

```toon
config:
  host: localhost
  port: 8080
  cache:
    enabled: true
    ttl: 300
```

### Schema.org Integration

```toon
@type: CreateAction
@id: outcome/005-authentication
name: authentication-provider
actionStatus: CompletedActionStatus
result: Successfully completed
x-maturity: 75
x-tokens: 48500
```

## API Reference

### `parse_toon(text: str) -> Dict[str, Any]`

Parse TOON format text to Python dictionary.

**Args:**
- `text`: TOON format string

**Returns:**
- Parsed dictionary

**Raises:**
- `ValueError`: If TOON format is malformed

### `to_toon(data: Dict[str, Any], indent: int = 0) -> str`

Convert Python dictionary to TOON format string.

**Args:**
- `data`: Dictionary to serialize
- `indent`: Indentation level (default: 0)

**Returns:**
- TOON format string

### `validate_toon(data: Dict[str, Any]) -> Tuple[bool, List[str]]`

Validate TOON structure for schema.org compatibility.

**Checks:**
- `@type` is valid schema.org type
- `actionStatus` is valid ActionStatusType
- Custom properties use `x-` prefix

**Args:**
- `data`: Dictionary to validate

**Returns:**
- Tuple of (is_valid, list of error/warning messages)

### `detect_format(text: str) -> str`

Detect format of input text.

**Args:**
- `text`: Input text to analyze

**Returns:**
- `'toon'`, `'json'`, or `'unknown'`

### `convert_json_to_toon(json_str: str) -> str`

Convert JSON string to TOON format.

**Args:**
- `json_str`: JSON formatted string

**Returns:**
- TOON formatted string

**Raises:**
- `json.JSONDecodeError`: If input is not valid JSON

### `convert_toon_to_json(toon_str: str, indent: Optional[int] = 2) -> str`

Convert TOON string to JSON format.

**Args:**
- `toon_str`: TOON formatted string
- `indent`: JSON indentation (None for compact)

**Returns:**
- JSON formatted string

**Raises:**
- `ValueError`: If TOON format is malformed

## Schema.org Types

Common types used in Lucid Toolkit:

| Type | Use For |
|------|---------|
| `Action` | Generic operations, validations |
| `CreateAction` | Work producing artifacts |
| `UpdateAction` | State transitions, modifications |
| `AnalyzeAction` | Problem classification, analysis |
| `AssessAction` | Evaluations, verdicts |
| `ItemList` | Collections of items |

## ActionStatusType Values

| Status | Meaning | Lucid Mapping |
|--------|---------|---------------|
| `PotentialActionStatus` | Not started | queued, pending, ready |
| `ActiveActionStatus` | In progress | in-progress, current, active |
| `CompletedActionStatus` | Finished successfully | completed, success |
| `FailedActionStatus` | Did not succeed | failed, blocked |

## Custom Properties (x- prefix)

Use `x-` prefix for domain-specific properties:

| Extension | Purpose | Example |
|-----------|---------|---------|
| `x-maturity` | Capability maturity % | `x-maturity: 47` |
| `x-target` | Target maturity % | `x-target: 80` |
| `x-tokens` | Token count | `x-tokens: 48500` |
| `x-contribution` | Maturity contribution % | `x-contribution: 15` |
| `x-domain` | Capability domain | `x-domain: Security` |

## Examples

See `examples/toon_examples.py` for comprehensive usage examples:

```bash
python examples/toon_examples.py
```

## Testing

Run the test suite:

```bash
pytest tests/test_toon_parser.py -v
```

## Token Savings

TOON achieves significant token savings over JSON:

| Data Type | JSON Tokens | TOON Tokens | Savings |
|-----------|-------------|-------------|---------|
| 10-item list | 3000 | 1800 | 40% |
| 5 capabilities | 2500 | 1250 | 50% |
| Nested config | 2000 | 1200 | 40% |

**Typical savings: 40-55% for structured data exchanges**

## When to Use TOON

**Use TOON for:**
- Subagent return values
- Status displays with tabular data
- Cross-plugin data exchange
- Validation result reporting
- Lists and collections

**Use JSON/Markdown for:**
- Human-facing final output
- Narrative/analytical content
- Single-value responses
- Deeply nested structures (>3 levels)

## Integration with Lucid Toolkit

TOON is used throughout the Lucid Toolkit for efficient data exchange:

- **Capability plugin**: List capabilities, validation results
- **Outcome plugin**: State transitions, completion reports
- **Workspace plugin**: Health checks, validation reports
- **Context plugin**: Session info, budget status
- **Plan plugin**: Phase tracking, cost reports
- **Think plugin**: Classification, assessments

## References

- TOON Integration Guide: `/Users/rayk/Projects/lucid-toolkit/shared/TOON_INTEGRATION.md`
- Schema.org: https://schema.org/
- ActionStatusType: https://schema.org/ActionStatusType
