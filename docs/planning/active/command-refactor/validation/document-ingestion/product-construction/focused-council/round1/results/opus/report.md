# Opus seat — focused INGEST directive council, round 1/3

Verdict: CHANGES_REQUESTED
assessment_complete: true (8/8 areas)
Candidate 92e356d17bc3a97be18d3d7cc4fed740b06795d1, feature/cmd-ingest-001
Target CD-CMD-INGEST-001-product.md SHA256 8abad750e6346b7118c6c23ea0fd2f2550f19a880179d23e134487c4d32495f2

## F1-F8

| ID | Wt | Score | Assessment |
|---|---:|---:|---|
| F1 flow/contracts/ownership/headless | 2.0 | 9.5 | Owners clear (s2 l.97-104, s3.5 l.328-334); injected Core entry and no Tools<->Memory edge match REM ownership. Call direction (Memory entry invokes injected Tools Docling planner) is stated only in the REM. Headless document composition has no non-Chat witness (A1, A2). |
| F2 file command integration | 1.0 | 9.0 | Raw-tail/default-handler/options/`--`/lookalikes/line semantics are well specified (s3.2). Source confirms Chat `CommandRegistry.execute` splits on whitespace before handlers, so the raw-tail handoff needs a Chat dispatch change, which is implied but not named (A3). `/read`'s document conversion path is underspecified (M1). |
| F3 chunking/config/model guards | 1.5 | 9.5 | Independent override, then YAML, then built-in; budget is the final prepared input; no overlap, no second split; smaller-limit rule; once-only roles. The REM's no-clamp rule is inherited, not restated (A4). |
| F4 consumers/identity/upgrade/routes | 2.0 | 9.6 | Six exceptions with remedies, FC-01-14 safeguards, fresh-store and default-origin rules, CLI origin gap. Checked against source at `container.py:109-135`, which confirms the forwarded default. Route dispositions are traced via DI-19/34. |
| F5 errors/cancel/cache/destination | 1.0 | 8.5 | Ingestion worker/admission/quiescence and destination-bound receipts are strong. `/read` conversion has no lifecycle owner or witness (M1). |
| F6 package/dependency/install | 0.75 | 9.5 | The Tools extra plus Certifi floor, the narrow LLM counter via Memory, the stdlib-only Commands package, and the legacy extras are all consistent with current pyproject declarations. The packaging owner of the counter and qualified-profile assets is left to A2 (A5). |
| F7 tests/migration/docs | 1.0 | 9.2 | Meaningful registry, real-Chroma and separate-process reopen tests, zero-ingestion negatives, installed normal/-O lanes, a migration map and authored docs. There is no `/read` responsiveness or cancellation witness (M1). |
| F8 sequencing/gates/handoff | 0.75 | 9.5 | Q→I1→I2→I3→AG→UAT is coherent. Additive I1 staging, a stop if staging is not possible, per-exit regression blocking, and a mandatory DI-12 council before UAT. |

Weighted overall = 93.4/10 = **9.34**. Coverage = **9.5**. Rubric: F1 2.0, F2 1.0, F3 1.5, F4 2.0, F5 1.0, F6 0.75, F7 1.0, F8 0.75.

## Mandatory finding

**M1: Document `/read` conversion has no event-loop, cancellation or shutdown owner and no acceptance path.**

- **Requirement.**
  - s3.5 l.320-324 runs conversion and OCR off the event loop.
  - REM DI-26 requires that "Event loop remains responsive during conversion/counting".
  - s3.2 l.204-206 says "`SmartFileReader` delegates the four formats to the shared converter. `/read` renders actual content …".
- **Gap and evidence.**
  - s3.5's lifecycle is defined in terms of "the request's shared admission" and "Chat owns its request and admission lease". `/read` has no admission: `_SHARED_ADMISSION_COMMANDS` at `friday_chat/commands/registry.py:77-86` excludes `read`.
  - Chat's async `_read_handler` (registry.py:669-680) calls the synchronous `SmartFileReader().read()` (`commands/files.py:44`) inline.
  - If that sync API simply delegates to the converter, a scanned 50-page PDF can block Chat's loop for up to the 300 s ceiling, with no cancellation.
  - No exit owns this. I3-C4 is ingestion-only (`test_cancelled_ingestion_waits_for_quiescence_without_late_storage`). The phase-map JSON `/read` entries cover only option refusal and embedding independence (DI-29).
