# INGEST activation package council — Round 3 (final), Opus seat

- Seat: opus (claude-opus-5-5, high), fresh read-only context
- Candidate: fd7d9f5d429857906d53da8fc053dc85b901a635 on feature/cmd-ingest-001
- Request SHA256 verified before reading it (stdlib): 8b9421da…61ae11
- **assessment_complete: true; areas_assessed: 8/8**
- **Verdict: CHANGES_REQUESTED**
- **Overall: 9.27 / 10** (weighted, truncated, not rounded up)
- **Mandatory findings: 1**

## Boundary and identity checks

- Entry and exit, with GIT_OPTIONAL_LOCKS=0 and bytecode off: the logical index (`git ls-files -s -z` SHA256) was taken before status. It was 8524b5db…af46 both times, matching the request. HEAD and branch matched. Status had exactly the three expected entries, and nothing was staged.
- All eight preserved-metadata records matched (mode/size/mtime/ctime/birthtime and declared SHA256). I checked only metadata and hashes. I did not read the contents of user YAML, .friday*, exports or .venv.
- All 15 required inputs, 10 optional references and the controller-checks file matched their pins, both in the worktree and at the candidate commit. current-controls.json matched 192441…e9c1.
- I treated controller-checks.json as structural metadata only.
- I recomputed all five canonical-JSON digest vectors and the raw UTF-8 vector with stdlib. All match, and the receipt's plan_sha256 equals the plan vector's digest.
- Source reads were targeted questions only: Tools package import chain, `DIContainer.shutdown`, `FrameworkAsyncClientLifecycle` and the Chat runtime assembly, `ModelTarget`/`EmbeddingOptions`/`LiteLLMEmbeddingService`, `SmartFileReader` location, Core logging stream, and psutil declaration.
- Not done: no product import, test, build, install, network, model, provider or store call. No AST or inventory rebuild, provenance audit or harness replay. Finance `test_integration_massive.py` was not opened. No previous-round or peer reports, memory or history were used. Nothing was written to the repository or the inputs, and no delegates were used.

## D1–D3 correction requirements (assessed first)

- **D1 — satisfied.**
  - shared-contracts §4 names the canonical module `friday_tools.filesystem.readers.document_ingestion`. It also gives the exact `create_subprocess_exec(sys.executable,'-I','-B','-m',…,'--worker')` argv.
  - Inputs and controls: an explicit absolute `scratch_root` constructor argument, an owner-only per-session `request_root` beneath it, and connected stdin/stdout/stderr PIPEs.
  - Pipe handling: four-byte length-framed JSON capped at 128 MiB, a 1 MiB stderr ring with continued drain, retained writer/reader/drain tasks, and process-group TERM→KILL→reap.
  - The slice map assigns the installed nested-module launch, real exchange and malformed/oversize/timeout/reap witnesses to I3-C4. The validation plan states that an argv mock earns no proof. No pre-coding experiment is required.
- **D2 — satisfied.**
  - The test map places the three /read responsiveness, cancel/join and app-shutdown nodes at I3-C4. Basic extraction and hidden-workbook refusal are at I3-C3.
  - The validation plan's closing paragraph and requirement-reconciliation agree.
  - The I3-C4 assignments in the slice map for files.py, registry.py, adapters.py, runtime.py and di.py supply the matching lifecycle edits.
  - app.py remains a source-unchanged witness, and there is an explicit stop-and-reconcile rule.
- **D3 — satisfied for the embedding side.**
  - Discovery is exact: an explicit `manifest_path` wins, else the `FRIDAY_EMBEDDING_MANIFEST` snapshot. The path must be absolute, an invalid explicit path never falls back, and there is no cwd/HOME/YAML search.
  - The strict manifest and record schema is specified, including 1 MiB/2,048 caps, a non-cyclic asset manifest, an exact case-sensitive route triple and alias records.
  - The public pure resolver is assigned to I1-C2 (`embedding_limits`). I2-C1 composition binds `from_spec`/legacy, Chat, Runtime DI and CLI.
  - Unchanged YAML stays parseable. Supported defaults must resolve positively at I2-C1, with an explicit witness. Evidence hashes are optional, and there is no serving/parity gate.
  - I checked the interfaces against source: `ModelTarget(model_id,family,revision)` exists; `EmbeddingOptions` currently has only batch/cache keys; `from_spec` uses `execution_target`.
  - D3 does not cover the converter's deployment binding; that is finding M1.

## Review A1–A8

