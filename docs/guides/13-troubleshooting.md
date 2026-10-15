---
title: Troubleshooting and diagnostics
description: Diagnose installation, configuration, models, memory, tools and lifecycle failures without destroying state.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# Troubleshooting and diagnostics

Start with the failing boundary and the exact error category. Preserve the
configuration shape, installed versions, session identity and relevant safe
diagnostics. Do not paste credentials, full resolved configuration, raw prompts
or private tool outputs into a support report.

## Establish the baseline

```bash
python --version
friday-chat --version
friday-chat --help
python -m pip check
```

Use Python 3.13.4+ and an aligned 0.1.0a3 Friday cohort. This **offline Python
example** prints distribution versions without reading credentials or starting
services:

```python
from importlib.metadata import version

for name in ("friday-chat", "friday-framework-core", "friday-framework-llm",
             "friday-framework-memory", "friday-framework-agent"):
    print(name, version(name))
```

If a distribution is absent, `PackageNotFoundError` identifies it. Run this with
the same interpreter/environment as the failing app. The root distribution is
metadata-only; `import friday_framework` is not a valid installation check.

## Installation and startup

| Symptom | Likely boundary | Next check |
| --- | --- | --- |
| `friday-chat` not found | Executable environment/PATH | Activated venv or uv tool installation and `uv tool dir --bin` |
| `friday` fails to start | Historical placeholder CLI entry point | Install/use `friday-chat` |
| Import error for `friday_optimization` | Wrong import name/old example | Package imports as `friday_opt` and remains a skeleton |
| Python requirement conflict | Interpreter | Recreate the environment with 3.13.4+; do not weaken package metadata |
| Mixed Friday versions | Partial upgrade | Resolve a clean aligned cohort and run `pip check` |
| Real mode still returns fake responses | Runtime-mode override | Inspect/remove unintended `FRIDAY_CHAT_RUNTIME`; it overrides `--runtime` |
| `init` or `doctor` unknown | Unimplemented first-run commands | Copy templates manually and pass `--config` |
| Runtime path validation error | Headless root topology | Existing install/workspace, separate runtime state and writable parents |

