---
title: Memory budgeting and maintenance
description: Current token accounting, pruning order, compaction triggers, lifecycle math and safe operations.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# Memory budgeting and maintenance

Memory retrieval, prompt formatting, background compaction and durable-store
maintenance are separate mechanisms. This guide explains their current Chat
integration and underlying library contracts. Use [adaptive memory](04-adaptive-memory.md)
for store/controller architecture.

## Budget accounting

Use the actual model context limit as the outer bound and reserve output tokens.
Tools, base prompts, history, supporting context, formatting and the new query
all consume space. The attention layout computes:

```text
fixed_costs = system_prompt_tokens + tool_schema_tokens + output_buffer
dynamic_budget = max(0, context_window - fixed_costs)
supporting_context_budget = floor(dynamic_budget * budget_ratio)
```

For an **illustrative** 32000-token window with 1500 system tokens, 500 tool tokens,
2500 output tokens and a 0.30 ratio, dynamic budget is 27500 and supporting-context
budget is 8250. Those are example measurements, not fixed overhead defaults.
The remainder is not a separately enforced reserved history quota in the current
attention formatter: it emits retained history plus supporting context and query,
then records final budget diagnostics.

The assembler also reserves estimated formatting overhead before pruning.
Final token estimates are not exact provider tokenization for every route.
Leave headroom and inspect the formatted prompt rather than assuming a ratio
alone guarantees admission to every model.

## Supporting context section names

`SupportingContextConfig` library defaults are:

| Field | Default |
| --- | --- |
| `budget_ratio` | 0.30 |
| `section_priority` | `known_facts`, `passages`, `insights`, `summaries`, `tools`, `state` |
| `max_items.passages` | 10 |
| `max_items.known_facts` | 25 |
| `max_items.insights` | 25 |
| `max_items.summaries` | 10 |
| `max_items.tools` | 5 |

Higher-priority sections are added first within the supporting budget. Use
`known_facts`, not the earlier guide's `key_facts`, for this layout contract.
Chat's broad packaged template overrides the ratio/order/item counts. A template
value is not a library default, and a flexible dict accepting a misspelled key
does not mean the formatter uses it.

This **Chat configuration fragment** is a conservative starting point for a
32000-token model; tune it against your actual prompt and output needs:

```yaml
memory:
  context_window: 32000
  output_buffer: 2500
  max_history_turns: 15
  supporting_context:
    budget_ratio: 0.30
    section_priority: [known_facts, passages, insights, summaries, tools, state]
    max_items:
      passages: 5
      known_facts: 15
      insights: 10
      summaries: 5
      tools: 5
  priming:
    enabled: true
    token_budget: 4000
    top_entities: 20
    max_insights: 10
    max_summaries: 5
    max_known_facts: 20
    previous_sessions: 1
    previous_session_turns: 3
```

Priming retrieval limits and supporting-context formatting limits have different
roles. Retrieve only what has a reasonable chance to fit; a blanket “80% rule”
is an operator heuristic, not an enforced invariant. Prior-session history is
included in assembler estimates and is the first history dropped under pressure.

## Current pruning cascade

`ContextAssembler._apply_budget()` first filters decayed/superseded items,
conditionally excludes redundant summaries and applies configured query relevance.
It reserves formatting overhead and returns immediately if the payload fits.
When it does not fit, it progressively:

1. Drops all prior-session history.
2. Keeps at most the last 10 current-session turns.
3. Removes long-term passages with relevancy below 0.3.
4. Removes short/long-term passages with relevancy below 0.5.
5. Keeps at most the last 5 current turns.
6. Keeps up to 3 short-term and 2 long-term passages by relevance.
7. Keeps up to 3 insights and 3 summaries.
8. Keeps up to 5 entities and 5 facts.
9. Falls back to the last 2 turns and up to 2 short-term passages, clearing the
   other listed supporting items and emitting a pruning warning.

Each stage checks whether the remaining estimate fits. The emergency minimum
can itself exceed a very small budget or include very large turns; pruning is
not a hard byte/token bound on every retained field. Other payload fields,
tool schemas/results and final formatting still need their owning limits.
Do not increase the configured context window above the real model limit to
hide an overage.

## Automatic compaction is opt-in in Chat

The old guide said no automatic percentage-based compaction existed. Current
Chat can construct a `ContextBudgetMonitor` and compactor when
`memory.compaction.enabled` is explicitly true. The background coordinator
records budget status after turns, schedules compaction when eligible and
waits for in-flight compaction before the next foreground prompt.

This **Chat configuration fragment** enables the supported path:

```yaml
memory:
  compaction:
    enabled: true
    llm_service: compaction
    compaction_threshold: 0.85
    critical_threshold: 0.95
    target_utilization: 0.70
    cooldown_turns: 3
    max_duration_ms: 15000
    critical_max_duration_ms: 45000
    min_turns_to_summarize: 5
    max_turns_per_summary: 8
    compaction_recency_window: 4
    insight_dedup_enabled: true
    insight_similarity_threshold: 0.90
    max_insights_to_check: 50
    trend_window: 10
```

