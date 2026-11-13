# Gate-A harness directive — round 1 reconciliation

**CHANGES_REQUESTED.** All three seats request changes. The 9.5 target is unmet;
no construction, effects/window activation, acceptance or delivery is granted.
The test-only edit scope is tight; the open gaps concern how the harness runs.

Reviewed candidate: `f81453695007cacfa072fe295b8da7aa478438ba`.
Directive source: `494eed4f1c15d79d29cf0acc5e2203d7c7ebe5ef`, SHA256
`e44d4e4b28736d66a1de1e66314cb6da25343430dec0933be4ac9f1645ec91ad`.
The [directive](../../../../directives/CD-CMD-INGEST-GATE-A-001-readiness-harness.md)
and all 14 parent pins are unchanged at closeout. This is document readiness,
not executed harness/format/model/installed behavior proof.

## Council results

| Seat | Outcome | Coverage | Overall | Mandatory IDs |
| --- | --- | --- | --- | --- |
| [Sol](reports/sol-report.md) | CHANGES_REQUESTED | 10.0 | 8.9 | IGH-R1-SOL-001 |
| [Astra](reports/astra-report.md) | CHANGES_REQUESTED | 10.0 | 8.7 | IGH-R1-ASTRA-001 |
| [Opus](reports/opus-report.md) | CHANGES_REQUESTED | 8.6 | 8.3 | IGH-R1-OPUS-001–005 |

Scores are preserved as reported and are not averaged. Sol/Astra's coverage
scores measure review completeness, not requirement compliance. A majority PASS
on one criterion does not erase another seat's evidenced finding. All 16 HRC
criteria and HR-01–12 traces are retained in the raw reports.

## Six correction groups; all remain open

| Group | Reported IDs | Required design correction to prepare |
| --- | --- | --- |
| C01 — High | SOL-001; ASTRA-001 | Establish trusted Python startup before guards. Required `-I -B` forms permit site startup code. Specify safe interpreter/import loading and normal/optimized canary proof. |
| C02 — Major, as reported | OPUS-001 | Define staged manifest/promotion and resume bindings, when a model-window receipt can be created, and how `all` stops at missing promotion/window evidence. Preserve existing effect budgets. |
| C03 — Medium | OPUS-002 | Neutralize tool/user/system configuration, credentials, proxies and upward project/repository discovery; prove effective settings against pinned tool versions. |
| C04 — Medium | OPUS-003 | Define a read-only committed-source export, excluded dirty/untracked/ignored state and forbidden `.git` mutations. Never copy the live working tree indiscriminately. |
| C05 — Medium | OPUS-004 | Separate prevented from detected events, scope native/child controls and declare bounded fallback-cache metadata evidence. A detected forbidden write fails isolation; it is not prevention. |
| C06 — Medium | OPUS-005 | Bind the loaded model instance and loading/TTL/eviction conditions before requests. Preserve shared endpoint reuse while preventing unintended service/model lifecycle effects. |

Full IDs, severity, evidence/locations and future proofs are in each raw report
and [reconciliation JSON](reconciliation.json). The seven reported IDs collapse
only the duplicate startup concern, giving six distinct groups. No finding is
closed and no directive mitigation is implemented. All proposed corrections stay
within the readiness-harness contract; no Friday production-package rewrite is
proposed. The [advisory disposition](advisory-disposition.md) retains all seven
Opus advisories and guards against widening the time/effects budget.

Controller public-primary-source checks corroborate the relevant mechanisms:
[Python site startup](https://docs.python.org/3.13/library/site.html),
[uv configuration discovery](https://docs.astral.sh/uv/configuration/files/), and
[LM Studio loading/TTL/eviction](https://lmstudio.ai/docs/developer/core/ttl-and-auto-evict).
These are public documentation checks, not calls to the local service or proof
of its installed version/configuration. Exact source URLs/limits are recorded in
[source corroboration](source-corroboration.json).

## Evidence and limits

Every report SHA256 matches the terminal result. All seats record fresh task-only
contexts and opening/closing PASS for 17,773 protected files, 24 authority pins
and nine local metadata records. Each independently ran all eight read-only
administrative checks successfully. Command argv/exits, stdout/stderr, boundary
receipts and selected static evidence are archived under `evidence/<seat>/`.
The controller's own final frozen-candidate boundary also passed before closeout.

The original [request](frozen-inputs/request.json), [current controls](frozen-inputs/current-controls.json),
[compressed protected manifest](frozen-inputs/protected-manifest.json.gz), and
[review-helper audit text](frozen-inputs/review_tools.py.txt) are retained.
The [archive map](archive-map.json) records original/retained paths, byte hashes
and encoding. Decompressing the manifest recovers its exact original bytes.
Absolute original paths in raw receipts are provenance, never instructions to
reuse another agent's cache/output directory. Two source-excerpt receipts are also
losslessly compressed to retain their original whitespace. The initial controller
closeout committed them despite a failed staged whitespace check; the subsequent
combined-range check failed too. This packaging correction preserves their exact
source hashes and is recorded in [the controller audit](evidence/controller-archive-packaging.json).
It changes no reviewer verdict, directive or production file. Exploratory diff files not needed
for the formal evidence remain in original scratch and are not claimed archived.

No reviewer ran tests, dependency resolution/install/build, format conversion,
model inference, endpoint/network/provider/store operations, repairs or nested
agents. Static evidence varies by seat and is described honestly in their reports.
The controller consulted public official documentation only. No readiness harness
or `.friday_test/` environment was created; production application/configuration/
stores remain untouched. Review-time T3 Git checkpoint metadata is host activity,
not a harness mutation or changed source/index identity.

Root Ruff 534, the `test_display` conflict and registry formatting remain historical
FAILED/UNWAIVED debt, not fresh reproductions or a whole-repository green result.

## Next gate

The one authorized review pass is complete. Return the six-group bounded correction
list for maintainer direction, then obtain a fresh review authorization for a
revised frozen draft. No automatic remediation loop, replacement review, harness
construction, stage/model activation, acceptance or delivery follows. Existing
approval of unchanged package impact v0.6 persists.
