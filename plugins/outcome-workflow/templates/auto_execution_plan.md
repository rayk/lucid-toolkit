# [Component Name]: Execution Plan (Modular)

<!-- 
LLM INSTRUCTION:
This is a MODULAR template. Follow these steps:
1. Identify your project domain from the Quick Start Profiles.
2. Use ONLY the Core sections + verification checks tagged for your domain.
3. DELETE all irrelevant verification steps to keep the plan focused.
-->

**Version**: {{VERSION}}
**Design**: [Link to Design Doc]
**Implementation**: [Link to Implementation Doc]
**Status**: Ready for Execution

---

## Quick Start Profiles

| Profile | Core + Verification Tags |
|---------|-------------------------|
| **Simple Script** | CORE only |
| **API Service** | CORE + [API] [WEB] |
| **Data Pipeline** | CORE + [DATA] |
| **ML Service** | CORE + [ML] [DATA] |
| **IoT Device** | CORE + [IOT] [HARDWARE] |
| **Frontend App** | CORE + [FRONTEND] [WEB] |
| **Platform Tool** | CORE + [PLATFORM] [OPS] |
| **Finance** | CORE + [FINANCE] [REGULATED] |

---

## Document Hierarchy (Source of Truth)

1. **Design**: Governs intent, behavior, user experience, and "why".
2. **Implementation**: Governs file paths, class names, signatures, and technical specifics.
3. **Execution Plan** (This Document): Governs the order of operations and testing strategy.

---

## PART A: CORE (Mandatory - All Projects)

### 1. Execution Strategy [CORE]
<!-- TDD, Iterative, Parallel Agents. -->
{{EXECUTION_STRATEGY}}

### 2. Pre-Execution Checklist [CORE]
<!-- Prerequisites that must be true before starting. -->
- [ ] {{PREREQUISITE_1}}
- [ ] Environment ready (Conda/Docker).

### 3. Mocking Strategy [CORE]
<!-- How will we handle external dependencies? -->
- **Database**: In-memory SQLite.
- **API**: Mock responses.

### 4. Execution Phases [CORE]

#### Phase 0: Scaffolding
**Goal**: Set up structure.
1. Create directory structure.
2. Initialize config.

**Validation**:
- Run: `ls -R src/`
- Check: Structure matches spec.

#### Phase 1: {{PHASE_NAME}}
**Goal**: {{GOAL}}

**Batch 1.1**: {{BATCH_NAME}}
1. Create test: `{{TEST_FILE}}`
2. Implement: `{{SOURCE_FILE}}`
3. Verify.

**Validation**:
- Run: `pytest {{TEST_PATH}}`

#### Phase N: Integration & Polish
...

### 5. Core Verification [CORE]
<!-- Baseline checks for ALL projects. -->
```bash
{{VERIFICATION_COMMAND}}
```

**Automated Verification**:
- [ ] All tests pass.
- [ ] Linter clean.

---

## PART B: DOMAIN-SPECIFIC VERIFICATION

<!-- DELETE ALL CHECKS BELOW THAT DON'T MATCH YOUR DOMAIN -->

### [API] [WEB] Service Checks
- [ ] Load Test: {{N}} req/sec sustained.
- [ ] API Contract: OpenAPI spec valid.

### [DATA] Pipeline Checks
- [ ] Reconciliation: Source vs Target row counts match.
- [ ] Data Quality: All rules pass.

### [ML] Model Checks
- [ ] Benchmark: Precision > 0.9.
- [ ] Drift: Model accuracy stable.

### [FRONTEND] [WEB] UI Checks
- [ ] A11y: Lighthouse score > 90.
- [ ] Visual: No regressions (Percy/Chromatic).
- [ ] SEO: Googlebot render check.

### [PLATFORM] [OPS] Infrastructure Checks
- [ ] Dry Run: `terraform plan` succeeds.
- [ ] Cost: Daily spend < ${{BUDGET}}.
- [ ] Cleanup: No orphaned resources.

### [HARDWARE] [IOT] Physical Checks
- [ ] Hardware: Print test receipt (Physical).
- [ ] HIL: Hardware-in-the-Loop test.

### [FINANCE] [REGULATED] Compliance Checks
- [ ] Audit: Logs immutable/signed.
- [ ] Latency: p99 < 100us.
- [ ] Precision: Decimal rounding correct.

### [SECURITY] All Secure Systems
- [ ] Security: Old secret invalid, new valid.
- [ ] Network Partition: Split-brain handled.

### [MEDIA] Streaming Checks
- [ ] Transcode: Output quality verified.
- [ ] DRM: License validation works.

### [GEO] Spatial Checks
- [ ] Geofence: Point-in-polygon accuracy.
- [ ] Routing: TSP solution optimal.

---

## 6. Rollout Strategy [PLATFORM] [OPS]
<!-- Canary, Blue/Green, Feature Flag. -->
- **Strategy**: Feature Flag `{{FLAG}}`.
- **Steps**: 10% -> Monitor -> 100%.

## 7. Rollback Plan [CORE]
<!-- How to undo changes. -->
```bash
git checkout -- {{PATH}}
```
