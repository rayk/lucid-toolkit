# Schema Version Compatibility Matrix

**Last Updated**: 2025-11-29
**Document Version**: 1.0.0

## Overview

This document provides a comprehensive compatibility matrix for all schemas in the lucid-toolkit plugin marketplace. It tracks schema versions, ownership, cross-schema dependencies, and migration guidance to ensure smooth upgrades across the plugin ecosystem.

---

## Schema Registry

### Core Schemas by Plugin

| Schema Name | Version | Owner Plugin | File Path |
|-------------|---------|--------------|-----------|
| `capability_track_schema` | 2.0.0 | capability | `plugins/capability/schemas/capability_track_schema.json` |
| `capability_summary_schema` | 1.1.0 | capability | `plugins/capability/schemas/capability_summary_schema.json` |
| `outcome_track_schema` | 2.1.0 | outcome | `plugins/outcome/schemas/outcome_track_schema.json` |
| `outcome_summary_schema` | 1.0.0 | outcome | `plugins/outcome/schemas/outcome_summary_schema.json` |
| `context_tracking_schema` | 1.0.0 | context | `plugins/context/schemas/context_tracking_schema.json` |
| `workspace_schema` | 1.0.0 | workspace | `plugins/workspace/schemas/workspace_schema.json` |
| `project_map_schema` | 1.0.0 | workspace | `plugins/workspace/schemas/project_map_schema.json` |
| `actor_summary_schema` | 1.0.0 | workspace | `plugins/workspace/schemas/actor_summary_schema.json` |
| `workspaces_schema` | 1.0.0 | shared | `shared/workspaces/workspaces_schema.json` |
| `execution_result_schema` | N/A | plan | `plugins/plan/schemas/execution_result_schema.json` |
| `audit_trail_schema` | N/A | plan | `plugins/plan/schemas/audit_trail_schema.json` |
| `checkpoint_schema` | N/A | plan | `plugins/plan/schemas/checkpoint_schema.json` |

---

## Cross-Schema Dependencies

### Direct References

These schemas contain hard references to other schemas via file paths or patterns.

#### outcome_track_schema → capability_track_schema

**Dependency Type**: Path Reference
**Field**: `outcome.capabilityContributions[].capabilityPath`
**Pattern**: `^capabilities/[a-z0-9]+(-[a-z0-9]+)*/capability_track\\.json$`
**Description**: Outcomes reference capability tracking files to declare maturity contributions.

**Impact of Changes**:
- **Breaking**: Changes to capability directory structure or file naming
- **Non-breaking**: Changes to capability_track.json internal structure
- **Migration Required**: If capability path pattern changes

#### capability_track_schema → outcome_track_schema

**Dependency Type**: Bidirectional Path Reference
**Fields**:
- `outcomes.requiredOutcomes[].outcomeTrackingFile`
- `outcomes.builtByOutcomes[].outcomeTrackingFile`
- `outcomes.enablesOutcomes[].outcomeTrackingFile`

**Pattern**: `^outcomes/(queued|in-progress|completed)/[0-9]+-[a-z0-9]+(-[a-z0-9]+){0,4}/outcome_track\\.json$`
**Description**: Capabilities reference outcome tracking files to track build plan and maturity progress.

**Impact of Changes**:
- **Breaking**: Changes to outcome state directory names or structure
- **Non-breaking**: Changes to outcome_track.json internal structure
- **Migration Required**: When moving outcomes between states (state transitions)

#### outcome_track_schema → project_map_schema

**Dependency Type**: Reference by Name
**Field**: `outcome.projects[].projectName`
**Description**: Outcomes reference projects by name, which must exist in project_map.json

**Impact of Changes**:
- **Breaking**: Renaming or removing projects from project_map
- **Non-breaking**: Adding new projects
- **Migration Required**: When project names change

#### outcome_track_schema → actor_summary_schema

**Dependency Type**: Reference by ID
**Field**: `actors[].actorId`
**Pattern**: `^[a-z0-9]+(-[a-z0-9]+)*$`
**Description**: Outcomes reference actors by ID, which should exist in actor_summary.json

