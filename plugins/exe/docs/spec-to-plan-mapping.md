# Spec to Plan Mapping

How technical specification fields map to execution plan fields.

## Source Extraction

| Spec Field | Plan Field | Notes |
|------------|------------|-------|
| `@id` | `source.@id` | Strip `spec/` prefix for plan ID |
| `document.name` | `source.name` | Verbatim |
| `version` | `source.version` | Verbatim |
| `{spec-path}` | `source.url` | Spec file path |

## Task Generation

| Spec Section | Task Type | Mapping |
|--------------|-----------|---------|
| `components.item[]` | `behaviour` | One task per component |
| `types.item[]` | `behaviour` | One task per type definition |
| `fileStructure.items[]` | `infrastructure` | Create directory/file tasks |
| `contracts.item[]` | `verification` | Test tasks for contracts |
| `contracts.errorCases[]` | `verification` | Error case test tasks |
| `acceptanceCriteria.item[]` | `verification` | AC validation tasks |
| `enforcement.checks[]` | `verification` | CI/CD setup tasks |
| `migration.steps[]` | `configuration` | Migration tasks (if present) |
| `testing.utilities[]` | `behaviour` | Test helper tasks |

## Dependency Extraction

| Spec Field | Plan Usage |
|------------|------------|
| `dependencies.leafNodes[]` | Phase 1 components (no dependencies) |
| `dependencies.requires[]` | Task `dependsOn` relationships |
| `dependencies.parallelGroups[]` | Task `parallelGroup` assignment |
| `components.item[].dependencies` | Task `dependsOn` relationships |

## Acceptance Criteria Mapping

| Spec Field | Plan Field |
|------------|------------|
| `contracts.item[].given/when/then` | `taskDetails.acceptance` |
| `acceptanceCriteria.item[].description` | `checkpoint.validation` |
| `evidence.item[].verification` | `taskDetails.acceptance` |

## Input/Output Mapping

| Spec Field | Plan Field |
|------------|------------|
| `quickReference.patterns[]` | `taskInputs` (static ref to spec) |
| `quickReference.imports[]` | `taskInputs` (static ref to spec) |
| `fileStructure.items[].path` | `taskOutputs.path` |
| `types.item[].file` | `taskOutputs.path` |
