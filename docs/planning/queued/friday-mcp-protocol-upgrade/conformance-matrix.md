# MCP conformance target and research mapping

Approved scope clarification, 2026-10-12. Target: official Model Context Protocol
revision **2026-07-28**, selected by the official latest specification on this
date. MCP is the open protocol introduced by Anthropic; Claude's connector docs
describe a product integration and do not replace normative protocol authority.

## Required outcome

Friday's upgrade must conform to all applicable normative requirements of MCP
2026-07-28 and its dated authoritative schema for every role, transport and tools
feature in the [supported profile](protocol-contract.md#supported-profiles).
A changed version string or working tool call is insufficient. An SDK accepting
a message does not excuse an omitted mandatory rule. Unsupported optional
features must not be advertised. If a Friday safety constraint conflicts with a
mandatory rule, stop and reconcile authority instead of silently redefining it.

The first approved directive proves client core and stdio. HTTP, runtime/Chat
admission and modern server conformance require the remaining declared slices.
Reports must name tested revision/role/transport, map applicable MUST/MUST NOT
clauses to evidence and disclose optional-feature and schema/content limits.
Full OAuth, interactive sampling/roots/elicitation, Tasks, Apps, Skills and model
prompt/resource exposure remain the documented scope exclusions.

## Source authority and pinning

Normative authority is the [MCP 2026-07-28 specification](https://modelcontextprotocol.io/specification/2026-07-28)
and its [dated schema reference](https://modelcontextprotocol.io/specification/2026-07-28/schema).
The specification identifies [schema/2026-07-28/schema.ts](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/schema/2026-07-28/schema.ts)
as the authoritative TypeScript schema. [Official Python SDK v2.3.0](https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.3.0)
is pinned reference/interoperability evidence, not replacement normative authority.
[Anthropic connector docs](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector)
provide product context. Detailed inspection and SDK rationale are in
[research.md](research.md).

Construction binds to the dated revision, never a moving latest alias or SDK
default. The [frozen source manifest](research-sources/manifest.json) now records complete
bytes for nine dated normative documents and the TypeScript schema, source/resolved
URLs, sizes, SHA-256 hashes and lossless compressed artifacts. The schema was
independently fetched at upstream commit `271ecc9accafdd9b83a3c869fa67c22953b2af80`
and matched the captured bytes: SHA-256
`742750af0bb8c716e7030c4977c992b55d1adc4407e9e66997db5846baedc2cd`.
The active execution authority must retain these pins. Do not substitute search
snippets, partial extracts or hashes of our own research notes. SDK installation/
artifact pinning and conformance tests remain execution work.

## Requirements to acceptance evidence

| Dated primary source | Required behavior | Delivery / criteria / evidence |
| --- | --- | --- |
| [Base protocol](https://modelcontextprotocol.io/specification/2026-07-28/basic/index) and schema | Envelopes, IDs, metadata, result tags, reserved errors | UP-02A/05; UP-AC-01/04, CD-AC-01/02/03/05; malformed fields/IDs and local-versus-wire errors |
| [Versioning](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning) | Tested versions, modern errors and bounded legacy fallback | UP-02A/02B; UP-AC-01/02, CD-AC-02/03; supported intersection, unsupported revision and fallback cases |
| [Discovery](https://modelcontextprotocol.io/specification/2026-07-28/server/discover) | Supported versions, honest capabilities and untrusted identity | UP-02A/05; UP-AC-01/07, CD-AC-02; discovery and capability evidence |
| [Stdio](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio) | Framing, discovery/fallback and cancellation | UP-02A; UP-AC-01/06, CD-AC-06/07/08; official SDK real stdio child, exact legacy peer, deadline/reaping checks |
| [Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http) | POST, JSON/SSE, headers/encoding, modern no-session/no-GET/no-resumption and isolated cancellation | UP-02B/05; UP-AC-02/07; independent HTTP counterpart, header/body errors, adversarial streams/concurrency |
| [Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) and schema | Pagination, structured/text results, output schemas and error distinction | UP-02A/04; UP-AC-04, CD-AC-04/05; cycles/caps, scalar/null/mixed content and schema failures |
| [MRTR](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr) | Input-required recognition and opaque state boundaries | UP-02A/04; UP-AC-04, CD-AC-05; safe unsupported-input disposition, no fabricated input or continuation |
| [Authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization) and HTTP security | Explicit authentication/trust profile and honest OAuth limits | UP-03/05; UP-AC-03/07; pre-I/O rejection, origin/credential/DNS/redirect checks; OAuth deferred |
| Accepted Friday MCP and telemetry contracts | Registry, sanitization/provenance/quarantine, memory opt-in and provider injection | Every affected slice; UP-AC-05/06; accepted regressions, content-safe diagnostics and no ambiguous mutation replay |

This table maps requirement families. Builder and reviewer must expand applicable
normative clauses into a frozen criterion-to-test ledger. It does not declare
existing tests or whole-initiative verification. Scope exclusions do not excuse
missing mandatory rules within the declared profile.
