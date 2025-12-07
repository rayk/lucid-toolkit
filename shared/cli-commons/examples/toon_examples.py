#!/usr/bin/env python3
"""
TOON Parser Usage Examples

Demonstrates parsing and serialization of TOON format with schema.org integration.
"""

from lucid_cli_commons.toon_parser import (
    parse_toon,
    to_toon,
    validate_toon,
    detect_format,
    convert_json_to_toon,
    convert_toon_to_json,
)
import json


def example_1_simple_parsing():
    """Parse simple TOON format."""
    print("=" * 60)
    print("Example 1: Simple TOON Parsing")
    print("=" * 60)

    toon = """
@type: Action
@id: test-action-123
name: authentication-check
actionStatus: CompletedActionStatus
result: All checks passed
x-duration: 45
x-tokens: 12500
"""

    result = parse_toon(toon)
    print("\nInput TOON:")
    print(toon)
    print("\nParsed result:")
    print(json.dumps(result, indent=2))


def example_2_tabular_arrays():
    """Parse tabular arrays (most efficient for structured data)."""
    print("\n" + "=" * 60)
    print("Example 2: Tabular Arrays")
    print("=" * 60)

    toon = """
@type: ItemList
name: capabilities
numberOfItems: 3

itemListElement[3]{name,x-maturity,x-target,actionStatus}:
authentication-system,47,80,ActiveActionStatus
tenant-isolation,35,90,ActiveActionStatus
admin-portal,100,80,CompletedActionStatus
"""

    result = parse_toon(toon)
    print("\nInput TOON:")
    print(toon)
    print("\nParsed result:")
    print(json.dumps(result, indent=2))


def example_3_tab_delimited():
    """Use tab delimiter for fields containing commas."""
    print("\n" + "=" * 60)
    print("Example 3: Tab-Delimited Arrays")
    print("=" * 60)

    toon = """
@type: ItemList
name: health-check-results

issues[2]{severity,description|tab}:
HIGH\tCircular dependency: auth-system -> user-management -> auth-system
MEDIUM\tStale index for deprecated capability, needs cleanup
"""

    result = parse_toon(toon)
    print("\nInput TOON:")
    print(toon)
    print("\nParsed result:")
    print(json.dumps(result, indent=2))


def example_4_serialization():
    """Serialize Python dict to TOON format."""
    print("\n" + "=" * 60)
    print("Example 4: Python to TOON Serialization")
    print("=" * 60)

    data = {
        '@type': 'CreateAction',
        '@id': 'outcome/005-authentication',
        'name': 'authentication-provider',
        'actionStatus': 'CompletedActionStatus',
        'result': 'Successfully implemented JWT authentication',
        'x-maturity': 75,
        'x-tokens': 48500,
        'steps': [
            {'name': '01-jwt.md', 'status': 'done', 'tokens': 25000},
            {'name': '02-session.md', 'status': 'done', 'tokens': 23500}
        ],
        'tags': ['auth', 'security', 'jwt']
    }

    print("\nInput Python dict:")
    print(json.dumps(data, indent=2))
    print("\nSerialized to TOON:")
    print(to_toon(data))


def example_5_validation():
    """Validate TOON structure."""
    print("\n" + "=" * 60)
    print("Example 5: TOON Validation")
    print("=" * 60)

    # Valid TOON
    valid_data = {
        '@type': 'Action',
        'name': 'test',
        'actionStatus': 'ActiveActionStatus',
        'x-maturity': 50
    }

    is_valid, messages = validate_toon(valid_data)
    print("\nValidating:", json.dumps(valid_data, indent=2))
    print(f"Valid: {is_valid}")
    if messages:
        for msg in messages:
            print(f"  - {msg}")

    # Invalid TOON
    invalid_data = {
        '@type': 'Action',
        'actionStatus': 'InvalidStatus',  # Wrong status
        'customField': 'value'  # Should use x- prefix
    }

    is_valid, messages = validate_toon(invalid_data)
    print("\n\nValidating:", json.dumps(invalid_data, indent=2))
    print(f"Valid: {is_valid}")
    if messages:
        for msg in messages:
            print(f"  - {msg}")


def example_6_format_detection():
    """Detect format of input text."""
    print("\n" + "=" * 60)
    print("Example 6: Format Detection")
    print("=" * 60)

    samples = [
        ('{"@type": "Action", "name": "test"}', 'JSON'),
        ('@type: Action\nname: test', 'TOON'),
        ('items[3]{id,name}:', 'TOON'),
        ('plain text here', 'Unknown')
    ]

    for text, expected in samples:
        detected = detect_format(text)
        print(f"\nText: {text[:50]}")
        print(f"Detected: {detected} (expected: {expected})")


def example_7_json_conversion():
    """Convert between JSON and TOON."""
    print("\n" + "=" * 60)
    print("Example 7: JSON <-> TOON Conversion")
    print("=" * 60)

    json_str = json.dumps({
        '@type': 'Action',
        'name': 'workspace-health',
        'actionStatus': 'CompletedActionStatus',
        'phases': [
            {'name': 'Capability sync', 'status': 'ok'},
            {'name': 'Cross-refs', 'status': 'failed'}
        ]
    }, indent=2)

    print("\nOriginal JSON:")
    print(json_str)

    toon = convert_json_to_toon(json_str)
    print("\nConverted to TOON:")
    print(toon)

    back_to_json = convert_toon_to_json(toon)
    print("\nConverted back to JSON:")
    print(back_to_json)


def example_8_nested_objects():
    """Handle nested objects."""
    print("\n" + "=" * 60)
    print("Example 8: Nested Objects")
    print("=" * 60)

    toon = """
@type: Action
name: session-info

config:
  timeout: 30
  retries: 3
  cache:
    enabled: true
    ttl: 300

stats:
  files: 5
  commits: 2
  tokens: 45000
"""

    result = parse_toon(toon)
    print("\nInput TOON:")
    print(toon)
    print("\nParsed result:")
    print(json.dumps(result, indent=2))


def example_9_subagent_return():
    """Typical subagent return format."""
    print("\n" + "=" * 60)
    print("Example 9: Subagent Return Value")
    print("=" * 60)

    # This is what a subagent might return to the main context
    data = {
        '@type': 'Action',
        'name': 'capability-list.md',
        'actionStatus': 'CompletedActionStatus',
        'result': 'Found 5 capabilities',
        'capabilities': [
            {
                'name': 'auth-system',
                'x-maturity': 47,
                'x-domain': 'Security',
                'actionStatus': 'ActiveActionStatus'
            },
            {
                'name': 'admin-portal',
                'x-maturity': 100,
                'x-domain': 'Product',
                'actionStatus': 'CompletedActionStatus'
            }
        ],
        'x-avgMaturity': 52,
        'x-tokens': 3500
    }

    toon = to_toon(data)
    print("\nSubagent return value (TOON format):")
    print(toon)
    print("\nToken savings vs JSON:")
    json_str = json.dumps(data)
    print(f"  JSON size: ~{len(json_str)} chars")
    print(f"  TOON size: ~{len(toon)} chars")
    print(f"  Savings: ~{100 - (len(toon) / len(json_str) * 100):.1f}%")


def main():
    """Run all examples."""
    example_1_simple_parsing()
    example_2_tabular_arrays()
    example_3_tab_delimited()
    example_4_serialization()
    example_5_validation()
    example_6_format_detection()
    example_7_json_conversion()
    example_8_nested_objects()
    example_9_subagent_return()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == '__main__':
    main()
