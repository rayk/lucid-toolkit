# IDE MCP Tools Reference

Detailed patterns for using IDE integration tools effectively.

## Tool Overview

IDE MCP tools (`mcp__ide__*`) provide integration with the development environment, enabling file operations, project navigation, and diagnostic access.

## File Operations

### mcp__ide__readFile

Read contents of any project file.

**Use Cases:**
- Understanding existing implementations
- Reading configurations
- Checking test patterns
- Reviewing models/entities

**Best Practices:**
- Read before modifying (understand context)
- Read related files together (model + repository + tests)
- Check imports for dependencies

### mcp__ide__writeFile

Create or overwrite files.

**Use Cases:**
- Creating new Dart files
- Generating test files
- Writing configuration files
- Creating boilerplate

**Best Practices:**
- Verify directory exists first
- Follow project naming conventions
- Include proper imports
- Add file-level documentation

### mcp__ide__getCurrentEditor

Get the file currently active in the IDE.

**Use Cases:**
- Context-aware assistance
- Operating on user's focus
- Understanding user intent

**Best Practices:**
- Use to understand what user is working on
- Combine with getDiagnostics for targeted help

### mcp__ide__getOpenEditors

Get all files currently open in the IDE.

**Use Cases:**
- Understanding user's workspace context
- Finding related files user is working with
- Multi-file operations

## Project Navigation

### mcp__ide__searchInProject

Search for patterns across the project.

**Use Cases:**
- Finding usages of a function/class
- Locating implementations
- Finding test files for a module
- Searching for TODOs or FIXMEs

**Search Patterns:**
```
# Find class definitions
"class UserRepository"

# Find method usages
".authenticate("

# Find imports
"import 'package:my_app/src/auth"

# Find annotations
"@riverpod"

# Find TODOs
"// TODO"
```

**Best Practices:**
- Be specific to reduce noise
- Use with dart_resolve_symbol for full context
- Check test files alongside implementation

### mcp__ide__getProjectStructure

Get the project file tree.

**Use Cases:**
- Understanding project layout
- Finding correct directories for new files
- Verifying Clean Architecture layers
- Discovering existing patterns

**Typical Flutter Project Structure:**
```
lib/
├── src/
│   ├── core/           # Shared utilities, constants
│   ├── features/       # Feature modules
│   │   └── auth/
│   │       ├── data/       # Repositories, data sources
│   │       ├── domain/     # Entities, use cases
│   │       └── presentation/ # Widgets, view models
│   └── shared/         # Shared widgets, themes
├── main.dart
test/
├── src/
│   └── features/
│       └── auth/
│           ├── data/
│           └── domain/
integration_test/
```

## Diagnostics

### mcp__ide__getDiagnostics

Get IDE diagnostics for a specific file.

**Use Cases:**
- Pre-check before running analyzer
- Getting file-specific issues
- Understanding IDE errors

**Difference from dart_analyzer:**
- `getDiagnostics` → IDE's view of single file
- `dart_analyzer` → Full project analysis

**Best Practices:**
- Use for quick single-file checks
- Use dart_analyzer for comprehensive analysis
- Check diagnostics after edits

## Combined Workflows

### Creating a New Feature File

```
1. mcp__ide__getProjectStructure
   → Find correct directory for feature

2. mcp__ide__searchInProject("class.*Repository")
   → Find existing patterns to follow

3. mcp__ide__readFile (existing similar file)
   → Understand conventions

4. mcp__ide__writeFile (new file)
   → Create following patterns

5. dart_analyzer
   → Verify no issues

6. mcp__ide__getDiagnostics
   → Check IDE sees it correctly
```

### Understanding Existing Code

```
1. mcp__ide__getCurrentEditor
   → See what user is looking at

2. mcp__ide__getOpenEditors
   → Understand related context

3. mcp__ide__searchInProject
   → Find usages and implementations

4. dart_resolve_symbol
   → Get documentation for APIs
```

### Multi-File Refactoring

```
1. mcp__ide__searchInProject("oldMethodName")
   → Find all usages

2. For each file:
   mcp__ide__readFile → understand context
   mcp__ide__writeFile → apply changes

3. dart_analyzer
   → Verify no broken references

4. dart_run_tests
   → Verify behavior unchanged
```

## Tips

**File Path Handling:**
- Use absolute paths for reliability
- Check project structure for correct paths
- Follow platform conventions (lib/, test/, etc.)

**Search Efficiency:**
- Start specific, broaden if needed
- Use file extension filters when possible
- Combine with Glob for pattern matching

**Diagnostic Integration:**
- Check diagnostics after every write
- Address issues immediately
- Keep IDE and analyzer in sync
