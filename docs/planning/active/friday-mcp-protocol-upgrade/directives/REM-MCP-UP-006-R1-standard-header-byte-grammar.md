# REM-MCP-UP-006-R1: Standard metadata-header byte grammar

Status: bounded continuation within the **already approved REM-MCP-UP-006** scope.
No new maintainer approval is claimed or requested. Existing receipt and original
six-path directive remain immutable and controlling. This continuation narrows to
three of those paths and enforces the same mandatory HTTP header grammar and exact
wire errors under SRV-AC-01/05/06/12; it adds no feature, dependency, interface,
protocol role or external effect. Original four fixes passed64 independent cases;
new VAL-UP05-005 is a further malformed-header error-category case in the same
approved policy module and complete-work-unit verification requirement.

Authority: [approved REM006](../authority-REM-MCP-UP-006.json), its pinned original
CD005/AMEND001/002 contract, and [original independent report](../validation/VAL-UP05-02/report.md).
The tactical plan authorizes bounded remediation within existing authority and
requests new scope only when the repair exceeds it. A separate remediator remains
required; no builder/reviewer self-approval. This is remediation cycle2 after one
unsuccessful formal correction review; stop after a second unsuccessful cycle.

## Allowed existing paths

- `packages/friday-mcp/src/friday_mcp/server/http_policy.py`
- `packages/friday-mcp/tests_mcp/server/test_streamable_http.py`
- `docs/guides/18-mcp-server.md`

All other15 original UP05 products, all19 metadata/60 accepted product hashes and
original controls/runner/guard/libraries remain unchanged. Board/process evidence
and new prospective/final mappings may be recorded separately. Preserve root
unrelated files and two-task/three-event board overlay; no broad git operations.

## Exact correction

Validate plain Mcp-Method and MCP-Protocol-Version header bytes before comparing
with the UTF8 JSON body. Reject C0 controls except permitted horizontal tab, DEL
and raw non-ASCII with fixed HTTP400/-32020 HeaderMismatch and zero handler effects.
Keep RFC field-value visibleASCII/space/HTAB semantics and exact case-sensitive
header/body matching. Do not strip/normalize values or reclassify invalid bytes as
unknown methods/versions. Keep existing valid unknown ASCII method404/-32601 and
unknown ASCII version400/-32022 with required supported/requested data. Preserve
standard-header duplicate/missing/mismatch behavior, Mcp-Name/Mcp-Param Base64,
Unicode decoded values, authentication/Host/Origin/TLS/media access statuses,
optional capabilities and privacy/no-id-before-body grammar. Never replay a call.

## Required evidence and checks

Before source edits, read the original report/probes and all three allowed files
plus relevant immutable protocol/HTTP contracts; freeze a prospective clause/
field/variant/source/test/command plan. Add exact-code zero-handler negatives for
both standard fields with matching body values, C0 boundary/sweep excluding valid
HTAB, DEL/non-ASCII; valid visibleASCII/space/HTAB and existing unknown method/version
errors; original Name/Param sentinel and access-policy cases. Independently preserved
original failing probes plus disclosed corrected counterparts are required. Guide
may clarify byte grammar without changing defaults or unsupported-role claims.

Repeat all20 unchanged exact commands plus Mypy columns, full normalized327 Ruff
objects/fixes and4 inherited complete Mypy diagnostics, complete skip/warning
comparisons and strict before-first/after-last dependency snapshots. All12 criteria
and all18 products remain in the fresh read-only remediation delta then full UP05
review. Original four mitigation regressions must remain passing. VERIFIED required
before completion proposal; maintainer acceptance, UP06 and publication separate.
Only the existing synthetic guarded subprocess/literal127 privateTLS/ASGI effects
are permitted; no installs/public network/user stores/credentials/providers/scope
expansion. No source suppression, Any/cast/checker weakening or unrelated repair.

## Original new finding

