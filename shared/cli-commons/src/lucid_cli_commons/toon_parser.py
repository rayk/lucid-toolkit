"""
TOON (Token-Oriented Object Notation) parser and serializer.

Provides utilities for parsing TOON format to Python dictionaries,
serializing Python dictionaries to TOON format, and validating
TOON structure with schema.org integration.
"""
import re
import json
from typing import Dict, Any, List, Tuple, Optional, Union


# Valid schema.org ActionStatusType values
VALID_ACTION_STATUS = {
    "PotentialActionStatus",
    "ActiveActionStatus",
    "CompletedActionStatus",
    "FailedActionStatus"
}

# Common schema.org types used in Lucid Toolkit
COMMON_SCHEMA_TYPES = {
    "Action", "CreateAction", "UpdateAction", "DeleteAction",
    "AnalyzeAction", "ChooseAction", "AssessAction",
    "ItemList", "HowToStep", "Project", "Intangible"
}


def detect_format(text: str) -> str:
    """
    Detect the format of the input text.

    Args:
        text: Input text to analyze

    Returns:
        'toon', 'json', or 'unknown'

    Examples:
        >>> detect_format("@type: Action\\nname: test")
        'toon'
        >>> detect_format('{"key": "value"}')
        'json'
        >>> detect_format("plain text")
        'unknown'
    """
    if not text or not text.strip():
        return 'unknown'

    text = text.strip()

    # Try JSON first
    if text.startswith('{') or text.startswith('['):
        try:
            json.loads(text)
            return 'json'
        except (json.JSONDecodeError, ValueError):
            pass

    # Check for TOON markers
    toon_patterns = [
        r'@type:\s*\w+',           # @type: Something
        r'@id:\s*\S+',             # @id: something
        r'\w+\[\d+\](\{[^}]+\})?:', # array[N]{fields}:
        r'actionStatus:\s*\w+ActionStatus',  # actionStatus: ...ActionStatus
    ]

    for pattern in toon_patterns:
        if re.search(pattern, text):
            return 'toon'

    return 'unknown'


def _unquote(value: str) -> str:
    """Remove quotes from a quoted string."""
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        # Unescape internal quotes
        return value[1:-1].replace('\\"', '"').replace('\\\\', '\\')
    return value


def _quote(value: str, delimiter: str = ',') -> str:
    """
    Quote a string if it contains special characters.

    Args:
        value: String to potentially quote
        delimiter: The delimiter being used (comma or tab)

    Returns:
        Quoted string if needed, otherwise original
    """
    if not isinstance(value, str):
        return str(value)

    # Check if quoting is needed
    needs_quote = (
        not value or  # Empty string
        value != value.strip() or  # Leading/trailing whitespace
        value in ('true', 'false', 'null') or  # Reserved words
        ':' in value or
        '"' in value or
        '\\' in value or
        '{' in value or '}' in value or
        '[' in value or ']' in value or
        delimiter in value or
        (value.startswith('-') and len(value) > 1 and value[1].isalpha())
    )

    if needs_quote:
        # Escape internal quotes and backslashes
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'

    return value


def _parse_value(value: str) -> Any:
    """
    Parse a TOON value to Python type.

    Args:
        value: String value to parse

    Returns:
        Parsed value (str, int, float, bool, or None)
    """
    value = value.strip()

    # Handle quoted strings
    if value.startswith('"') and value.endswith('"'):
        return _unquote(value)

    # Handle null
    if value == 'null' or value == '-':
        return None

    # Handle booleans
    if value == 'true':
        return True
    if value == 'false':
        return False

    # Try number
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _parse_inline_array(value: str) -> List[Any]:
    """
    Parse inline array format: tags[3]: a,b,c

    Args:
        value: Comma-separated values

    Returns:
        List of parsed values
    """
    if not value.strip():
        return []

    # Simple CSV parsing (handles quoted values)
    items = []
    current = []
    in_quotes = False

    for char in value:
        if char == '"' and (not current or current[-1] != '\\'):
            in_quotes = not in_quotes
            current.append(char)
        elif char == ',' and not in_quotes:
            items.append(''.join(current).strip())
            current = []
        else:
            current.append(char)

    if current:
        items.append(''.join(current).strip())

    return [_parse_value(item) for item in items]


