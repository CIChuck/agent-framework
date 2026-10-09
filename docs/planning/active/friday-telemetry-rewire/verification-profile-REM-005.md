# Proposed REM-005 verification profile

Status: proposed, not approved. Bound to [REM-005](remediation/REM-005-execution-correlation.md),
unchanged approved CD-004 and the complete TELEM-04 contract/profile. No source
remediation has occurred. Candidate1547fae and VAL-009 remain immutable.

## Isolation and effects

Retain fresh exact-revision tracked snapshots with all267 protected paths omitted
before checkout, private caches/temp, credential-free allowlisted environment,
uv run --no-sync/offline/no-download and the accepted socket guard hash
6f61ea4ca34c7abef9e0c709eb1e1feb0f3cf7733cbc59bc465d6b01182e9e81.
Use installed Python3.13.10/Ruff0.14.10/Mypy1.19.1/Pytest9.0.2/OTel1.39.1.
Record versions/module/binary/metadata hashes, source resolution, commands/cwd/env,
timestamps/exits/counts/skips, omissions and before/after hashes. No provisioning,
original .env/.friday/Chroma/transcript data, credentials, installs or downloads.

New tests construct only fake/in-memory components, including ContextVar-based
fake sinks; no SDK/provider/listener/database fixture activation. Independently
reconcile the unchanged13 existing loopback nodes and frozen fixture hashes before
effect gates. Native gRPC requires literal127.0.0.1, finite deadline, retry0/proxy0
and owned server/channel/executor cleanup. The separate actual installed SDK probe
uses Debug/two-child Composite/owned in-memory exporter, no transport/global
registration or borrowed close, with explicit owned cleanup.

## Behavioral gates

Reproduce each original VAL-009 finding against1547fae before source edits using
the original independent probes. Freeze helper/source versions; distinguish the
inherited F04 gap from new violations. These baseline reproductions use only
fakes except the separately approved owned SDK consumer.

After remediation, verify every finding's required regression in REM-005 and the
full AC04-01–08 matrix. In particular: foreground/background and nested/concurrent
SDK/event parentage; independent child provider stacks; valid/None mixed item
origins, preemption/requeue/resume/shutdown; exact MCP rejection kind/zero dispatch;
actual retained upstream iterator closure through both adapter paths with callback/
cleanup/cancellation primary identity; strict integer version before metrics/sink.
Inspect serialized records/snapshots/spans/metrics for privacy sentinels and verify
bounded retention, fixed labels, saturation and single terminal contributions.

## Required commands and independent review

Repeat every mandatory command in the approved [TELEM-04 profile](verification-profile-TELEM-04.md):
six new modules; Chat/LLM/Telemetry; root collection/full suite; all13 aggregate
owning trees; exact changed unit/aggregate Ruff and genuine Mypy; raw root Ruff;
offline lock; board validate/next/show/render; documentation; both full unit and
aggregate committed diff checks. Derive current exact path lists from commits,
including non-package Python changes. Also check the exact REM delta against1547fae.
Do not substitute a delta-only review for the full unit/aggregate review.

The only exclusions remain the two exact live-LMStudio files named in CD-004.
The only allowed skip is the existing optional SciPy adapter test. Raw root Ruff
must remain visible as exit1 with exactly327 WVR-006 identities, four archive hashes,
CLI CommandRegistry whole-source/class AST,17 lint-config hashes, Ruff version and
py313 target matched. No new waiver/suppression/skip or typing exception.

Verify all accepted authority/evidence, unchanged three-method interface/LLM/MCP/
persist_mcp_interaction/storage/config/defaults/metadata/lock; all18 >=3.13.4 floors;
Python3.13 ASTs and public generic Parent/Child consumers. Preserve unrelated dirty
bytes/deletions/board objects and any later unrelated metadata without broad staging.
No original product import leaks or remaining owned workers/spans are permitted.

Freeze a new committed candidate, exact unit/REM/aggregate diffs, expanded checks
and authority hashes. Dispatch a new fresh-context read-only full validator.
Record exactly VERIFIED, CHANGES_REQUESTED or BLOCKED with immutable original
reports/receipts/hashes and all failed attempts. VERIFIED is required before a
completion proposal; maintainer acceptance and delivery are separate.
