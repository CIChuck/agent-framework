# CD-MCP-UP-001 implementation handoff

Prepared 2026-10-12. Work unit MCP-UP-02A. Builder evidence; independent verdict pending.

The twelve authorized product paths implement explicit modern/auto stdio profiles,
immutable bounded protocol models, discovery/request metadata, typed errors,
complete paginated catalogs, structured/text preservation, bounded output-schema
validation, request deadlines/concurrency and retained cleanup ownership.
Existing callers retain the 2024-11-05 default. Modern target is the frozen
2026-07-28 specification/schema, with official Python SDK 2.3.0 used only in the
real stdio interoperability fixture. HTTP/YAML/modern server remain later units.

The construction checkpoint is 9e11fb7; the controlling product baseline remains
46005353046553477417a730f05ff21ead64a00d. No other product path is changed.
Original approval bytes and A01 receipt remain intact. Product hashes and every
criterion/test mapping are in client-core/. The normative ledger retains all
captured MUST paragraphs for independent applicability review, including server,
HTTP and optional-feature obligations outside this unit.

## Final evidence

Focused tests: 123 passed. MCP package: 159 passed. Runtime/Chat/Telemetry:
1,211 passed, five existing live-provider skips. Workspace: 3,226 passed,
14 existing skips, 15 warnings. Independent baseline environment: 3,132 passed,
the same 14 skips and 15 warnings. Exact skip lines/reasons are compared.
Scoped Ruff and both Mypy gates pass (three/18 source files). Raw root Ruff exits
one with 327 findings on each baseline/candidate, zero new or removed identities.
No source suppression or lint exclusion was introduced. Historical executed IDNA
scripts were losslessly archived as .py.gz, retaining original raw hashes and
bytes; this keeps execution evidence outside executable source discovery.

Complete raw receipts/stdout/stderr include failed setup and superseded attempts.
The final named checks in artifact-manifest.json are the product gates. Baseline
and candidate use the same importlib pytest collection mode and private Chat test
directory on PYTHONPATH to resolve existing duplicate basename/sibling imports;
no test is excluded and no repository pytest configuration is changed.

## Environment and permitted effects

Both sparse checkouts omit 267 protected paths before checkout. All source
resolution points to the isolated candidate or baseline. Shared .venv and user
state are untouched. Python 3.13.10, MCP/mcp-types 2.3.0, IDNA 3.20 are private.
The approved lock SHA256 is aab33ed773dcdb50a65dd86af84bd1e6e26dc3486da7b04588082d72a7b18ce2.
A01 is the sole existing-version change (IDNA 3.11 to 3.20); supported context and
original artifact preservation evidence is retained under idna-regression/.

The no-build requirements install initially could not obtain a PyPika 0.48.9
wheel. Version-matching original locked installed library files/metadata were
copied with per-file SHA256 receipts into private environments; no console scripts
or editable links were copied. Missing approved artifacts were installed with
require-hashes/no-deps/no-build. Ruff is a hash-preserved original 0.14.10 binary.
Baseline has original versions, including IDNA 3.11. Workspace dist-info version
metadata was copied for existing checks; source resolves only to private paths.
No shared environment synchronization or all-extras installation occurred.

New real children are only private Python plus modern_sdk_server.py or
legacy_protocol_server.py; their synthetic counters record names/methods only.
Existing broader fixture entry points are tests/integration/mcp_fake_server.py,
Chat test_reorganization_terminal.py (provider-free Python PTY),
test_llm_adapter_migration.py (127.0.0.1 HTTP), and Telemetry
test_otlp_collector.py (127.0.0.1 gRPC). Stores use private synthetic temp paths.
Telemetry testing exercises this explicit synthetic collector, never a live
exporter. No credential, provider, real MCP, npm/npx or user tool is authorized.
The archived audit guard blocks Python external DNS/TCP and shared checkout
access. Native gRPC socket operations are not audited by Python; their explicit
fixture-only loopback endpoint is separately inventoried. This guard is test
evidence, not a production security boundary. Per-check allowlisted environments
and the guard hash are in every raw receipt; no ambient OTEL_* flags are inherited.

## Limits and disposition

Limits are documented in the package README: 1 MiB frame/catalog budget,
64 KiB tool result, depth 32, four concurrent/retained exchanges, 16 pages,
256 tools, and a shared 30-second modern deadline. Schema limits are 8 KiB,
depth 16, 256 expanded nodes and a conservative evaluation budget; cycles,
external refs and regex/composition features are rejected with fixed failures.
Supported schema keywords and fixed unsupported content/input outcomes are
documented. No retry, MRTR continuation, caching, subscription, roots, sampling,
elicitation or icon rendering is advertised. Structured null/scalars/arrays and
mixed text/structured results retain fidelity; legacy text compatibility remains.
Cancellation-resistant sends retain ownership and capacity until bounded cleanup
can finish; a deadline cannot silently discard an active exchange.

Unit validation cannot establish completion of the full MCP initiative. Fresh
read-only review, maintainer acceptance and delivery remain separate gates.
