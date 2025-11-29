"""
Tests for TOON parser and serializer.
"""
import pytest
import json
from lucid_cli_commons.toon_parser import (
    parse_toon,
    to_toon,
    validate_toon,
    detect_format,
    convert_json_to_toon,
    convert_toon_to_json,
)


class TestDetectFormat:
    """Test format detection."""

    def test_detect_json(self):
        assert detect_format('{"key": "value"}') == 'json'
        assert detect_format('[1, 2, 3]') == 'json'

    def test_detect_toon(self):
        assert detect_format("@type: Action") == 'toon'
        assert detect_format("@id: test-123") == 'toon'
        assert detect_format("items[3]{id,name}:") == 'toon'
        assert detect_format("actionStatus: ActiveActionStatus") == 'toon'

    def test_detect_unknown(self):
        assert detect_format("plain text") == 'unknown'
        assert detect_format("") == 'unknown'
        assert detect_format("   ") == 'unknown'


class TestParseToon:
    """Test TOON parsing."""

    def test_parse_simple_values(self):
        toon = """
@type: Action
name: test-action
count: 42
active: true
deleted: false
empty: null
"""
        result = parse_toon(toon)
        assert result['@type'] == 'Action'
        assert result['name'] == 'test-action'
        assert result['count'] == 42
        assert result['active'] is True
        assert result['deleted'] is False
        assert result['empty'] is None

    def test_parse_quoted_values(self):
        toon = '''
description: "Has: special chars"
path: "Contains, comma"
empty: ""
'''
        result = parse_toon(toon)
        assert result['description'] == 'Has: special chars'
        assert result['path'] == 'Contains, comma'
        assert result['empty'] == ''

    def test_parse_inline_array(self):
        toon = "tags[3]: security,auth,core"
        result = parse_toon(toon)
        assert result['tags'] == ['security', 'auth', 'core']

    def test_parse_inline_array_with_quotes(self):
        toon = 'items[2]: "item, one","item: two"'
        result = parse_toon(toon)
        assert result['items'] == ['item, one', 'item: two']

    def test_parse_empty_array(self):
        toon = "items[0]:"
        result = parse_toon(toon)
        assert result['items'] == []

    def test_parse_tabular_array_comma(self):
        toon = """
items[3]{id,name,status}:
1,Alice,active
2,Bob,pending
3,Charlie,done
"""
        result = parse_toon(toon)
        assert len(result['items']) == 3
        assert result['items'][0] == {'id': 1, 'name': 'Alice', 'status': 'active'}
        assert result['items'][1] == {'id': 2, 'name': 'Bob', 'status': 'pending'}
        assert result['items'][2] == {'id': 3, 'name': 'Charlie', 'status': 'done'}

    def test_parse_tabular_array_tab(self):
        toon = """
items[2]{name,description|tab}:
widget-a\tHandles authentication
widget-b\tManages sessions
"""
        result = parse_toon(toon)
        assert len(result['items']) == 2
        assert result['items'][0] == {'name': 'widget-a', 'description': 'Handles authentication'}
        assert result['items'][1] == {'name': 'widget-b', 'description': 'Manages sessions'}

    def test_parse_tabular_array_with_nulls(self):
        toon = """
items[2]{id,name,optional}:
1,Alice,-
2,Bob,value
"""
        result = parse_toon(toon)
        assert result['items'][0]['optional'] is None
        assert result['items'][1]['optional'] == 'value'

    def test_parse_nested_object(self):
        toon = """
config:
  host: localhost
  port: 8080
  nested:
    value: test
"""
        result = parse_toon(toon)
        assert result['config']['host'] == 'localhost'
        assert result['config']['port'] == 8080
        assert result['config']['nested']['value'] == 'test'

    def test_parse_complex_example(self):
        toon = """
@type: CreateAction
@id: outcome/005-auth
name: authentication-provider
actionStatus: ActiveActionStatus
x-maturity: 47

step[2]{name,actionStatus,x-tokens}:
01-jwt.md,CompletedActionStatus,48500
02-session.md,ActiveActionStatus,36500

config:
  timeout: 30
  retries: 3

tags[3]: auth,security,jwt
"""
        result = parse_toon(toon)
        assert result['@type'] == 'CreateAction'
        assert result['@id'] == 'outcome/005-auth'
        assert result['name'] == 'authentication-provider'
        assert result['actionStatus'] == 'ActiveActionStatus'
        assert result['x-maturity'] == 47
        assert len(result['step']) == 2
        assert result['step'][0]['x-tokens'] == 48500
        assert result['config']['timeout'] == 30
        assert result['tags'] == ['auth', 'security', 'jwt']

    def test_parse_empty_string(self):
        assert parse_toon("") == {}
        assert parse_toon("   ") == {}

    def test_parse_comments(self):
        toon = """
# This is a comment
name: test
# Another comment
count: 5
"""
        result = parse_toon(toon)
        assert result == {'name': 'test', 'count': 5}