**Impact of Changes**:
- **Breaking**: Changing actor ID patterns
- **Non-breaking**: Adding new actors
- **Migration Required**: If actor ID format changes

#### capability_track_schema → actor_summary_schema

**Dependency Type**: Reference by ID
**Field**: `actors[].actorId`
**Pattern**: `^[a-z0-9]+(-[a-z0-9]+)*$`
**Description**: Capabilities reference actors by ID to track relationships

**Impact of Changes**:
- **Breaking**: Changing actor ID patterns
- **Non-breaking**: Adding new actors
- **Migration Required**: If actor ID format changes

#### workspace_schema → project_map_schema

**Dependency Type**: Structural Alignment
**Description**: Workspace projects should align with projects declared in project_map.json

**Impact of Changes**:
- **Breaking**: Major structural changes to project organization
- **Non-breaking**: Adding new project properties
- **Migration Required**: When project structure fundamentally changes

#### workspaces_schema → workspace_schema

**Dependency Type**: Semantic Consistency
**Description**: Shared workspaces registry uses similar project structures as workspace_schema

**Impact of Changes**:
- **Breaking**: Incompatible project structure changes
- **Non-breaking**: Adding new workspace properties
- **Migration Required**: When workspace organization changes

### Summary Schemas

These schemas aggregate data from their corresponding tracking schemas:

| Summary Schema | Aggregates From | Sync Requirement |
|----------------|-----------------|------------------|
| `capability_summary_schema` | `capability_track_schema` | Update on capability create/update/delete |
| `outcome_summary_schema` | `outcome_track_schema` | Update on outcome state change |

**Breaking Change Impact**: If tracking schema fields referenced in summary indexes change, summary schemas must be updated in parallel.

---

## Version Compatibility Matrix

### v1.0.0 (Current Stable)

| Schema | Version | Compatible With | Notes |
|--------|---------|-----------------|-------|
| capability_track | 2.0.0 | outcome_track 2.1.0, actor_summary 1.0.0 | Stable |
| capability_summary | 1.1.0 | capability_track 2.0.0 | Stable |
| outcome_track | 2.1.0 | capability_track 2.0.0, actor_summary 1.0.0, project_map 1.0.0 | Stable |
| outcome_summary | 1.0.0 | outcome_track 2.1.0 | Stable |
| context_tracking | 1.0.0 | - | Independent |
| workspace | 1.0.0 | project_map 1.0.0 | Stable |
| project_map | 1.0.0 | - | Stable |
| actor_summary | 1.0.0 | - | Stable |
| workspaces | 1.0.0 | workspace 1.0.0 | Stable |
| execution_result | N/A | - | Independent |
| audit_trail | N/A | - | Independent |
| checkpoint | N/A | - | Independent |

### Known Incompatibilities

**None at this time.** All schemas in the current release are compatible.

---

## Breaking vs Non-Breaking Changes

### Breaking Changes

These changes **REQUIRE** version bumps and migration:

1. **Changing Required Fields**
   - Adding new required fields without defaults
   - Removing or renaming required fields
   - Changing field types (string → number, etc.)

2. **Changing Path Patterns**
   - Modifying file path regex patterns (`outcomeTrackingFile`, `capabilityPath`)
   - Changing directory structure (state directories, capability folders)
   - Renaming tracking file names (`outcome_track.json` → something else)

3. **Changing ID/Reference Formats**
   - Modifying ID patterns (`folderName`, `actorId`, `projectName`)
   - Changing enum values that affect cross-references
   - Altering state names (`queued` → `pending`)

4. **Removing or Renaming Fields Used in Indexes**
   - Fields referenced in summary schemas
   - Fields used for cross-referencing between schemas

### Non-Breaking Changes

These changes are **BACKWARDS COMPATIBLE**:

1. **Adding Optional Fields**
   - New properties with default values
   - New optional nested objects

2. **Expanding Enums**
   - Adding new enum values (append-only)
   - New allowable states or types

3. **Adding to Arrays**
   - New items in description arrays
   - Additional index types in summary schemas

4. **Documentation Updates**
   - Clarifying descriptions
   - Adding examples
   - Improving field documentation

