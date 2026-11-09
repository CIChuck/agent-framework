# MEMQ-001 user acceptance test plan

Status: **planned — all cases NOT RUN**. Prepared 2026-11-09 for Chuck Russell.
Execute after the complete MEMQ candidate passes D2/D3 validation and independent
review. D1 supplies neutral code only; it does not provide the integrated Chat
application or installed-artifact evidence required for this plan.

This plan covers `/memory`, `/insights`, `/summaries`, `/meta`, `/entities` and
`/list-ingested`, including the approved option R persisted-document listing.
It supplements the accepted [Chat UAT roadmap](friday-chat-user-acceptance-roadmap.md).
The [contract](../memory-query-command-contract.md) and
[directive](../directives/CD-CMD-MEMQ-001-memory-queries.md) define the expected
behavior. Record this plan's results separately from automated tests and from
maintainer acceptance.

## Run setup

- Obtain the exact candidate commit, installed launch command, three council
  results, automated evidence and known limitations from the D3 handoff.
- Use a disposable configuration, transcript, memory store and export folder.
  Record their paths below. Keep existing personal stores and exports intact.
- Run the interface cases first in fake mode. For persisted listing, use the
  real FrameworkMemoryAdapter with a fresh disposable store; fake output cannot
  demonstrate persistence, grouping or promotion behavior.
- Use a configured provider only for conversational checks you choose to run.
  None of the six query commands should initiate synthesis or another model
  response. Record ordinary conversation latency separately from command latency.
- Obtain a prepared disposable fixture for populated insights, summaries, meta
  records and graph values, plus an independently recorded expected inventory.
  Empty output alone cannot verify populated rendering. Do not invoke synthesis
  or maintenance commands merely to manufacture these fixtures.
