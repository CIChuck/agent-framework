# CD-GUIDE-001 — Technical end-user guide upgrade

Controlling authority: Chuck Russell's 2026-10-15 explicit instruction to review
every document in docs/guides and fix consistency, clarity, accuracy and front
matter. This selects the guides work; it does not activate queued product work.
Base123d9ed943519c4e68bf9249705e55d1a1ebf8b8; branch docs/guides-refresh.

Allowed deliverables: all25 Markdown files in docs/guides, enumerated and hashed
in authority.json, plus this initiative's planning and validation evidence and
board/dashboard records. No runtime source, tests, package metadata, dependency,
version or lock changes. No publication, push, PR, merge, provider calls,
credentials, hardware, Docker, or access to shared user stores.

Acceptance: review each document's complete structure, examples and claims;
retain a useful deep technical guide series with clear task-oriented navigation,
real public APIs/configuration/CLI commands, precise integration and safety
boundaries, and links to implementation contracts. Consolidate redundant prose
and replace fabricated or retired commands/examples. Preserve materially useful
MCP transport/profile, trust, ownership and schema limits. Explain current
telemetry and optional queued Langfuse separately. Apply consistent metadata
with framework_version0.1.0a3, last_reviewed2026-10-15, title, description,
audience, status and document type. Dates represent actual review, not acceptance
or a new release. Plans remain plans; do not invent conformance or compliance.

Build order: audit all25 originals and current source/templates; correct core
architecture/install/config/CLI first, then memory/tools/agents/workflows,
operations/security/speech, MCP and reference/navigation. Record per-file findings
and resolutions with source references. Maintain existing filenames.

Required verification: metadata/schema and scope checks; Markdown rendering;
local links including anchors; complete Python examples compile and declared
offline examples execute against installed alpha3 in isolated paths without
network or credentials; YAML/config examples checked against actual parsers or
clearly labeled fragments; CLI help/command handlers and package/extras/import
names checked against source. Live provider/HTTP/audio/Docker/deployment examples
are explicitly marked and not executed. Run board/render/docs and whitespace
checks. Full product suites are not required for this documentation-only work.

Commit a stable candidate and dispatch a fresh-context read-only independent
validator under AGENTS.md before completion. Record exact hashes, diff range,
checks and exclusions. A changed candidate requires fresh review. Preauthorized
remediation is limited to low-risk factual, prose, link, metadata and example
corrections within the same25 documents. Stop on required product behavior
changes, unavailable external evidence that prevents an accurate claim, scope
expansion, unsafe examples or exposure of secret/user data. No self acceptance.
