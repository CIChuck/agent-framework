---
title: Application patterns and examples
description: Practical application designs with explicit prerequisites, observable results and acceptance criteria.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# Application patterns and examples

These patterns combine current Friday components. They are application designs,
not prebuilt domain products. Start with synthetic data and decide what evidence
will establish success before connecting real services or allowing mutations.

## A complete offline component composition

This **offline Python example** registers a local function, executes it and
records the result in a temporary transcript. It needs the Tools and Transcript
packages at 0.1.0a3. It demonstrates explicit composition without a model,
external tools or persistent user data:

```python
import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
from friday_tools import DefaultToolRegistry, FunctionTool
from friday_transcript import SQLiteTranscriptStore, TranscriptEntry, TranscriptSession

def count_words(text: str) -> str:
    """Count whitespace-separated words in supplied text."""
    return str(len(text.split()))

async def main() -> None:
    registry = DefaultToolRegistry()
    registry.register(FunctionTool(count_words, category="text"))
    result = await registry.get_callable("count_words")(text="Friday keeps context")
    with TemporaryDirectory() as directory:
        store = SQLiteTranscriptStore(Path(directory) / "demo.db")
        await store.create_session(TranscriptSession(
            session_id="demo", model_name="no-model",
        ))
        await store.append_entry(TranscriptEntry(
            id="turn-1", session_id="demo", turn_number=1,
            user_message="Count the supplied words.",
            assistant_message=f"The count is {result}.",
        ))
        entries = await store.get_entries("demo")
        print(entries[0].assistant_message)

asyncio.run(main())
```

Expected output: `The count is 3.` This records an application-generated response,
not an LLM response. Adding a model later does not change who owns authorization,
result validation or persistence.

## Research assistant with cross-session context

Use Chat or a headless interactive agent with a configured model/embedding pair,
durable transcripts and memory extraction. Begin with an explicitly supplied
source bundle. If web/MCP research tools are added, admit only those destinations
and operations needed for the task.

| Step | Implementation | Evidence to inspect |
| --- | --- | --- |
| Record the request/source | Transcript and source metadata | Exact input and source identity |
| Build context | Memory recall and context assembly | `/context` or captured application payload |
| Produce draft | Interactive model execution | Draft with citations to actual sources |
| Extract reusable memory | Enabled extraction/ingestion | Derived records and provenance |
| Resume later | Same stores plus intended session/priming policy | Persisted session and selected prior context |
| Review | Independent comparison with the source bundle | Unsupported claims, omissions and corrected draft |

Accept on source support and required coverage, not a plausible answer or a
“completed” execution label. Source fetch failure, empty content and a cached
search snippet provide different evidence. Do not treat generated citations as
proof that a document was retrieved.