Bind `compaction` to an actual chat service. Compaction can call models, summarize
turns, supersede duplicate insights and promote memory. `target_met`, errors and
time-budget exhaustion must be inspected; a configured 70% target is not a
guaranteed outcome. `/compact` requests a manual run and first attempts to flush
pending extraction. Explicit `enabled: false` disables that command's path.

### Trigger and severity details

The monitor requires enablement, available history, no in-progress compaction and
elapsed cooldown. With those satisfied, warning/critical/overage severity triggers
a run; otherwise a rising trend above `compaction_threshold` can trigger one.
The code checks cooldown **before** critical/overage, so those severities do not
bypass cooldown.

`BudgetSeverity.from_utilization()` has fixed boundaries: greater than 70% is
elevated, greater than 85% warning, greater than 95% critical and greater than 100%
overage. Exact boundary values stay in the lower category. `critical_threshold`
is an accepted config field but does not replace that fixed classifier in the
current monitor. Critical/overage uses the larger time budget.

This **offline Python example** checks a deterministic trigger without performing
compaction or calling an LLM:

```python
from friday_memory.context.budget_monitor import ContextBudgetMonitor
from friday_memory.models.budget import BudgetSeverity, BudgetStatus, CompactionConfig

monitor = ContextBudgetMonitor(CompactionConfig(enabled=True, cooldown_turns=1))
monitor.record_turn(BudgetStatus(
    total_tokens=900, available_budget=1000, utilization_pct=90.0,
    severity=BudgetSeverity.from_utilization(90.0),
))
print(monitor.should_compact())
monitor.mark_compaction_started()
print(monitor.should_compact())
```

Expected output: `True`, `False`.

## Lifecycle scoring is a different mechanism

Default lifecycle decay is `score * exp(-0.01 * hours_since_last_access)`.
For an initial score 1.0, 24/72/168 hours produce about 0.787/0.487/0.186.
Retrieval inclusion uses its separate default 0.005/hour age-from-creation factor
and usage boost `1 + 0.1 * log(1 + hit_count)` multiplied by similarity.
These are prioritization heuristics, not factual reliability estimates.

Promotion combines normalized age/access/confidence/connections with default
weights 0.2/0.4/0.2/0.2. Library `DecayConfig` defaults to promotion threshold 0.7,
decay threshold 0.2, minimum age 24 hours and decayed retention 30 days. Chat's
packaged template overrides some values. Graph hit-count reinforcement, access
buffer flushing and collection promotion require their actual configured owners;
every pure graph read does not necessarily count as an access.

## Maintenance and recovery

Use `/memory`, `/sessions`, `/context`, `/prompt`, `/debug-budget` and
`/tool-budget` to diagnose first. `/prompt` and file exports can contain private
content. Budget diagnostics and telemetry are not a substitute for inspecting
what the provider actually received in a controlled synthetic reproduction.

`/reorganize` previews coordinated maintenance by default. Exact `--execute`
requests mutation only after capability, quiescence, backup/recovery and other
preflight checks. Adapter gaps can refuse the operation. `/lifecycle` and
`/migrate` have separate dry-run/execute contracts. `/reset` deletes/resets data
and must not be presented as a routine recall fix.

Quiesce background extraction, compaction, access-buffer work and foreground
mutations before snapshot/restore. A byte copy of a live directory is not a
consistent all-store backup. Retain manifests, categorical outcomes and recovery
ownership; uncertain partial mutation needs reconciliation rather than replay.

## Diagnose missing or oversized context

| Observation | Check and action |
| --- | --- |
| Supporting sections truncate | Align priming counts/budget with section limits and priorities |
| Old turns dominate | Lower retained history/previous-session counts; inspect the actual payload |
| Compaction never runs | Explicit enablement, initialized monitor/compactor, status and cooldown |
| Compaction runs but target missed | Result errors/time budget, summarizable turns and protected recent window |
| Tools crowd out recall | Narrow schemas/results; inspect MCP reservations and memory floor |
| Stored fact not retrieved | Session/namespace, similarity, stage, supersession and query relevance |
| Empty insights after a turn | Extraction scheduling, pending work, model binding and rejection log |
| Context error despite pruning | Final formatting/query/tools, estimator mismatch and emergency minimum |

## Implementation references

- [Assembler](../../packages/friday-memory/src/friday_memory/context/assembler.py)
- [Layout and supporting-context defaults](../../packages/friday-memory/src/friday_memory/context/layout.py)
- [Budget models](../../packages/friday-memory/src/friday_memory/models/budget.py) and [monitor](../../packages/friday-memory/src/friday_memory/context/budget_monitor.py)
- [Chat background coordination](../../packages/friday-chat/src/friday_chat/background.py)
- [Lifecycle decay](../../packages/friday-memory/src/friday_memory/lifecycle/decay.py) and [inclusion scoring](../../packages/friday-memory/src/friday_memory/retrieval/inclusion_scorer.py)
- [Packaged Chat template](../../packages/friday-chat/src/friday_chat/config_templates/config.example.yaml)

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