5. **Relaxing Constraints**
   - Increasing maxLength limits
   - Removing minimum requirements (with defaults)

### Version Increment Rules

Follow semantic versioning for schemas:

- **Major (X.0.0)**: Breaking changes
- **Minor (x.Y.0)**: New features (backwards compatible)
- **Patch (x.y.Z)**: Bug fixes, documentation

---

## Migration Guidance

### Upgrading capability_track_schema

**From 1.x to 2.0.0**

**Breaking Changes**:
- Moved maturity definitions to external documentation
- Restructured `coreValues` field
- Changed hierarchical folder structure requirements

**Migration Steps**:
1. Extract maturity milestones from capability_track.json to separate milestones.md
2. Convert `coreValues` from array to object with `primary`/`secondary` structure
3. Add `metadata.directoryPath` and `metadata.childFolderName` for hierarchical capabilities
4. Update any scripts reading maturity definitions

**Automated Migration**: Available in capability plugin v1.1.0+
```bash
python plugins/capability/scripts/migrate_v1_to_v2.py
```

### Upgrading outcome_track_schema

**From 2.0.0 to 2.1.0**

**Breaking Changes**:
- Replaced `capabilities` array with `capabilityContributions` array
- Added maturity percentage tracking
- Introduced `parentContribution` for child outcomes

**Migration Steps**:
1. Convert `capabilities` paths to `capabilityContributions` objects
2. Add `maturityContribution` percentage for each capability
3. Add `isPrimary` flag to primary capability
4. For child outcomes, add `parentContribution` percentage

**Automated Migration**: Available in outcome plugin v1.1.0+
```bash
python plugins/outcome/scripts/migrate_v2_0_to_v2_1.py
```

### Upgrading capability_summary_schema

**From 1.0.0 to 1.1.0**

**Breaking Changes**: None (minor version)

**New Features**:
- Added `averageMaturityByDomain` aggregation
- Added `maturityVelocity` tracking
- Enhanced progress metrics

**Migration Steps**:
1. Regenerate summary using latest capability plugin
2. New fields populated automatically

**Automated**: Run capability snapshot command
```bash
/capability:snapshot
```

---

## Cross-Version Compatibility

### Reading Older Versions

Most plugins can read older schema versions with graceful degradation:

| Plugin | Can Read | Notes |
|--------|----------|-------|
| capability | 1.x, 2.x | Auto-migrates on read |
| outcome | 2.0.0, 2.1.0 | Falls back to empty `capabilityContributions` if missing |
| workspace | 1.0.0 | No backwards compatibility yet |
| context | 1.0.0 | No backwards compatibility yet |

### Writing to Older Versions

**Not Supported**. Plugins always write using their declared schema version.

**Workaround**: Pin plugin versions if mixed-version environments needed.

---

## Schema Dependency Graph

```
┌─────────────────────────────────────────────────┐
│         workspaces_schema (1.0.0)               │
│                    [shared]                      │
└────────────────────┬────────────────────────────┘
                     │ structural alignment
                     ▼
┌─────────────────────────────────────────────────┐
│          workspace_schema (1.0.0)               │
│               [workspace plugin]                 │
└────────────────────┬────────────────────────────┘
                     │ alignment
                     ▼
┌─────────────────────────────────────────────────┐
│         project_map_schema (1.0.0)              │
│               [workspace plugin]                 │
└────────────────────┬────────────────────────────┘
                     │ projectName reference
                     ▼
┌─────────────────────────────────────────────────┐
│        outcome_track_schema (2.1.0)             │
│               [outcome plugin]                   │
└─────────┬──────────────────────────┬────────────┘
          │                          │
          │ outcomeTrackingFile      │ capabilityPath
          │                          │
          ▼                          ▼
┌──────────────────────┐   ┌────────────────────────┐
│  outcome_summary     │   │  capability_track      │
│     (1.0.0)          │   │      (2.0.0)           │
│  [outcome plugin]    │   │ [capability plugin]    │
└──────────────────────┘   └────────┬───────────────┘
                                    │
                                    │ aggregates
                                    ▼
                          ┌────────────────────────┐
                          │  capability_summary    │
                          │      (1.1.0)           │
                          │ [capability plugin]    │
                          └────────────────────────┘

┌─────────────────────────────────────────────────┐
│        actor_summary_schema (1.0.0)             │
│               [workspace plugin]                 │
└────────────────────┬────────────────────────────┘
                     │ actorId reference
                     │
          ┌──────────┴────────────┐
          ▼                       ▼
  outcome_track           capability_track
     (actors)                (actors)

┌─────────────────────────────────────────────────┐
│     context_tracking_schema (1.0.0)             │
│               [context plugin]                   │
│              (independent)                       │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Plan Plugin Schemas (N/A versions)             │
│   - execution_result_schema                     │
│   - audit_trail_schema                          │
│   - checkpoint_schema                           │
│              (independent)                       │
└─────────────────────────────────────────────────┘
```

