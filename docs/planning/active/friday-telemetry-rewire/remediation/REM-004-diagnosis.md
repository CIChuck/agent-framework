# REM-004 diagnosis and evidence

Status: Preparation complete; proposed scope, no implementation or exception approval.
Date: 2026-10-05. Original HEAD: 686a5bd17d84fea3ec3a3d329df2d39c70d10c03.
Diagnostic checkout: 4c0afdb11b663e11ae08a927950dd3e968bbb566, isolated tracked
REM-003 candidate. Its product source/tests/lock match the current HEAD.

The [directive](REM-004-verification-closeout-directive.md) maps the sole aggregate
finding [VAL-005-F01](../validation/VAL-005/report.md) to six bounded components.
The [machine-readable inventory](REM-004-scope.json) supplies all exact lint IDs,
file hashes and failed/error node IDs. This diagnosis does not alter the earlier
review outcome.

| Component | Evidence and proposed disposition |
| --- | --- |
| Seven native-tool failures | All seven pass alone (exit0, 7 passed). A preceding TestDefaultToolRegistry::test_load_decorated_tools produces exit1, 7 failed, 1 passed. Agent conftest clears _GLOBAL_TOOL_REGISTRY before/after each test; runtime's cached catalog reads that registry. Restore fixture state; preserve all native/MCP expectations. |
| Two optional-reader failures | Current reader implementations distinguish missing imports from malformed containers. Existing tests write invalid PK bytes and assume the optional library is absent. Force exact ImportError for dependency tests and separately test malformed/valid synthetic containers. |
| Six Web/private-IP failures | Under the unchanged guard, is_safe_url returns true for 10.0.0.1, 192.168.1.1, 169.254.1.1 and fc00::1; 127.0.0.1 returns false through the localhost check. validate_url catches the guard's DNS RuntimeError and returns the literal URL. Classify literal IPs before DNS; stub domain resolver answers and test transport rejection. This is a latent security behavior independent of telemetry. |
| One PTY acknowledgment failure | Existing 0.8-second timer begins after Popen and includes child imports/setup. Use a two-way readiness/trigger handshake while retaining the same post-trigger acknowledgment deadline and bounded work delay. |
| Eleven fixture errors | ThreadingHTTPServer binds synthetic 127.0.0.1 ephemeral ports; sandbox returns PermissionError. Three Chat nodes already passed their approved privileged rerun; eight LLM nodes need precise new execution authority. Complete suites must pass in the approved listener environment. |
| Root lint | 459 findings: 326 in four historical probes, 133 live findings across 80 files. Baseline 337 consists of those same 326 plus 11 live E501; 122 additions are py313-target driven. Fix live findings, preserve accepted archive bytes and request the exact WVR-002 disposition. |

New probe metadata/logs are frozen in `../execution/REM-004-diagnosis/` with
SHA-256 inventory. They record exact commands, candidate, allowlisted environment,
source-resolution setup and exit status. No credentials, provider activation,
non-loopback traffic, environment synchronization or original runtime data were
used. Guard SHA-256: 6f61ea4ca34c7abef9e0c709eb1e1feb0f3cf7733cbc59bc465d6b01182e9e81.
Guard source: `/private/tmp/telem-01/REM-001/network-guard/sitecustomize.py`.

One exploratory ordered invocation used the wrong class name TestToolRegistry,
returning exit4/no tests. Its raw log is retained as native-after-agent; the
corrected invocation uses the actual TestDefaultToolRegistry class and establishes
the 7-failure result. Neither invocation is represented as a product check passing.

Remaining uncertainty: no product/test remediation has run; targeted type/API
compatibility must be assessed before PEP695 edits, full-suite listener safety must
be freshly frozen at the changed candidate, and WVR-002 remains unapproved.
Preparation readiness cannot establish aggregate acceptance.

Raw logs are gzip-compressed byte-for-byte; sha256.json records their original
uncompressed names and hashes. Compression preserves the original whitespace.
