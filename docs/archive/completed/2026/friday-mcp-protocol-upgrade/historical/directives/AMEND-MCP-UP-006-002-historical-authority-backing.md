# AMEND-MCP-UP-006-002: Represent immutable historical authority backing

Status: Proposed; no new product/code-generation authority granted.
Parent CD-MCP-UP-006 and AMEND001 remain approved. The eight-path MCP candidate
is complete and its24 builder checks meet their exact contracts. Whole independent
validation is BLOCKED at the current closure representation; this is not a new
protocol/runtime defect and not an unsuccessful remediation cycle.

## Concrete conflict

CD006 step7 requires a canonical completed/local review index while retaining
frozen original authority paths. The active packet README is a frozen control.
The lifecycle requires a completed task's packet under docs/planning/review/.
Current scripts/friday-dev-board.py::_current_packet_paths lists every lane
folder with a README as current; validate_board subtracts only canonical task
packet paths. Keeping the canonical active packet fails the completed-lane rule;
pointing to a new review index makes the retained active packet an orphan. Moving,
deleting, rewriting or concealing the frozen index, fabricating a second started
task, ignoring validation or cleaning user state is not an authorized resolution.
The independent original BLOCKED report and its read-only simulation are controlling
evidence for this stop and must remain unchanged.

## Recommended bounded resolution

Add an explicit optional `authority_backing_packets` field to a board task. The
ordinary `packet` stays its single canonical lifecycle index. Each backing entry
names a retained repository-relative planning packet and a SHA-pinned manifest
under the owner's canonical review/archive index. The manifest identifies the
backing packet and explicitly lists immutable historical files with SHA256 hashes;
its original README and authority/approval/directive/report records are mandatory.
It grants no code-generation, acceptance, publication or task-state authority.

Only a completed or accepted task may declare this backing. Validate all declared
manifest/file hashes, safe path containment, README existence, owner identity and
allowed review/archive canonical location. Reject unknown fields, malformed hashes,
missing/stale files, absolute/traversal or symlink escape, duplicate backing entries,
multiple owners, a backing equal to the canonical packet, and a backing that is
another task's current canonical packet. Never silently skip a bad declaration.
Keep the ordinary orphan check intact for every undeclared current packet. Only
fully validated explicit backing paths are removed from the orphan set. Current
started/queued/approved tasks retain existing canonical lane/approval checks.
No automatic scan-based exemption, second fabricated task or historical acceptance.

After fresh full-feature VERIFIED, the controller can create the review index and
manifest, declare the MCP retained backing, and propose completed/local. Later
maintainer acceptance changes only the canonical index to the archive and updates
its manifest reference; original active authority bytes stay fixed. Exercise both
transitions in synthetic board tests. Retain telemetry and tool-manifest overlays;
this amendment does not change their work state or implementation.

## Exact added product scope

Only four additional existing paths, making the parent8-path budget12:

1. scripts/friday-dev-board.py — typed optional-field and backing validation;
   preserve existing CLI operations, state transitions and undeclared orphan checks.
2. docs/planning/board.schema.json — backward-compatible optional field/strict
   entry schema; keep version1 and existing required fields/unknown-key rejection.
3. tests/integration/test_development_board.py — meaningful positive review/archive
   backing and negative stale/hash/path/ownership/undeclared-orphan/active-state cases.
4. docs/reference/policies/development-task-lifecycle.md — describe current canonical
   packet versus immutable historical backing and unchanged approval/acceptance gates.

The lifecycle policy is a prospective, explicitly approved control supersession;
archive its current bytes/hash before any change and bind its new candidate hash
in the new authority/review request. Original manifests/receipts/reports remain
historical immutable bytes; do not pretend an old current-path hash still matches.
AGENTS/engineering/independent policy and other original controls stay unchanged.
All74 accepted MCP products, all19 package/workspace metadata/lock files, dependencies,
runtime source, MCP defaults/fixtures beyond the already-approved one, telemetry,
providers, Langfuse, CLI/model/user stores and primary captures remain frozen.
The board schema is governance metadata, not package/dependency metadata.

## Required construction and verification after exact approval

Record separate approval and amended authority. Preserve root unrelated hashes,
board overlay and original four proposed-path baseline hashes. Archive the old
lifecycle/control bytes before edits. Prepare a prospective case/source plan;
implement only the four added paths. Use read-only synthetic board roots under
private HOME/TMP, with no peer/network/provider/dependency effects added.

Retain all24 original commands, guard, private Python3.13.10 environment and exact
327 Ruff diagnostic/fix objects/4 Mypy column diagnostics/complete14 skip and15
warning baseline comparisons. Add these three required commands, total27:

- private Python -m pytest tests/integration/test_development_board.py -q
- private Ruff check scripts/friday-dev-board.py tests/integration/test_development_board.py
- private Python -m mypy scripts/friday-dev-board.py tests/integration/test_development_board.py

All three require exit0; no checker weakening, new debt waiver or omitted original
command. Run actual complete library/source/control before-first/after-last samples.
Freeze a new stable candidate and request fresh independent FULL whole-feature
aggregate review against the original telemetry base, now explicitly including
four governance paths/all27 checks/all12+8 criteria. The earlier BLOCKED result is
retained; it supplies no VERIFIED or acceptance. A changed controlling authority
requires this fresh review even though MCP runtime source stays unchanged.

## Stops and later gates

Extra paths, package/runtime/dependency effects, integrity mismatch or a remaining
mandatory conflict stop for exact disposition. Existing maximum two unsuccessful
formal remediation-cycle rule remains; the blocked authority reconciliation is
not a failed implementation cycle. No checker/source changes before exact approval.
Whole MCP remains started/local. Only independent VERIFIED permits a completion
proposal; only new maintainer whole acceptance closes it. Push/merge/release/deploy
and optional Langfuse implementation remain separate.
