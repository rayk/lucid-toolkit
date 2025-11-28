# Token Tracking Reference

## CLI Environment Note

Claude Code CLI does not directly expose token counts. Use estimation:

```python
def estimate_tokens(text: str) -> int:
    """Estimate token count from text.

    Approximation: ~4 characters per token for English text.
    More accurate for code: ~3.5 characters per token.
    """
    return len(text) // 4
```

## Cost Formula (November 2025 Pricing)

| Model | Input (per 1M) | Output (per 1M) |
|-------|----------------|-----------------|
| Haiku | $0.25 | $1.25 |
| Sonnet | $3.00 | $15.00 |
| Opus | $15.00 | $75.00 |

**Update these values if pricing changes.**

## Cost Calculation

```python
COST_PER_MILLION = {
    "haiku": {"input": 0.25, "output": 1.25},
    "sonnet": {"input": 3.00, "output": 15.00},
    "opus": {"input": 15.00, "output": 75.00}
}

def calculate_cost(model, input_tokens, output_tokens):
    rates = COST_PER_MILLION[model]
    return (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000
```

## Audit Trail Schema

```json
{
  "execution_id": "uuid",
  "started_at": "ISO timestamp",
  "completed_at": "ISO timestamp",
  "total_duration_seconds": 0,
  "token_usage": {
    "total": {
      "input_tokens": 0,
      "output_tokens": 0,
      "estimated_cost_usd": 0.00
    },
    "by_model": {
      "haiku": {"input": 0, "output": 0, "calls": 0, "cost": 0.00},
      "sonnet": {"input": 0, "output": 0, "calls": 0, "cost": 0.00},
      "opus": {"input": 0, "output": 0, "calls": 0, "cost": 0.00}
    },
    "by_phase": {
      "phase_0_setup": {"input": 0, "output": 0, "duration_seconds": 0},
      "phase_1_scaffolding": {"input": 0, "output": 0, "duration_seconds": 0},
      "phase_2_foundation": {"input": 0, "output": 0, "duration_seconds": 0},
      "phase_3_core": {"input": 0, "output": 0, "duration_seconds": 0},
      "phase_4_features": {"input": 0, "output": 0, "duration_seconds": 0},
      "phase_5_integration": {"input": 0, "output": 0, "duration_seconds": 0},
      "phase_6_verification": {"input": 0, "output": 0, "duration_seconds": 0},
      "phase_7_debug": {"input": 0, "output": 0, "duration_seconds": 0},
      "phase_8_crosscheck": {"input": 0, "output": 0, "duration_seconds": 0}
    },
    "by_agent": []
  },
  "planned_estimates": {
    "total_tokens": 0,
    "total_duration_minutes": 0,
    "model_distribution": {"haiku": 0, "sonnet": 0, "opus": 0}
  },
  "variance": {
    "token_variance_percent": 0,
    "duration_variance_percent": 0,
    "notes": []
  }
}
```

## Per-Agent Tracking Protocol

Before each Task call:
```python
agent_start = {
    "agent_id": generate_uuid(),
    "phase": current_phase,
    "task": task_description,
    "model": model_name,
    "started_at": now()
}
```

After each Task call:
```python
agent_end = {
    **agent_start,
    "completed_at": now(),
    "duration_seconds": elapsed,
    "input_tokens": estimate_tokens(prompt),
    "output_tokens": estimate_tokens(response)
}
audit_trail["token_usage"]["by_agent"].append(agent_end)
```
