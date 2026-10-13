# AMEND-MCP-UP-005-001: required immediately stale cache metadata

Status: Proposed; not approved. Construction stopped at this authority conflict.
Parent: approved CD-MCP-UP-005 and immutable authority-UP-05.json.

## Concrete conflict and normative basis

The approved up05-server-contract.md says “No caching TTL/cacheScope is supplied
in this profile” and “Never advertise ... subscriptions/caching/logging”. The
pinned complete TypeScript schema at upstream
`271ecc9accafdd9b83a3c869fa67c22953b2af80` instead requires
`CacheableResult.ttlMs: number` and `cacheScope: "public" | "private"`.
`DiscoverResult` and `ListToolsResult` inherit CacheableResult. The source
SHA256 is `742750af0bb8c716e7030c4977c992b55d1adc4407e9e66997db5846baedc2cd`;
CacheableResult is at lines1081–1110, DiscoverResult at678 and
ListToolsResult at1779. These are already captured approved inputs, not a
new spec revision or new dependency.

The actual official SDK2.3.0 Client against Friday subprocess stdio and private
verified TLS JSON/SSE rejects tool-list results: dated ListToolsResult requires
both cacheScope and ttlMs. The internal SDK convenience model defaults do not
make these wire fields optional. Raw failed attempts, actual SDK wire-model
bytes, controller scripts and incomplete product snapshot are retained in
execution/up05/construction-artifacts-manifest.json and construction-checkpoint.json.
No stable candidate or VERIFIED result exists. This is an authority correction,
not a formal validator finding or a consumed remediation cycle.

## Exact proposed override

Supersede only the cache-metadata prohibition for server/discover and tools/list:

- Every complete discovery and tool-list result, including empty and all
  paginated pages, includes exactly `ttlMs: 0` and `cacheScope: "private"`.
- Zero means immediately stale; private disallows sharing across authorization
  contexts. The server implements no result-cache storage, cache reuse or new
  caching RPC. Official counterpart cache remains `None`.
- Tool-call results do not gain cache fields merely because discovery/list need
  them. No positive TTL, public cache scope, cross-user reuse or optional
  capability is introduced. The existing no-caching non-goal refers to a cache
  engine or RPC feature; it does not forbid these mandatory stale wire fields.
- Preserve all original proposal/control bytes. Record this separate amendment,
  approval receipt and superseding execution-authority manifest on approval.

## Exact implementation, verification and unchanged boundaries

Within the same18 product paths, update modern.py discovery/page result
construction, test_modern_protocol.py exact result/page assertions,
test_server_interop.py typed SDK discovery/list and cache-disabled proof,
and the already scoped README/server guide. No new product path, dependency,
lock, checker, private library or fixture permission is needed.

Positive assertions cover empty/nonempty discovery and every byte/count-bounded
catalog page carrying integer0/private. Negative assertions reject missing/null/
malformed dated cache fields through the unmodified official SDK wire decoder;
tool-call results remain complete without those cacheable-only fields. Prove
actual subprocess/TLS requests and handler counters rather than synthesized
SDK discovery. Retain earlier failures. Rerun the entire original20-command
profile, supplemental inherited-debt/warning/skip comparisons and library/hash
integrity on the stable completed candidate. Fresh full-unit read-only review is
still mandatory, followed by separate maintainer acceptance.

All12 original criteria and all other CD-MCP-UP-005/contract/profile requirements
remain controlling. Original18 product budget,19 metadata/60 preserved products,
22,009 libraries/192 distributions, async-only handlers, private guarded fixtures,
provider-neutral telemetry, legacy compatibility and local-only delivery remain.
No UP06, publication, OAuth or Langfuse authority is granted by this amendment.

## Approval gate

Approve this exact amendment and its proposed authority manifest before resuming
product construction. The contract’s stop-on-control-conflict requirement and
AGENTS.md reconciliation rule require this narrow approval; passing raw tests or
an earlier broad instruction cannot silently alter the frozen contract.
