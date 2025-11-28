# User Elicitation Reference

> **Purpose**: Guide Claude Code in gathering information from users intelligently—minimizing friction, maximizing accuracy through inference and smart defaults.

**Core Principle**: **Infer first, ask second.** Use context to reduce what users must provide from scratch.

---

## Quick Start: When to Use This

```
Generating a prompt that needs user input?
│
├─ Simple confirmation/yes-no?
│  └─ Use: Natural language pattern (Rule 1-2)
│
├─ 2-4 choices that need explanation?
│  └─ Use: AskUserQuestion tool
│
├─ 2-3 equal alternatives (self-explanatory)?
│  └─ Use: Natural language numbered list (Rule 6)
│
├─ Multiple related fields to confirm?
│  └─ Use: Natural language batch pattern (Rule 3)
│
└─ Complex decision with many options?
   └─ Use: AskUserQuestion tool with intelligent ordering
```

---

## Mental Model: The Two-Phase Process

### Phase 1: Internal Processing (YOU do this)
Before asking ANY question:

1. **Parse** user input for keywords, patterns, action verbs
2. **Load** workspace context (actors, values, capabilities, existing patterns)
3. **Infer** likely answers using rules + context
4. **Calculate** confidence scores (0-100%) for each inference
5. **Decide** presentation strategy based on confidence:
   - `>80%`: Show inferred value, ask confirmation only
   - `40-80%`: Pre-order options with likely ones first
   - `<40%`: Organize logically, no pre-selection

### Phase 2: Presentation (YOU structure the output)

**For AskUserQuestion tool**:
- Order options array by confidence (highest → lowest)
- Add "detected from X" hints to descriptions for high-confidence options
- The tool renders a flat list in the order YOU provide
- Your intelligence comes from pre-processing, not from special tool features

**For natural language**:
- Show inferred values prominently with "(inferred from X)"
- Structure as confirmation rather than open-ended question
- Provide escape hatch ("or specify different...")

---

## Decision Matrix: Which Approach?

| Scenario | Use | Why |
|----------|-----|-----|
| Yes/no decision | Natural language | Fastest, minimal ceremony |
| Confirm inferred value | Natural language | Show value, make rejection easy |
| 2-3 self-explanatory choices | Natural language (numbered) | Quick selection, no descriptions needed |
| 2-4 choices needing explanation | AskUserQuestion | Descriptions clarify implications |
| 5+ options, some inferable | AskUserQuestion + ordering | Intelligent ordering reduces cognitive load |
| Multiple related confirmations | Natural language (batch) | One context switch vs many |
| Complex research-backed options | Natural language + progressive disclosure | Summary first, details on request |

---

## Part 1: Natural Language Patterns

### Rule 1: Action Upfront, Explanation Brief

**Pattern**: `[ACTION]? (brief context)`

✅ **GOOD**:
- "Cleanup files? (I will delete all *.tmp and *.cache)"
- "Commit changes? (3 files modified)"
- "Run tests? (~2 minutes)"

❌ **BAD**:
- "I notice there are several temporary files. Would you like me to delete them?"

**Why**: User scans → decides → reads context if needed. Reduces time-to-decision from ~10s to ~2s.

---

### Rule 2: Show Inferred, Ask Confirmation

**Pattern**: Show value + reasoning, make rejection easy

✅ **GOOD**:
```
I'll use ID: `authentication-system` (from "Authentication System").

Continue? (or specify different ID)
```

❌ **BAD**:
```
What ID would you like to use?
```

**Why**: Review is faster than recall. Provides smart default + one-click confirmation.

---

### Rule 3: Batch Related Confirmations

**Pattern**: Group related decisions

✅ **GOOD**:
```
Ready to proceed with:
- ID: authentication-system
- Domain: Data Security & Privacy
- Type: Atomic
- Status: Active

Confirm? (or specify what to adjust)
```

❌ **BAD**: Asking each field separately in sequence

**Why**: One context switch instead of four. User sees complete picture.

---

### Rule 4: Progressive Detail

**Pattern**: Minimal initially, details on request

✅ **GOOD**:
```
Delete 47 temp files? (*.tmp, *.cache in /workspace/temp)
```

❌ **BAD**: Listing all 47 file paths upfront

**Why**: Reduces clutter. Details available if needed.

