# Language-Specific Configuration Reference

## Python

```yaml
testing:
  framework: pytest
  async_support: pytest-asyncio
  mocking: unittest.mock
  test_location: tests/{module_name}/
  test_naming: test_{name}.py
  run_command: "pytest {test_path} -v"
  coverage_command: "pytest --cov={source_dir} --cov-report=json --cov-fail-under=80"
  type_checker: "mypy {source_dir} --strict"

linting:
  linter: "ruff check {source_dir}"
  strict: "ruff check {source_dir} --select=ALL"

documentation:
  style: Google docstrings with LLM extensions
  required_sections:
    - Summary
    - LLM Context
    - Args
    - Returns
    - Raises
    - Example
    - Related

stub_templates:
  class: |
    class {name}:
        """TODO: Add LLM-optimized documentation."""
        pass

  function: |
    def {name}({params}) -> {return_type}:
        """TODO: Add LLM-optimized documentation."""
        raise NotImplementedError()
```

## TypeScript

```yaml
testing:
  framework: jest | vitest
  test_location: __tests__/
  run_command: "npm test"
  coverage_command: "npm test -- --coverage --coverageThreshold='{\"global\":{\"lines\":80}}'"
  type_checker: "tsc --noEmit"

linting:
  linter: "npx eslint {source_dir}"
  strict: "npx eslint {source_dir} --max-warnings=0"

documentation:
  style: JSDoc with @llm-context
  required_sections:
    - "@description"
    - "@llm-context"
    - "@param"
    - "@returns"
    - "@throws"
    - "@example"
    - "@see"

stub_templates:
  class: |
    /**
     * TODO: Add LLM-optimized documentation.
     */
    export class {name} {}

  function: |
    /**
     * TODO: Add LLM-optimized documentation.
     */
    export function {name}({params}): {return_type} {
      throw new Error('Not implemented');
    }
```

## Go

```yaml
testing:
  framework: testing
  test_location: same directory
  test_naming: "{name}_test.go"
  run_command: "go test ./... -v"
  coverage_command: "go test -coverprofile=coverage.out -covermode=atomic ./..."
  type_checker: "go vet ./..."

linting:
  linter: "golangci-lint run"

documentation:
  style: Godoc with LLM Context section
  required_sections:
    - Summary
    - LLM Context
    - Parameters
    - Returns
    - Example
    - See also

stub_templates:
  struct: |
    // {name} TODO: Add LLM-optimized documentation.
    type {name} struct {}

  function: |
    // {name} TODO: Add LLM-optimized documentation.
    func {name}({params}) {return_type} {
      panic("not implemented")
    }
```

## Rust

```yaml
testing:
  framework: built-in
  test_location: mod tests
  run_command: "cargo test"
  coverage_command: "cargo tarpaulin --out Json --output-dir coverage"
  type_checker: "cargo check"

linting:
  linter: "cargo clippy -- -D warnings"

documentation:
  style: Rustdoc with LLM Context section
  required_sections:
    - Summary
    - LLM Context
    - Arguments
    - Returns
    - Errors
    - Example
    - See Also

stub_templates:
  struct: |
    /// TODO: Add LLM-optimized documentation.
    pub struct {name} {}

  function: |
    /// TODO: Add LLM-optimized documentation.
    pub fn {name}({params}) -> {return_type} {
      todo!()
    }
```

## JavaScript (Node.js)

```yaml
testing:
  framework: jest | mocha
  test_location: __tests__/ or test/
  run_command: "npm test"
  coverage_command: "npm test -- --coverage"
  type_checker: null  # No static types

linting:
  linter: "npx eslint {source_dir}"
  strict: "npx eslint {source_dir} --max-warnings=0"

documentation:
  style: JSDoc
  required_sections:
    - "@description"
    - "@param"
    - "@returns"
    - "@throws"
    - "@example"
```

## Ruby

```yaml
testing:
  framework: rspec
  test_location: spec/
  test_naming: "{name}_spec.rb"
  run_command: "bundle exec rspec"
  coverage_command: "bundle exec rspec --format json --out coverage/rspec.json"
  type_checker: "bundle exec srb tc"  # Sorbet

linting:
  linter: "bundle exec rubocop"

documentation:
  style: YARD with LLM extensions
  required_sections:
    - Summary
    - "@param"
    - "@return"
    - "@raise"
    - "@example"
```

## Java

```yaml
testing:
  framework: JUnit 5
  test_location: src/test/java/
  test_naming: "{name}Test.java"
  run_command: "mvn test" or "gradle test"
  coverage_command: "mvn jacoco:report"
  type_checker: built-in (compiler)

linting:
  linter: "mvn checkstyle:check"

documentation:
  style: Javadoc with LLM extensions
  required_sections:
    - Summary
    - "@param"
    - "@return"
    - "@throws"
    - "@see"
```