def _parse_tabular_array(lines: List[str], fields: List[str], delimiter: str = ',') -> List[Dict[str, Any]]:
    """
    Parse tabular array format.

    Args:
        lines: Data rows
        fields: Field names
        delimiter: ',' or '\t'

    Returns:
        List of dictionaries
    """
    result = []

    for line in lines:
        if not line.strip():
            continue

        # Parse row based on delimiter
        if delimiter == '\t':
            values = line.split('\t')
        else:
            # CSV parsing with quote handling
            values = []
            current = []
            in_quotes = False

            for char in line:
                if char == '"' and (not current or current[-1] != '\\'):
                    in_quotes = not in_quotes
                    current.append(char)
                elif char == ',' and not in_quotes:
                    values.append(''.join(current).strip())
                    current = []
                else:
                    current.append(char)

            if current:
                values.append(''.join(current).strip())

        # Match fields to values
        row = {}
        for i, field in enumerate(fields):
            if i < len(values):
                row[field] = _parse_value(values[i])
            else:
                row[field] = None

        result.append(row)

    return result


def parse_toon(text: str) -> Dict[str, Any]:
    """
    Parse TOON format text to Python dictionary.

    Handles:
    - Simple key: value pairs
    - Inline arrays: tags[3]: a,b,c
    - Tabular arrays: items[3]{name,status}:\\nrow1,val1\\nrow2,val2
    - Tab-delimited arrays (when |tab specified)
    - Nested objects (indentation-based)

    Args:
        text: TOON format text

    Returns:
        Parsed dictionary

    Raises:
        ValueError: If TOON format is malformed

    Examples:
        >>> parse_toon("@type: Action\\nname: test")
        {'@type': 'Action', 'name': 'test'}

        >>> parse_toon("tags[2]: a,b")
        {'tags': ['a', 'b']}

        >>> parse_toon("items[2]{id,name}:\\n1,Alice\\n2,Bob")
        {'items': [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]}
    """
    if not text or not text.strip():
        return {}

    result = {}
    lines = text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            i += 1
            continue

        # Check for array declaration (with or without count)
        # Pattern 1: key[N]{fields|delimiter}: or key[N]: or key[N]{fields}:
        # Pattern 2: key{fields|delimiter}: (without count)
        # Keys can contain hyphens and dots (e.g., x-tokens, outcomes.summary)
        array_match = re.match(r'^(\s*)([\w.-]+)\[(\d+)\](?:\{([^}|]+)(?:\|(\w+))?\})?:\s*(.*)$', line)

        # Try pattern without count if first pattern didn't match
        count = None  # Initialize count
        if not array_match:
            array_match_no_count = re.match(r'^(\s*)([\w.-]+)\{([^}|]+)(?:\|(\w+))?\}:\s*(.*)$', line)
            if array_match_no_count:
                indent, key, fields_str, delimiter_hint, inline_value = array_match_no_count.groups()
                indent_level = len(indent)
                count = None
                # Set array_match to truthy value so the if block below executes
                array_match = array_match_no_count
        else:
            # Pattern with count matched
            indent, key, count, fields_str, delimiter_hint, inline_value = array_match.groups()
            indent_level = len(indent)

        if array_match:

            # Inline array
            if inline_value.strip():
                result[key] = _parse_inline_array(inline_value)
                i += 1
                continue

            # Tabular array
            if fields_str:
                fields = [f.strip() for f in fields_str.split(',')]
                delimiter = '\t' if delimiter_hint == 'tab' else ','

                # Collect data rows
                data_lines = []
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    # Skip empty lines
                    if not next_line.strip():
                        i += 1
                        continue

                    # Check if this line is a new declaration (contains : but not part of data)
                    # A data row should not match key: value or key[N]: patterns
                    # Keys can contain hyphens, dots, @ (e.g., x-tokens, outcomes.summary, @type, workspace@type)
                    if re.match(r'^\s*[@\w.-]+(\[\d+\])?(\{[^}]+\})?(\|\w+)?:\s*', next_line):
                        # This is a new declaration, stop collecting data
                        break

                    # Check if still properly indented (at same level or slightly indented)
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent == indent_level or (next_indent == 0 and not next_line.startswith(' ')):
                        # Data row (no indentation or same level)
                        data_lines.append(next_line.strip())
                        i += 1
                    else:
                        # Different indentation, stop
                        break

                result[key] = _parse_tabular_array(data_lines, fields, delimiter)
                continue

            # Empty array
            result[key] = []
            i += 1
            continue

        # Check for nested object
        # Keys can contain hyphens and dots (e.g., x-config, workspace.info)
        obj_match = re.match(r'^(\s*)([\w.-]+):\s*$', line)
        if obj_match:
            indent, key = obj_match.groups()
            indent_level = len(indent)

            # Collect nested lines
            nested_lines = []
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if not next_line.strip():
                    i += 1
                    continue
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent > indent_level:
                    # Remove the extra indentation
                    nested_lines.append(next_line[indent_level + 2:])
                    i += 1
                else:
                    break

            # Parse nested content recursively
            if nested_lines:
                result[key] = parse_toon('\n'.join(nested_lines))
            else:
                result[key] = {}
            continue

        # Simple key: value
        # Keys can contain hyphens, dots (e.g., x-tokens, @type, @id, workspace.name)
        kv_match = re.match(r'^(\s*)([@\w.-]+):\s*(.*)$', line)
        if kv_match:
            indent, key, value = kv_match.groups()
            key = key.strip()
            result[key] = _parse_value(value)
            i += 1
            continue

        # Unrecognized format
        i += 1

    return result


