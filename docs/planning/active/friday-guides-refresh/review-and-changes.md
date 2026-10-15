# Guide review and changes

Status: initial review CHANGES_REQUESTED; bounded corrections applied; fresh validation pending.
Review date: 2026-10-15. Framework basis: published0.1.0a3, source base123d9ed9.

All25 original documents were inventoried by complete-file parsing: header,
every heading, code fence, Friday import and flagged legacy/overclaim terms.
The [baseline audit](validation/baseline-audit.json) preserves per-file hashes,
structure and example diagnostics. Substantive claims were reconciled with
current package metadata, loaders, command handlers, public exports and source.
The original series mixed implementation, future designs, duplicated references,
invented APIs and retired test-app transcripts. The replacement keeps technical
concepts and recipes with precise ownership, operational limits and source links.
Original content remains recoverable from the pinned Git base.

## Per-document findings and resolutions

| Guide | Original issue | Current correction and implementation basis |
| --- | --- | --- |
| [01 Overview](../../../guides/01-executive-summary.md) | Production/compliance/learning claims and stale roadmap presented as current | Alpha status, context-based memory, implemented capability map, adoption paths and host responsibilities; package metadata, public exports and current board |
| [02 Getting started](../../../guides/02-getting-started.md) | Retired test-app entry point, wrong distribution/API examples, overpromised memory and unsafe lock deletion | Pinned Chat install, complete fake/offline session, safe template copy, explicit real-session setup and separate persistence checks; Chat CLI/config/templates and Transcript API |
| [03 Core concepts](../../../guides/03-core-concepts.md) | Old package count, assumed backends and incomplete constructors | All16 member roles, actual contracts, isolated RuntimeConfig/Kernel construction, live lifecycle and borrowed/shared ownership; Core/Runtime/Chat source |
| [04 Adaptive memory](../../../guides/04-adaptive-memory.md) | Unsupported optimizer API, overly broad isolation/recall claims, stale math and fictitious operations | Explicit stores/controller dependencies, runnable SQLite/vector/decay examples, actual scoring/priming/pruning and recovery boundaries; Memory adapters/controller/context/lifecycle |
| [05 Tools](../../../guides/05-tools.md) | Universal ToolResult/type-validation/registration/sandbox claims; stale MCP transport description | Separate FunctionTool/BaseTool/FridayTool contracts, isolated examples, current registry/selection, explicit security limits and145-definition source inventory; Tools and Chat tool source |
| [06 Agents](../../../guides/06-agents.md) | Unsupported profile fields, assumed default agent/loader behavior and autonomous functionality | Strict loader-compatible profile, offline loading, factories, explicit cache/reload/service/tool semantics and AutonomousAgent placeholder; profile/loader/registry/agent source |
| [07 Multi-agent](../../../guides/07-multi-agent.md) | Shared-memory guarantees, pools/parallelism/team loader and automatic context propagation overclaimed | Single-active framework routing, real factory requirements, explicit handoffs, namespace limitations, Chat deterministic adapter disclosed; orchestrator and multi-agent memory source |
| [08 Workflows](../../../guides/08-workflows.md) | Flat-only examples presented as comprehensive/current automation | Complete canonical bundle plus flat compatibility example, actual loaders/executors, owner/input/artifact/HITL/lease boundaries and Chat adapter limits; workflow models/loader/engine and Chat adapter |
| [09 CLI](../../../guides/09-cli-reference.md) | Thousands of lines of retired test-app syntax and invented commands | Current process options and all50 canonical commands from registry metadata, real/fake limits, actual syntax and side effects; interactive replay's reset/reprocessing semantics explicitly described |
| [10 Configuration](../../../guides/10-configuration.md) | Monolithic mixed schema, legacy LLM settings, stale telemetry and assumed environment precedence | Separate Chat/Runtime/profile/display ownership, complete strict model library and Chat config, role overrides, interpolation and credential exceptions, memory/MCP/telemetry boundaries; actual parsers and models |
| [11 Advanced](../../../guides/11-advanced-topics.md) | Nonexistent backend classes, unmeasured savings/latencies and deployment products | Current adapter contracts, typed requests, measurable tuning, owned telemetry/TLS/lifecycle, mock versus real isolation and explicit deployment design; Core/LLM/Telemetry/Sandbox/Runtime source |
| [12 Use cases](../../../guides/12-use-cases.md) | Long fictional transcripts/configs and domain/compliance/connector promises | Runnable offline tool/transcript composition, research/code/document/team/ops/finance/audio patterns with prerequisites and acceptance evidence; package source/READMEs and current integration limits |
| [13 Troubleshooting](../../../guides/13-troubleshooting.md) | Missing APIs, unsafe destructive repairs and obsolete telemetry setup | Boundary-specific diagnosis, real distribution versions, no store/lock deletion, actual MCP failures, timeout/retry/ownership distinctions and replay caution; source contracts and handlers |
| [14 Reference](../../../guides/14-appendices.md) | Duplicated obsolete full config/CLI/API reference | Metadata-derived16-package map, actual API entry points,145 statically named native definitions with source/stub labels, migration mapping and glossary |
| [15 Contributing](../../../guides/15-contributing.md) | Retired paths, invented community/release promises and stale setup | Current uv workspace/dev checks, actual suite paths, governance and guide maintenance rules; AGENTS/policies/pyproject and existing scripts |
| [16 Desktop](../../../guides/16-desktop-deployment.md) | Planned init/doctor/config lookup mixed into operational procedure; uvx cache claims stale | Pinned persistent/on-demand installs, manual resource copying, explicit paths/environment, actual OS/audio/app limits and staged validation; uv help/docs and Chat CLI/templates |
| [17 MCP client](../../../guides/17-mcp-client.md) | Relatively current but repository test fixture required and refresh example used top-level await | Preserve detailed accepted transport/trust/budget/result/generation limits; use installed owned modern server, add complete offline client, label refresh fragment and source references |
| [18 MCP server](../../../guides/18-mcp-server.md) | Current contract but absent release metadata/prerequisites and undefined HTTP token input | Preserve server admission/schema/lifecycle contracts; explicit install/extra, named server file and caller-token factory fragment; server source and accepted protocol contract |
| [19 MCP migration](../../../guides/19-mcp-migration.md) | Current matrix but weak release/application context and unclear remaining roles | Preserve dated matrix/config/TLS/rollback, add alpha3 checks, explicit MRTR exclusion and independent Langfuse scope; pinned protocol contract/metadata/source |
| [Index](../../../guides/README.md) | Retired CLI/package-count/capability labels | Task-oriented reading paths, precise descriptions for all25 files and example/metadata conventions |
| [Outline](../../../guides/OUTLINE.md) | Large speculative second architecture/roadmap | Current section map and one subject owner per guide, consistent with actual headings |
| [Capabilities](../../../guides/FRIDAY-FEATURES.md) | Stale package APIs and unimplemented features treated as functional | Evidence-linked implemented/limited/placeholder/queued matrix; Chat orchestration/speech, STT, Optimization, MRTR and Langfuse limits explicit |
| [Memory management](../../../guides/memory-management-guidelines.md) | Said automatic compaction absent/prior history unbudgeted, wrong section names and decay arithmetic | Current overhead/pruning order, known_facts defaults, actual severity/cooldown/compaction behavior, precise math and safe operations; layout/assembler/budget monitor/Chat background source |
| [Security](../../../guides/security-configuration-guidelines.md) | Target architecture described as all-path guarantee, mismatched control vocabularies and retention claims | Per-path coverage, validated Core config/example, bounded prefix scanning, original-content retention and Chat versus Core command distinctions; actual sanitizer/processors/handlers |
| [Speech](../../../guides/speech.md) | Retired app references, YAML credential assumptions, STT/audio platform limits unclear | Standalone lifecycle/live assembly, real file/live constraints, Chat deterministic adapter and different tags, explicit STT placeholder and harness behavior; Speech/Chat source |

