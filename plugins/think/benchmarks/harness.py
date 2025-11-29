#!/usr/bin/env python3
"""
Benchmark harness for measuring think plugin performance.
Tracks: execution time, token usage, agent calls, model distribution.

Usage:
    python harness.py --baseline    # Measure v1.0
    python harness.py --v2          # Measure v2.0
    python harness.py --compare     # Compare both
"""

import json
import time
import sys
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class AgentCall:
    """Record of a single agent invocation."""
    agent_name: str
    model: str  # haiku, sonnet, opus
    input_tokens: int
    output_tokens: int
    cache_tokens: int
    duration_ms: int
    success: bool


@dataclass
class BenchmarkRun:
    """Complete record of a benchmark test run."""
    run_id: str
    command: str  # consider, assess, debate, swarm
    problem_type: str
    problem_text: str
    version: str  # v1.0 or v2.0
    start_time: str
    end_time: str
    total_duration_ms: int
    agent_calls: List[AgentCall] = field(default_factory=list)
    parallel_batches: int = 0
    sequential_steps: int = 0
    final_confidence: float = 0.0
    consensus_votes: Optional[Dict[str, int]] = None

    @property
    def total_tokens(self) -> int:
        return sum(
            a.input_tokens + a.output_tokens + a.cache_tokens
            for a in self.agent_calls
        )

    @property
    def model_distribution(self) -> Dict[str, int]:
        dist = {"haiku": 0, "sonnet": 0, "opus": 0}
        for call in self.agent_calls:
            if call.model in dist:
                dist[call.model] += 1
        return dist

    @property
    def estimated_cost(self) -> float:
        """Estimate cost based on model pricing (per 1M tokens)."""
        cost = 0.0
        for call in self.agent_calls:
            tokens = call.input_tokens + call.output_tokens
            if call.model == "haiku":
                cost += tokens * 0.25 / 1_000_000
            elif call.model == "sonnet":
                cost += tokens * 3.00 / 1_000_000
            elif call.model == "opus":
                cost += tokens * 15.00 / 1_000_000
        return cost