- **Bounded fix.** In s3.2/s3.5 and the phase map, state that `/read` document conversion uses the same Tools-owned worker off the event loop, under a Chat-owned request handle with no Memory admission. Cancellation or exit discards output and joins the worker before the handler or session returns. Also state the `SmartFileReader` sync→async (or offload) contract change, and its owner (Chat).
- **Acceptance implication.** Add an I3-C3/C4 witness: `/read` on a slow or scanned document keeps the loop responsive; cancellation before, during and after completion leaves no late render or orphan worker; shutdown waits for quiescence. Trace it to DI-11/26.

## Advisories (non-blocking)

- **A1.** Add an I3-C2/C5 headless witness: Tools converter → injected Docling planner → Memory entry → store, without Chat. DI-23 is text-only, so for documents only Chat proves the "another frontend" claim (s1 l.44-45).
- **A2.** Restate the REM ownership line ("Memory … inject Docling adaptation and exact counting"; Tools "retain structure internally") in s3.3, and state that A2 freezes the Core counter/preparation protocol that the Tools Docling adapter consumes. Tools has no default LLM dependency.
- **A3.** Name Chat's `CommandRegistry.execute`/`_parse_command_input` as the raw-tail seam, and the identity check for default versus custom handlers.
- **A4.** Restate in s3.3 the REM rule (l.811-814): a configured or default budget above the effective capacity is refused, never clamped. This matters for N-CAP with the 512 default.
- **A5.** In A2's manifest, name the package and installed location of the qualified capability record and counter tokenizer assets for headless Memory/Runtime/CLI/Agent profiles.
- **A6.** State that RuntimeConfig gains no ingestion YAML, so headless defaults are Memory built-ins plus per-call options, and that smart_read processor chunk settings do not govern stored source chunks.

## Source reads and limits

**Read in full:**
- The target directive.
- criteria.md, review-context.md and authorization.json.
- phase-evidence-map.md.
- The TOOLS-DOC companion.
- package-impact-assessment.md (P01–P17, test/docs, dependencies, details to settle).
- readiness-decision.md.

**Read in targeted sections:**
- REM ownership (l.100-125), overflow (l.795-830), execution (l.1052-1076), and DI-07/11/16/19/23/26/29/30.
- A regex search of the phase-map JSON for `/read`.

**Product source read:**
- The dependency sections of the Chat/Tools/Memory/LLM/Commands/Runtime/CLI/Core `pyproject.toml` files.
- friday_commands `registry.py` (`execute_text`) and `contracts.py` (`CommandRequest`).
- In Chat: `registry.py` (dispatch, read/ingest handlers, admission set), `files.py` (`SmartFileReader`), and `adapters.py` (smart_read construction, ingest slicer).
- Tools `smart_read.py` (imports and cache layers).
- CLI `container.py` (`to_runtime_config`).

**Not read:**
- The test-migration, architecture and guide plans, the embedding contract, the authority manifest, the qualification plan and the inventories, beyond what is noted above.
- The controller checks (they were hashed only).
- Finance's massive test was not opened.

No imports, tests, builds, installs or network calls were run.

## Integrity (entry = exit)

- **request.json:** 32ab367a…99fe ✔. **controls:** 9098046d…9d66 ✔.
- **Target and all required/optional inputs:** hashes match, and they are committed-clean.
- **HEAD:** 92e356d1. **Branch:** feature/cmd-ingest-001.
- **Logical index:** 610562634bfd…cf26 ✔. **Status:** as declared. **Staged:** 0.
- **Preserved metadata (8 entries):** all OK. GIT_OPTIONAL_LOCKS=0 and bytecode off.
- **Writes:** only to this scratch directory.
