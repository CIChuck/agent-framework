# INGEST-001 — Friday guide update handoff

Status: **proposed construction-documentation requirement**, 2026-11-11.

Chuck asked whether this unit updates the Friday guides because the planned
command architecture and installed packages change substantially. The current
REM explicitly names Tools/Chat package READMEs, packaged configuration examples,
and provisioning/upgrade instructions, but its proposed path list does **not**
name `docs/guides/` files. This is a documentation coverage gap to resolve in the
exact construction directive, not a claim that the guide updates are already
implemented or independently reviewed.

The maintained [guide index](../../../guides/README.md) currently describes the
released `0.1.0a3` documentation baseline. Upcoming INGEST behavior must not be
presented as available in that release before candidate source/installed proof.
Keep accepted guide-refresh archives and evidence immutable. No current guide
file or reviewed technical contract is changed by this handoff.

## Proposed exact guide coverage

| Guide files | Scoped documentation change required for this implementation |
| --- | --- |
| [Quick start](../../../guides/00-quick-start.md), [Getting started](../../../guides/02-getting-started.md) | Candidate/release-qualified installation commands; default Chat's document stack versus optional Tools support; effective Certifi security floor; explicit local converter/OCR/tokenizer provisioning, resource expectations and actionable missing-assets behavior. Avoid automatic first-use downloads or claiming a dependency extra exists before it is implemented. |
| [Core concepts](../../../guides/03-core-concepts.md) | Update the affected package/ownership explanation: Commands interprets file arguments; Tools converts; Memory owns ingestion policy/storage admission; LLM owns embedding preparation/counting/limits; Chat/Runtime compose. Document headless reuse and shared typed contracts without claiming a complete FILE-001/TUI migration. |
| [Adaptive memory](../../../guides/04-adaptive-memory.md), [Memory management](../../../guides/memory-management-guidelines.md) | Explain identity-bound vector/graph state, explicitly configured fresh-store policy and coherent associated paths, unchanged-model preparation changes, first-run/unset refusals, Runtime-root consequences and old-release backup/recovery guidance. Distinguish document chunk tokens, embedding capacity and context/maintenance budgets. Preserve maintenance ordering and rollback semantics. |
| [Tools](../../../guides/05-tools.md) | Explain the new shared document capability, supported formats/limits, sandbox and missing-dependency errors, injected Memory handoff and source/derived storage. Distinguish completed INGEST support from ReaderFactory/smart_read four-format adoption, which remains the separately directed TOOLS-DOC companion. Do not advertise every direct legacy reader as migrated. |
| [Multi-agent](../../../guides/07-multi-agent.md) | Make the narrow embedding compatibility implication explicit where needed: visibility namespaces are authorization partitions over a shared physical space; preserve visibility and truthful partial-promotion results. No new multi-agent feature, coordinator algorithm or transaction claim. |
| [Friday Chat CLI](../../../guides/09-cli-reference.md) | Document genuine PDF/DOCX/XLSX/PPTX `/read`/`/ingest`, quoted paths/descriptions, the two ingestion overrides, defaults and precedence, document `--lines` refusals, effective statistics/errors and conversion progress/cancellation. Preserve other command contracts; add no URL-ingest/automatic-tool route or standalone CLI launcher. |
| [Configuration](../../../guides/10-configuration.md) | Show the final qualified `ingestion.chunking.strategy/max_tokens` schema and command → YAML → built-in precedence; explain why `smart_file.chunk_size/chunk_overlap` cease controlling ingestion. Document model-profile capability fields/readiness records, preserved pool selection, explicit destination origin, local asset root and compatible shared-space rules. Qwen remains illustrative unless separately selected. |
| [Troubleshooting](../../../guides/13-troubleshooting.md) | Provide safe diagnostics/remedies for missing packages/assets, corrupt/encrypted/partial/empty documents, OCR limitations, overflow/shape/identity refusal, unset or existing-unbound paths, and cancellation/busy behavior. Explain which Memory operations are unavailable and that help, `/read` and exit remain usable. Do not recommend deleting stores, bypassing TLS, silent fallback or interpreting a listing as extraction proof. |
| [Guide index](../../../guides/README.md), [Appendices](../../../guides/14-appendices.md) where affected | Repair navigation and supported-format/dependency/version matrices. Identify the implemented candidate/release baseline accurately. Limit edits to facts changed by this unit; no unrelated whole-guide refresh or automatic publication. |

Package [Tools README](../../../../packages/friday-tools/README.md),
[Chat README](../../../../packages/friday-chat/README.md), packaged templates and
final provisioning/upgrade instructions remain required alongside these guides.
Only future TOOLS-DOC acceptance permits its adoption claims; INGEST's shared
converter alone does not satisfy that documentation milestone.

## Bind into the construction directive

1. Reconcile the named guide paths with the final approved allowlist and the
   [Package Impact Assessment](package-impact-assessment.md). This adds explicit
   documentation coverage, not another runtime package or broader product feature.
2. Freeze dependency versions, extra names, assets, limits, model/counter facts
   and commands from Gate A. Guide examples must use those measured facts and
   synthetic/disposable destinations, never the dirty user examples or stores.
3. Require a changed-behavior → guide-section → source/configuration authority →
   exact example/installed verification matrix. Check positive and failure
   examples; no credit for old alpha3 snippets or fabricated model/format proof.
4. Make guide completion an explicit implementation acceptance criterion and
   independent review input. Run lifecycle/link checks and the guide checks
   appropriate to the affected examples; document any operator-only steps.
5. Present the final scope and any material impact addition to Chuck before
   construction approval. The exact post-readiness assessment/directive binding
   and his remaining approval conditions still apply.

The Package Impact Assessment council reviewed v0.2 at `1a040de3`; it did not
review this subsequent guide handoff. Its verdict must not be extended to this
new input. This document does not update the frozen REM, satisfy Chuck's package
impact sign-off, activate Gate A, authorize product/guide implementation or grant
publication/delivery authority.
