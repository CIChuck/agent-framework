# UP-02B normative construction mapping

Prepared before product edits, 2026-10-12. Status: requirements and test plan,
not executed proof. Complete dated source/schema identities are pinned in
[effects and check profile](effects-and-check-profile.json). Apply the original
client-core/schema ledger to preserved base behavior, then the HTTP rows below.
All mandatory clauses within these selected roles/fields control implementation.
The stable-candidate ledger must reconcile every captured MUST/REQUIRED occurrence
and selected schema field with actual evidence; unexplained exclusions block review.

| Source / applicable client obligation | Criteria | Positive evidence planned | Negative evidence planned |
| --- | --- | --- | --- |
| 2026 base/versioning/discover + RequestParams, Result, Discovery, Tool and Text schema | 01,10 | modern discover and every-request identity/version/empty capabilities | malformed/unsupported version, metadata/envelopes and stale catalog; accepted stdio tests |
| 2026 HTTP Sending Messages + Request Metadata: own POST, Accept, version/body/method/name agreement | 01,02,03 | JSON and request-scoped SSE, inspect exact wire headers/body | wrong status/content-type, envelopes/IDs and safe fixed wire errors |
| 2026 HTTP Receiving Messages + modern cancellation | 02,05,08 | isolated concurrent SSE results; closing only cancelled stream | server requests, unrelated notifications, late/wrong/duplicate IDs, partial EOF |
| 2026 HTTP Schema Extension and Value Encoding, tools inputSchema extensions | 03 | nested property path, absent/null omission, all scalar types and exact Base64 sentinel | names/collision/types/safe integer limits, unreachable annotations, invalid call value before I/O |
| 2026 tools/results/output schema, bounded client core | 01,04 | full pagination, text/structured/scalar/null fidelity | malformed page, total/cycle/depth/nodes/schema complexity and unsupported/input-required results |
| 2025 base/lifecycle: InitializeRequest/Result, Implementation, ServerCapabilities and InitializedNotification | 01,06 | exact version/capabilities and initialized ordering | unsupported negotiation, malformed capability/identity and no initialize cancellation |
| 2025 HTTP Sending/Receiving + Session Management + Protocol Version Header | 02,06 | JSON/SSE, session headers, 404 fresh initialize without old ID, DELETE | bad/non-ASCII/oversized/duplicate IDs, no replay after 404, rejected notification/DELETE |
| 2025 cancellation rules | 05,08 | issued request cancellation with bounded separate notification | unissued/initialize cancellation; notification cleanup cannot replace primary failure |
| 2025 Tool/InputSchema/OutputSchema/TextContent/CallToolResult dated fields | 01,10 | object output, typed text and honest legacy capabilities | 2024 bare string blocks, nonobject structured/output schemas and malformed annotations |
| 2025 session-security and accepted remote contract | 07,08 | exact origin/address/port and secret-safe session ownership | mixed DNS answers/rebinding, URL/redirect/proxy/cookie/credential leakage |
| Both eras endpoint/request/resource ownership and accepted safety contracts | 04,05,07,08 | deadline across DNS/send/read/catalog; retained cleanup owner and borrowed backend | stalls, resistant cancellation, limits before retention and ambiguous mutation count exactly one |
| Both dated schema general JSON boundaries and package/runtime compatibility | 09,10 | official SDK modern and exact deterministic 2025 real wire, original accepted package/cross/root tests | adversarial fixture rejection, new debt/failures, scope/dependency/hash drift |

Not applicable with explicit profile reasons: server-only MUST duties (origin
validation, header validation/error production, server cancellation response,
session assignment and server capability implementations) are peer expectations,
not Friday server construction; Friday server work is UP-05. Core protocol
JSON/metadata/error/capability parsing obligations still apply to received values.
Subscription/listen, resource/prompt handlers, roots, sampling, elicitation,
Tasks, cache sharing, MRTR continuation and extension handlers are not advertised
or invoked. No GET/resumption/Last-Event-ID, no cross-call cache or trace propagation
is performed. Authorization OAuth/client login and remote Runtime/YAML assembly
are deferred, with explicit origin-scoped bearer or unauthenticated programmatic
operation only. Receive unsupported content safely without executing it. Full
OAuth support or full optional-feature conformance is not claimed.

Progress/log notifications never authorize side effects or reset deadlines;
modern client advertises no progress token or log level, so unsolicited variants
are rejected or ignored under bounded parsing without propagation. Opaque peer
trace metadata remains bounded data, not emitted, trusted or forwarded context.