def to_toon(data: Dict[str, Any], indent: int = 0) -> str:
    """
    Convert Python dictionary to TOON format.

    Generates:
    - @type, @id, name, actionStatus lines (if present)
    - Tabular arrays for lists of dicts with uniform keys
    - Inline arrays for simple lists
    - Nested objects with indentation

    Args:
        data: Dictionary to serialize
        indent: Current indentation level (for recursion)

    Returns:
        TOON format string

    Examples:
        >>> to_toon({'@type': 'Action', 'name': 'test'})
        '@type: Action\\nname: test'

        >>> to_toon({'tags': ['a', 'b']})
        'tags[2]: a,b'

        >>> to_toon({'items': [{'id': 1, 'name': 'Alice'}]})
        'items[1]{id,name}:\\n1,Alice'
    """
    lines = []
    indent_str = ' ' * indent

    # Priority keys (output first)
    priority_keys = ['@type', '@id', 'name', 'description', 'actionStatus',
                     'startTime', 'endTime', 'result', 'error']

    # Sort keys: priority first, then alphabetical
    def key_sort(k):
        if k in priority_keys:
            return (0, priority_keys.index(k))
        return (1, k)

    sorted_keys = sorted(data.keys(), key=key_sort)

    for key in sorted_keys:
        value = data[key]

        # Handle None
        if value is None:
            lines.append(f"{indent_str}{key}: null")
            continue

        # Handle lists
        if isinstance(value, list):
            if not value:
                lines.append(f"{indent_str}{key}[0]:")
                continue

            # Check if all items are dicts with same keys (tabular)
            if all(isinstance(item, dict) for item in value):
                # Get all unique keys preserving order
                all_keys = []
                for item in value:
                    for k in item.keys():
                        if k not in all_keys:
                            all_keys.append(k)

                if all_keys:
                    # Determine if we should use tab delimiter
                    # (use tab if any field might contain commas)
                    use_tab = any(
                        ',' in str(item.get(k, ''))
                        for item in value
                        for k in all_keys
                    )

                    delimiter = '\t' if use_tab else ','
                    delimiter_hint = '|tab' if use_tab else ''

                    # Generate header
                    fields_str = ','.join(all_keys)
                    lines.append(f"{indent_str}{key}[{len(value)}]{{{fields_str}}}{delimiter_hint}:")

                    # Generate rows
                    for item in value:
                        row_values = [
                            _quote(str(item.get(k, '-')), delimiter)
                            for k in all_keys
                        ]
                        lines.append(f"{indent_str}{delimiter.join(row_values)}")
                else:
                    lines.append(f"{indent_str}{key}[{len(value)}]:")
                continue

            # Inline array for primitives
            if all(not isinstance(item, (dict, list)) for item in value):
                value_strs = [_quote(str(v), ',') for v in value]
                lines.append(f"{indent_str}{key}[{len(value)}]: {','.join(value_strs)}")
                continue

            # Mixed array (fall back to verbose format)
            lines.append(f"{indent_str}{key}[{len(value)}]:")
            for item in value:
                if isinstance(item, dict):
                    nested = to_toon(item, indent + 2)
                    for line in nested.split('\n'):
                        lines.append(f"{indent_str}  {line}")
                else:
                    lines.append(f"{indent_str}  - {_quote(str(item), ',')}")
            continue

        # Handle nested objects
        if isinstance(value, dict):
            lines.append(f"{indent_str}{key}:")
            nested = to_toon(value, indent + 2)
            lines.append(nested)
            continue

        # Handle primitives
        if isinstance(value, bool):
            lines.append(f"{indent_str}{key}: {'true' if value else 'false'}")
        elif isinstance(value, (int, float)):
            lines.append(f"{indent_str}{key}: {value}")
        else:
            lines.append(f"{indent_str}{key}: {_quote(str(value), ',')}")

    return '\n'.join(lines)


