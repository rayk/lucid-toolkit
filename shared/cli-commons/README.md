# Lucid CLI Commons

Shared Python library for Lucid Toolkit Claude Code plugins.

## Overview

`lucid-cli-commons` provides common utilities used by plugin hooks, scripts, and commands across the Lucid Toolkit ecosystem.

## Features

- **Schema Validation** - JSON Schema validation for tracking files
- **JSON/YAML Parsing** - Safe parsing with error handling
- **Git Operations** - Common git utilities (status, branch detection, etc.)
- **File System Utilities** - Path resolution, atomic writes, safe reads
- **Cross-Reference Management** - Update capability/outcome cross-references

## Installation

### Development Mode

```bash
cd shared/cli-commons
pip install -e .
```

### With Dev Dependencies

```bash
pip install -e ".[dev]"
```

## Usage

```python
from lucid_cli_commons.schema import validate_json
from lucid_cli_commons.git import get_current_branch
from lucid_cli_commons.fs import atomic_write

# Validate tracking file
validate_json(data, schema_path="schemas/outcome_track_schema.json")

# Get git branch
branch = get_current_branch()

# Atomic file write
atomic_write("/path/to/file.json", data)
```

## Module Structure

```
lucid_cli_commons/
├── __init__.py
├── schema.py          # Schema validation utilities
├── git.py            # Git operations
├── fs.py             # File system utilities
├── crossref.py       # Cross-reference management
└── yaml_utils.py     # YAML parsing utilities
```

## Requirements

- Python 3.11+
- pyyaml>=6.0
- jsonschema>=4.19.0
- click>=8.1.0

## Testing

```bash
pytest
pytest --cov=lucid_cli_commons
```

## License

MIT - See LICENSE in repository root
