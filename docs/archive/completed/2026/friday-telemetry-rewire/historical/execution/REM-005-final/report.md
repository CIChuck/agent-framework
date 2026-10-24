# REM-005 builder closeout

Approved five-finding remediation is committed at
`5c3a0e6dc8ba995bad9e7dfb8c574f5dfd335bc8`, exactly15 approved product paths.
The [candidate manifest](../REM-005-candidate/product-manifest.json) matches the
committed bytes. This is builder evidence; fresh independent VAL-010 is in review.

| Required builder gate | Final result |
| --- | --- |
| Six regression modules |132 passed |
| Chat/LLM/Telemetry |1,247 passed |
| Root collection/full suite |3,129 collected;3,128 passed;existing optional SciPy skip |
|13 aggregate owning trees |3,110 passed;same optional skip |
| Changed-unit/aggregate Ruff and genuine Mypy |pass;12/81 source files |
| Raw root Ruff |exit1;exact327 separately approved WVR-006 identities |
| Five original defect probes |all repaired against final bytes |
| Scope/API/metadata/lock/board/docs/diffs |pass |

The [unaltered original report](raw/report.md.gz) and
[original artifact manifest](original-artifact-manifest.json) are preserved.
[Stored manifest](stored-artifact-manifest.json) binds all300 original artifacts
and their compressed hashes. Original report SHA256
`e91da9addb786777efbd99bbad30d7ed4181324e5500d4f27f9176fd0ec726d5`;
original manifest SHA256
`1ccb18f2ade01a3e8203ac9da546d354599665a8873da9419621a9fea36cd6e9`.

Original failed attempts and successful reruns remain distinct. Earlier private
freeze v1 is superseded by the final malformed-origin diagnostic correction and
four regressions; all final gates ran against v2 bytes. Initial sandbox runs
failed the same approved loopback fixtures; authorized reruns passed. One failed
aggregate Mypy stdout was reconstructed from tool output after receipt overwrite,
and the interrupted initial focused run lacked buffered stdout; neither is
represented as a complete original receipt. Exact limitations/provenance appear
in the unaltered builder report. No new skip, suppression, waiver or effect.

Separate independent full REM/unit/aggregate verification and maintainer
acceptance remain required. Delivery remains local.
