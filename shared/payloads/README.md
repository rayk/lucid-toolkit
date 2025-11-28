# Shared Payloads

Session-scoped storage for large subagent outputs. Enables context conservation by storing verbose outputs externally while returning compact summaries to the main agent.

## Purpose

When subagents (research, analysis, documentation) generate large outputs:

1. **Full payload** saved to `shared/payloads/{session-id}/`
2. **Compact summary** returned to main agent with path reference
3. **Main agent** can Read full payload if details needed
4. **Auto-cleanup** when session ends

## Directory Structure

```
shared/payloads/
├── README.md                           # This documentation
├── .gitkeep                            # Ensures directory exists in git
│
├── {session-id}/                       # Session-scoped directory
│   ├── manifest.json                   # Index of stored payloads
│   ├── {timestamp}-{topic-slug}.md     # Individual payload files
│   └── ...
│
└── {another-session-id}/               # Another session
    └── ...
```

## Payload File Format

Each stored payload follows this structure:

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

{if applicable, list of sources used}
```

## Manifest File

Each session directory contains a `manifest.json`:

```json
{
  "sessionId": "sess-abc123",
  "createdAt": "2025-11-28T10:00:00Z",
  "payloads": [
    {
      "id": "20251128-100500-nsw-strata-legislation",
      "path": "20251128-100500-nsw-strata-legislation.md",
      "topic": "NSW Strata Legislation",
      "source": "research",
      "tokens": 4500,
      "createdAt": "2025-11-28T10:05:00Z",
      "summary": "Comprehensive research on NSW strata legislation..."
    }
  ],
  "totalTokensStored": 4500
}
```

## Retention Policy

- **Session-scoped**: Payloads deleted when session ends
- **Cleanup trigger**: Session end hook or 24h inactivity
- **Manual access**: User can Read payloads during session
- **No persistence**: Not intended for long-term storage

## Integration

### With payload-store Skill

The `payload-store` skill in `plugins/context/skills/` handles:
- Deciding when to store (>500 tokens or explicit instruction)
- Generating file paths and manifest entries
- Returning compact summaries with path references

### With Subagents

Subagents like `research` use payload-store protocol:
1. Generate full research output
2. Call payload-store pattern if output exceeds budget
3. Return TOON summary + `@stored: path/to/payload.md`

### With Session Lifecycle

Session end hooks should:
1. Check for session directory in `shared/payloads/`
2. Delete directory and contents
3. Log cleanup in session summary

## Usage Example

**Subagent returns:**
```toon
@stored: shared/payloads/sess-abc123/20251128-100500-nsw-strata-legislation.md

summary[3]{aspect,finding}:
  Primary Acts,"Strata Schemes Management Act 2015, Development Act 2015"
  Regulator,NSW Fair Trading
  Reform Status,Phase 2 of 5 reforms in progress

keyFindings: 2 main acts + 2 regulations govern strata in NSW
confidence: High
tokens_stored: 4500
```

**Main agent can:**
- Use summary for immediate response
- Read full payload if user asks for details
- Reference path in follow-up delegations