def validate_toon(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate TOON structure for schema.org compatibility.

    Checks:
    - @type is valid schema.org type (warns if not in common set)
    - actionStatus is valid ActionStatusType
    - Custom properties use x- prefix

    Args:
        data: Dictionary to validate

    Returns:
        Tuple of (is_valid, list of error/warning messages)

    Examples:
        >>> validate_toon({'@type': 'Action', 'actionStatus': 'ActiveActionStatus'})
        (True, [])

        >>> validate_toon({'@type': 'Action', 'actionStatus': 'Invalid'})
        (False, ['actionStatus must be a valid ActionStatusType: ...'])

        >>> validate_toon({'@type': 'Action', 'customField': 'value'})
        (True, ['Warning: Custom property "customField" should use x- prefix'])
    """
    errors = []
    warnings = []

    # Check @type
    if '@type' in data:
        type_val = data['@type']
        if not isinstance(type_val, str):
            errors.append(f'@type must be a string, got {type(type_val).__name__}')
        elif type_val not in COMMON_SCHEMA_TYPES:
            warnings.append(
                f'Warning: @type "{type_val}" not in common schema.org types. '
                f'Verify it exists at https://schema.org/{type_val}'
            )

    # Check actionStatus
    if 'actionStatus' in data:
        status = data['actionStatus']
        if not isinstance(status, str):
            errors.append(f'actionStatus must be a string, got {type(status).__name__}')
        elif status not in VALID_ACTION_STATUS:
            errors.append(
                f'actionStatus must be a valid ActionStatusType: '
                f'{", ".join(sorted(VALID_ACTION_STATUS))}'
            )

    # Check custom properties
    # Common schema.org properties that we know about
    standard_properties = {
        '@type', '@id', '@context',
        'name', 'description', 'actionStatus',
        'startTime', 'endTime', 'result', 'error',
        'agent', 'object', 'instrument', 'location',
        'numberOfItems', 'itemListElement', 'position',
        # Common schema.org array/list properties
        'step', 'steps', 'phase', 'phases', 'items',
        'findings', 'results', 'check', 'issues',
        'tags', 'config', 'summary', 'breakdown',
        'stats', 'health', 'delta', 'accomplishments',
        'decisions', 'nextSteps', 'classification',
        'selection', 'verdict', 'finding', 'signals',
        'assumptions', 'missingConstraints', 'blackBoxes',
        'children', 'transitions', 'maturity', 'errors',
        'warnings', 'chain', 'filesCreated', 'crossRefsUpdated',
        'itemListElement', 'model', 'external', 'preExisting',
        'created', 'completed', 'pending', 'schemaResults',
        'brokenRefs', 'entryPoints'
    }

    for key in data.keys():
        if key not in standard_properties and not key.startswith('x-'):
            # Warn about potential custom properties
            # But only if they look suspicious (not following schema.org naming)
            warnings.append(
                f'Warning: Custom property "{key}" should use x- prefix '
                f'(e.g., "x-{key}") unless it\'s a standard schema.org property'
            )

    is_valid = len(errors) == 0
    messages = errors + warnings

    return is_valid, messages


def convert_json_to_toon(json_str: str) -> str:
    """
    Convert JSON string to TOON format.

    Args:
        json_str: JSON formatted string

    Returns:
        TOON formatted string

    Raises:
        json.JSONDecodeError: If input is not valid JSON
    """
    data = json.loads(json_str)
    return to_toon(data)


def convert_toon_to_json(toon_str: str, indent: Optional[int] = 2) -> str:
    """
    Convert TOON string to JSON format.

    Args:
        toon_str: TOON formatted string
        indent: JSON indentation (None for compact)

    Returns:
        JSON formatted string

    Raises:
        ValueError: If TOON format is malformed
    """
    data = parse_toon(toon_str)
    return json.dumps(data, indent=indent)
