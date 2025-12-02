# Changelog

All notable changes to the ws plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-12-02

### Fixed

- `/ws:version` command now works in installed plugins by embedding version info directly
- Removed dependency on @path dynamic context that only resolves in source repo

### Changed

- `/pub-ws` command now syncs version.md during releases (Phase 5.5)

## [0.1.0] - 2025-12-02

### Added

- Initial plugin structure with plugin.json metadata
- Five key areas: Capabilities (cap), Outcomes (out), Designs (des), Plans (pln), Execution (exe)
- `/ws:version` command - display version and recent changelog entries
- `/ws:report` command - capture fault reports for debugging with session context
- `/ws:enviro` command - idempotent workspace environment management (setup, repair, migrate, report)
- `workspace-info.toon` template using schema.org vocabulary for workspace snapshots
- Comprehensive scanning for IntelliJ .idea/, project-map.json, and technology indicators
- README.md documentation
