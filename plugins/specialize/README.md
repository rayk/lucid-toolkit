# Specialize Plugin

Technology-specialized subagents with integrated MCP servers for working with specific platforms and tools.

## Installation

```
/plugin marketplace add rayk/lucid-toolkit
/plugin install specialize@lucid-toolkit
```

## Agents

### Neo4j (`neo4j`)

Expert agent for Neo4j AuraDB cloud database interactions.

**Capabilities:**
- Cypher query execution and optimization
- Graph data modeling and schema design
- Data import/export (CSV, JSON, APOC)
- AuraDB administration guidance
- Performance profiling and index recommendations

**Usage:**
```
Task tool with subagent_type: neo4j
```

### Research (`research`)

Web research specialist using Firecrawl MCP for comprehensive investigation of topics, technologies, APIs, and documentation.

**Capabilities:**
- Deep web research and source discovery
- Documentation scraping and synthesis
- Multi-source information gathering
- API documentation extraction and structuring
- Competitive analysis and technology evaluation
- Problem investigation across forums and issues

**Research Patterns:**
- Technology evaluation (pros/cons, comparisons)
- API documentation gathering
- Problem/error investigation
- Competitive analysis
- Documentation compilation
- Emerging topic exploration

**Usage:**
```
Task tool with subagent_type: research
```

**Example:**
> "Research the best practices for implementing OAuth 2.0 with PKCE flow"
> "Compare Prisma vs Drizzle vs TypeORM for a new TypeScript project"
> "Find documentation on the Stripe API webhooks"

### Debugger (`debugger`)

Expert debugging specialist using systematic root-cause analysis, defense-in-depth validation, and parallel investigation patterns.

**Core Principle:** NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST

**Methodology:**
1. **Root Cause Investigation** - Error analysis, reproducibility, change review, evidence gathering, data flow tracing
2. **Pattern Analysis** - Find working examples, study references, document differences
3. **Hypothesis Testing** - State hypothesis, make minimal change, verify results
4. **Implementation** - Create failing test, fix at root cause, add defense-in-depth

**Capabilities:**
- Systematic bug diagnosis (never guesses at fixes)
- Root cause tracing through call chains
- Defense-in-depth validation layers
- Parallel agent dispatch for multiple failures
- Regression investigation with git bisect
- Intermittent/flaky bug analysis

**Defense-in-Depth Layers:**
1. Entry point validation (reject invalid input)
2. Business logic validation (verify context)
3. Environment guards (prevent wrong-context operations)
4. Debug instrumentation (capture forensic context)

**Usage:**
```
Task tool with subagent_type: debugger
```

**Example:**
> "Debug why the authentication tests are failing intermittently"
> "Investigate the root cause of this TypeError in the payment flow"
> "We have 5 failing tests across different modules - help diagnose"

## MCP Servers

### Neo4j Server (`mcp-neo4j-cypher`)

Provides direct database connectivity to Neo4j instances including AuraDB.

