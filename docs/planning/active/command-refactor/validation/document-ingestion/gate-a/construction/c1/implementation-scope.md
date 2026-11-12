# C1 synthetic document inputs

This is an incremental implementation slice of the approved
[harness directive](../../../../../directives/CD-CMD-INGEST-GATE-A-001-readiness-harness.md),
under the [recorded continuation](continuation.json). It does not replace or
reduce any HR-01–18 requirement. All A0–A4 runtime qualification remains open.

The deliverable is deterministic candidate input generation and safe publication,
with independent literal content expectations. There are 30 original synthetic
containers: six PDF, six DOCX, ten XLSX and eight PPTX. They exercise body order,
late content, Unicode, tables, hidden units, notes versus comments, formula
caches, external relationships, encryption, empty content and image-only input.
The structural Office probe emits facts and refusal codes, never document text.
It is not a complete Office schema validator or the production reader boundary.
Native-reader compatibility, OCR quality, extracted text, source references and
chunk/embedding semantics require the later actual installed profiles.

`prepare-fixtures` publishes new, exclusive, read-only run-local inputs and a
digest inventory. The operation holds the ledger writer lease and checks the
sticky stop before each publication. An interrupted publication has no ready
manifest; the partial evidence is retained and a new run is required. The command
does not promote a stage or imply converter qualification. Reported preparation
receipts are ledger witnesses, explicitly not revalidation of current file bytes.

Only `tests/readiness/ingest/{fixtures.py,ledger.py,stages.py,reports.py,README.md}`,
the literal `fixtures/expectations.json`, and appended cases in the four matching
test modules change executable behavior in this slice. Bootstrap, guards, path,
environment, export and model-window code stay unchanged. Packet navigation and
evidence may change. All production code, dependencies, locks, configurations,
stores, model services and protected local state remain outside scope.

| Criterion | Required evidence |
| --- | --- |
| CI-01 Authority and preservation | Exact directive/continuation pins; permitted diff only; protected hashes, dirty configurations and ignored-state metadata preserved. |
| CI-02 Complete deterministic inputs | Exact 6/6/10/8 selection, repeatable bytes, unique hashes; PDF object offsets/pages/image stream/encryption and Office ordered structures independently inspected. |
| CI-03 Independent oracles | Literal expected markers, exclusions, unit counts and failure dispositions; no converter output used to generate expectations. |
| CI-04 Structural facts and bounds | Hidden sheet/row/column/slide/shape distinctions; formula-cache and external-relation facts; bounded ZIP/XML/coordinates/merged expansion; no text extraction claim. |
| CI-05 Publication integrity | Absent physical destination, complete oracle before writes, exclusive files, read-only inventory, wrong bytes/extra or aliased files refused; partial stop never publishes ready manifest. |
| CI-06 Writer ownership | Held append accepts only the live same-instance/same-process token; stale tip, foreign/released token and competing writer refuse. |
| CI-07 Manual command and reports | Frozen manual preflight/init/prepare-fixtures/report/stop flow works; exact input hashes; no stage promotion, no false conversion/full-readiness success. |
| CI-08 Retained controls | Original 43 test bodies preserved; all selected tests run under the committed loader in normal and optimized modes; previous controls still covered by current execution. |
| CI-09 Static and administration | Root-rule Ruff/format and mypy using activated private tools, explicit 25-source selection; board/dashboard/docs/metadata/owned whitespace pass. |
| CI-10 Independent review and limits | Stable candidate, source/blob identities, private scratch, fresh read-only validator; executed/inspected/unrun evidence distinguished. |

The private [resolver-tool proposal](private-resolver-tool-profile.md) is pending
separate activation. It supplies neither consent for a download nor permission
to run actual dependency resolution, Docling conversion or LM Studio requests.
The already approved private static-tool profile may be reused by verified copy.
No package-impact satisfaction, full-readiness score, human acceptance or delivery
authority follows from a bounded C1 result.