- For real-adapter ingestion supply an explicit non-empty description, for example
  `/ingest /path/document.txt project notes`. Existing `/ingest FILE` with no
  description passes `None` metadata to Chroma and raises `TypeError`; paired
  clean pre-D2/candidate controls reproduce it. This baseline defect is tracked
  in [FU-009](../../../backlog/friday-chat-framework-followups/upgrade-log.md#fu-009-omit-absent-ingestion-description-metadata). It is neither repaired nor waived
  by MEMQ. Use prepared persisted metadata for missing-description listing cases.
- Prepare small single-chunk and multi-chunk UTF-8 files in the disposable folder.
  Record their source paths and expected actual stored chunk counts. Keep a
  second fixture with promoted chunks and malformed/partial data for the cases
  requiring it; use the approved test setup rather than editing a personal store.

| Run information | Value |
| --- | --- |
| Run ID, date, tester | |
| Candidate commit / installed version | |
| Installed launch command | |
| OS, terminal and dimensions | |
| Fake / real adapter, provider and model if used | |
| Disposable config, store, transcript and export paths | |
| Fixture revision and expected inventory | |
| Single / multi-chunk source paths and actual chunk counts | |
| Store baseline / snapshot evidence | |
| Automated report and council result links | |

Enter slash commands at the Chat prompt. Capture the exact output, command
latency and any traceback for each case. Use PASS, FAIL, NOT RUN or BLOCKED;
explain a blocked prerequisite rather than marking an unexercised case PASS.

## Acceptance cases

| ID | Steps | Expected result |
| --- | --- | --- |
| MQ-UAT-01 Discoverability | Run `/help`, then `/help memory`, `/help insights`, `/help summaries`, `/help meta`, `/help entities`, `/help list-ingested`. | The six retained commands have their established descriptions, usages, argument details and grouping. No additional aliases, renamed commands or invented flags. Text is readable at the recorded terminal width. |
| MQ-UAT-02 Empty runtime | In the prepared fresh, empty disposable runtime run all six commands. | Statistics show the actual empty state. Record queries, graph and document listing show their appropriate empty messages, without an exception or a fabricated record. `/entities` says `No entities found.` and `/list-ingested` says `No ingested documents.` when their fixtures are empty. |
| MQ-UAT-03 Session statistics | Complete two conversational turns in the disposable session; run `/memory`. Compare session ID, history/turn counts, variables, store/transcript and budget facts against the fixture/configuration. Run it a second time. | Eight sections and 24 metrics retain labels/order and display actual facts. Zero is displayed as zero, unavailable and not configured remain distinguishable, utilization keeps its percent suffix. Querying does not add a conversational turn. Record any changing operational metric with its cause. |
| MQ-UAT-04 Insights | With the populated fixture, run `/insights`, then `/insights ignored words`. | Ordered insight previews match the fixture and the two commands agree. Unicode/newlines render correctly; previews preserve the existing 160-character rule. No metadata invented from unrelated record fields. |
| MQ-UAT-05 Summaries | Run `/summaries` and `/summaries ignored words` with populated and empty fixtures. | Ordered summary previews match their fixture and established empty output. Extra arguments are ignored, as before. |
| MQ-UAT-06 Meta records | Run `/meta` against full and sparse meta fixtures, then against empty complete and empty incomplete fixtures. | Previewed IDs/text, lifecycle, timestamps, confidence, source counts/provenance, verification and the decayed-policy line agree with expected fixture output. Missing values differ from present-empty values where specified. Both empty states retain their distinct messages. No duplicate formatting or repeated fragments. |
| MQ-UAT-07 Graph listing | Run `/entities`, `/entities nodes`, and `/entities nodes ignored words`. | General listing includes entities and relationships in the fixture order, with the established blank separator. Both exact `nodes` forms show nodes only and never relationships. Values `0` and `False` remain visible; absent values are omitted according to the contract. |
| MQ-UAT-08 Graph selection | Run `/entities NODES`, `/entities Ada Lovelace` and `/entities "Ada Lovelace"` against a fixture with known selections. | Only exact lowercase first-argument `nodes` selects nodes-only mode. Other words are joined with one space. Quote characters remain literal parser fragments; shell-style quote removal is not introduced. Compare the recorded selections and output with the fixture. |
| MQ-UAT-09 Caps and long values | Use a fixture with more than 100 records/entities/relationships and long Unicode text; run the relevant queries. | Each capped category displays at most 100 entries in established order. Existing text/ID preview lengths remain intact. No terminal crash or unreadable duplicate blocks. Document listing has no new 100-row cap. |
| MQ-UAT-10 Ingest and list | In the disposable real-adapter runtime, ingest each prepared single-chunk and multi-chunk file with an explicit non-empty description, for example `/ingest /path/document.txt project notes`. Omitted descriptions hit the separately tracked baseline TypeError; do not count that as a MEMQ listing regression. Run `/list-ingested`, then `/list-ingested ignored words`. | Each persisted `(source, description)` group appears once as `- PATH (N chunks): DESCRIPTION` under `Ingested documents:`. Counts equal stored chunk records, rather than a configured chunk-count value. Extra listing arguments are ignored. Existing ingestion behavior is unchanged. |
| MQ-UAT-11 Re-ingest grouping | Re-ingest one test file, inspect the independently recorded store inventory, and run `/list-ingested`. | Rows group by source and description. The count equals all currently stored chunks in the group, including repeated ingestion records actually retained by the store. The command introduces no deduplication or per-ingestion identity. |
| MQ-UAT-12 Restart and promotion | Restart Chat with the same disposable store. Run `/list-ingested`; then use the prepared fixture with chunks distributed across short- and long-term collections and repeat. | Listing survives restart, groups across both collections, and counts their stored records once each. Fake insertion-order behavior is assessed separately in MQ-UAT-15. |
| MQ-UAT-13 Listing order and historical paths | Use fixture groups with different sources and descriptions, including a missing description. Include a persisted path whose source file is absent. Run `/list-ingested`. | Sort by source, then description with missing description first. Missing description renders empty. Historical persisted paths still list; listing does not inspect source-file existence or content. Source validation and consolidation remain deferred. |
| MQ-UAT-14 Partial reads and warnings | Use the approved disposable partial-failure fixture for statistics, records and listing, with repeated/out-of-order warnings and malformed listing records. | Usable results remain visible with unique sorted warnings. A malformed listing record produces the `memory record` warning; a failed collection produces its collection warning. Query failure retains `Unable to query TITLE: store read failed.` where applicable. No misleading all-success display. |
| MQ-UAT-15 Fake listing compatibility | In fake mode, ingest two fixture documents and run `/list-ingested`; restart a separate fake session if appropriate. | Existing fake insertion order and its recorded counts remain unchanged. Record fake lifecycle behavior as fake-only evidence; it is not a real persistence result. |
| MQ-UAT-16 Unavailable runtime | Launch the supplied disposable runtime-missing scenario and run each of the six commands with empty and extra arguments, including `/entities nodes`. | Each returns `Memory runtime is not initialized.` without a capability query, usage error or model response. If that launch scenario is unavailable, mark this case BLOCKED and cite automated coverage separately. |
| MQ-UAT-17 Read-only behavior | Snapshot the disposable store/session/transcript before a query-only sequence of all six commands, excluding conversation, ingest and clear. Repeat it, then compare persistent records and conversational history. | Queries add no memory, synthesis, reorganization or conversational entries and do not alter session state. Expected operational logging is identified separately. No context/prompt export file is created by these commands. Preserve the before/after evidence. |
| MQ-UAT-18 Existing session flow | In a fresh disposable session: complete one turn, run all six queries, `/history`, `/clear`, `/history`, `/cls`, then `/q`. | History preserves the turn until clear. Clear retains its accepted current-session meaning; cls affects display. Exit and resource cleanup occur once. Queries do not duplicate assistant responses or consume their own conversational turn. |
| MQ-UAT-19 Responsiveness and cancellation | With the supplied delayed disposable query scenario, start a memory query and use the application's established cancellation mechanism. Repeat normal queries after recovery. | The pending operation is not falsely reported complete. Cancellation retains the host's existing behavior, with no retry or success output. Record actual recovery and latency; if no interactive cancellation fixture exists, mark BLOCKED and link automated cancellation evidence. |
| MQ-UAT-20 Presentation and repeatability | Repeat populated queries at normal and narrow terminal widths, then compare with captured expected output and the accepted prior command behavior. | Labels, punctuation, warning placement and line breaks remain readable; no extra trailing blank blocks or raw object representations. Record command latency and visible regression separately from model latency. |

Cases involving injected wrong record kinds, subclass payloads, direct non-string
arguments, invalid outcome effects and optimized Python invariants belong to
automated D1/D2/installed checks. A human terminal run cannot establish those
boundaries. Cite their evidence without counting it as an executed UAT case.

## Result record and handoff

| Case | Result | Output / screenshot or log | Latency | Defect / notes |
| --- | --- | --- | --- | --- |
| MQ-UAT-01–20 (one row per case when executing) | NOT RUN | | | |

For each failure, record the fixture, exact command, observed versus expected
output and reproducibility in a fresh process. Keep functional defects separate
from readability observations and ordinary model quality. Retain disposable
evidence until the run is reconciled; cleanup is a separate deliberate action.

The tester records the overall result, unresolved cases and explicit acceptance
decision after reviewing evidence. A completed checklist, automated pass or
council VERIFIED result does not itself accept MEMQ, approve another command
family, or authorize delivery.
