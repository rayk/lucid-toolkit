"""
workspace_info.constants - Default values and valid options.

This module defines constants used throughout workspace_info:
- VALID_ACTION_STATUS: Valid values for focus.actionStatus
- DEFAULTS: Default values when creating new workspace-info.toon
- WORKSPACE_INFO_PATH: Relative path to the file
- PROJECT_TYPES: Valid @type values for projects
"""
from typing import FrozenSet, Dict, Any

# Relative path to workspace-info.toon from workspace root
WORKSPACE_INFO_PATH = ".claude/workspace-info.toon"

# Valid values for focus.actionStatus field
# See: https://schema.org/ActionStatusType
VALID_ACTION_STATUS: FrozenSet[str] = frozenset({
    "PotentialActionStatus",   # Not started / no focus
    "ActiveActionStatus",      # Currently working on
    "CompletedActionStatus",   # Finished successfully
    "FailedActionStatus",      # Blocked or failed
})

# Valid @type values for projects in the project tabular array
PROJECT_TYPES: FrozenSet[str] = frozenset({
    "SoftwareApplication",  # Application code
    "SoftwareSourceCode",   # Library/shared code
    "WebApplication",       # Web app
    "MobileApplication",    # Mobile app
    "APIReference",         # API service
    "Plugin",               # Plugin module
})

# Default values for new workspace-info.toon files
# Used by WorkspaceInfo.create()
DEFAULTS: Dict[str, Any] = {
    "@context": "https://schema.org",
    "@type": "SoftwareSourceCode",
    "softwareVersion": "0.2.2",
    "workspace@type": "Project",
    "projects@type": "ItemList",
    "projects.numberOfItems": 0,
    "capabilities@type": "ItemList",
    "capabilities.path": "capabilities/",
    "capabilities.numberOfItems": 0,
    "outcomes@type": "ItemList",
    "outcomes.path": "outcomes/",
    "plans@type": "ItemList",
    "plans.path": "plans/",
    "plans.numberOfItems": 0,
    "executions@type": "ItemList",
    "executions.path": "executions/",
    "executions.numberOfItems": 0,
    "research@type": "ItemList",
    "research.path": "research/",
    "research.numberOfItems": 0,
    "ide@type": "SoftwareApplication",
    "ide.name": "none",
    "focus@type": "Action",
    "focus.name": None,
    "focus.target": None,
    "focus.actionStatus": "PotentialActionStatus",
    "lastSession.id": None,
    "lastSession.timestamp": None,
    "lastSession.event": None,
}