---

### Rule 5: Safe Default

**Pattern**: Make safe/reversible option the default

✅ **GOOD**:
```
Overwrite production config? (This will replace live settings)

Type 'yes' to confirm | Any other key to cancel
```

❌ **BAD**: Equal treatment of destructive vs safe options

**Why**: Accidental Enter doesn't cause damage.

---

### Rule 6: Numbered Choices for Equal Alternatives

**Pattern**: 2-3 equally valid options → numbered list

✅ **GOOD** (self-explanatory options):
```
Save files to:
1. /workspace/temp
2. /workspace/cache
3. Specify custom directory

Enter 1, 2, or 3:
```

**When to use**:
- Options are self-explanatory (no description needed)
- 2-4 choices
- No clear default
- User decision based on preference

**When NOT to use**:
- Options need explanation → use AskUserQuestion tool instead
- One option clearly better → use Rule 2 (show inferred)
- >4 options → use AskUserQuestion

---

### Rule 7: Order by Confidence

**Pattern**: First = most recommended/likely, Last = escape hatch

✅ **GOOD**:
```
Save build artifacts to:
1. /workspace/dist (recommended - standard)
2. /workspace/build (alternative)
3. Specify custom directory
```

**Why**: First option = implicit recommendation. Ordering signals understanding.

**Signal interpretation**: If user picks last option → your context understanding may be incomplete.

---

### Rule 8: Progressive Disclosure for Complex Research

**Pattern**: Summary → Full details (on request)

✅ **GOOD**:
```
I've analyzed three caching approaches:

**Option 1: Redis with client-side caching**
In-memory key-value with local cache
- Mature ecosystem, extensive tooling
- Client-side caching reduces roundtrips 60-80%
- Requires separate Redis instance
- Best for: Distributed systems

**Option 2: In-memory LRU with persistence**
Application-level cache with disk snapshots
- Zero infrastructure dependencies
- Simpler deployment
- Limited to single-instance
- Best for: Single-instance or dev

**Option 3: Hybrid (in-memory + Redis)**
Two-tier caching
- Combines benefits of both
- Increased invalidation complexity
- Best for: High-traffic with complexity budget

Which approach?
1. Redis with client-side caching
2. In-memory LRU
3. Hybrid
4. Show full analysis (benchmarks, trade-offs, code examples)

Enter 1-4:
```

**If user selects 4**: Display comprehensive markdown document, then re-ask with option 4 changed to "Skip this decision"

**Why**: Respects user time. Most decide from summary. Detailed users get full context without forcing it on everyone.

---

## Part 2: AskUserQuestion Tool

### Tool Parameters

The tool accepts ONLY:
```typescript
{
  question: string,        // The question text
  header: string,          // Short label (max 12 chars)
  multiSelect: boolean,    // true = multiple, false = single
  options: Array<{
    label: string,         // Concise (1-5 words)
    description: string    // Explanation of what this means
  }>
}
```

### How Confidence Translates to Tool Parameters

| Your Confidence | What YOU Do | Result |
|----------------|-------------|--------|
| **>80%** | Place first in options array | Rendered first |
|  | Add "(detected from X)" to description | Shows inference |
| **40-80%** | Place in middle of array | Rendered middle |
|  | Use standard explanatory description | Helpful context |
| **<40%** | Place toward end of array | Rendered later |
|  | Use neutral description | Generic help |

**Key insight**: The intelligence comes from YOUR pre-processing and ordering, not from special tool features. You make a flat list FEEL smart.

---

### Header Guidelines

**Rule**: Max 12 characters. Displayed as compact chips/tags.

✅ **GOOD**:
- "Auth method"
- "Library"
- "Actor"
- "Domain"
- "Value type"

❌ **BAD**:
- "Which authentication method would you like?"
- "Select the library you want to use"

**Why**: Long headers break layout. Keep noun-focused, not question-focused.

---

### Option Design

#### Labels
- Concise (1-5 words max)
- Parallel structure across options
- Use canonical names from workspace

✅ "Security", "Data Security & Privacy", "lot-owner", "OAuth 2.0"
❌ "Security-related concerns and threat protection"

