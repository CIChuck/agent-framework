# Final INGEST approval documents — council outcome

2026-11-13. **CHANGES_REQUESTED — one mandatory document inconsistency.**
All three fresh seats assessed FD1–FD8 completely. Two pass; Opus identifies a
Certifi baseline/phase contradiction and scores below 9.5. The per-seat gate is
unmet; this is not a majority vote or an averaged score. The single authorized
round is complete and inactive. Neither a repair nor another council is launched.

Reviewed candidate: `c2fcee0db2fc5b8dbf3a4682bd31cd2ce95963a0`, branch
`feature/cmd-ingest-001`. The [approval request](../../../README.md), canonical
[impact assessment](../../../../../../../package-impact-assessment.md), current
bound JSONs and all reviewed input bytes are unchanged. This outcome adds only
archived evidence and current routing metadata.

## Complete independent assessments

| Seat | Verdict | Reported overall /10 | Areas | Mandatory findings |
| --- | --- | ---: | ---: | ---: |
| [GPT-6.1 Sol](sol/report.md) | VERIFIED | 9.6325 | 8/8 | 0 |
| [GPT-6 Astra](astra/report.md) | VERIFIED | 9.640 | 8/8 | 0 |
| [Claude Opus 5.5](opus/report.md) | CHANGES_REQUESTED | 9.30 | 8/8 | 1 |

Opus reports raw weighted total 9.305 and truncates its displayed result to 9.30.
The scores remain exact as reported; no result is inflated or carried forward.
All three describe the package as coherent and bounded. Sol/Astra consider both
documents decision-ready; Opus identifies the concrete dependency-timing issue
below. Controller source verification supports that issue despite the other two
passes. There is no incomplete seat or runtime-test claim in this review.

## Mandatory MF-1 — Certifi baseline and introduction timing

The [approval summary](../../../README.md) requires the new Certifi floor after
**every private install**; the impact assessment similarly says after every
installation. The selected Tools document-extra and its lock delta arrive only
at **I3-C1**, while earlier I1/I2 changes are limited to their own scopes.

A fresh controller read of `uv.lock` confirms Certifi **2025.11.12**. Root and
workspace package metadata declare no direct Certifi requirement today. Therefore
an earlier phase installed from that lock cannot satisfy the unconditional
`certifi>=2026.10.19` check without an unplanned early dependency update or a stop.
The wording also obscures the actual shared CA-bundle upgrade to selected
Certifi **2026.10.23** at I3-C1, affecting every HTTPS consumer.

Controller disposition: **accept MF-1 as a bounded planning correction**, not a
request to change packages now. Recommended exact policy, if Chuck authorizes:

- Record the locked Certifi version/module and certificate origin during I1/I2;
  do not pretend the future floor is already supplied by those phase deltas.
- Introduce selected Certifi 2026.10.23 with the Docling/Tools delta at I3-C1,
  satisfying the required minimum 2026.10.19 after Docling installation.
- From I3-C1 onward enforce the floor and module/CA origin after applicable private
  installs, including every final I3-C5 normal/optimized/headless/Chat lane.
- Align the two documents and any phase-specific execution-profile wording, then
  refresh the approval-request and current binding hashes. No source, test, lock,
  production environment, vendor study or model operation is needed for this fix.

An alternative is an explicitly authorized earlier Certifi delta at I1-C2. The
controller does not choose that broader timing change under a read-only review.
The recommendation above follows the planned Docling introduction stage and the
maintainer's requirement to upgrade Certifi when installing Docling.

Future implementation evidence must show the recorded early baseline and the
later enforced version, module and CA origin. This is phase/install acceptance,
not a new wheel-provenance campaign or new pre-coding runtime experiment.

## Optional advice and controller disposition

- **Opus A1 — shared tokenizer upgrade:** controller confirms the lock contains
  tokenizers 0.22.1, consumed by Chroma and LiteLLM. The selected 0.23.3 pin at I1-C2
  changes their shared installed dependency too. Recommend a short disclosure in
  the existing dependency impact text and retaining the already required I1
  legacy-positive controls. A resolution conflict stops the intended phase;
  it does not authorize another model/backend or unrelated dependency upgrade.
- **Opus A2 — operator prerequisite:** make the already specified embedding-
  manifest/local-counter requirement prominent in the operator summary, including
  fresh stores. This is not a new model-config key or parity prerequisite.
- **Opus A3 — work-state clarity:** if expanded, explain phase activation under
  the existing started initiative and exact maintainer approval. Do not move the
  whole initiative backward or infer code authority from its historical flag.
- **Opus A4 and Sol/Astra — exact approval receipt:** prominently bind the final
  presented commit, request digest and effects after any authorized correction.
  Current request fields already require it; do not bind approval to changed,
  unpresented bytes.
- **Sol/Astra — operator quick reference:** consolidate the two bindings, fresh
  destinations and old-release recovery guidance within the already assigned
  documentation work. This remains optional, not an added preconstruction gate.

These recommendations are recorded, **not applied**. No advisory is promoted to
an implementation feature or expanded package owner.

## Evidence, qualification and preservation

Original reports and minimal boundary evidence are retained byte-exact, with
[hashes and verdicts](index.json), [frozen request](request.json) and the
[controller closing boundary](controller-closing.json). All frozen pins, HEAD,
branch, logical index, status, empty staging, 16,690 nonplanning file hashes,
26 symlinks and eight preserved metadata/hash records matched before outcome edits.
No product imports/tests/builds/installs, archive/AST replay, network/model/provider/
store action or production change occurred. Lock/TOML reads are static evidence,
not executed installations or a vulnerability assessment.

Opus disclosed that its first command hashed the raw Git index and ran locks-off
status before the required logical-index measurement. Its later logical entry and
exit match the frozen identity. The report and disclosure are preserved; this
brief does not require automatic disqualification for that deviation. The
controller independently reproduced the source finding and observed no mutation.
It is not hidden or relabelled as perfect procedural compliance.

## Chuck's next task

Review this finding alongside your document comments. Authorize the bounded
Certifi wording/timing correction and, if desired, the shared-tokenizer disclosure
and other small clarifications; then request a fresh review of changed bytes.
The previous single-round permission does not authorize automatic remediation or
another pass. Construction remains unapproved until the requested gate and exact
impact/scope/effects approval are resolved. Product acceptance and delivery remain
separate. No new delegate is running for this completed council.