```json
{
  "id": "VAL-UP05-005",
  "number": 5,
  "severity": "medium",
  "title": "Malformed standard metadata header values bypass HeaderMismatch validation",
  "classification": [
    "protocol conformance",
    "HTTP security boundary"
  ],
  "locations": [
    {
      "path": "packages/friday-mcp/src/friday_mcp/server/http_policy.py",
      "line": 149
    },
    {
      "path": "packages/friday-mcp/src/friday_mcp/server/http_policy.py",
      "line": 226
    },
    {
      "path": "packages/friday-mcp/src/friday_mcp/server/http.py",
      "line": 225
    }
  ],
  "criteria": [
    "SRV-AC-01",
    "SRV-AC-05",
    "SRV-AC-06"
  ],
  "requirements": [
    {
      "path": "docs/planning/active/friday-mcp-protocol-upgrade/up05-server-contract.md",
      "line": 110,
      "requirement": "Header failures are HTTP400/-32020; access/header/body checks precede handler admission."
    },
    {
      "path": "docs/planning/active/friday-mcp-protocol-upgrade/up05-server-contract.md",
      "line": 120,
      "requirement": "Validate required standard metadata headers against the body; preserve exact malformed/header status grammar."
    }
  ],
  "normative_source": {
    "capture": "inputs/normative/specification--2026-07-28--basic--transports--streamable-http.md",
    "sha256": "93daa4bb4e189f0bd51d866950b3b8a3b4e7d0b1e0e6eede5ba1998641d0b955",
    "lines": [
      479,
      480,
      481,
      596,
      597,
      602,
      623,
      629
    ],
    "requirement": "Header values use visibleASCII/space/HTAB; malformed required headers and invalid-character validation failures require HTTP400 JSON-RPC -32020. Base64 is permitted for Mcp-Name/Mcp-Param, not Method/Version."
  },
  "schema_source": {
    "sha256": "742750af0bb8c716e7030c4977c992b55d1adc4407e9e66997db5846baedc2cd",
    "declaration": "HeaderMismatchError",
    "line": 468,
    "field": "code: typeof HEADER_MISMATCH; (-32020)"
  },
  "observation": "With matching header/body values, Mcp-Method containing U+0001, DEL or literal UTF8 Unicode returns404/-32601; MCP-Protocol-Version returns400/-32022. Six independently authored ASGI cases fail. Literal UTF8 Unicode reproduces over the real named Friday subprocess on verified privateTLS in BOTH JSON/SSE modes, with0 handler starts, final active0 and child exit0. h11 rejects raw control/DEL bytes before ASGI with400/plaintext; that parser behavior is recorded separately and is not claimed as a new application finding.",
  "cause": "HTTPServerPolicy.validate checks only CR/LF/NUL and duplicates for mirrored values. validate_rpc_headers compares Method/Version raw bytes without complete character validation, unlike decode_header for Name/custom parameters. Matching malformed bytes therefore pass the header gate and reach method/version routing.",
  "evidence": [
    "checks/independent-edges-001/stdout",
    "checks/independent-edges-001/receipt.json",
    "checks/independent-live-standard-001/stdout",
    "checks/independent-live-standard-001/receipt.json",
    "test_review_edges.py::test_standard_metadata_header_invalid_characters_exact_code",
    "test_standard_header_live.py::test_real_verified_tls_standard_header_boundary"
  ],
  "risk": "The application violates its dated header/error contract and lets malformed mirrored standard values reach RPC routing. No authorization bypass, mutating replay or handler invocation is demonstrated.",
  "required_mitigation": "Within the existing bounded HTTP policy path, validate standard Method/Version metadata values for the required character/value grammar before RPC routing and return fixed400/-32020 for malformed recognized metadata. Retain separate Host/Origin/Bearer/TLS access handling, byte bounds, duplicate rejection, exact Name/custom Base64 rules and privacy. No accepted client, checker, dependency or other product-path change.",
  "required_tests": [
    "Matching Method/Version values with control,DEL and raw nonASCII ASGI cases: exact400/-32020 and0 handlers; positive valid ASCII and case rules.",
    "Actual private verifiedTLS JSON/SSE raw nonASCII negatives bypass SDK retry; zero handler counters, owner/child settlement.",
    "Retain valid unsupported ASCII version400/-32022 supported/requested and unknown ASCII method404/-32601, standard/custom duplicate/CRLFNUL and access-specific status/privacy regressions.",
    "Rerun unchanged full20 profile plus exact diagnostic/skip/warning/dependency integrity and a fresh separate delta/full review."
  ],
  "documentation_configuration_impact": "Guide18 exact HeaderMismatch claim must match all required standard metadata values. No configuration/default/metadata/optional-role change.",
  "remediation_role": "Separate remediator required for HTTP security-boundary correction; this report grants no implementation or publication authority."
}
```
