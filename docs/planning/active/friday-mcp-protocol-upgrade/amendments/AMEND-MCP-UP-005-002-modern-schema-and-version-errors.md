# AMEND-MCP-UP-005-002: correct modern schema plan and version-error data

Status: Proposed; exact maintainer approval is required before construction resumes.
Parent: CD-MCP-UP-005 plus approved AMEND-MCP-UP-005-001.
Current unreviewed product: `ed8f8cbdc27b469b389487dd931678b4777b13b9`.

## Confirmed conflict and cause

The approved up05-server-contract.md line57 prescribes
“UnsupportedProtocolVersion -32022 with only supportedVersions safe data.”
The pinned2026 TypeScript schema instead requires
`UnsupportedProtocolVersionError.error.data.supported: string[]` and
`requested: string` (schema lines494/498). `DiscoverResult.supportedVersions`
is a different field and remains correct for discovery.

Normative schema SHA256:
`742750af0bb8c716e7030c4977c992b55d1adc4407e9e66997db5846baedc2cd`,
upstream `271ecc9accafdd9b83a3c869fa67c22953b2af80`.
The retained guarded live-wire audit returns exit1: actual error data has only
supportedVersions; required data is supported/requested. The ordinary SDK error
wrapper checks a generic JSON-RPC error, so a passing SDK call does not validate
this particular error variant. No handler runs in this failing audit.

The controller also found a planning defect: plan_up05_requirements.py replaced
its schema variable with the later captured2025 schema. The previously reported
145 declarations/355 fields described2025, not2026. All19 captures were retained,
but that field plan did not fulfill the required modern preconstruction mapping.
It remains immutable historical evidence and cannot establish2026 conformance.
The new explicit SHA-selected prospective plan parses both schemas separately:
2026 has155 declarations/337 field references;2025 has145/355 and is historical
client-compatibility evidence only. Counts describe parsing, not passed assertions.

## Exact proposed correction and prospective rebaseline

1. Supersede only the version-error data instruction: emit error code-32022
   with fixed safe message and data exactly
   `{"supported": ["2026-07-28"], "requested": <this request's protocolVersion>}`.
   Bound/validate the requested version string using the existing individual
   identity budget before use. Echo it only in that request's required wire
   error data. Do not log it, label telemetry with it or expose other metadata,
   headers, arguments, credentials or exception details. Discovery continues
   to use supportedVersions; HeaderMismatch stays-32020 and HTTP400.
2. Recognize the historical preconstruction-plan failure explicitly rather than
   backdating a replacement. Approve prospective-modern-schema-replan.json as
   the new pre-edit plan for the remaining construction phase. Rebaseline the
   current unreviewed18-path draft, re-audit every source module against the
   actual2026 schema and every applicable captured modern clause, then complete
   a field/variant/source/test/command mapping before formal review. No original
   incorrect field-plan artifact or approval/control bytes are rewritten.
3. Within existing scope, correct any dependent-field omissions found by that
   audit. Already identified: requestState must be validated or explicitly refused
   under the unsupported interactive-state role, and emitted text/result MetaObject
   reserved trace fields must be format-validated. MissingRequiredClientCapability
   requires requiredCapabilities if that error is ever emitted; this tools-only
   profile activates no such role and must not emit a malformed reserved variant.
   These are enforcement of the existing complete-field criteria, not optional
   feature expansion, a new provider, a new path, or a checker waiver.

## Product budget, regression proof and gates

The original18 product paths,12 criteria,20 required checks, metadata/dependency
pins, private library environment and guarded fixture permissions remain intact.
Affected existing scoped locations include server/protocol.py, modern.py, HTTP/
stdio error plumbing as needed, the existing new server tests and server guide.
No accepted client/Core/Runtime/Chat/telemetry/config/legacy source may change.
AMEND001's required ttlMs0/private discovery/list behavior remains approved.
No cache engine, optional callbacks, interactive state, Tasks, subscriptions,
OAuth implementation, Langfuse, later unit or remote publication is authorized.

Positive and negative proof must distinguish discovery supportedVersions from
unsupported-version supported/requested, test missing/null/malformed dependent
fields, exact HTTP400 versus header/method errors, zero handler admission,
owner-local data and diagnostic/telemetry privacy. Validate every emitted error
variant against its pinned fields rather than merely its generic code. Actual
SDK stdio/TLS JSON/SSE and raw negatives remain mandatory. Re-audit complete
modern-role fields, retain each failure and repeat the entire20-check profile
with supplemental column/debt/skip/warning/library comparisons on the corrected
stable candidate. A fresh read-only full-unit validator is required before any
completion proposal; maintainer acceptance remains separate.

## Evidence already available, with its limits

All20 original commands completed against the unchanged draft product candidate:
381 focused tests and5125 repository tests passed; accepted baseline4744 passed.
Both runs have identical14 skip locations/reasons and complete15-warning sections.
All changed Python files are Ruff clean, all7 touched source files and the MCP
package pass Mypy. Full Ruff retains the exact327 inherited diagnostic/fix
objects; full Mypy retains the exact four inherited path/line/column/code/message
objects. Before/after all22,009 private library files/192 distributions match,
as do19 metadata and60 accepted product hashes. Raw nonzero inherited-debt exits
and the failing version-error schema audit are retained without rewriting.

Those checks do not cure the schema/authority contradiction or the historical
planning failure, and are not an independent VERIFIED result. No formal validator
finding or remediation cycle has been consumed. The complete original outputs,
controllers, freeze and comparisons are archived by amendment002-artifacts-manifest.json.

## Approval gate

Approve this exact correction and prospective rebaseline before further product
edits. The frozen contract stop rule and AGENTS.md reconciliation requirement are
why approval is needed. This amendment does not waive typing, engineering policy,
full conformance evidence, independent review or acceptance. A later review may
still identify source findings; they follow the existing bounded remediation rules.