**Package:** [mcp-neo4j-cypher](https://github.com/neo4j-contrib/mcp-neo4j/tree/main/servers/mcp-neo4j-cypher)

**Tools provided:**
- `read_neo4j_cypher` - Execute read-only Cypher queries
- `write_neo4j_cypher` - Execute write queries (CREATE, MERGE, DELETE, etc.)
- `get_neo4j_schema` - Retrieve database schema

**Required Environment Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Connection URI (e.g., `neo4j+s://xxx.databases.neo4j.io` for AuraDB, `bolt://localhost:7687` for local) | Required |
| `NEO4J_USERNAME` | Database username | `neo4j` |
| `NEO4J_PASSWORD` | Database password | Required |
| `NEO4J_DATABASE` | Target database name | `neo4j` |

**Optional Environment Variables:**

| Variable | Description |
|----------|-------------|
| `NEO4J_READ_TIMEOUT` | Query timeout in seconds |
| `NEO4J_RESPONSE_TOKEN_LIMIT` | Limit response size |
| `NEO4J_SCHEMA_SAMPLE_SIZE` | Schema sampling size (default 1000) |

### Neo4j Data Modeling Server (`mcp-neo4j-data-modeling`)

Provides graph data modeling tools without requiring database connection.

**Package:** [mcp-neo4j-data-modeling](https://github.com/neo4j-contrib/mcp-neo4j/tree/main/servers/mcp-neo4j-data-modeling)

**Capabilities:**
- Validate node, relationship, and complete data model structures
- Generate Mermaid diagrams for visualization
- Import/export Arrows.app JSON format
- Convert to/from OWL Turtle ontology format
- Generate Cypher constraints and bulk ingest queries
- Access example models (patient journey, supply chain, software dependencies, fraud detection)

**No environment variables required** - works standalone for modeling tasks.

### Firecrawl Server (`firecrawl`)

Provides web scraping, crawling, and search capabilities for research tasks.

**Package:** [firecrawl-mcp](https://github.com/firecrawl/firecrawl-mcp-server)

**Tools provided:**
- `firecrawl_scrape` - Extract content from a single URL (markdown, HTML, screenshots)
- `firecrawl_batch_scrape` - Process multiple URLs efficiently with parallel processing
- `firecrawl_check_batch_status` - Monitor batch operation progress
- `firecrawl_map` - Discover all indexed URLs on a website
- `firecrawl_crawl` - Multi-page extraction with depth control
- `firecrawl_search` - Web search to find information across the internet
- `firecrawl_extract` - Pull structured data from pages into JSON format

**Required Environment Variables:**

| Variable | Description |
|----------|-------------|
| `FIRECRAWL_API_KEY` | API key from [firecrawl.dev](https://firecrawl.dev) |

**Setup:**

1. Install the plugin:
   ```
   /plugin install specialize@lucid-toolkit
   ```

2. Set environment variables in your shell or `.claude/settings.json`:
   ```json
   {
     "env": {
       "NEO4J_URI": "neo4j+s://your-instance.databases.neo4j.io",
       "NEO4J_USERNAME": "neo4j",
       "NEO4J_PASSWORD": "your-password",
       "FIRECRAWL_API_KEY": "fc-your-api-key"
     }
   }
   ```

3. Restart Claude Code to activate the MCP servers

4. Verify with `/mcp` command - you should see all servers listed:
   - `neo4j-cypher` - database operations
   - `neo4j-modeling` - data modeling
   - `firecrawl` - web research

## Example Prompts

**Query data:**
> "Find all Person nodes connected by KNOWS relationships and show me the network"

**Design schema:**
> "Help me model a movie database with actors, directors, and genres"

**Import data:**
> "Import this CSV of customers and their orders into Neo4j"

**Optimize:**
> "This query is slow, help me profile and optimize it"

**Model data (no DB required):**
> "Design a graph model for a social network with users, posts, and comments"

**Generate Mermaid diagram:**
> "Create a visualization of this data model"

**Export to Arrows.app:**
> "Export this model to Arrows.app format so I can edit it visually"

**Research a technology:**
> "Research the Bun runtime - how does it compare to Node.js and Deno?"

**Investigate an API:**
> "Gather documentation on the OpenAI Assistants API and create a quick reference"

**Problem investigation:**
> "Research solutions for 'CORS errors with fetch' in serverless environments"

**Competitive analysis:**
> "Compare Supabase, Firebase, and PlanetScale for a new SaaS backend"

**Debug a failing test:**
> "This test started failing after the last PR - help me find the root cause"

**Investigate an error:**
> "Getting 'Cannot read property of undefined' deep in the middleware stack"

**Multiple failures:**
> "5 tests are failing with different errors - help me systematically diagnose them"

**Flaky test:**
> "This test passes locally but fails intermittently in CI"

## Adding New Specialists

This plugin is designed to be extended with additional technology specialists. Each specialist includes:

1. **Subagent** (`agents/{tech}.md`) - Expert agent definition
2. **MCP Server** (in `plugin.json`) - Tool integration for the technology

To add a new specialist, create the agent definition following the neo4j.md pattern and add the corresponding MCP server configuration to plugin.json.