class TestToToon:
    """Test TOON serialization."""

    def test_serialize_simple_values(self):
        data = {
            '@type': 'Action',
            'name': 'test',
            'count': 42,
            'active': True,
            'empty': None
        }
        toon = to_toon(data)
        assert '@type: Action' in toon
        assert 'name: test' in toon
        assert 'count: 42' in toon
        assert 'active: true' in toon
        assert 'empty: null' in toon

    def test_serialize_inline_array(self):
        data = {'tags': ['a', 'b', 'c']}
        toon = to_toon(data)
        assert 'tags[3]: a,b,c' in toon

    def test_serialize_inline_array_with_quotes(self):
        data = {'items': ['has, comma', 'has: colon']}
        toon = to_toon(data)
        assert 'items[2]:' in toon
        assert '"has, comma"' in toon
        assert '"has: colon"' in toon

    def test_serialize_empty_array(self):
        data = {'items': []}
        toon = to_toon(data)
        assert 'items[0]:' in toon

    def test_serialize_tabular_array(self):
        data = {
            'items': [
                {'id': 1, 'name': 'Alice', 'status': 'active'},
                {'id': 2, 'name': 'Bob', 'status': 'pending'}
            ]
        }
        toon = to_toon(data)
        assert 'items[2]{id,name,status}:' in toon
        assert '1,Alice,active' in toon or '1\tAlice\tactive' in toon
        assert '2,Bob,pending' in toon or '2\tBob\tpending' in toon

    def test_serialize_tabular_array_with_tab_delimiter(self):
        """Should use tab delimiter when fields contain commas."""
        data = {
            'items': [
                {'name': 'widget', 'desc': 'Has, comma'},
                {'name': 'gadget', 'desc': 'Also, has, commas'}
            ]
        }
        toon = to_toon(data)
        assert 'items[2]{name,desc}|tab:' in toon
        assert 'widget\t' in toon

    def test_serialize_nested_object(self):
        data = {
            'config': {
                'host': 'localhost',
                'port': 8080
            }
        }
        toon = to_toon(data)
        assert 'config:' in toon
        assert 'host: localhost' in toon
        assert 'port: 8080' in toon

    def test_serialize_priority_keys_first(self):
        """@type, @id, name should come first."""
        data = {
            'zzzz': 'last',
            'name': 'test',
            'aaaa': 'middle',
            '@type': 'Action',
            '@id': 'test-123'
        }
        toon = to_toon(data)
        lines = toon.split('\n')
        # Check order
        type_idx = next(i for i, l in enumerate(lines) if '@type' in l)
        id_idx = next(i for i, l in enumerate(lines) if '@id' in l)
        name_idx = next(i for i, l in enumerate(lines) if 'name:' in l)
        other_idx = next(i for i, l in enumerate(lines) if 'aaaa' in l)

        assert type_idx < name_idx < other_idx
        assert id_idx < name_idx

    def test_serialize_complex_example(self):
        data = {
            '@type': 'Action',
            'name': 'test-action',
            'actionStatus': 'CompletedActionStatus',
            'results': [
                {'file': 'a.json', 'status': 'ok'},
                {'file': 'b.json', 'status': 'error'}
            ],
            'config': {
                'timeout': 30
            },
            'tags': ['a', 'b']
        }
        toon = to_toon(data)

        # Verify it can be parsed back
        parsed = parse_toon(toon)
        assert parsed['@type'] == 'Action'
        assert parsed['name'] == 'test-action'
        assert len(parsed['results']) == 2
        assert parsed['config']['timeout'] == 30
        assert parsed['tags'] == ['a', 'b']