## Front matter and technical depth

Every file now has valid YAML metadata with title, description, framework_version,
last_reviewed, status, audience and doc_type. All name release0.1.0a3 and actual
review date2026-10-15. Current means documentation basis, not maintainer acceptance
or production certification. The numbered filenames remain stable.

Technical coverage includes complete model/profile/workflow/config examples,
store and scoring calculations, budget/compaction details, tool/CLI inventories,
transport/security/ownership constraints and direct implementation references.
Redundant speculative scripts, fixed pricing/performance promises, retired
transcripts and future deployment instructions were removed rather than relabeled
as working recipes. Detailed MCP contracts were preserved and clarified.

## Builder verification

[Builder receipts](validation/builder-checks.json), [replayable checker](validation/check-guides.py.txt),
[network/state guard](validation/network-and-state-guard.py.txt),
[published source comparison](validation/published-source-comparison.json) and
[repository checks](validation/repository-checks.json) record the actual checks.

- 25 metadata/body renders;29 Python fences compile;24 complete offline scenarios,
including an owned MCP stdio client/server exchange, pass with network/credential
file/shared-checkout access blocked and private writes only.
- 34 owning-schema checks plus exact canonical profile/workflow loading, headless
fragment parsing and non-started real Chat assembly pass. The latter uses only
synthetic credentials/private state and confirms current adapter identities.
- CLI help/version,50-command registry and fake hello/help/history/exit pass.
- 560 Markdown links enumerated; local target/anchor checks pass, including48
anchor references. External links are not claimed to be exhaustively fetched.
- 426 published alpha3 Python source files match this checkout byte for byte.
- Board31 tasks, documentation lifecycle609 Markdown files and whitespace pass.

Live Runtime startup/provider calls, HTTP deployment/TLS listener, audio hardware,
Docker, Windows execution and production-data migrations were not run. The two
live Python examples and two callable API fragments are compiled/excluded from
standalone execution with reasons in the receipts. No package source, tests,
dependencies, versions, locks or artifacts changed; no push or publication.

## External reference checks

Checked primary sources for conceptual/install reference on2026-10-15:
[MCP2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/),
[MCP2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/),
[uv tools](https://docs.astral.sh/uv/concepts/tools/),
[uv installation](https://docs.astral.sh/uv/getting-started/installation/), and
[Python Packaging installation](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).
Friday support remains pinned to its bounded dated implementation/accepted
contract; external documentation does not imply every optional role is present.

## Independent findings and bounded corrections

[Initial review](validation/initial-review/report.md) found GUIDE-001 and GUIDE-002.
[REM-GUIDE-001](directives/REM-GUIDE-001.md) corrects four manual-selection
descriptions across Tools, CLI and Troubleshooting and marks the screenshot
operation as a stub. The [guarded probe](validation/remediation/probes.log)
reproduces the existing required/manual union and unimplemented screenshot
result; [scope evidence](validation/remediation/scope.json) proves other21
guides and all code fences unchanged. A new candidate needs fresh review.