Do not reinstall or clean stores to diagnose a configuration failure. The
[offline Chat session](02-getting-started.md#run-an-offline-chat-session) isolates
terminal setup from model/storage integrations.

## Configuration loading

| Symptom | Check |
| --- | --- |
| Missing environment reference | Every ordinary `${NAME}` in the main Chat YAML, even disabled sections |
| Editing `.env` has no effect | Chat does not load it automatically; supply the process environment explicitly |
| Unknown/ignored top-level section | Chat diagnostics and the owning schema; Runtime YAML is different |
| Model profile not found | Relative `model_library.path`, profile name and role binding |
| Wrong profile kind | Chat versus embedding binding; do not bind an embedding role to a chat profile |
| Mixed generation controls rejected | Contradictory legacy flat and canonical typed settings |
| State created in the wrong place | Process cwd and effective absolute paths; not all Chat paths are config-relative |
| MCP credential reference rejected | Literal environment name, not `${...}` or a token |

Load configuration without constructing services first. The
[canonical loading example](10-configuration.md#bind-models-to-chat-roles)
isolates schema/profile/credential resolution from network connectivity.

## Models, reasoning and timeouts

Check the exact endpoint, served model alias/revision, selected credential and
route. Validate embeddings separately from chat. A chat response does not prove
the extraction, compaction, smart-file or maintenance models are configured.

| Failure | Interpretation |
| --- | --- |
| Authentication/entitlement error | Verify the selected credential/account/route without printing the secret |
| Unsupported normalized control | Inspect transport/model identity and capability profile; do not globally drop controls |
| Missing reasoning text | Verify the route emits reasoning and the typed event/response path preserves it |
| Reasoning appears in user output | Keep reasoning events separate from text deltas |
| Context length error | Inspect the final formatted prompt, tool schemas/results, output reservation and retained history |
| Timeout before a response | Distinguish provider deadline, tool deadline, workflow deadline and app cancellation |
| Retry loop | Classify the failure; more retries do not repair invalid config or unsupported controls |

Current LiteLLM is pinned to 1.100.1. Do not substitute a newer/older version while
claiming the same validated runtime. Built-in cost rates are historical estimates;
missing usage is not zero usage and failed attempts can have unknown charges.

## Memory and persistence

| Symptom | Inspect first | Avoid |
| --- | --- | --- |
| Earlier conversation absent | Session ID, transcript path, `/sessions`, `/transcript` | Assuming recall failure means the database is empty |
| Transcript exists, no derived facts | Extraction interval/service, pending background work and rejection diagnostics | Treating one write receipt as all-store success |
| Fact stored, absent from prompt | Relevance/lifecycle filters, priming, namespace and token budgets | Resetting the vector store |
| Old history dominates context | Prior-session/current-history limits and actual prompt | Increasing every budget blindly |
| Repeated/low-quality insights | Extraction source/prompt/ontology and supersession/consolidation | Treating frequency as truth |
| Embedding dimension conflict | Model identity and collection dimensions | Mixing old/new embeddings in one collection |
| Database locked | Live owners, incomplete shutdown, concurrent writers, filesystem permissions | Deleting lock/WAL files from an active store |
| Recovery refused | Manifest, participant capabilities and quiescence/preflight result | Copying files into a running process |

Current assembly reserves formatting overhead and prunes prior-session history
first under pressure. Opt-in Chat compaction exists. See [memory management](memory-management-guidelines.md)
for the exact distinction between retrieval pruning, prompt formatting and
background summarization.

Before modifying persistent data, stop all owners, obtain a consistent verified
backup and use the supported mutation/recovery contract. `/reset` is destructive;
it is not a health check. An application crash can leave background or external
effects uncertain even when a final response is missing.

## Native tools and selection

Inspect `/tools`, `/recommend-tools <query>` and `/tool-budget`. Confirm an actual
implementation exists, its dependencies are installed, its constructor is
configured and its canonical name matches selection. `/inject-tools` replaces the
manual names but retains configured `tools.context.required_tools`, suppressing
optional automatic choices. The union of required and manually selected names
must fit admission, count and schema budgets; `/clear-tools` restores automatic selection.

Unknown names, missing required tools and schema/token caps can reject a set.
A registered tool may remain unselected. A selected schema is not permission to
perform an operation. Use `/run-tool` only when execution itself is intended;
choose harmless synthetic inputs in a disposable environment.

Inspect `ToolResult.error` when using the typed native API, and the specific
string/error behavior when using `execute()`. Returned error text is not success.
Shell and subprocess failures can have host side effects; retries need explicit
reconciliation.

## Integrated MCP diagnostics

| Symptom/category | Check |
| --- | --- |
| No connection in fake mode | MCP connects only through real application assembly |
| Empty discovery | Enabled provider/peer, trusted command, workspace `cwd`, protocol profile and catalog caps |
| `missing_include` | Canonical `mcp_<server>_<tool>` name; pinned includes fail even for optional peers |
| Optional peer failure stops startup | A separate pinned include or required peer policy may be controlling |
| HTTP rejected | Explicit dated version, global remote pair, per-peer remote trust, literal credential reference and strict endpoint/network policy |
| Tool registered but absent this turn | Chat count/schema/result budgets and minimum memory floor |
| `catalog_unavailable` | Stale/failed/removed generation; integrated rediscovery uses stop/start |
| `unsupported_content` | Valid unsupported media/resource output; Friday does not fetch/decode it |
| `input_required_unsupported` | Valid request for unsupported interactive continuation/MRTR |
| Truncated or blocked result | Protocol/result limits and sanitization policy |
| No long-term memory record | Default-disabled ingestion, explicit server/tool opt-in and pending publication state |
| Cleanup failure | Retained owners require another stop before replacement |

`RuntimeKernel.mcp_provider.operational_diagnostics` and Chat's local MCP provider
expose typed outcomes. No Chat MCP health command is implemented. Do not replay
a timed-out/ambiguous mutating call;2025 session recovery requires a new explicit
invocation, and modern HTTP has no session/fallback. See [MCP setup](17-mcp-client.md).

## Agents and workflows

Profile validation, registry factories and actual model/service assembly are
distinct. `AgentOrchestrator` requires a configured registry factory; there is
no implicit default profile. `AutonomousAgent.run()` is unimplemented.

Chat's orchestration remains deterministic in real mode; a successful `/delegate`
reply is not evidence of specialist-model execution. Real Chat's workflow run
path loads flat definitions; canonical bundles need the framework canonical
loader/executor. Check dependencies, missing `$variables`, owner bindings and
pending approval state before rerunning a task.

Workflow completion does not prove artifact correctness or external mutation
success. Validate required outputs and inspect failed/pending state first.

Interactive `/replay` is not a passive transcript viewer: for nonempty input it
resets the current runtime and reprocesses user turns. In real mode that can
change stores and call providers/tools. Use `/transcript` for inspection and
reserve replay for a disposable isolated runtime/state copy.

## Telemetry, logs and shutdown

Chat telemetry defaults disabled and currently selects local `debug` diagnostics.
The owned OpenTelemetry factory is a separate programmatic surface. If requested
SDK/exporter dependencies are missing, configure/install the declared extra
rather than silently substituting a global tracer.

Remote OTLP requires the supported verified-TLS profile; inherited OTEL/GRPC,
proxy and certificate overrides are rejected by the owned factory. No HTTP
exporter or custom credential-header profile is promised. Inspect categorical
flush/shutdown status; a successful attempt is not proof of collector ingestion.

Close caller-owned providers only after all borrowers settle. Process-shared
LiteLLM clients likewise need one coordinated shutdown. Do not erase stores or
create replacements to conceal incomplete cleanup. Langfuse's provider-neutral
integration remains queued; legacy callbacks are a separate content path.

## Report a reproducible issue

Include release/interpreter versions, entry point, fake/real mode, redacted
configuration shape, safe error category, expected/observed behavior and the
smallest synthetic reproduction. State which checks were offline versus live,
whether persistent state was copied and whether an external mutation is uncertain.
Use the [issue tracker](https://github.com/CIChuck/agent-framework/issues).

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
