# Neo4j Implementation Plugin

A Claude Code plugin providing 6 specialized agents for Neo4j graph database development, optimized for modern Neo4j 5.x with property graphs, Cypher query language, and graph-native patterns.

## Philosophy

Deep expertise through specialized agents with clear handoffs. Each agent owns a specific domain of graph database development and knows when to delegate to others.

## Agent Selection Guide

| Need | Agent | When |
|------|-------|------|
| Graph schema design | `neo4j-modeler` | Node labels, relationships, properties |
| Query writing | `neo4j-query` | Cypher queries, APOC, GDS algorithms |
| Data import/export | `neo4j-data` | CSV, JSON, ETL, migrations |
| Performance issues | `neo4j-perf` | Slow queries, indexes, profiling |
| Application integration | `neo4j-driver` | Python/JS/Java drivers, OGM |
| Deployment/ops | `neo4j-env` | Docker, clustering, backups |

## Key Design Decisions

### 1. neo4j-modeler Owns Schema
Graph schema design is fundamentally different from relational:
- Node labels and their properties
- Relationship types and directions
- Constraints and indexes
- Data modeling patterns (hub-and-spoke, tree, linked list)

### 2. neo4j-query Owns ALL Cypher
Whether simple MATCH or complex graph algorithms:
- CRUD operations
- Path finding
- Aggregations
- APOC procedures
- Graph Data Science (GDS) algorithms

### 3. Handoff Protocol
Each agent explicitly declares handoffs to prevent overlap.

## Technology Stack

| Category | Tools |
|----------|-------|
| Database | Neo4j 5.x, AuraDB |
| Query Language | Cypher |
| Extensions | APOC, GDS (Graph Data Science) |
| Python | neo4j-driver, neomodel, py2neo |
| JavaScript | neo4j-driver, @neo4j/graphql |
| Java | neo4j-java-driver, Spring Data Neo4j |
| Visualization | Neo4j Browser, Bloom, NeoDash |
| Testing | Testcontainers, embedded mode |

## Agent Architecture

```
Neo4j Implementation Plugin
├─ DESIGN LAYER
│  └─ neo4j-modeler: Graph schema, constraints, data modeling patterns
├─ QUERY LAYER
│  └─ neo4j-query: Cypher queries, APOC, GDS algorithms
├─ DATA LAYER
│  └─ neo4j-data: Import/export, ETL, migrations, data quality
├─ PERFORMANCE LAYER
│  └─ neo4j-perf: Query tuning, indexes, profiling, memory
├─ INTEGRATION LAYER
│  └─ neo4j-driver: Language drivers, OGM, connection management
└─ OPERATIONS LAYER
   └─ neo4j-env: Deployment, clustering, backups, monitoring
```

## Example Workflow

```
User: "Build a recommendation engine using Neo4j"

1. neo4j-modeler: Designs graph schema (users, items, interactions)
2. neo4j-data: Imports existing user/item data
3. neo4j-query: Writes collaborative filtering Cypher
4. neo4j-perf: Adds indexes, optimizes queries
5. neo4j-driver: Integrates with application layer
6. neo4j-env: Configures production deployment
```

## MCP Integration

This plugin integrates with Neo4j MCP (Model Context Protocol) servers when available:

| Tool | Purpose |
|------|---------|
| `mcp__neo4j__get_schema` | Get database schema (labels, relationships, constraints) |
| `mcp__neo4j__execute_query` | Execute Cypher queries (read/write) |

Agents automatically use MCP tools for direct database interaction, eliminating manual connection management.

## Installation

```bash
/plugin install impl-neo4j@lucid-toolkit
```

## Usage

Agents are automatically available as subagent types in the Task tool:
```
Task(subagent_type="specialize:neo4j-modeler", prompt="...")
```
