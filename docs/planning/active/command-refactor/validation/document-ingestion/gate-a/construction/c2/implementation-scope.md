# C2 dependency-selection consistency

Continue the already approved test-only harness construction under the unchanged
[directive](../../../../../directives/CD-CMD-INGEST-GATE-A-001-readiness-harness.md)
and [C1 continuation](../c1/continuation.json). The exact private parser
[activation](../c1/private-resolver-tool-approval.json) supplies the optional
standards implementation; there is no dependency download in this component.

The source increment is limited to `manifests.py`, its existing test module and
the harness README. It adds a pure declaration checker for proposed A0 wheel
closures, using the already approved private packaging 24.2 parser on explicit
target/environment metadata. Core startup/selftests remain standard-library only.
No artifact is downloaded, installed, imported as a candidate application package
or granted execution. Target fields are declarations, not observed machine facts.
Licenses remain unqualified even when a nonempty metadata string is present.

The checker validates Python and platform tags, distribution/wheel identities,
version constraints, additive base/extras and markers, cycles and late extra
requests, complete reachable closure, known hosts, explicit byte/count bounds,
and refusal of unknown/yanked/direct-reference selections. Its result always
withholds artifact/license/installed/execution qualification. Actual resolution,
metadata collection, source provenance, profile installation and later document/
model stages remain open. This is a necessary check inside the future adapter,
not a replacement for it or a reduction of HR-01–18.

| Criterion | Required evidence |
| --- | --- |
| CD-01 | Exact source/authority pins, only permitted delta, protected state and previously frozen C1 evidence unchanged. |
| CD-02 | Complete explicit schema/marker fields/tag selection; malformed control refuses before optional import. |
| CD-03 | Real approved parser handles versions, Python constraints, wheel/name identities, extras, markers, cycles and late extra expansion in positive flows. |
| CD-04 | Missing/conflicting/unreachable dependencies, malformed declarations, wrong wheel/platform/Python, unknown extras, unsafe host/reference/yanked/size selections refuse through actual call assertions. |
| CD-05 | Bound graph/requirements/count/byte declarations and no resolver/download/install effect or invented runtime/license permission. |
| CD-06 | All prior 54 test bodies retained; minimal selftests execute normal/-O without third-party import; explicit guarded parser-profile selector executes both modes with verified target/origin. |
| CD-07 | Root-rule Ruff/format and selected-source mypy with typed private parser API; no source/library edits, ignored errors or changed root rules. Treat the verified parser as a private PEP561 dependency, not an additional repository source. |
| CD-08 | Stable commit; fresh read-only delta then full bounded C0/C1/C2 aggregate, private tools/caches, administration, exact receipts and preservation, with real A0–A4 left unqualified. |

No full-readiness score, advancement, acceptance, model window or delivery is
granted by this incremental review. The initiative remains started/local.
