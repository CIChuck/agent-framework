# Independent A06 / WVR-003 compatibility proposal review

Verdict: **READY for maintainer consideration**.

This is a fresh-context, read-only review of a proposed construction amendment
and waiver. It is not approval, product VERIFIED, acceptance, or permission to
resume construction. No blocking or required-change finding was identified.

Reviewer: independent Codex agent `/root/rem004_compatibility_proposal_reviewer`.
Date: 2026-10-05. Model/version: not exposed by the runtime. No builder private
reasoning was received. The dispatch supplied only scope, authority pointers,
constraints and required checks. Controller operational messages did not replace
independent pin verification or command reproduction.

Candidate: `cdb1b8b6a07ff3cedda42b6c165d29b74020aeaf`.
Base: `1718ed21f6b60c9c51edfcdb288853be557cb9f3`.
Exact request: `request.json`; all **83** input hashes
match candidate blobs. All **16** current controlling authority pins match.
Read AGENTS, repository/independent/lifecycle policies, accepted MCP telemetry
authority, build/contract/tactical plans, CD-001, verification profile, REM-001
through REM-004, approved WVR-002, proposed A06/WVR-003 and exact scope, selected
diff, source copies, raw diagnostics, probe sources and partial-work evidence.
Full paths, input hashes, commands, outputs and preservation are in `evidence.json`.

## Compatibility result

The frozen six-class raw evidence contains exactly the expected return-value
diagnostics from the exact complete original modules and their one-header
variants. Every source copy matches the candidate; each conversion changes only
the named class header. Five classes reject both directions before and after.
CommandRegistry alone changes from invariant to contravariant. None of these
raw inner mypy exit-one results contains an unrelated tool/import error.
Wrapper exit zero is recording success, not a product mypy pass.

Independently reproduced CommandRegistry with installed Python **3.13.10**, mypy
**1.19.1**, Python target **3.13**, unchanged root mypy configuration, audited
private copies and the pinned guard. The fresh mypy invocation exits **1**, with
empty stderr and exactly three intentional return-value errors:

| Direction | Original Generic[T] | One-header CommandRegistry[T] |
| --- | --- | --- |
| Parent to Child | rejects, consumer line 6 | accepts, no line 12 error |
| Child to Parent | rejects, consumer line 9 | rejects, consumer line 15 |

See `registry-consumer-corrected-profile.stdout` and the recorded exact command. Existing source
suppression is retained byte-identically; no new suppression or configuration
relaxation was introduced. Consumers themselves remain checked, as the precise
return-value errors demonstrate. This bounded static result does not claim
arbitrary external-consumer or runtime compatibility for future conversions.

Fresh unchanged-config Ruff **0.14.10** against the exact commands module exits
**1** with empty stderr and exactly one diagnostic matching the complete pinned
identity: `UP046`, path `packages/friday-cli/src/friday_cli/commands.py`, location
**74:23**, end location **74:33**, message `Generic class CommandRegistry uses
Generic subclass instead of type parameters` (the machine identity retains
the exact backticks). No other inventoried diagnostic targets this module.

Whole-file SHA-256: `15992e7f38fe874f0104a164180679c7e76d7e09413d68152ef5cc77c0f99308`.
The class AST hash also matches WVR-003. Both base and candidate contain the
same module bytes. Retaining these exact bytes is an explicit final-candidate
condition; relocation or any source-hash change expires the proposed exception.

## Exact waiver and scope disposition

A06 lines 16–23 and WVR-003 lines 22–39 explicitly replace the all-133-fixed /
zero-live lint condition only if the maintainer approves both proposals. The
approved WVR-002 continues to require zero live findings until that decision.
Its original archive scope is not renewed or expanded.

The conditional final root result must contain **exactly 327** identities:
the unchanged **326** archived identities from REM-004-scope.json plus this
one live UP046. All four archive hashes and all **17** lint configuration hashes
match approved WVR-002. The independently derived full sorted multiset is saved
in `conditional-final-root-diagnostic-multiset.json`; its canonical SHA-256 is
in `evidence.json`. This is a proposed final disposition, not a current root lint
result. Root and changed-file Ruff remain required, with raw nonzero exits
disclosed separately. Any additional diagnostic remains a failure. All other
**132** live findings must still be fixed.

The candidate changes only planning/evidence paths. It changes no source, test,
dependency, configuration or lint target. The approved original source/test
permissions and stop conditions remain unchanged. A06 carries forward the
original scope inventory, original failure identities, exact typing repairs,
regressions, package/CLI contract tests, generic/alias/Pydantic checks, six-module
telemetry tests, complete root and Chat+telemetry zero-exit suites, exact aggregate
changed-source mypy, AST checks, offline lock and metadata/governance gates.
It preserves the listener safety preflight, credential-free allowlist, guard,
two live-module exclusions, immutable historical evidence and aggregate AC-01
through AC-06. There is no hidden weakening or new repository test path.

WVR-003 meets the policy waiver fields: exact scope and compatibility reason,
maintainer Chuck Russell as owner, follow-up REM-004-GENERIC-01, cleanup decision
before acceptance beyond TELEM-01, expiry after the TELEM-01 acceptance decision
or immediately upon any source/diagnostic/tool/target/lint-configuration change,
and explicit approval plus fresh review for renewal. WVR-002's own follow-up,
expiry, archive hashes and diagnostic identities remain binding.

## Partial work, preservation and remaining gates

The six partial edits are excluded from the committed candidate and disclosed
as uncommitted advisory work. Their durable diff and raw evidence preserve the
ordered Agent/Runtime 221 passes; Tools 105 passes / two unfinished assertion
failures; PTY one pass / one incorrect-resource-owner assertion failure. No
advisory pass or wrapper zero closes a mandatory gate, and no exception covers
the unfinished tests. The proposed corrections remain in already authorized
test files and require final verification.

All committed compressed artifact hashes match the artifact manifest. Historical
command metadata log hashes match their actual decompressed logs, and their
recorded snapshots remained tracked-content unchanged. This confirms the
saved evidence's integrity, not the final product's correctness.

Before/after HEAD, dirty path hashes, status and complete tracked diff hash match.
No original source, authority, index, staged content or runtime state was written.
No .env/.friday/Chroma/secrets/provider/exporter access, product tests,
network/download/sync/install, privileged work, staging or commits occurred.
Writes stayed inside this review directory. Private probe safety preflight,
allowlisted environment and unchanged guard hash are recorded in
`safety-preflight.json`. `git diff --check base candidate` exits zero.

The initial execution profile incorrectly redirected HOME to temporary state.
That override was removed, and versions, consumer mypy and module Ruff were
rerun successfully with fresh `*-corrected-profile` labels and the same exact
results. The corrected allowlist does not set HOME/home/CODEX_HOME. Initial raw
outputs and `initial-profile-evidence.json` remain labeled historical execution
evidence; the verdict relies on the corrected-profile reproduction.

Remaining gate: a precise maintainer decision. If approved, reconcile all
controlling authority and board metadata, freeze the new authority candidate,
obtain fresh independent readiness, and only then release separate bounded
remediation. Final product gates, delta/aggregate validation, completion and
acceptance remain outstanding. A candidate or controlling-authority change
invalidates this review for the changed deliverable.
