# /planner:generate

Generate an execution prompt from design documents.

## Usage

```
/planner:generate <design-doc-path> [options]
```

## Arguments

- `<design-doc-path>` - Path to the design document(s) to analyze

## Options

- `--output <path>` - Output directory for generated prompt (default: current directory)
- `--language <lang>` - Target language (python, typescript, go, rust, java, ruby)
- `--dry-run` - Analyze only, don't generate prompt

## Workflow

1. **Load Skill**: Activate `execution-prompt-generator` skill
2. **Analyze Documents**: Extract system identity, dependencies, patterns
3. **Validate Prerequisites**: Check pre-existing dependencies exist
4. **Estimate Metrics**: Calculate tokens, duration, cost
5. **Generate Prompt**: Create complete execution prompt

## Output

On success, generates:
- `execution-prompt.md` - The generated execution prompt
- `analysis-report.md` - Dependency and validation analysis

## Example

```
/planner:generate ./docs/design/neo4j-service.md --language python
```

## Behavior

When invoked:

1. Read the specified design document(s)
2. Activate the `execution-prompt-generator` skill
3. Extract all required information per the analysis checklist
4. Validate dependencies and prerequisites
5. If validation fails, report errors and stop
6. If validation passes, generate the execution prompt
7. Write output files to the specified directory

## Error Handling

| Error | Resolution |
|-------|------------|
| DEPENDENCY_UNCLEAR | Clarify in design documents |
| PREREQ_MISSING | Implement missing dependency first |
| CIRCULAR_DEPENDENCY | Refactor design to break cycle |
| MISSING_LANGUAGE | Specify --language option |
