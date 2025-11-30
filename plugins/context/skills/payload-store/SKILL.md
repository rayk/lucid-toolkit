---
name: payload-store
description: MANDATORY storage protocol for large subagent outputs. ALWAYS use when output exceeds 500 tokens, contains reference material, or caller specifies storage path. Triggers on research results, MCP tool output, documentation, comprehensive analysis, or any output that may need re-access.
allowed-tools:
  - Write
  - Read
---

<objective>
Prevent context bloat by storing verbose outputs externally while preserving accessibility. Returns compact TOON summary with `@stored` path reference so main context stays lean while full content remains accessible.

**This is not optional.** Any subagent output exceeding 500 tokens MUST use this protocol.
</objective>

<quick_start>
**When output exceeds 500 tokens:**

1. **Write payload** to `shared/payloads/{session-id}/{timestamp}-{topic-slug}.md`
2. **Update manifest** at `shared/payloads/{session-id}/manifest.json`
3. **Return TOON summary** with `@stored` path:

```toon
@stored: shared/payloads/sess-abc/20251128-topic.md

summary[N]{aspect,finding}:
  aspect1,finding1
  aspect2,finding2

keyFindings: One sentence synthesis
confidence: High
tokens_stored: 4500
```

**For explicit paths:** Skip manifest, use exact path provided.
</quick_start>

<triggers>
Store output externally when ANY apply:
- Output exceeds 500 tokens
- Contains reference material (legislation, specifications, documentation)
- Contains structured data (tables, lists >10 items)
- Caller provides explicit storage path
- Research depth is "comprehensive" or "thorough"
</triggers>

<storage_protocol>
<default_storage>
**When no path provided:**

Path: `shared/payloads/{session-id}/{timestamp}-{topic-slug}.md`

- `session-id`: From current session context (or generate UUID if unavailable)
- `timestamp`: Format `YYYYMMDD-HHMMSS`
- `topic-slug`: Lowercase, hyphens, max 50 chars derived from topic

Example: `shared/payloads/sess-abc123/20251128-100500-nsw-strata-legislation.md`
</default_storage>

<explicit_storage>
**When path provided:**

Use exact path and filename as specified. Supported formats:
- `.md` - Markdown (default structure)
- `.json` - JSON (preserve structure)
- `.txt` - Plain text (minimal formatting)

Example: If caller specifies `docs/research/strata-laws.md`, store there exactly.
</explicit_storage>

<file_structure>
```markdown
# {Topic Title}

**Generated:** {ISO timestamp}
**Source:** {subagent-name}
**Tokens:** {approximate token count}

---

## Summary

{2-3 sentence executive summary}

---

## Full Content

{complete payload content}

---

## Sources

{list of sources if applicable}
```
</file_structure>

<manifest_update>
When storing to default location, update or create manifest:

Path: `shared/payloads/{session-id}/manifest.json`

```json
{
  "sessionId": "{session-id}",
  "createdAt": "{first payload timestamp}",
  "payloads": [
    {
      "id": "{timestamp}-{topic-slug}",
      "path": "{filename}",
      "topic": "{human-readable topic}",
      "source": "{subagent-name}",
      "tokens": {count},
      "createdAt": "{ISO timestamp}",
      "summary": "{first 200 chars of summary}"
    }
  ],
  "totalTokensStored": {cumulative}
}
```
</manifest_update>
</storage_protocol>

<return_format>
**Always return this structure to caller:**

```toon
@stored: {full-path-to-payload}

summary[N]{aspect,finding}:
  {key aspect 1},{concise finding}
  {key aspect 2},{concise finding}
  ...

keyFindings: {1-2 sentence synthesis}
confidence: {High|Medium|Low}
tokens_stored: {count}
```

<constraints>
- Summary MUST be under 300 tokens
- Maximum 5-7 summary rows in TOON
- `keyFindings` is single line, no commas
- Path is always absolute from repository root
</constraints>
</return_format>

<workflow>
<step name="assess">
**1. Assess Storage Need**

Check triggers:
- Estimate output tokens (rough: chars / 4)
- Check for reference material markers
- Check if caller provided explicit path
- Default: store if >500 tokens
</step>

<step name="resolve_path">
**2. Resolve Storage Path**

If explicit path provided:
- Use exactly as specified
- Respect file extension for format

If no path:
- Get session ID from context
- Generate timestamp: `YYYYMMDD-HHMMSS`
- Slugify topic: lowercase, replace spaces with hyphens, max 50 chars
- Construct: `shared/payloads/{session-id}/{timestamp}-{slug}.md`
</step>

