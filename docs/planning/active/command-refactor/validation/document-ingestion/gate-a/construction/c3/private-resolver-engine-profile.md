# Private resolver engine — proposed, not activated

[Exact profile](private-resolver-engine-profile.json), SHA256
`a9c64ca1ccc63ebe54c26108bc58c033792905394736fe048f29e84d74103a0f`.

The approved packaging parser checks requirement/version/marker and wheel
metadata. Completing actual dependency solving also needs a backtracking engine.
Use [resolvelib 1.2.1](https://pypi.org/project/resolvelib/1.2.1/) in private
scratch rather than writing a new resolver or bringing native uv resolution into
this profile. Its public release metadata specifies Python >=3.9 and ISC licensing;
those facts and its full wheel inventory must be inspected before execution.

This proposal permits **one exact 18,737-byte wheel**, one request, no retries,
redirects, extras or source build. Its SHA256 and URL are pinned from official PyPI
metadata. It is a new private tool, not a workspace-lock or production dependency
change. Reuse the already qualified packaging24.2 target without a new transfer.

Execution is limited to guarded synthetic/offline solving and typing tests, normal
and optimized Python, within private paths and bounded rounds/inputs/time. No real
package-index resolution, Docling/OCR/model/asset installation, service call,
store mutation, runtime A0–A4 activation or production change is included.

The reviewed [harness directive](../../../../../directives/CD-CMD-INGEST-GATE-A-001-readiness-harness.md)
requires: "Required private validation tools need their own exact activated offline
manifest; do not borrow `.venv`." The earlier one-wheel approval includes only
packaging. The next exact private-tool activation therefore needs approval.
No transfer or engine import has occurred. The frozen C2 correction review has
ended; exact profile activation is still awaiting approval.
