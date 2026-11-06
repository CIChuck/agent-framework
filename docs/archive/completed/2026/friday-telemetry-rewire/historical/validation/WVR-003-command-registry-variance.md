# Approved WVR-003: preserve CommandRegistry invariance

Status: explicitly approved, 2026-10-06, by repository maintainer Chuck Russell.
Approval evidence: "I approve A06 and WVR-003".
Proposal date: 2026-10-05.
Work unit: TELEM-01 / REM-004. Owner: repository maintainer Chuck Russell.
Follow-up: REM-004-GENERIC-01; cleanup decision before acceptance beyond TELEM-01.

The [exact scope](WVR-003-command-registry-scope.json) covers **one** current-code
Ruff UP046 diagnostic for `CommandRegistry` in `friday_cli/commands.py` at
74:23 through 74:33. The source remains byte-identical, including its invariant
`TypeVar("T")` and `CommandRegistry(Generic[T])` declaration. No new source
suppression, artificial member/base, cast, runtime default, dependency, lint
configuration, or Python target change is permitted.

The [compatibility evidence](../execution/REM-004-compatibility/report.md)
demonstrates that replacing only this header with `CommandRegistry[T]` infers
contravariance: mypy accepts a Parent-registry-to-Child-registry assignment that
the existing public generic rejects. REM-004 requires preserved variance. The
other five UP046 class probes preserve existing assignment rejection in both
directions and remain subject to the original implementation and API gates.
Retaining this one declaration protects the existing contract while the remaining
132 current-code findings are fixed.

Approved together with A06, this supplements WVR-002 **only** by
replacing its zero-live condition with exactly this single, independently matched
UP046 identity and frozen source hash. All WVR-002 archive identities, four file
hashes, Ruff 0.14.10, py313 target, seventeen lint configuration hashes, follow-up,
expiry and immutable archive constraints remain unchanged. Raw root Ruff and
changed-file Ruff must both run unchanged. Root must have exactly327 diagnostics:
326 WVR-002 archival findings plus this one live UP046. Changed-file Ruff may
have only this one when commands.py is among its targets; all other diagnostics
remain failures. Reports disclose the raw nonzero exits and each approved
exception separately. This approval grants no passing raw lint claim and no
pytest, typing, security, provider, telemetry or acceptance exception.

The independent validator must match the complete sorted diagnostic multiset
(path/code/location/end_location/message), exact commands.py SHA-256 and all
WVR-002 pins. The final source hash cannot drift; commands.py has no other
inventoried lint diagnostic requiring edits. An existing cancellation test in this
same module is not a reason to edit it. Frozen private consumer probes must reject
both directions at the final candidate under mypy 1.19.1 / Python3.13; run the
required CLI contract tests, exact aggregate changed-source mypy and every
remaining original verification gate. No new repository test path is authorized.

This exception expires after the TELEM-01 acceptance decision or immediately if
its source, diagnostic, Ruff version/target or lint configuration changes. A changed
source location/hash requires fresh explicit approval; there is no relocation
allowance. REM-004-GENERIC-01 requires a maintainer compatibility/lint-policy
decision before acceptance beyond this work unit; no automatic API redesign or
permanent global rule exclusion is authorized. Renewal requires explicit approval
and fresh independent review.