def parse_transcript(transcript_path: str) -> Dict:
    """
    Parse Claude Code transcript JSONL to extract metrics.

    Transcript format (one JSON per line):
    {
        "timestamp": "ISO-8601",
        "message": {
            "usage": {
                "input_tokens": N,
                "output_tokens": N,
                "cache_read_input_tokens": N,
                "cache_creation_input_tokens": N
            }
        },
        "isSidechain": bool,
        "isApiErrorMessage": bool
    }
    """
    metrics = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_tokens": 0,
        "agent_calls": 0,
        "models_used": {"haiku": 0, "sonnet": 0, "opus": 0},
        "start_time": None,
        "end_time": None,
    }

    try:
        with open(transcript_path, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    usage = data.get("message", {}).get("usage", {})

                    if usage:
                        metrics["input_tokens"] += usage.get("input_tokens", 0)
                        metrics["output_tokens"] += usage.get("output_tokens", 0)
                        metrics["cache_tokens"] += (
                            usage.get("cache_read_input_tokens", 0) +
                            usage.get("cache_creation_input_tokens", 0)
                        )

                    # Track timestamps
                    timestamp = data.get("timestamp")
                    if timestamp:
                        if metrics["start_time"] is None:
                            metrics["start_time"] = timestamp
                        metrics["end_time"] = timestamp

                    # Count Task tool calls (agent invocations)
                    content = data.get("message", {}).get("content", [])
                    if isinstance(content, list):
                        for block in content:
                            if block.get("type") == "tool_use":
                                if block.get("name") == "Task":
                                    metrics["agent_calls"] += 1
                                    # Try to extract model from params
                                    params = block.get("input", {})
                                    model = params.get("model", "sonnet")
                                    if model in metrics["models_used"]:
                                        metrics["models_used"][model] += 1

                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print(f"Transcript not found: {transcript_path}")

    return metrics


def calculate_duration_ms(start: str, end: str) -> int:
    """Calculate duration in milliseconds between two ISO timestamps."""
    try:
        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
        return int((end_dt - start_dt).total_seconds() * 1000)
    except:
        return 0


def create_comparison_report(v1_runs: List[BenchmarkRun],
                             v2_runs: List[BenchmarkRun]) -> str:
    """Generate comparison report between v1 and v2."""
    report = []
    report.append("# Think Plugin Performance Comparison\n")
    report.append(f"Generated: {datetime.now().isoformat()}\n")

    # Aggregate metrics
    v1_avg_duration = sum(r.total_duration_ms for r in v1_runs) / len(v1_runs) if v1_runs else 0
    v2_avg_duration = sum(r.total_duration_ms for r in v2_runs) / len(v2_runs) if v2_runs else 0

    v1_avg_tokens = sum(r.total_tokens for r in v1_runs) / len(v1_runs) if v1_runs else 0
    v2_avg_tokens = sum(r.total_tokens for r in v2_runs) / len(v2_runs) if v2_runs else 0

    v1_avg_cost = sum(r.estimated_cost for r in v1_runs) / len(v1_runs) if v1_runs else 0
    v2_avg_cost = sum(r.estimated_cost for r in v2_runs) / len(v2_runs) if v2_runs else 0

    # Calculate improvements
    speedup = v1_avg_duration / v2_avg_duration if v2_avg_duration > 0 else 0
    token_change = ((v2_avg_tokens - v1_avg_tokens) / v1_avg_tokens * 100) if v1_avg_tokens > 0 else 0
    cost_change = ((v2_avg_cost - v1_avg_cost) / v1_avg_cost * 100) if v1_avg_cost > 0 else 0

    report.append("\n## Summary\n")
    report.append(f"| Metric | v1.0 | v2.0 | Change |")
    report.append(f"|--------|------|------|--------|")
    report.append(f"| Avg Duration | {v1_avg_duration:.0f}ms | {v2_avg_duration:.0f}ms | {speedup:.1f}x faster |")
    report.append(f"| Avg Tokens | {v1_avg_tokens:.0f} | {v2_avg_tokens:.0f} | {token_change:+.1f}% |")
    report.append(f"| Avg Cost | ${v1_avg_cost:.4f} | ${v2_avg_cost:.4f} | {cost_change:+.1f}% |")

    # Model distribution for v2
    if v2_runs:
        total_haiku = sum(r.model_distribution.get("haiku", 0) for r in v2_runs)
        total_sonnet = sum(r.model_distribution.get("sonnet", 0) for r in v2_runs)
        total_opus = sum(r.model_distribution.get("opus", 0) for r in v2_runs)
        total_calls = total_haiku + total_sonnet + total_opus

        report.append("\n## v2.0 Model Distribution\n")
        report.append(f"| Model | Calls | Percentage |")
        report.append(f"|-------|-------|------------|")
        if total_calls > 0:
            report.append(f"| Haiku | {total_haiku} | {total_haiku/total_calls*100:.1f}% |")
            report.append(f"| Sonnet | {total_sonnet} | {total_sonnet/total_calls*100:.1f}% |")
            report.append(f"| Opus | {total_opus} | {total_opus/total_calls*100:.1f}% |")

    return "\n".join(report)


def save_results(runs: List[BenchmarkRun], output_path: str):
    """Save benchmark results to JSON."""
    with open(output_path, 'w') as f:
        json.dump([asdict(r) for r in runs], f, indent=2, default=str)


if __name__ == "__main__":
    print("Think Plugin Benchmark Harness")
    print("Usage: python harness.py [--baseline|--v2|--compare]")
    print("\nThis script provides utilities for parsing transcripts and calculating metrics.")
    print("Run benchmark tests via the run_benchmarks.md command file.")