| ID | Weight | Score | Contribution | Evidence |
|---|---:|---:|---:|---|
| A1 | 1.50 | 9.6 | 1.440 | All three maintainer decisions are applied, with no reintroduced parity campaign. Gates A1–A5 are honestly open. requirement-reconciliation explains the superseded "no new council" clause. The council is separated from construction authority. |
| A2 | 1.75 | 9.0 | 1.575 | The frozen typed values, codes, signatures, canonical JSON and plan/receipt/destination identity are exact and the vectors are valid. One gap: the converter's injected construction inputs have no defined production source (M1). |
| A3 | 1.75 | 9.3 | 1.6275 | Ownership split is exact. Bounds: 1 active/1 queued, busy before I/O, deadlines, a failed-reap health state, and ordered shutdown with retained close tasks. Seams I checked against current source: `DIContainer.shutdown`, the dataclass-only `FrameworkAsyncClientLifecycle`, the builder at runtime.py:1419, and app.py's finally→`async_clients.close()`. Headless recipe is renderer-free. Minor issue: worker import side effects (advisory A-1). |
| A4 | 1.50 | 9.0 | 1.350 | Old call shapes are retained, capabilities are optional keyword-only, and there is a staged I1→I2 guarded switch. Fresh-store marker and strict v1/v2 recovery are exact. However, no operator configuration shape exists for document conversion in Chat or Runtime (M1). |
| A5 | 1.25 | 9.3 | 1.1625 | 91 exact path assignments, 49 mapped cases with frozen identities, 42 planned witnesses, module and helper classes, and explicit non-default selectors. The Finance live file is excluded. Small traceability gaps remain (advisories A-2, A-3). |
| A6 | 0.75 | 9.6 | 0.720 | Typed codes cover workbook refusal with safe and actionable text. Chunk policy is deterministic with no overlap or lost tail. Capacity refusal comes before effects, `PreparedWriteResult` is exact, and a receipt is issued only after readback. |
| A7 | 0.75 | 9.2 | 0.690 | Package roles are clear: Core neutral; LLM counter/resolver/`tokenizers` extra; Tools converter (psutil already declared); Memory policy. TOOLS-DOC is separate. Headless profiles are named. The converter's profile/asset deployment ownership is not stated for consumers (M1). |
| A8 | 0.75 | 9.5 | 0.7125 | I1, I2 and I3 each have coherent intermediate compatibility. Per-slice approval and independent validation are required. Gates A4 and A5 have a named owner and timing. Aggregate review then UAT is set out. |
| **Total** | 10.00 | | **9.2775 → 9.27** | |

## Mandatory finding

**M1 — No production binding or discovery for the document converter's construction inputs (A2/A4/A7; Chat, Runtime and CLI composition).**

Evidence:
- shared-contracts §2 requires `DoclingDocumentConverter(*, assets_root, profile_id, asset_manifest_sha256, scratch_root)`.
- §4 says `scratch_root` is "bound by the execution profile" and forbids an implicit production fallback or an inferred .friday path.
- §3 says Runtime gains no document YAML, and that "Disabled memory/read-only startup and /read do not resolve this manifest". That manifest is the only defined deployment discovery: FRIDAY_EMBEDDING_MANIFEST.
- In the slice map, Chat config.py at I3-C3 adds only `ingestion.chunking` strategy/max_tokens. runtime.py at I3-C3 says only "framework composition of shared entry/converter/counter".
- I found no document that names where the real Chat app, Runtime DI or a headless consumer obtains `assets_root`, `profile_id`, `asset_manifest_sha256` and `scratch_root`. This includes the read-only /read path, which by rule may not consult the embedding manifest.

Violated requirement:
- The brief asks for exact injected dependencies and configuration shapes, and for no unclear owner that would misdirect a builder.
- This is the converter-side counterpart of D3. A builder must currently invent a configuration key, an environment variable or a temp-dir fallback, each of which the contracts forbid. Otherwise the builder stops at I3-C3/C4.

Bounded fix (planning documents only):
- Specify one exact document-conversion deployment binding in shared-contracts §3/§4 and requirement-reconciliation. One option is a public pure resolver with explicit path precedence over a single env snapshot, which /read is permitted to resolve. The other is an explicit section of the existing deployment manifest whose use by /read is expressly allowed without resolving embedding capability.
- Give its strict fields: absolute `scratch_root`, `profile_id`, `assets_root`, and an asset-manifest hash reference.
- Give its precedence, and a typed `missing_asset`/`readiness` outcome for the four document formats only, so text /read and disabled-memory startup stay unaffected.
- Assign the owning files and exits: Chat runtime/adapters at I3-C3, the Runtime/headless recipe, and guides at I3-C5.

Required future acceptance:
- An I3-C1/C3 witness for positive resolution from provisioned local assets.
- Absent/invalid-binding refusal with no worker spawn and an unaffected text /read.
- Installed-probe use of the same binding.

## Advisories (non-blocking)

- **A-1 (worker launch chain).** `-m friday_tools.filesystem.readers.document_ingestion` executes the parent package `__init__` modules first. friday_tools/__init__ eagerly imports finance (→friday_finance), smart_read, the sandbox and the existing readers.
  - So "redirect vendor stdout before imports" cannot precede those imports.
  - State that fd-level redirection happens first in the module body, that parent-package imports must remain stdout-silent, and that their cold-start cost counts against the 300 s bound at I3-C4. Package `__init__` files are not in the slice map.
- **A-2 (resolver strictness witness).** The I1-C2 witnesses do not name the manifest-schema/containment negatives: unknown or duplicate keys, the size/record caps, record hash mismatch, traversal/escaping symlink, and a relative path. These map only via DI-24 and the I2-C1 integration node. Add a named I1-C2 node in test_embedding_limits.py.
- **A-3 (I1 regression selector).** simple_vector.py is edited at I1-C3, but `test_simple_vector.py` (already classified) is absent from the I1 selector list. Add it as an unchanged regression run.
- **A-4.** `FrameworkAsyncClientLifecycle` is currently `@dataclass(frozen=True)`. Note that `bind_ingestion` requires a non-frozen holder or an explicit lock-guarded slot, and that the change is within the adapters.py scope.
- **A-5.** Reword "No new constructor-required parameter or YAML key" to "required YAML key", to avoid contradicting the optional `max_input_tokens`/`expected_dimensions` additions.

## Limits

- This is a document-design assessment of the frozen candidate. It is not product conformance or evidence of runtime behaviour.
- Source reads were targeted, not exhaustive. Parent directives were consulted only by keyword for M1, which found no converter binding.
- The score reflects the design as written. This seat grants no construction, effects, acceptance, push or delivery authority, and no further pass follows from it.
