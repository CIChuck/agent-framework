# Friday MCP First-Pass Aggregate Review Readiness

- Date: 2026-09-29
- Status: Read-only aggregate review preparation; no initiative verdict
- Initiative: `friday-mcp`
- Branch: `feature/friday-mcp-ws08-docs`
- Initiative baseline: `20c70dd70622e5f1b80029076a789fb58c748fb5`
- Accepted work-unit state: WS-00 through WS-08 independently VERIFIED and explicitly accepted
- Aggregate candidate: `847d410` (WS-08 acceptance record; no product change after corrected `08141407`)
- Delivery: Local

The build and tactical plans define an initial tools-only integrated MCP client
pass across Core, MCP, Runtime, Chat, Transcript, Memory, Telemetry, tests and
guides. The nine accepted work units were each reviewed within their own
construction boundaries. [Independent validation policy](../../../../reference/policies/independent-validation-policy.md)
also requires a complete feature-branch aggregate review before merge to test
their interaction. The frozen initiative baseline is the recorded WS-00 start
base, not the older Git merge-base that includes unrelated prior initiatives.

`20c70dd..847d410` changes 287 paths: 75 product, test, config, guide or
package-metadata paths and 212 planning/evidence paths. The product path list,
current hashes, complete diff path list and five unrelated dirty-path
fingerprints belong in the aggregate manifest. A fresh-context read-only
validator should review the complete candidate diff against the accepted
first-pass authority, original and final work-unit evidence, and current
public source; exercise cross-work-unit local stdio behavior and distinguish
inherited failures from new regressions. The aggregate review must not be
reduced to concatenating nine prior VERIFIED work-unit verdicts.

Known nonzero evidence remains visible: broad Friday Chat has a PTY timing
failure and three localhost bind PermissionErrors; top-level integration has
the stale 22-versus-23 board-count assertion; default mypy has installed NumPy
syntax debt under the repository Python target. The exact current results and
baseline comparison are for the validator to establish. Run only local fake
peers and scratch storage; do not call a live provider or use credentials.

WS-09 external `config_file` support is optional and deferred, and the current
parser rejects that key. This review neither approves WS-09 nor requests its
implementation. It also does not authorize merge, push, release, deployment,
paid/live UAT or initiative acceptance. If the aggregate returns VERIFIED,
prepare an initiative completion proposal for a separate maintainer decision.
