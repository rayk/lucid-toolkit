Hierarchy & Abstraction Model

Three-Tier Abstraction

Platform Level (architecture/)
↓ describes intent, contracts, cross-cutting concerns
Repository Level (individual repos)
↓ describes implementation patterns, internal structure
Component Level (apps, services, packages)
↓ describes specific modules, APIs, data flows

Abstraction Principle: Each level answers questions appropriate to its scope. When you find yourself describing implementation details at the platform level, you've gone too deep—link to the child document instead.

Document Type Hierarchy

| Pattern           | Role                                              | Trust Level           |
  |-------------------|---------------------------------------------------|-----------------------|
| README.md         | Navigation index, entry point                     | Meta                  |
| ARCHITECTURE.md   | Root architecture (uppercase = authoritative)     | Highest at that level |
| architecture.md   | Child architecture (lowercase = inherits context) | Inherits from parent  |
| {topic}.md        | Focused topic document                            | Scoped to topic       |
| adr-NNN-{slug}.md | Decision record                                   | Historical record     |

  ---
Top-Level Platform Documents

| Document                   | Purpose                                                                                                                                             |
  |----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| README.md                  | Governance model, naming conventions, navigation index. Defines how to write architecture docs.                                                     |
| platform-overview.md       | Executive summary—what the platform is, project map showing all repositories and their relationships, deployment context. The "30,000 foot view."   |
| shared-concepts.md         | The nouns of the system—domain entities, semantic vocabulary, namespace/multi-tenancy model, entity identifiers, glossary. Defines shared language. |
| communication-protocols.md | The verbs of the system—how components communicate (transport protocols, serialization formats, message structures).                                |
| integration-patterns.md    | End-to-end flows—how components interact across boundaries. Shows how the nouns move via the verbs.                                                 |
| data-residency.md          | Where data lives—storage boundaries, sync patterns, privacy considerations, data locality.                                                          |
| cross-cutting-concerns.md  | Auth, security, observability, error handling—concerns that span all components.                                                                    |
| decisions/                 | ADR directory—captures why decisions were made, options considered, tradeoffs accepted. Append-only history.                                        |

  ---
Reading Paths

For understanding the platform:
platform-overview.md → shared-concepts.md → communication-protocols.md → integration-patterns.md

For implementing a feature:
Platform doc → Repository ARCHITECTURE.md → Component architecture.md

For understanding past decisions:
decisions/adr-NNN-*.md