---

## Testing Schema Compatibility

### Validation Commands

Test schema compatibility after upgrades:

```bash
# Validate all tracking files against schemas
/workspace:validate --schemas

# Check cross-references
/workspace:validate --refs

# Full health check
/workspace:health --verbose
```

### Pre-Upgrade Checklist

Before upgrading any schema:

- [ ] Read migration guidance for the specific schema
- [ ] Backup all tracking files (`capabilities/`, `outcomes/`, `status/`)
- [ ] Run validation on current state
- [ ] Test migration script on a copy of data
- [ ] Update plugin to version supporting new schema
- [ ] Run automated migration
- [ ] Validate migrated data
- [ ] Run full workspace health check

---

## Version History

### capability_track_schema

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-01 | Major restructure: hierarchical capabilities, external milestones, coreValues object |
| 1.x | 2024 | Original version |

### outcome_track_schema

| Version | Date | Changes |
|---------|------|---------|
| 2.1.0 | 2025-11 | Added capabilityContributions with maturity percentages, parentContribution |
| 2.0.0 | 2025-01 | Major restructure with observableEffects, parent/child outcomes |
| 1.x | 2024 | Original version |

### capability_summary_schema

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2025-11 | Added maturityVelocity, averageMaturityByDomain |
| 1.0.0 | 2025-01 | Initial release |

### All Other Schemas

| Schema | Version | Date | Notes |
|--------|---------|------|-------|
| outcome_summary | 1.0.0 | 2025-01 | Initial release |
| context_tracking | 1.0.0 | 2025-11 | Initial release |
| workspace | 1.0.0 | 2025-01 | Initial release |
| project_map | 1.0.0 | 2025-01 | Initial release |
| actor_summary | 1.0.0 | 2025-11 | Initial release |
| workspaces | 1.0.0 | 2025-01 | Initial release (shared) |

---

## Future Compatibility Considerations

### Planned Changes

Track upcoming breaking changes here:

**None currently planned.**

### Deprecation Notices

Fields/patterns scheduled for deprecation:

1. **outcome_track_schema.capabilities** (DEPRECATED in 2.1.0)
   - **Replacement**: `capabilityContributions`
   - **Removal Target**: v3.0.0
   - **Migration Path**: Automatic conversion in v2.1.0+

---

## Support and Questions

For schema compatibility questions:

1. Check this document first
2. Review plugin-specific migration guides in `plugins/{name}/MIGRATIONS.md`
3. Run workspace health check: `/workspace:health`
4. Open issue on GitHub: [lucid-toolkit/issues](https://github.com/rayk/lucid-toolkit/issues)

---

## Appendix: Schema Version Quick Reference

```
capability_track         v2.0.0  (Major: hierarchical + coreValues)
capability_summary       v1.1.0  (Minor: velocity tracking)
outcome_track            v2.1.0  (Minor: contribution percentages)
outcome_summary          v1.0.0  (Stable)
context_tracking         v1.0.0  (Stable)
workspace                v1.0.0  (Stable)
project_map              v1.0.0  (Stable)
actor_summary            v1.0.0  (Stable)
workspaces               v1.0.0  (Stable - shared)
execution_result         N/A     (Plan plugin)
audit_trail              N/A     (Plan plugin)
checkpoint               N/A     (Plan plugin)
```

---

**End of Document**
