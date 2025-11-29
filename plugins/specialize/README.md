# Specialize Plugin

Technology-specialized subagents with integrated MCP servers for working with specific platforms and tools.

## Installation

```
/plugin marketplace add rayk/lucid-toolkit
/plugin install specialize@lucid-toolkit
```

## Color Coding System

Each specialist agent is assigned an intuitive color based on its function category:

| Color | Category | Meaning | Agents |
|-------|----------|---------|--------|
| 🔴 **Red** | Diagnostic | Problems, errors, investigation | `debugger` |
| 🔵 **Blue** | Construction | Building, generating, creating | `flutter-coder` |
| 🟢 **Green** | Construction | Building, generating, creating | `python-coder` |
| 🟣 **Purple** | Knowledge | Research, analysis, information | `research` |
| 🩵 **Cyan** | Data | Databases, queries, storage | `neo4j` |
| 🟡 **Yellow** | Infrastructure | Environment, config, deployment | `flutter-env`, `python-env` |

**Color Philosophy:**
- **Red** signals attention-requiring work (debugging, fixing)
- **Blue** represents Flutter/Dart code generation
- **Green** represents Python code generation
- **Purple** denotes intellectual/analytical work (research)
- **Cyan** indicates data-centric operations (databases)
- **Yellow** indicates infrastructure/environment work (setup, config, CI/CD)

Colors appear in the Claude Code CLI when agents are invoked, making it easy to visually track which specialist is active.

---

## Agents

### Debugger (`debugger`) 🔴

Expert debugging specialist using systematic root-cause analysis and defense-in-depth validation.

**Core Principle:** NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST

