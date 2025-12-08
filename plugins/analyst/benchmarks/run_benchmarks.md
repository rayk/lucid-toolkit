---
description: Run full benchmark suite for think plugin
allowed-tools: Task, Read, Bash, Write
---

<objective>
Execute comprehensive benchmark suite measuring performance, accuracy, and cost.
Compare v1.0 baseline against v2.0 parallel implementation.
</objective>

<workflow>

## Phase 1: Setup

1. Read test cases from benchmarks/test_cases.json
2. Verify benchmark harness exists
3. Initialize results collection

## Phase 2: Baseline Measurement (v1.0)

For each test case in test_cases.json:

1. Record start timestamp
2. Execute current /think:consider with test problem
3. Record end timestamp
4. Parse transcript for metrics:
   - input_tokens, output_tokens, cache_tokens
   - Number of tool calls
   - Duration

Store as:
```toon
@type: BenchmarkRun
version: v1.0
testId: {id}
command: consider
problem: {problem text}
durationMs: {end - start}
tokens:
  input: {N}
  output: {N}
  cache: {N}
agentCalls: {count}
modelDistribution:
  haiku: 0
  sonnet: {count}
  opus: 0
```

## Phase 3: v2.0 Measurement

For each test case:

1. Record start timestamp
2. Execute refactored /think:consider with parallel agents
3. Record end timestamp
4. Parse transcript for:
   - Token usage per model tier
   - Parallel batch count
   - Total agent calls
   - Confidence score

Store as:
```toon
@type: BenchmarkRun
version: v2.0
testId: {id}
command: consider
problem: {problem text}
durationMs: {end - start}
tokens:
  input: {N}
  output: {N}
  cache: {N}
agentCalls: {count}
parallelBatches: {count}
modelDistribution:
  haiku: {count}
  sonnet: {count}
  opus: {count}
confidence: {0.0-1.0}
```

## Phase 4: Generate Report

Calculate:
- Average duration per version
- Average tokens per version
- Speedup factor
- Cost comparison
- Model distribution

Write report to: benchmarks/results/benchmark_report_{timestamp}.md

## Phase 5: Validate Success Criteria

Check against test_cases.json success_criteria:
- Classification accuracy >= 90%
- Model selection accuracy >= 80%
- Confidence thresholds met >= 85%
- Output format valid = 100%

</workflow>

<output_format>
## Benchmark Report

**Run Date:** {timestamp}
**Test Cases:** {count}

### Performance Comparison

| Metric | v1.0 | v2.0 | Improvement |
|--------|------|------|-------------|
| Avg Duration | {ms} | {ms} | {X}x faster |
| Avg Tokens | {N} | {N} | {%} change |
| Avg Cost | ${N} | ${N} | {%} cheaper |

### v2.0 Model Distribution

| Model | Calls | % of Total |
|-------|-------|------------|
| Haiku | {N} | {%} |
| Sonnet | {N} | {%} |
| Opus | {N} | {%} |

### Success Criteria

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Classification Accuracy | 90% | {%} | PASS/FAIL |
| Model Selection | 80% | {%} | PASS/FAIL |
| Confidence Met | 85% | {%} | PASS/FAIL |
| Format Valid | 100% | {%} | PASS/FAIL |

### Individual Test Results

{table of each test case with metrics}
</output_format>