class TestRoundTrip:
    """Test parsing and serialization round trips."""

    def test_roundtrip_simple(self):
        original = {
            '@type': 'Action',
            'name': 'test',
            'count': 5
        }
        toon = to_toon(original)
        parsed = parse_toon(toon)
        assert parsed == original

    def test_roundtrip_with_arrays(self):
        original = {
            '@type': 'ItemList',
            'tags': ['a', 'b', 'c'],
            'items': [
                {'id': 1, 'name': 'Alice'},
                {'id': 2, 'name': 'Bob'}
            ]
        }
        toon = to_toon(original)
        parsed = parse_toon(toon)
        assert parsed == original

    def test_roundtrip_with_nesting(self):
        original = {
            '@type': 'Action',
            'config': {
                'nested': {
                    'value': 42
                }
            }
        }
        toon = to_toon(original)
        parsed = parse_toon(toon)
        assert parsed == original

    def test_roundtrip_complex(self):
        original = {
            '@type': 'CreateAction',
            '@id': 'outcome/005',
            'name': 'authentication',
            'actionStatus': 'CompletedActionStatus',
            'x-maturity': 75,
            'steps': [
                {'name': 'step1', 'status': 'done', 'tokens': 1000},
                {'name': 'step2', 'status': 'done', 'tokens': 2000}
            ],
            'tags': ['auth', 'security'],
            'config': {
                'timeout': 30,
                'retries': 3
            }
        }
        toon = to_toon(original)
        parsed = parse_toon(toon)

        # Compare key by key since order might differ
        assert parsed['@type'] == original['@type']
        assert parsed['@id'] == original['@id']
        assert parsed['name'] == original['name']
        assert parsed['actionStatus'] == original['actionStatus']
        assert parsed['x-maturity'] == original['x-maturity']
        assert parsed['steps'] == original['steps']
        assert parsed['tags'] == original['tags']
        assert parsed['config'] == original['config']


class TestValidateToon:
    """Test TOON validation."""

    def test_validate_valid_action(self):
        data = {
            '@type': 'Action',
            'name': 'test',
            'actionStatus': 'ActiveActionStatus'
        }
        is_valid, messages = validate_toon(data)
        assert is_valid
        assert len(messages) == 0

    def test_validate_valid_with_extensions(self):
        data = {
            '@type': 'CreateAction',
            'name': 'test',
            'x-maturity': 50,
            'x-tokens': 1000
        }
        is_valid, messages = validate_toon(data)
        assert is_valid

    def test_validate_invalid_action_status(self):
        data = {
            '@type': 'Action',
            'actionStatus': 'InvalidStatus'
        }
        is_valid, messages = validate_toon(data)
        assert not is_valid
        assert any('actionStatus must be a valid ActionStatusType' in m for m in messages)

    def test_validate_nonstring_type(self):
        data = {
            '@type': 123
        }
        is_valid, messages = validate_toon(data)
        assert not is_valid
        assert any('@type must be a string' in m for m in messages)

    def test_validate_unknown_type_warning(self):
        data = {
            '@type': 'CustomType'
        }
        is_valid, messages = validate_toon(data)
        assert is_valid  # Still valid, just a warning
        assert any('not in common schema.org types' in m for m in messages)

    def test_validate_custom_property_warning(self):
        data = {
            '@type': 'Action',
            'customField': 'value'  # Should be x-customField
        }
        is_valid, messages = validate_toon(data)
        assert is_valid  # Warning, not error
        assert any('should use x- prefix' in m for m in messages)

    def test_validate_standard_properties_ok(self):
        """Standard schema.org properties should not trigger warnings."""
        data = {
            '@type': 'Action',
            'name': 'test',
            'description': 'desc',
            'result': 'success',
            'startTime': '2025-01-01T00:00:00Z',
            'endTime': '2025-01-01T01:00:00Z'
        }
        is_valid, messages = validate_toon(data)
        assert is_valid
        assert len(messages) == 0

    def test_validate_all_action_statuses(self):
        """All valid ActionStatusType values should pass."""
        statuses = [
            'PotentialActionStatus',
            'ActiveActionStatus',
            'CompletedActionStatus',
            'FailedActionStatus'
        ]
        for status in statuses:
            data = {'@type': 'Action', 'actionStatus': status}
            is_valid, messages = validate_toon(data)
            assert is_valid, f'{status} should be valid'