**Methodology:**
1. **Investigation** - Error analysis, reproducibility, change review, evidence gathering, data flow tracing
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
Task tool with subagent_type: specialize:debugger
```

**Example Prompts:**
> "Debug why the authentication tests are failing intermittently"
> "Investigate the root cause of this TypeError in the payment flow"
> "We have 5 failing tests across different modules - help diagnose"

---

### Python Environment (`python-env`) 🟡

Python environment infrastructure specialist for setup, diagnosis, and repair of development, testing, and deployment environments.

**Core Principle:** DIAGNOSE BEFORE FIXING - Never apply fixes without confirming root cause matches symptom.

**Methodology:**
1. **Diagnose** - Gather environment state with diagnostic commands
2. **Plan** - Identify minimal fix and verification command
3. **Apply** - Execute fix with rollback strategy
4. **Verify** - Confirm original symptom is resolved

**Capabilities:**
- uv package management and shell integration
- pyright strict mode configuration and IDE integration
- ruff linting and formatting setup
- Docker multi-stage builds with uv
- GitHub Actions CI/CD with caching optimization
- PyPI trusted publishers (OIDC)
- Google Cloud Functions and Cloud Run deployment
- BigQuery, Pub/Sub, and Secret Manager integration
- Jupyter kernel management with uv
- Neo4j Python driver and Docker setup
- IntelliJ/PyCharm JVM tuning
- pre-commit hook configuration
- Local automation with just/nox
- Data science stack (NumPy, Pandas, Polars, GPU)

**Complementary to python-coder:** This agent handles infrastructure (environment, build, CI/CD, deployment). Use python-coder for application code generation.

**Usage:**
```
Task tool with subagent_type: specialize:python-env
```

**Example Prompts:**
> "uv sync fails with resolver conflicts"
> "pyright shows errors but my IDE shows none"
> "Docker build is slow, help optimize caching"
> "CI builds take 15+ minutes on GitHub Actions"
> "Cloud Function cold starts are too slow"
> "Help me set up Jupyter with the project's uv environment"
> "Neo4j connection fails from Python"

---

### Python Coder (`python-coder`) 🟢

Python 3.12+ code generation specialist with modern Rust-based tooling (uv, ruff, pyright) and production-grade patterns.

**Core Principles:**
- Strict typing with pyright strict mode
- Modern tooling (uv, ruff, pyright, just)
- Structured logging with structlog
- Test-Driven Development (Red-Green-Refactor)

**Capabilities:**
- Python 3.12 generic syntax (PEP 695)
- uv package management and virtual environments
- ruff linting with security rules (Bandit)
- pyright strict type checking
- structlog with correlation IDs
- Pydantic for boundary validation
- Pydantic Settings for configuration
- Hypothesis property-based testing
- Multi-stage Docker builds with uv

**Modern Toolchain:**
- `uv` - Universal package manager (10-100x faster than pip)
- `ruff` - Linter and formatter (replaces flake8, black, isort)
- `pyright` - Type checker (strict mode)
- `just` - Task runner (replaces Makefile)

**Usage:**
```
Task tool with subagent_type: specialize:python-coder
```

**Example Prompts:**
> "Generate a FastAPI service with Pydantic models"
> "Create a CLI tool with structured logging"
> "Build a data processing pipeline with proper error handling"

---

### Flutter Coder (`flutter-coder`) 🔵

Flutter/Dart code generation specialist enforcing functional programming patterns, Riverpod 3.0, and Clean Architecture.

**Core Principles:**
- Errors as values (Either/TaskEither, not try-catch)
- Immutability (Dart 3 records, Freezed)
- Test-Driven Development (Red-Green-Refactor)
- Zero lint tolerance (0 errors, 0 warnings)

**Capabilities:**
- fpdart functional patterns (Option, Either, TaskEither, Do notation)
- Riverpod 3.0 code generation (@riverpod annotations)
- Clean Architecture layer separation (domain/data/presentation)
- Sealed class failure hierarchies
- AsyncNotifier with ref.mounted checks
- Widget extraction and const optimization

**MCP Servers Used:**
- `mcp__ide__*` - IntelliJ IDE for file operations
- `mcp__dart__*` - Dart/Flutter for analysis, testing, formatting

**TDD Workflow:**
1. Write test file first
2. Verify RED (tests fail)
3. Implement minimally
4. Verify GREEN (tests pass)
5. Refactor for patterns
6. Run dart_analyzer (0 issues)
7. Run dart_format

**Usage:**
```
Task tool with subagent_type: specialize:flutter-coder
```

**Example Prompts:**
> "Generate a UserRepository with TaskEither patterns"
> "Create an authentication feature following Clean Architecture"
> "Build a shopping cart AsyncNotifier with proper mounted checks"

---

### Research (`research`) 🟣

Senior Research Analyst and Fact-Checker using Firecrawl MCP for rigorous investigation with authoritative source evaluation.

**Core Principle:** Every claim must be traceable to a credible, evaluated source.

**Source Authority Priority:**
1. `.edu` - Educational institutions
2. `.gov` - Government agencies
3. Reputable `.org` - Standards bodies, professional associations
4. Official vendor/project documentation
5. Peer-reviewed journals and academic publications
6. Major news outlets with editorial standards

**Automatic Disqualification:**
- Content farms, SEO blogs
- Forums as primary sources (Reddit, Quora)
- Anonymous or "admin" bylines
- Affiliate-heavy product reviews
- Sites without clear editorial process

**Capabilities:**
- Deep web research with source verification
- Documentation scraping and synthesis
- Cross-reference verification across sources
- Structured data extraction from official sources
- Technology evaluation and comparison
- API documentation gathering

**MCP Server:** `firecrawl` (search, scrape, crawl, extract)

**Usage:**
```
Task tool with subagent_type: specialize:research
```

**Example Prompts:**
> "Research the best practices for implementing OAuth 2.0 with PKCE flow"
> "Compare Prisma vs Drizzle vs TypeORM for a new TypeScript project"
> "Find official documentation on the Stripe API webhooks"
> "Investigate solutions for CORS errors in serverless environments"

---

### Flutter Environment (`flutter-env`) 🟡

Flutter environment infrastructure specialist for setup, diagnosis, and repair of development, testing, and deployment environments.

**Core Principle:** DIAGNOSE BEFORE FIXING - Never apply fixes without confirming root cause matches symptom.

**Methodology:**
1. **Diagnose** - Gather environment state with diagnostic commands
2. **Plan** - Identify minimal fix and verification command
3. **Apply** - Execute fix with rollback strategy
4. **Verify** - Confirm original symptom is resolved

**Capabilities:**
- FVM version management and shell/IDE integration
- Apple Silicon CocoaPods architecture conflicts
- Firebase emulator networking (Android/iOS/physical device)
- R8 code shrinking and ProGuard keep rules
- macOS entitlements and notarization
- very_good_analysis strict mode configuration
- Melos monorepo orchestration
- IntelliJ JVM heap tuning
- Gradle flavors and signing configuration
- CI/CD caching strategies (GitHub Actions, Codemagic)
- DTD runtime connection for hot reload and debugging

**Complementary to flutter-coder:** This agent handles infrastructure (environment, build, CI/CD). Use flutter-coder for application code generation.

**Usage:**
```
Task tool with subagent_type: specialize:flutter-env
```

**Example Prompts:**
> "iOS simulator build fails with arm64 linker errors on my M2 Mac"
> "Flutter app can't connect to Firebase emulators from Android emulator"
> "Release build crashes but debug works fine"
> "CI builds are taking 15+ minutes, help optimize caching"
> "Help me set up FVM for this project"

---

### Neo4j (`neo4j`) 🩵

Expert Neo4j graph database specialist for AuraDB cloud, Cypher queries, data modeling, and capability-driven development integration.

**Capabilities:**
- Cypher query language (read, write, aggregations, path traversal, APOC)
- Neo4j AuraDB cloud platform administration
- Graph data modeling best practices
- Data import/export (CSV, JSON, Arrows.app, OWL ontologies)
- Performance optimization (indexes, query profiling)
- Lucid Toolkit integration (capabilities, outcomes, workspaces)

**MCP Servers:**
- `neo4j-cypher` - Database operations (read/write queries, schema)
- `neo4j-modeling` - Data modeling (validation, visualization, import/export)

**Workflow Phases:**
1. **Connect** - Verify environment variables
2. **Understand** - Inspect schema or find templates
3. **Design** - Define and validate model
4. **Implement** - Generate constraint and ingest queries
5. **Execute** - Run safely with verification
6. **Validate** - Query counts, test traversals

**Usage:**
```
Task tool with subagent_type: specialize:neo4j
```

**Example Prompts:**
> "Find all Person nodes connected by KNOWS relationships"
> "Help me model a movie database with actors, directors, and genres"
> "Import this CSV of customers and their orders into Neo4j"
> "This query is slow, help me profile and optimize it"

---

## MCP Servers

### Neo4j Cypher Server (`mcp-neo4j-cypher`)

Direct database connectivity to Neo4j instances including AuraDB.

**Package:** [mcp-neo4j-cypher](https://github.com/neo4j-contrib/mcp-neo4j/tree/main/servers/mcp-neo4j-cypher)

**Tools:**
- `read_neo4j_cypher` - Execute read-only Cypher queries
- `write_neo4j_cypher` - Execute write queries (CREATE, MERGE, DELETE)
- `get_neo4j_schema` - Retrieve database schema

**Required Environment Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Connection URI | Required |
| `NEO4J_USERNAME` | Database username | `neo4j` |
| `NEO4J_PASSWORD` | Database password | Required |
| `NEO4J_DATABASE` | Target database | `neo4j` |

### Neo4j Data Modeling Server (`mcp-neo4j-data-modeling`)

Graph data modeling tools (no database connection required).

**Package:** [mcp-neo4j-data-modeling](https://github.com/neo4j-contrib/mcp-neo4j/tree/main/servers/mcp-neo4j-data-modeling)

**Capabilities:**
- Validate node, relationship, and data model structures
- Generate Mermaid diagrams for visualization
- Import/export Arrows.app JSON format
- Convert to/from OWL Turtle ontology format
- Generate Cypher constraints and bulk ingest queries
- Access example models (patient journey, supply chain, fraud detection)

### Firecrawl Server (`firecrawl`)

Web scraping, crawling, and search for research tasks.

**Package:** [firecrawl-mcp](https://github.com/firecrawl/firecrawl-mcp-server)

**Tools:**
- `firecrawl_scrape` - Extract content from single URL
- `firecrawl_batch_scrape` - Process multiple URLs in parallel
- `firecrawl_map` - Discover all URLs on a website
- `firecrawl_crawl` - Multi-page extraction with depth control
- `firecrawl_search` - Web search across the internet
- `firecrawl_extract` - Structured data extraction to JSON

**Required:** `FIRECRAWL_API_KEY` from [firecrawl.dev](https://firecrawl.dev)

### Dart/Flutter MCP Server

Official Dart and Flutter development tools.

**Tools:**
- `dart_analyzer` - Static analysis for errors and warnings
- `dart_run_tests` - Execute tests and analyze results
- `dart_format` - Code formatting
- `dart_fix` - Apply automated fixes
- `pub_dev_search` - Search packages on pub.dev
- `dart_resolve_symbol` - Resolve symbols and documentation

**Required:** Dart 3.9+ / Flutter 3.35+ beta

### IntelliJ IDE MCP Server

IDE integration for file operations and project navigation.

**Tools:**
- `mcp__ide__readFile` - Read file contents
- `mcp__ide__writeFile` - Write/create files
- `mcp__ide__getDiagnostics` - Get IDE diagnostics
- `mcp__ide__searchInProject` - Search across project
- `mcp__ide__getProjectStructure` - Get file tree

---

## Setup

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

3. Restart Claude Code to activate MCP servers

4. Verify with `/mcp` command

---

## Adding New Specialists

Each specialist includes:

1. **Agent definition** (`agents/{name}.md`)
   - YAML frontmatter with name, description, tools, model, color
   - XML-structured prompt with role, constraints, workflow

2. **MCP Server** (in `plugin.json`)
   - Tool integration for the technology

3. **Color assignment**
   - Red: Diagnostic/debugging
   - Blue: Construction/generation (Flutter/Dart)
   - Green: Construction/generation (Python)
   - Purple: Research/analysis
   - Cyan: Data/databases
   - Yellow: Infrastructure/environment
   - Orange: Deployment/operations (reserved)
   - Pink: Design/creative (reserved)
