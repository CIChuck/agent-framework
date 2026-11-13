# Gate-A harness directive — full council criteria

Review readiness of the proposed construction instructions, not an implemented
harness. No executable test infrastructure exists yet. Future installs, genuine
format/model proofs and implementation tests are specified obligations, not
missing current runtime evidence. Every seat assesses every row and maps the
directive's HR-01–12 requirements to this matrix.

| ID | Mandatory design/source-feasibility question |
| --- | --- |
| HRC-01 | Is authority and stage separation coherent: directive draft, exact approved parents, separate construction/effect/window permissions, no inference of acceptance or prior review coverage? |
| HRC-02 | Is the edit allowlist test-only under `tests/readiness/ingest/`, with no production package/source/test/config/lock/environment/store edits, and only the explicitly named test ignore metadata change? |
| HRC-03 | Can bootstrap, private dependency targets, configuration, environment, imports, bytecode, caches/temp/logs and subprocesses stay isolated before and during execution, with no live-checkout/working-venv fallback? |
| HRC-04 | Are physical path ownership/alias/escape/archive and shared input/asset publication rules implementable and fail-closed, with accurate containment limits rather than intent presented as proof? |
| HRC-05 | Are manual preflight/init/full/selected/offline/report operations coherent, including no-effects preflight, fresh initialization, explicitly owned continuation, and incomplete versus complete qualification? |
| HRC-06 | Do dependency/asset/input manifests bind exact versions, URLs/digests/licenses and effects promotion, Certifi floor and candidate inputs without modifying production metadata or silently fetching extras? |
| HRC-07 | Does shared LM Studio reuse require operator-confirmed production shutdown, restart and actual test-log separation, exact model/endpoint/request scope, expiry/revocation and per-batch checks, without harness service-management rights? |
| HRC-08 | Is the served-model reuse exception distinguished from isolated Docling/OCR/tokenizer assets and application state, with unknown endpoint/model/counter facts blocking only dependent effects and no unsupported server capability assumed? |
| HRC-09 | Are genuine deterministic fixture expectations and explicitly supplied private-document copies sufficient to evaluate meaningful extraction/ordering/warnings/refusals while originals and production data remain untouched? |
| HRC-10 | Are document/recursive/fixed, 512-token/override and complete prepared-input limits specified, distinguishing preliminary counts, synthetic protocol vectors and real model qualification? |
| HRC-11 | Is the unit bounded to A0–A4 upstream feasibility with no Memory/Chroma writes or framework feature extraction, preserving later command/store/consumer/test-migration/guide obligations? |
| HRC-12 | Are network/process/resource/admission/termination controls measurable and restricted to owned work, with no production restart, automatic cleanup or runtime side effects during this review? |
| HRC-13 | Are HR-01–12 positive/negative/regression checks meaningful, normal/optimized, private and explicitly selectable, accounting for root discovery excluding `tests/` and minimal versus dependency-requiring lanes? |
| HRC-14 | Do reports distinguish observed results, operator attestation, inspected history, skipped/blocked work and future obligations, with actual reproducibility/origin/protected-state evidence? |
| HRC-15 | Do current authority/navigation/roster agree on this one read-only council pass, no implementation/effects/window activation and no production code change, with historical records preserved? |
| HRC-16 | Are scope boundaries, independent implementation review, remaining operator inputs, stop conditions and human decisions precise enough for construction without inventing authority or expanding unrelated product work? |

Read the complete directive and relevant pinned parents. Inspect source only to
validate a concrete claim or boundary; do not restart a framework-wide product
design audit or demand future integration evidence in this document-only gate.
Do not reintroduce a separate LM Studio server requirement: the maintainer has
explicitly permitted the shared endpoint under the production-offline window.

Each PASS needs a document/source/command citation. A mandatory violation yields
CHANGES_REQUESTED regardless of score. Use BLOCKED only for genuine inability to
review this candidate, not because future construction or stage activation is
intentionally pending. Historical labels or references to unrelated past reviews
are not current peer evidence; disclose relevant exposure without inventing a
procedural failure for merely encountering an unrelated navigation label.

Return separate coverage and overall scores out of 10 with a justified breakdown.
Coverage measures these 16 criteria and HR-01–12 traceability. Overall measures
scope/authority (2), isolation/effects enforceability (3), clarity/feasibility (2),
verification/evidence (2), and manual operator usability (1). Score honestly;
never raise a score to reach the 9.5 target. No score grants construction authority.