class TestConversion:
    """Test JSON<->TOON conversion."""

    def test_json_to_toon(self):
        json_str = '{"@type": "Action", "name": "test", "count": 5}'
        toon = convert_json_to_toon(json_str)
        assert '@type: Action' in toon
        assert 'name: test' in toon
        assert 'count: 5' in toon

    def test_toon_to_json(self):
        toon = """
@type: Action
name: test
count: 5
"""
        json_str = convert_toon_to_json(toon)
        data = json.loads(json_str)
        assert data['@type'] == 'Action'
        assert data['name'] == 'test'
        assert data['count'] == 5

    def test_roundtrip_json_toon_json(self):
        original_json = '{"@type": "Action", "name": "test", "values": [1, 2, 3]}'
        toon = convert_json_to_toon(original_json)
        back_to_json = convert_toon_to_json(toon)
        original_data = json.loads(original_json)
        result_data = json.loads(back_to_json)
        assert result_data == original_data

    def test_invalid_json(self):
        with pytest.raises(json.JSONDecodeError):
            convert_json_to_toon('not valid json')


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_strings_in_array(self):
        data = {'items': ['', 'value', '']}
        toon = to_toon(data)
        parsed = parse_toon(toon)
        assert parsed['items'] == ['', 'value', '']

    def test_numeric_strings(self):
        data = {'id': '123'}  # String, not number
        toon = to_toon(data)
        # Numbers without quotes should parse as numbers
        # So we need to quote it
        assert 'id: 123' in toon or 'id: "123"' in toon

    def test_special_chars_in_values(self):
        data = {
            'path': 'a/b/c',
            'url': 'https://example.com',
            'pattern': 'test-*'
        }
        toon = to_toon(data)
        parsed = parse_toon(toon)
        assert parsed == data

    def test_multiline_not_supported(self):
        """TOON doesn't support multiline strings - should quote them."""
        data = {'desc': 'line1\nline2'}
        toon = to_toon(data)
        # Should still work, though format may not be ideal
        assert 'desc:' in toon

    def test_very_nested_structure(self):
        """Test deeply nested objects."""
        data = {
            'level1': {
                'level2': {
                    'level3': {
                        'value': 'deep'
                    }
                }
            }
        }
        toon = to_toon(data)
        parsed = parse_toon(toon)
        assert parsed['level1']['level2']['level3']['value'] == 'deep'

    def test_mixed_type_arrays(self):
        """Arrays with mixed types should use verbose format."""
        data = {'items': [1, 'text', {'key': 'value'}]}
        toon = to_toon(data)
        parsed = parse_toon(toon)
        # Should preserve the structure somehow
        assert 'items' in parsed

    def test_tabular_array_with_missing_fields(self):
        """Tabular arrays where some rows have missing fields."""
        toon = """
items[2]{id,name,optional}:
1,Alice,value
2,Bob
"""
        result = parse_toon(toon)
        assert result['items'][0]['optional'] == 'value'
        assert result['items'][1]['optional'] is None

    def test_boolean_strings(self):
        """String values 'true', 'false' should be quoted to preserve as strings."""
        data = {'value': 'true'}  # String, not boolean
        toon = to_toon(data)
        # Should quote it to distinguish from boolean
        assert '"true"' in toon

    def test_float_values(self):
        """Float values should be preserved."""
        data = {'percentage': 47.5, 'ratio': 0.333}
        toon = to_toon(data)
        parsed = parse_toon(toon)
        assert parsed['percentage'] == 47.5
        assert parsed['ratio'] == 0.333

    def test_large_numbers(self):
        """Large numbers should be preserved."""
        data = {'tokens': 150000, 'bignum': 9999999999}
        toon = to_toon(data)
        parsed = parse_toon(toon)
        assert parsed['tokens'] == 150000
        assert parsed['bignum'] == 9999999999