#### Descriptions
- Explain what option means (don't restate label)
- Describe implications of selecting
- Provide context for trade-offs
- Under 100 chars when possible

✅ "Protect against threats, vulnerabilities, unauthorized access"
❌ "Security" (just repeating label)

---

### MultiSelect Decision

**Set `multiSelect: true` when**:
- Choices NOT mutually exclusive
- User commonly selects multiple (e.g., 1-3 values)
- Example: Primary business values

**Set `multiSelect: false` when**:
- Choices ARE mutually exclusive
- Only one makes logical sense
- Example: Domain category (capability has one domain)

---

### Intelligent Ordering Algorithm

```
1. Infer likely selections from context
2. Calculate confidence score (0-100%) for each option
3. Group options by category (if >10 options)
4. Score each category by aggregate relevance
5. Sort categories: highest → lowest score
6. Within category: Sort by individual confidence
7. Build options array in this order
```

**Example result**:
```javascript
options: [
  // High confidence (>80%) - place first
  { label: "Security", description: "Protect against threats (detected from 'secure auth')" },
  { label: "Compliance", description: "Meet regulatory requirements (detected from 'audit')" },

  // Medium confidence (40-80%) - middle
  { label: "Trust & Confidence", description: "User trust, brand reputation" },
  { label: "Privacy", description: "Data protection, user control" },

  // Low confidence (<40%) - end
  { label: "Revenue Enablement", description: "Unlock revenue opportunities" }
]
```

---

## Part 3: Inference Strategies

### Keyword Mapping Table

| Value | Keywords | Confidence |
|-------|----------|------------|
| Security | secure, authentication, authorization, encrypt, protect, auth, login, credentials, access control | 90% if 2+, 70% if 1 |
| Compliance | audit, compliance, regulatory, GDPR, SOC2, logging, tracking, governance | 85% if 2+, 65% if 1 |
| Performance | fast, optimize, performance, speed, efficient, latency, cache, scale | 80% if 2+, 60% if 1 |
| UX | user experience, UX, usability, interface, UI, intuitive, friendly, accessible | 85% if 2+, 65% if 1 |
| Data Quality | validate, verification, accuracy, completeness, consistency, quality, integrity | 80% if 2+, 60% if 1 |

**Multi-keyword boost**: When multiple keywords detected, boost confidence by 5-10%

Example: "Secure authentication with audit logging"
- "secure", "authentication" → Security (90% base → 95%)
- "audit", "logging" → Compliance (85% base → 90%)

---

### Semantic Patterns

| Pattern | Inference | Values Prioritized |
|---------|-----------|-------------------|
| "Enable users to...", "Allow customers to..." | User-facing capability | UX, Convenience, Trust |
| "Support multi-tenant...", "Ensure isolation..." | Platform/infrastructure | Security, Scalability, Maintainability |
| "Meet regulatory...", "Comply with..." | Compliance-driven | Compliance, Transparency, Data Quality |
| "Optimize...", "Improve performance..." | Technical optimization | Performance, Efficiency, Scalability |

### Action Verb Detection

| Verb Category | Examples | Inferred Value | Confidence |
|---------------|----------|----------------|------------|
| Protect verbs | secure, protect, guard, prevent, defend | Security | 80% |
| Enable verbs | enable, allow, permit, support, facilitate | User empowerment | 70% |
| Optimize verbs | optimize, improve, enhance, accelerate, streamline | Efficiency/Performance | 75% |
| Validate verbs | validate, verify, check, ensure, confirm | Data Quality/Compliance | 70% |

---

### Workspace Context Inference

**Load these before inferring**:
1. **Actor catalog**: `research/actor-stakeholders/actor-catalog.md`
2. **Value framework**: `research/value-framework/values-master.md`
3. **Existing capabilities**: `capabilities/**/*` (check for overlap)

**Adaptive inference per actor type**:

| Actor Type | High-Probability Values | Low-Probability Values |
|------------|------------------------|----------------------|
| End user (lot-owner, resident-tenant) | Security, Trust, Convenience, Privacy, UX | Observability, Maintainability, Cost Optimization |
| Administrator (strata-manager) | Security, Control, Observability, Efficiency, Compliance | UX, Convenience, Peace of Mind |
| Regulatory (ncat) | Compliance, Transparency, Fairness, Security, Data Quality | Revenue Enablement, Cost Optimization, UX |

---

## Part 4: Confidence-Based Presentation

### >80% Confidence: Show and Confirm

**Strategy**: Show inferred values prominently, ask for confirmation only

```
Inferred metadata (90% confidence):

ID: authentication-system
Domain: Data Security & Privacy
Type: Atomic
Status: Active

Options:
  ○ Confirm as shown (recommended)
  ○ Adjust ID
  ○ Adjust Domain
```

**User experience**: Fast confirmation for likely-correct inferences

---

### 40-80% Confidence: Pre-order with Guidance

**Strategy**: Order intelligently, place high-probability first, don't force selection

```
Select 1-3 PRIMARY business values:

High likelihood (detected from description):
  □ Security (75% confidence)
  □ Compliance (65% confidence)
  □ Trust & Confidence (55% confidence)

Technical Quality (category relevance: 60%):
  □ Privacy
  □ Dependability
  □ Performance

User & Stakeholder (category relevance: 45%):
  □ User Experience (UX)
  □ Convenience
```

**User experience**: Guided selection with intelligent ordering, user makes final call

---

### <40% Confidence: Organize, Don't Pre-select

**Strategy**: Logical organization by category, clear descriptions, no bias

```
Select the capability domain:

Technical Quality:
  ○ Data Security & Privacy - Security, authentication, authorization
  ○ Platform & Infrastructure - Scalability, deployment, infrastructure

Business Logic:
  ○ Business Logic - Core business rules and processes
  ○ Product Lifecycle - Feature development, roadmap

User Experience:
  ○ User Experience - UI/UX, interfaces, interactions

Operational:
  ○ Data Quality - Validation, accuracy, completeness
```

**User experience**: Unbiased selection with clear organization

---

## Part 5: Anti-Patterns (What NOT to Do)

| Anti-pattern | Why It's Bad | Fix |
|--------------|--------------|-----|
| **Too many questions** | Each question = context switch | Combine related fields into single questions |
| **No inference** | Forces user to select from 34 values alphabetically | Pre-select based on description, organize by relevance |
| **Flat lists** | Alphabetical dump is hard to scan | Group by category, sort by likelihood within groups |
| **No defaults** | Every field requires explicit input | Smart defaults for 80% of fields, user adjusts only what's wrong |
| **Vague options** | Options without descriptions are ambiguous | Clear labels + explanatory descriptions |
| **Forced multi-select** | Requiring exactly N when some need fewer | Allow flexibility (1-3) within bounds |
| **Inconsistent terminology** | "actors" vs "stakeholders" vs "personas" | Use one term consistently |
| **Asking before reading** | Proposing changes to code you haven't seen | ALWAYS read files before suggesting modifications |

---

## Part 6: Quick Reference Checklist

### Before Asking Any Question

- [ ] Parse user input for keywords, patterns, action verbs
- [ ] Load workspace context (actors, values, existing capabilities)
- [ ] Run inference rules (keyword + semantic + workspace)
- [ ] Calculate confidence scores (0-100%)
- [ ] Decide presentation strategy based on confidence

### For Natural Language Questions

- [ ] Action upfront, brief explanation after
- [ ] Show inferred values, ask confirmation (don't ask from scratch)
- [ ] Batch related confirmations
- [ ] Use progressive detail (minimal → more on request)
- [ ] Safe option as default for destructive actions
- [ ] Numbered choices for 2-3 equal alternatives
- [ ] Order by confidence (best first, escape hatch last)

### For AskUserQuestion Tool

- [ ] Short header (max 12 chars)
- [ ] Clear option labels (1-5 words)
- [ ] Explanatory descriptions (not just label restatement)
- [ ] MultiSelect appropriate (true if non-exclusive, false if exclusive)
- [ ] Intelligent ordering (high confidence → low confidence)
- [ ] Group by category if >10 options
- [ ] Add "(detected from X)" hints for high-confidence options

---

## Part 7: Complete Example

### Scenario
User creating: "Secure Authentication System"
Purpose: "Enable users to authenticate securely by implementing session management"

### Step 1: Inference Process

**Keyword extraction**:
- "secure", "authentication" → Security value (90%)
- "users", "authenticate" → User-facing (85%)
- "session management" → Compliance (70%)

**Load workspace**:
- Actors: lot-owner, strata-manager, resident-tenant, committee-member, owners-corporation, contractor, ncat
- Values: 34 values across 8 categories

**Apply rules**:
- User-facing → lot-owner (85%), strata-manager (80%), resident-tenant (75%)
- Admin keywords → strata-manager (boost to 90%)

**Final actor scores**:
- strata-manager: 90%
- lot-owner: 85%
- resident-tenant: 75%
- committee-member: 50%
- others: <40%

### Step 2: Actor Selection Question

```javascript
// Natural language approach (since actors are relatively self-explanatory):
"I've analyzed the capability description. Based on 'users authenticate', these actors likely benefit:

Detected actors (high confidence):
- strata-manager (manages authentication credentials)
- lot-owner (property owners using system)
- resident-tenant (tenants requiring access)

Should I also include:
- committee-member (governance functions)
- contractor (service provider access)

Which actors should I include? (confirm detected, add others, or specify different set)"

// OR AskUserQuestion approach (if actors need more explanation):
{
  question: "Which actors benefit from this capability?",
  header: "Actor",
  multiSelect: true,
  options: [
    {
      label: "strata-manager",
      description: "Manages authentication credentials and user access (detected: admin role)"
    },
    {
      label: "lot-owner",
      description: "Property owners using the system (detected: user-facing)"
    },
    {
      label: "resident-tenant",
      description: "Tenants requiring portal access (detected: user-facing)"
    },
    {
      label: "committee-member",
      description: "Committee members requiring secure access"
    },
    {
      label: "owners-corporation",
      description: "Corporate entity with governance oversight"
    },
    // Lower-confidence options at end...
  ]
}
```

### Step 3: Value Selection Per Actor

**For lot-owner (end user)**:
```javascript
{
  question: "Select the type of value lot-owner realizes from this capability",
  header: "Value type",
  multiSelect: true,
  options: [
    // High confidence for end user
    {
      label: "Security",
      description: "Protect personal data and prevent unauthorized access (detected from 'secure auth')"
    },
    {
      label: "Trust & Confidence",
      description: "Reliable authentication builds trust in platform"
    },
    {
      label: "Convenience",
      description: "Quick, easy login experience"
    },
    // Medium confidence
    {
      label: "Privacy",
      description: "Control over personal data and access information"
    },
    // Lower confidence...
  ]
}
```

**For strata-manager (admin)**:
```javascript
{
  question: "Select the type of value strata-manager realizes from this capability",
  header: "Value type",
  multiSelect: true,
  options: [
    // High confidence for admin
    {
      label: "Security",
      description: "Protect client scheme data and prevent unauthorized access (detected from 'secure auth')"
    },
    {
      label: "Control & Autonomy",
      description: "Manage user access and authentication policies (detected from admin role)"
    },
    {
      label: "Observability",
      description: "Monitor authentication activity and detect suspicious access"
    },
    // Medium confidence
    {
      label: "Efficiency",
      description: "Streamline user access management tasks"
    },
    // Lower confidence...
  ]
}
```

**Key difference**: Same capability, different actors → different value priorities and ordering

---

## Part 8: Token Efficiency Impact

### Naive Approach (no inference)
- User sees 34 values alphabetically
- Reads all descriptions
- Manually filters
- May select suboptimal choices
- **Tokens: ~750** | **Time: 2-3 min**

### Intelligent Approach (with inference)
- System pre-selects 2-3 likely values
- User reviews + confirms/adjusts
- Rarely needs to expand other groups
- **Tokens: ~350** | **Time: 30-60 sec**

### Efficiency Gains
- **53% token reduction**
- **67% time reduction**
- **80% accuracy on first try** (vs ~50% without)
- **Fewer clarification rounds** (1 in 5 vs 1 in 2)

---

## Summary: Core Principles

1. **Infer first, ask second** - Use all available context
2. **Show, don't ask** - Present inferred values for confirmation
3. **Order intelligently** - High confidence first, escape hatch last
4. **Adapt to context** - Different actors/domains → different priorities
5. **Respect attention** - Minimal cognitive load, progressive detail
6. **Combine questions** - Related fields together, reduce context switches
7. **Safe defaults** - Eliminate obvious questions with smart defaults
8. **Make rejection easy** - Always provide escape hatch

**Your role**: Calculate confidence internally, structure questions intelligently, make the user's job as easy as possible.