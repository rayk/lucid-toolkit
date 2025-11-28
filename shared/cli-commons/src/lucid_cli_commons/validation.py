"""
Schema validation and pattern matching utilities.

Provides JSON schema validation using jsonschema library and pattern
validation for session IDs and outcome paths.
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any
import jsonschema


class SchemaValidator:
    """
    Schema validator with caching for JSON schema validation.

    Caches loaded schemas to avoid repeated file reads.
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize schema validator.

        Args:
            workspace_root: Override workspace root (defaults to finding .git)
        """
        if workspace_root:
            self.workspace_root = Path(workspace_root).resolve()
        else:
            self.workspace_root = self._find_workspace_root()

        self._schema_cache: Dict[str, Dict[Any, Any]] = {}

    def _find_workspace_root(self) -> Path:
        """
        Find workspace root by searching for .git directory.

        Returns:
            Path to workspace root
        """
        current = Path.cwd()

        # Walk up directory tree looking for .git
        for parent in [current] + list(current.parents):
            if (parent / ".git").exists():
                return parent

        # Fallback to current working directory
        return current

    def load_schema(self, schema_name: str) -> Dict[Any, Any]:
        """
        Load JSON schema from file with caching.

        Args:
            schema_name: Name of schema file (without .json extension)

        Returns:
            Parsed schema dictionary

        Raises:
            FileNotFoundError: If schema file doesn't exist
            json.JSONDecodeError: If schema is not valid JSON
        """
        # Check cache first
        if schema_name in self._schema_cache:
            return self._schema_cache[schema_name]

        # Construct path
        schema_path = self.workspace_root / ".claude" / "schema" / f"{schema_name}.json"

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")

        # Load and cache
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        self._schema_cache[schema_name] = schema
        return schema

    def validate(self, data: Dict[Any, Any], schema_name: str) -> bool:
        """
        Validate data against JSON schema.

        Args:
            data: Data to validate
            schema_name: Name of schema to validate against

        Returns:
            True if validation succeeds

        Raises:
            ValidationError: If data doesn't match schema
            FileNotFoundError: If schema doesn't exist
        """
        schema = self.load_schema(schema_name)
        jsonschema.validate(instance=data, schema=schema)
        return True


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID pattern.

    Session IDs must match pattern: sess-{identifier}
    where identifier is alphanumeric with optional hyphens.

    Args:
        session_id: Session ID to validate

    Returns:
        True if valid, False otherwise

    Examples:
        >>> validate_session_id("sess-1234567890")
        True
        >>> validate_session_id("sess-test-session")
        True
        >>> validate_session_id("invalid")
        False
    """
    import re

    if not session_id:
        return False

    # Pattern: sess-{one or more alphanumeric/hyphen chars}
    pattern = r'^sess-[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$'
    return bool(re.match(pattern, session_id))


def validate_outcome_path(path: str) -> bool:
    """
    Validate outcome path pattern.

    Outcome paths must match pattern:
    outcomes/{state}/{number}-{name}

    where:
    - state: queued, in-progress, or completed
    - number: 3-digit number (001-999)
    - name: lowercase alphanumeric with hyphens

    Args:
        path: Outcome path to validate

    Returns:
        True if valid, False otherwise

    Examples:
        >>> validate_outcome_path("outcomes/queued/001-test-outcome")
        True
        >>> validate_outcome_path("outcomes/in-progress/123-another")
        True
        >>> validate_outcome_path("invalid/path")
        False
    """
    import re

    if not path:
        return False

    # Pattern: outcomes/{state}/{nnn-name}
    pattern = r'^outcomes/(queued|in-progress|completed)/\d{3}-[a-z0-9]+(-[a-z0-9]+)*$'
    return bool(re.match(pattern, path))
