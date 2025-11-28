---
description: Resolve a module reference to its absolute path
arguments:
  - name: reference
    description: "Module reference to resolve. Formats: project:module, module_id, project:module#entry, project:module/subpath"
    required: true
---

# Module Reference Resolver

Resolve module references to absolute paths for quick navigation.

## Reference Syntax

| Pattern | Example | Resolves To |
|---------|---------|-------------|
| `project:module` | `luon:neo4j_service` | `/Users/.../luon/neo4j_service` |
| `module_id` | `neo4j_service` | Same (if unique) |
| `project:module/subpath` | `luon:neo4j_service/cypher_loader` | `.../neo4j_service/cypher_loader` |
| `project:module#entry` | `luon:neo4j_service#CypherLoader` | `.../cypher_loader/loader.py` |

## Input
Reference: $ARGUMENTS

## Workflow

1. **Parse Reference**
   - Extract: project (optional), module_id, subpath (optional), entry (optional)
   - Validate format against pattern

2. **Lookup Module**
   - If project specified: lookup `project:module_id` in project_map.json
   - If no project: search all projects for module_id
   - Error if not found or ambiguous

3. **Compute Path**
   - workspace_root + project.path + module.path = base path
   - Append subpath if specified
   - If entry specified, lookup in module.entryPoints

4. **Return Result**
   ```json
   {
     "reference": "luon:neo4j_service",
     "project": "luon",
     "module": "neo4j_service",
     "path": "/absolute/path/to/module",
     "entry_file": "/path/to/entry.py"  // if #entry specified
   }
   ```

## CLI Usage

```bash
# Via Python script
python3 scripts/module_resolver.py luon:neo4j_service

# List all modules
python3 scripts/module_resolver.py --list

# List modules for specific project
python3 scripts/module_resolver.py --list luon
```

## Agent Usage

When an agent needs to find a module path:

1. Check if reference matches a known module in project_map.json
2. Use this command to get the absolute path
3. Navigate directly instead of searching

Example:
```
User: "Where is neo4jService?"
Agent: /project:resolve neo4j_service
Result: luon:neo4j_service -> /Users/rayk/Projects/luon/neo4j_service
```

## Error Cases

- **Not found**: Module ID doesn't exist in any project
- **Ambiguous**: Multiple projects have modules with same ID (use `project:module` form)
- **Invalid format**: Reference doesn't match expected pattern
- **Entry not found**: Specified #entry doesn't exist in module.entryPoints