See [memory](04-adaptive-memory.md), [MCP tools](17-mcp-client.md) and the
[canonical workflow bundle](08-workflows.md#canonical-bundle-layout).

## Code assistance and review

Use a narrowly scoped workspace and separate read, edit, execute and publish
permissions. Register typed file/Git operations or a constrained external tool
server. Supply the reviewer the exact diff, requirements and relevant test
results; shared memory is background, not the canonical change artifact.

Framework orchestration can route to real agents when you supply factories and
services. Chat's alpha3 orchestration adapter remains deterministic even in
real mode; `/delegate coder ...` is not a working autonomous coding service.

For an application-owned code pipeline, validate:

1. The proposed files and API contracts match the authorized task.
2. Generated code compiles and the narrow meaningful checks pass.
3. The review addresses actual changed behavior and failure paths.
4. Any repository write/push/merge is separately admitted by your host policy.

Python subprocess execution runs on the host; a blocklist is not containment.
Use the chosen [execution backend](11-advanced-topics.md#execution-backends)
with verified mounts/network/resource policy before evaluating untrusted code.

## Document analysis and question answering

Choose explicit document ingestion and source-retention rules. Smart-file readers
can select format/chunking and optional summarization; vector/graph memory then
supplies candidate evidence. Install document/spreadsheet extras only when the
selected reader requires them.

Keep source paths/versions, extraction quality and chunk boundaries available
to the application. A retrieved passage is a similarity match, not a complete
answer. Require page/section support for factual conclusions and report when
the input is unreadable or insufficient. Changing the embedding model requires
a compatible collection/migration rather than mixing dimensions.

Test answerable, unanswerable and conflicting-source questions against a small
synthetic corpus. Record retrieval misses separately from unsupported synthesis.
See [tools](05-tools.md), [memory budgets](memory-management-guidelines.md) and
[security handling](security-configuration-guidelines.md).

## Project and team knowledge

Represent named entities and relationships through the configured ontology.
Use explicit author/source/time metadata and distinguish observations from
decisions. A frequent mention can raise access priority but cannot establish
the current project status or supersede an authoritative decision.

For multiple agents, choose shared versus private memory deliberately. The
namespace-aware wrapper and promotion journal provide useful in-process
contracts, but the host still authenticates identities and protects authoritative
metadata. Pass exact deliverables between workflow stages rather than relying
on graph recall to reconstruct the latest accepted state.

## Support and operations assistance

A support application can combine a curated knowledge corpus, conversation
history and read-only service tools. CRM, ticketing, database and infrastructure
mutations need explicit implementations and host authorization; several named
integration tools in this repository are placeholders.

Start with diagnosis and a proposed action artifact. Before a mutation, validate
the target/resource, intended effect and idempotency. After a timeout, reconcile
the external state before retrying. Transcripts and tool outputs can contain
credentials/customer data; content-free telemetry does not sanitize them.

Friday does not ship the old guide's complete CRM connectors, Kubernetes
operator or autonomous incident-remediation product. Build and evaluate those
boundaries explicitly if the application needs them.

## Finance data assistance

The Finance package wraps Massive data access for equities, cryptocurrency and
indicators. `AssetRegistry.resolve_ticker()` works offline; actual queries need
a provider key, entitlement, network access and the correct account tier.
`probe_tier()` is a placeholder. Availability/freshness depends on the provider
endpoint and plan; a successful query does not establish real-time suitability.

`execute_query()` maps message-containing-429 errors to `MassiveRateLimitError`;
other provider/transport failures propagate. Do not assume declared timeout or
not-found exception classes normalize every SDK failure. The package's weekend
rollback is not a full exchange-holiday calendar.

Use [the Finance package](../../packages/friday-finance/README.md) for the actual
live API example. Keep data retrieval separate from investment decisions and
remote account/trading mutations; this package is a data integration.

## Sensitive-domain applications

Medical, legal and other sensitive workloads require domain-specific acceptance,
access controls, retention and provider agreements outside the framework.
Selecting a local model or namespace does not confer regulatory compliance.
The earlier guide's “PHI-compliant” application label was not an implemented
certification or a validated clinical product.

Use synthetic examples for integration tests. Evaluate source support, omissions,
contradictions and human review requirements in context before accepting outputs.
Framework workflow completion and valid artifact formatting are not domain
correctness checks.

## Speech and social integrations

Speech can render selected output through configured adapters. Validate selection
and disabled-mode lifecycle first, then explicitly provision credentials,
hardware and consent for capture/playback. See [speech](speech.md).

Moltbook has read and mutation endpoints with typed request/response models.
Constructing its client is offline; calling endpoints is live. Posting, voting,
deleting and moderation change remote state. Expose only the operations intended
by your host and do not replay uncertain writes automatically. See [the client
package](../../packages/friday-moltbook/README.md).

## Evaluate the application you actually assembled

Record the release, model revisions, configuration, admitted tools and state
layout with each evaluation. Keep loader/schema checks, offline component
checks, live provider checks, recovery checks and semantic acceptance separate.
The [troubleshooting guide](13-troubleshooting.md) helps identify which boundary
failed without resetting or deleting existing data.

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
