# Python Development Tools

Expert guidance for using Python development tools including IDE integration, static analysis, testing, and debugging workflows.

## Analysis Tools

### Static Analysis

| Tool | MCP Pattern | Purpose |
|------|-------------|---------|
| pyright | `Bash: pyright --outputjson` | Type checking |
| ruff | `Bash: ruff check --output-format=json` | Linting |
| ruff format | `Bash: ruff format --check` | Code formatting |
| mypy | `Bash: mypy --show-error-codes` | Alternative type checker |

### Code Quality Commands

```bash
# Type check entire project
pyright

# Type check specific file
pyright src/module.py

# Lint with auto-fix
ruff check --fix .

# Format code
ruff format .

# Check if formatting needed
ruff format --check .
```

## Testing Tools

### pytest Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_module.py

# Run specific test function
pytest tests/test_module.py::test_function

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run async tests
pytest -v --asyncio-mode=auto

# Run with verbose output
pytest -vv

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Run tests matching pattern
pytest -k "test_user"
```

### Test Output Interpretation

```
PASSED  - Test succeeded
FAILED  - Test failed (assertion or exception)
ERROR   - Test setup/teardown failed
SKIPPED - Test was skipped (@pytest.mark.skip)
XFAIL   - Expected failure (@pytest.mark.xfail)
XPASS   - Expected failure but passed
```

## IDE Tools

### Available MCP IDE Tools

| Tool | Purpose |
|------|---------|
| `mcp__ide__getDiagnostics` | Get IDE diagnostics for file |
| `mcp__ide__readFile` | Read file content |
| `mcp__ide__writeFile` | Write/create file |
| `mcp__ide__getCurrentEditor` | Get active editor |
| `mcp__ide__getOpenEditors` | List open files |
| `mcp__ide__searchInProject` | Project-wide search |
| `mcp__ide__getProjectStructure` | Get project file tree |

### Diagnostic Workflow

```xml
<workflow name="diagnostics">
  <step>Get diagnostics: mcp__ide__getDiagnostics</step>
  <step>Parse error messages and locations</step>
  <step>Read affected files for context</step>
  <step>Propose fixes based on error type</step>
</workflow>
```

## Development Workflows

### TDD Workflow

```xml
<workflow name="tdd">
  <step name="write_test">
    Write failing test in tests/
  </step>
  <step name="run_test">
    pytest tests/test_file.py::test_function -v
    Expect: FAILED (RED)
  </step>
  <step name="implement">
    Write minimal code to pass
  </step>
  <step name="verify">
    pytest tests/test_file.py::test_function -v
    Expect: PASSED (GREEN)
  </step>
  <step name="refactor">
    Improve code while keeping tests passing
  </step>
  <step name="type_check">
    pyright src/
  </step>
  <step name="lint">
    ruff check --fix .
    ruff format .
  </step>
</workflow>
```

### Debug Workflow

```xml
<workflow name="debug">
  <step name="gather_info">
    Get full traceback and error message
  </step>
  <step name="locate">
    Find file and line from traceback
  </step>
  <step name="read_context">
    Read affected file(s)
  </step>
  <step name="diagnose">
    Form hypothesis from error type:
    - ImportError: Check imports, PYTHONPATH
    - TypeError: Check types, function signatures
    - AttributeError: Check object has attribute
    - KeyError: Check dict keys exist
  </step>
  <step name="fix">
    Apply minimal fix
  </step>
  <step name="verify">
    Run tests or reproduce scenario
  </step>
</workflow>
```

### Code Quality Workflow

```xml
<workflow name="quality">
  <step name="type_check">
    pyright
    Fix any type errors
  </step>
  <step name="lint">
    ruff check .
    Fix or acknowledge warnings
  </step>
  <step name="test">
    pytest --cov
    Ensure coverage thresholds met
  </step>
  <step name="format">
    ruff format .
    Ensure consistent style
  </step>
</workflow>
```

## Tool Configuration

### pyproject.toml Reference

```toml
[tool.pyright]
include = ["src"]
exclude = ["**/__pycache__"]
typeCheckingMode = "strict"
pythonVersion = "3.12"
venvPath = "."
venv = ".venv"

[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "SIM", # flake8-simplify
    "TCH", # type-checking imports
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-ra -q"

[tool.coverage.run]
source = ["src"]
branch = true
```

## Error Resolution Patterns

### Common pyright Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Cannot find module` | Missing stubs or package | Install types-* package or add to exclude |
| `Type "X" is not assignable` | Type mismatch | Check types match, use Union if needed |
| `"None" is not callable` | Optional not handled | Add None check or use `assert x is not None` |
| `Missing return statement` | Function path without return | Add return or raise |

### Common ruff Errors

| Code | Cause | Fix |
|------|-------|-----|
| `E501` | Line too long | Break line or adjust config |
| `F401` | Unused import | Remove import |
| `F841` | Unused variable | Remove or prefix with `_` |
| `I001` | Import order | Run `ruff check --fix` |
| `UP006` | Deprecated syntax | Use modern Python syntax |

## Sub-References

- `references/ide-patterns.md` - IDE tool usage patterns
- `references/test-patterns.md` - Testing patterns and fixtures
- `references/async-patterns.md` - Async/await patterns