<step name="write_payload">
**3. Write Payload File**

Using Write tool:
- Create directory if needed (for default path)
- Write full content with metadata header
- Include sources section if applicable
</step>

<step name="update_manifest">
**4. Update Manifest** (default path only)

If storing to `shared/payloads/`:
- Read existing manifest or create new
- Append payload entry
- Update `totalTokensStored`
- Write manifest
</step>

<step name="generate_summary">
**5. Generate Return Summary**

Create TOON summary:
- Extract 5-7 key aspects and findings
- Synthesize 1-2 sentence `keyFindings`
- Assess confidence based on source quality
- Count tokens stored
- Format as return structure
</step>
</workflow>

<integration>
<with_research_agent>
Research agent should:
1. Complete full research workflow
2. Before returning, check output size
3. If >500 tokens or comprehensive research, invoke payload-store
4. Return TOON summary with `@stored` path
</with_research_agent>

<with_delegate_skill>
When delegating tasks that may produce large output:
```
Task(research, opus):
  "Research X comprehensively.

   If output exceeds 500 tokens, use payload-store protocol:
   - Store full output to shared/payloads/
   - Return TOON summary with @stored path

   @constraints: summary_max_tokens: 300"
```
</with_delegate_skill>

<with_conserve_skill>
The conserve skill should recommend payload-store when:
- Delegating to research/analysis agents
- MCP tools will return large content
- Output format specified as "report" or "comprehensive"
</with_conserve_skill>

<with_main_agent>
Main agent receives summary and can:
- Use summary for immediate user response
- Read full payload if user requests details
- Pass `@stored` path to subsequent subagents for context
</with_main_agent>
</integration>

<examples>
<example name="research_output">
**Scenario:** Research agent completed NSW strata legislation research (4500 tokens)

**Stored to:** `shared/payloads/sess-abc123/20251128-100500-nsw-strata-legislation.md`

**Returns:**
```toon
@stored: shared/payloads/sess-abc123/20251128-100500-nsw-strata-legislation.md

summary[4]{aspect,finding}:
  Primary Legislation,"Strata Schemes Management Act 2015 + Development Act 2015"
  Regulations,"Management Regulation 2016 + Development Regulation 2016"
  Regulator,NSW Fair Trading (mediation and compliance)
  Reform Status,5-phase reform 2023-2026 currently at Phase 2

keyFindings: NSW strata governed by 2 main acts from 2015 with major reform underway through 2026
confidence: High
tokens_stored: 4500
```
</example>

<example name="explicit_path">
**Scenario:** Caller specifies `docs/api-analysis.json`

**Input:**
```
Store this API analysis to docs/api-analysis.json
{large JSON payload}
```

**Action:**
- Write to exact path: `docs/api-analysis.json`
- Preserve JSON format
- No manifest update (not default location)

**Returns:**
```toon
@stored: docs/api-analysis.json

summary[3]{aspect,finding}:
  Endpoints,47 REST endpoints across 8 resources
  Auth,Bearer token with refresh flow
  Rate Limits,100 req/min standard tier

keyFindings: Well-structured REST API with comprehensive auth and rate limiting
confidence: High
tokens_stored: 3200
```
</example>

<example name="below_threshold">
**Scenario:** Output is 350 tokens, no explicit path

**Action:** Do NOT store externally. Return output directly.

This skill only activates when triggers are met.
</example>
</examples>

<error_handling>
<scenario name="write_failure">
If Write fails:
1. Report error to caller
2. Return full output inline (fallback)
3. Note: "payload-store failed, returning inline"
</scenario>

<scenario name="no_session_id">
If session ID unavailable:
1. Generate UUID for session directory
2. Proceed with storage
3. Note generated ID in manifest
</scenario>

<scenario name="path_conflict">
If file already exists at path:
1. For default path: append `-2`, `-3` etc. to slug
2. For explicit path: overwrite (caller's intent)
</scenario>
</error_handling>

<success_criteria>
**Verify successful storage:**

- File exists at reported `@stored` path (use Read to confirm)
- Manifest contains new entry with matching ID (for default paths)
- Returned summary is under 300 tokens
- `keyFindings` synthesizes core insights in 1-2 sentences (no commas)
- `tokens_stored` count matches actual stored content
- Path is absolute from repository root

**Anti-success indicators (storage failure):**

- Full output returned inline instead of stored
- Summary exceeds 300 tokens
- Missing `@stored` path in return
- Manifest not updated for default storage location
- Path uses relative instead of absolute reference
</success_criteria>
