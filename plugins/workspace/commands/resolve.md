---
description: Resolve module references to absolute paths
argument-hint: <project:module[/subpath][#entry]>
---

<objective>
Resolve module references to absolute file paths for quick navigation within the workspace.

This command:
- Parses module reference syntax
- Looks up module in project_map.json
- Computes absolute path
- Returns structured resolution result
</objective>

<context>
Project map: @project_map.json
</context>

<reference_syntax>
## Reference Patterns

| Pattern | Example | Description |
|---------|---------|-------------|
| project:module | luon:neo4j_service | Module in specific project |
| module_id | neo4j_service | Search all projects (if unique) |
| project:module/subpath | luon:neo4j_service/cypher | Subpath within module |
| project:module#entry | luon:neo4j_service#CypherLoader | Entry point file |

## Examples

```
/workspace:resolve luon:neo4j_service
→ /Users/dev/luon/src/neo4j_service/

/workspace:resolve neo4j_service/cypher_loader
→ /Users/dev/luon/src/neo4j_service/cypher_loader/

/workspace:resolve luon:neo4j_service#CypherLoader
→ /Users/dev/luon/src/neo4j_service/cypher_loader.py
```
</reference_syntax>

<process>
1. **Parse Reference**:
   - Extract project name (optional)
   - Extract module_id
   - Extract subpath (optional)
   - Extract entry point (optional)

2. **Lookup Module**:
   - If project specified: Find in that project's modules
   - If module only: Search all projects (error if ambiguous)
   - Load from project_map.json

3. **Compute Path**:
   ```
   absolute_path = workspace_root + project.path + module.path + subpath
   ```

4. **Resolve Entry Point** (if specified):
   - Find entry point by name in module.entryPoints
   - Return file path for that entry

5. **Return Result**:
   ```json
   {
     "reference": "luon:neo4j_service",
     "project": "luon",
     "module": "neo4j_service",
     "path": "/absolute/path/to/module",
     "entry_file": "/path/to/entry.py",
     "exists": true
   }
   ```
</process>

<output_format>
## Success Output
```
Resolved: luon:neo4j_service

Project: luon
Module: neo4j_service
Type: service
Path: /Users/dev/luon/src/neo4j_service/

Entry Points:
- CypherLoader → cypher_loader.py
- QueryEngine → query_engine.py
```

## With Entry Point
```
Resolved: luon:neo4j_service#CypherLoader

File: /Users/dev/luon/src/neo4j_service/cypher_loader.py
Symbol: CypherLoader (class)
```

## Error Output
```
Error: Module 'unknown_service' not found

Did you mean:
- neo4j_service (luon)
- db_service (backend)
```

## Ambiguous Reference
```
Error: Module 'db_service' exists in multiple projects

Found in:
- luon: /src/db_service/
- backend: /services/db/

Use project:module syntax to disambiguate:
  /workspace:resolve luon:db_service
  /workspace:resolve backend:db_service
```
</output_format>

<project_map_structure>
## Module Definition in project_map.json

```json
{
  "projects": [
    {
      "name": "luon",
      "path": "./luon",
      "modules": [
        {
          "id": "neo4j_service",
          "name": "Neo4j Service",
          "path": "src/neo4j_service",
          "type": "service",
          "entryPoints": [
            {
              "name": "CypherLoader",
              "file": "cypher_loader.py",
              "symbol": "CypherLoader"
            }
          ]
        }
      ]
    }
  ]
}
```
</project_map_structure>

<success_criteria>
- Reference parsed correctly
- Module found in project_map
- Path computed and validated
- Entry point resolved (if specified)
- Clear error messages for not found/ambiguous
</success_criteria>
