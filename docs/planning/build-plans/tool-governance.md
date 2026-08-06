# Tool Governance Build Plan

**Status:** Draft
**Origin:** Security review of MCP enhancement plan; generalized to framework-level governance
**Related:** `friday-framework-mcp-enhancements.md`

---

## 1. Purpose

Establish a single, framework-level governance layer for all tool execution. Applies to every registered tool regardless of origin: native tools, MCP-provided tools, and future integrations. The MCP gateway inherits this policy rather than defining its own, preventing per-surface reimplementation and policy drift.

## 2. Core Invariant

> Model output alone can never authorize a non-READ tool call.

Approval decisions originate only from the human user's channel.

## 3. Permission Model

### 3.1 Classification Taxonomy

| Class | Meaning |
|---|---|
| READ | No side effects; safe to auto-approve |
| WRITE | Creates or mutates state (local or remote) |
| DESTRUCTIVE | Irreversible data loss or arbitrary system impact |

Rules:

- Classification is assigned **in configuration at registration**, never inferred from tool or server metadata.
- **Default-deny:** an unclassified tool is blocked.
- Runtime configuration may only **tighten** policy. Downgrading a DESTRUCTIVE tool to auto-approve requires an explicit, audited override — never a silent config edit.

### 3.2 Arg-Sensitive Escalation

Classification is per-call, not merely per-tool. The policy engine must support escalation rules based on argument values:

- `file_write` with `overwrite=false` → WRITE; with `overwrite=true` → DESTRUCTIVE.
- `file_read` with `store_to_memory=true` mutates long-term memory — a WRITE hiding inside a READ; escalate accordingly.

### 3.3 Egress Dimension (Orthogonal Flag)

The mutation taxonomy does not capture confidentiality. Add an independent `egress` flag for tools whose arguments or content leave the host:

- Egress-capable tools require destination-host allowlists.
- First contact with any new host requires per-call approval.
- Rationale: prompt injection's most likely payoff is data exfiltration. `http_upload` of a sensitive file to an attacker-controlled host causes zero local mutation and would pass a mutation-only taxonomy.

## 4. Approval Flow (Strategic)

- Human confirmation step in the chat flow for every WRITE or DESTRUCTIVE call, and for first-contact egress to unapproved hosts.
- Approval semantics: bound to the **exact tool and arguments**, **single-use**, and **expiring**. Any change to arguments invalidates the approval.
- Optional session-scoped grants may relieve confirmation fatigue on high-frequency writes, but must be narrowly path/arg-constrained. Broad session grants erode the arg-exact binding that makes the control meaningful.

## 5. Native Tool Classification (Phase 0 Seed)

| Tool | Class | Notes |
|---|---|---|
| get_current_datetime, echo, directory_list | READ | No side effects |
| file_read | READ | Escalates to WRITE with `store_to_memory=true` |
| serper_search, web_reader, http_get | READ + egress | Query content leaves the host |
| file_write | WRITE | Escalates to DESTRUCTIVE with `overwrite=true` |
| http_download | WRITE | Local file creation |
| http_post, http_put | WRITE + egress | Remote mutation; data leaves the host |
| http_upload | WRITE + egress | Primary exfiltration vector |
| http_delete | DESTRUCTIVE | Remote data loss |
| command_execute | DESTRUCTIVE | Existing blocklist migrates into PolicyEngine deny-rule |

The team validates this table against actual tool parameter schemas before it is adopted.

## 6. Configuration Schema (Illustrative)

```yaml
tool_policy:
  default: deny
  tools:
    file_read: read
    file_write: write
    command_execute: destructive
    filesystem.read_file: read        # MCP tools, namespaced
    filesystem.write_file: write
  approval:
    write: per_call
    destructive: per_call
  egress:
    serper_search: [api.serper.dev]
    http_get: []                      # empty = per-call approval for all hosts
```

Final schema is owned by the tactical implementation plan. Escalation rules and egress host lists are formalized there.

## 7. Enforcement Architecture

- **Single chokepoint:** enforcement lives inside tool dispatch, after schema validation, before execution. No tool bypasses it.
- **Components (contracts defined in the tactical plan):**
  - `PolicyEngine` — config load, classification lookup, arg-sensitive escalation, egress rules.
  - `ApprovalManager` — pending → confirmed/expired/denied; single-use.
  - `AuditWriter` — append-only record of every governed call.

## 8. Audit Requirements

- Every WRITE/DESTRUCTIVE call logs its approval token ID, so every mutation traces to a human decision.
- Append-only format required at launch.
- Hash-chaining for tamper evidence is acceptable to defer.

## 9. Migration Path

1. Wrap the existing tool dispatch with the policy chokepoint.
2. Seed the classification table (Section 5).
3. Convert the existing `command_execute` blocklist into a PolicyEngine deny-rule — one enforcement point, not two drifting ones.
4. MCP adapter adopts this policy when the approval-gate phase ships; no parallel approval logic in the gateway.

## 10. Phases and Dependencies

| Phase | Deliverable | Depends On |
|---|---|---|
| 0 | Classification table validated; config schema ratified | — |
| 1 | PolicyEngine + dispatch chokepoint (enforcement only) | 0 |
| 2 | ApprovalManager + chat confirmation flow | 1 |
| 3 | AuditWriter with approval token linkage | 1 |
| 4 | Egress host allowlists | 1 |
| 5 | Any write-capable MCP server enabled | 2 |

Hard rule: no write-capable tool (native reclassification or MCP) is enabled before Phase 2.

## 11. Open Questions

- ~~Should any write-capable MCP tool be registrable before the approval-gate phase ships?~~ **Answered: no (Phase 0 decision).**
- What session-grant scope, if any, is acceptable for high-frequency WRITE tools?
- What egress allowlist is appropriate for `web_reader` and `http_get`, which need open-web access to be useful?

## 12. Revision History

| Version | Change | Rationale |
|---|---|---|
| 0.1 | Initial draft; governance generalized from MCP-only to framework-wide | Security review: destructive native tools predated MCP; per-surface approval logic would drift |
