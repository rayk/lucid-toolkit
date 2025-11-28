# [Component Name]: Implementation Specification (Modular)

<!-- 
LLM INSTRUCTION:
This is a MODULAR template. Follow these steps:
1. Identify your project domain from the Quick Start Profiles.
2. Use ONLY the Core sections + sections tagged for your domain.
3. DELETE all Extension sections not relevant to your project.
-->

**Version**: {{VERSION}}
**Design Document**: [Link to Design Doc]

---

## Quick Start Profiles

| Profile | Use Sections | Domain Tags |
|---------|--------------|-------------|
| **Simple Script** | CORE only | N/A |
| **API Service** | CORE + [API] [WEB] | API, WEB |
| **Data Pipeline** | CORE + [DATA] | DATA |
| **ML Service** | CORE + [ML] [DATA] | ML, DATA |
| **IoT Device** | CORE + [IOT] [HARDWARE] | IOT, HARDWARE |
| **Frontend App** | CORE + [FRONTEND] [WEB] | FRONTEND, WEB |
| **Platform Tool** | CORE + [PLATFORM] [OPS] | PLATFORM, OPS |
| **Finance System** | CORE + [FINANCE] [REGULATED] | FINANCE, REGULATED |

---

## Document Hierarchy (Source of Truth)

1. **Design**: Governs intent, behavior, user experience, and "why".
2. **Implementation** (This Document): Governs file paths, class names, signatures, and technical specifics.
3. **Execution Plan**: Governs the order of operations and testing strategy.

---

## PART A: CORE (Mandatory - All Projects)

### 1. Overview [CORE]
<!-- Brief technical summary of what is being built. -->
{{TECHNICAL_SUMMARY}}

### 2. Module Structure [CORE]
<!-- File tree of new/modified files. Mark as # NEW, # UPDATE, # DELETE. -->
```
src/
├── components/
│   └── my_component.py      # NEW
└── config.py                # UPDATE
```

### 3. Component Specifications [CORE]
<!-- For each file, describe classes and functions. -->

#### 3.1 {{FILE_PATH}}

**Action**: {{NEW/UPDATE/EXTEND}}

**Class / Resource**: {{NAME}}
```python
class {{CLASS_NAME}}:
    """{{DOCSTRING}}"""
```

**Functions**:
```python
def {{FUNCTION_NAME}}() -> None:
    pass
```

**Error Handling**:
- **Edge Case**: {{CASE}} -> Returns None
- **Exception**: `{{ERROR}}` when {{CONDITION}}

### 4. Dependencies [CORE]
<!-- Runtime and Dev dependencies. -->
- Runtime: `{{PACKAGE}}` ({{VERSION}})
- System: `{{TOOL}}`

### 5. Requirement Traceability [CORE]
<!-- Map Design requirements to Implementation components. -->
| Requirement (Design) | Component | Test |
|---------------------|-----------|------|
| {{REQ_1}} | `{{CLASS}}` | `{{TEST}}` |

---

## PART B: EXTENSIONS (Domain-Specific - Use Only If Tagged)

<!-- DELETE ALL SUBSECTIONS BELOW THAT DON'T MATCH YOUR DOMAIN -->

### 6. Configuration & Secrets [API] [PLATFORM] [OPS]
- **Env Vars**: `{{VAR}}` (Default: `{{VALUE}}`).
- **Secrets**: `vault/app/db-pass`.
- **Feature Flags**: `enable_new_ui`.

### 7. Queries & Events [DATA] [API] [INTEGRATION]
- **Query**: `SELECT * FROM users WHERE ...`
- **Event Emits**: `ORDER_CREATED`
- **Event Listens**: `PAYMENT_RECEIVED`

### 8. Frontend & Assets [WEB] [MOBILE] [FRONTEND] [GAME]
- **Assets**: Textures, Fonts, 3D Models.
- **i18n**: Translation Keys (ICU MessageFormat).

### 9. Systems & Hardware [HARDWARE] [IOT] [EMBEDDED] [FINANCE]
- **Hardware**: GPIO `/dev/ttyUSB0` (9600 baud).
- **Memory**: Unsafe blocks / Manual management.
- **Numerics**: `BigDecimal` / Banker's Rounding.

### 10. Data & ML [DATA] [ML] [PLATFORM]
- **Lineage**: DVC Paths / S3 Buckets.
- **CRDs**: Kubernetes Custom Resources.
- **Metadata**: Catalog Owner / Docstrings.

### 11. Domain Specifics [MEDIA] [GEO] [HEALTH] [FINANCE] [INDUSTRIAL]
- **[MEDIA]** FFmpeg: `libx264` (Preset: slow).
- **[GEO]** Spatial Index: H3 (Resolution 9).
- **[HEALTH]** Standards: FHIR R4.
- **[FINANCE]** Protocol: FIX 4.4.
- **[INDUSTRIAL]** Protocol: Modbus TCP (Port 502).

### 12. Observability [API] [PLATFORM] [OPS] [DATA]
<!-- Metrics/Logs/Spans. -->
- **Metric**: `order_processing_time` (Histogram).
- **Log**: Error trace on failure.
- **Span**: `db_query` (Middleware).
