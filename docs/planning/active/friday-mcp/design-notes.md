# Friday — MCP Integration Thoughts

Companion document to `friday-framework-mcp-enhancements.md`. Captures Friday's MCP-specific
recommendations. Tool governance (permission taxonomy, approval gates, egress policy) is
deliberately excluded here — it lives at the framework dispatch layer in
`tool-governance.md`, and the MCP gateway *inherits* that policy rather than defining its own.

## 1. Core Architectural Stance

- Treat MCP as an **untrusted interoperability layer**, not a free upgrade. Every server is
  semi-hostile until proven otherwise.
- **Gateway/adapter pattern**: Friday talks only to the gateway; the gateway talks to MCP
  servers. Nothing reaches a server unless the gateway allows it.
- **Config-driven allowlist**: servers are declared in config, loaded at startup. No dynamic
  server registration at runtime. Any server not in the allowlist is refused.
- **Namespaced tools**: aggregate tools as `server.tool_name` (e.g., `filesystem.read_file`)
  to prevent tool-name collisions across servers.

## 2. Sandboxing

Workspace/path scoping alone is insufficient. Containment requirements:

- **Process isolation**: dedicated least-privilege user or container per server.
- **Network egress**: default-deny for stdio servers; pin egress to specific hosts only for
  servers that genuinely need network access.
- **Resource limits**: memory and CPU caps per server process.
- **Process-level kill timeout**: distinct from `tool_timeout_seconds`, which bounds call
  duration — this bounds *containment* of a hung or malicious process.

## 3. Pre-Dispatch and Post-Call Validation

Distinct from registration-time schema/description sanitization — do not conflate the two.

- **Before dispatch**: validate tool-call arguments against the tool's declared JSON schema.
  Reject unknown fields (`additionalProperties: false` where possible).
- **After the call**: validate outputs against an expected shape and sanitize returned text.
  A compromised server's output is the primary prompt-injection surface.

## 4. Per-Tool Evals

Generic injection tests are not sufficient; each tool gets its own eval suite.

- **Per-tool case files**: normal, boundary, and adversarial inputs (e.g., path escape
  attempts, files containing injected instructions).
- **Version pinning**: server versions are pinned; evals run in CI on any version bump.
- **Disable-on-fail rule**: a tool that fails evals stays disabled.
- **Metrics per tool**: schema conformance rate, p95 latency, selection accuracy (does Friday
  pick this tool when it should).

## 5. Audit (Reduced Scope)

- Structured, append-only diagnostics are acceptable for pass one.
- Hash-chaining / tamper-evidence is deferred.
- Approval-token traceability for write calls is **not** specified here — that requirement
  moved with governance to `tool-governance.md`.

## 6. Risks (Restated)

- Prompt/tool injection through malicious servers or returned content.
- Overbroad tool scopes and accidental write access.
- Version/schema drift and tool-name collisions.
- Latency and debugging complexity.
- Degraded tool-selection accuracy as tool count grows — more tools is not free.

## 7. Extraction Checklist

After moving governance out of this plan, confirm the build plan still carries as explicit
phases:

- [ ] Sandboxing (Section 2)
- [ ] Pre-dispatch and post-call validation (Section 3)
- [ ] Per-tool evals with version pinning (Section 4)

Nothing above should have been accidentally dropped when the approval-gate work relocated to
the framework layer.

## References

- `friday-framework-mcp-enhancements.md` — the MCP build plan this document critiques
- `tool-governance.md` — framework-level permission taxonomy, approval gates, egress policy
- MCP specification and security guidance: modelcontextprotocol.io (verify before
  implementing — the spec has been revising quickly)
- OWASP LLM Top 10 — excessive agency, insecure plugin design
