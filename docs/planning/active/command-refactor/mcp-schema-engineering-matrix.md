# MCP schema engineering matrix for CD-CMD-MCP-003

**Status:** implementation design recorded before source edits on 2026-10-25.
The [approved directive](directives/CD-CMD-MCP-003-server-neutral-schema.md)
controls scope; this matrix cannot expand it.

| Input/profile | Canonical validation | Model export | Decision |
| --- | --- | --- | --- |
| Existing inline subset, 2020-12 | Existing complete-tree and keyword checks; local argument validation added | Sanitize annotations; preserve constraints | Retain existing admission where export passes |
| 2025 Draft-07 root declaration | Draft-07 validation and version gate | Preserve its constraint semantics; a `$ref` with sibling validation keywords is rejected unless a faithful provider export is demonstrated | Admit only under 2025 profile |
| 2020-12 `$defs` + local JSON Pointer `$ref` | Resolve within the same tool document, honor `~0`/`~1`, reject unresolved/external refs and pure alias cycles | Preserve references and definitions without expansion | Admit only within bounded graph/instance limits and provider capability |
| Draft-07 `$defs` + local `$ref` | Same pointer and graph checks, Draft-07 evaluation semantics | Preserve references without expansion | Admit only when provider export can preserve Draft-07 semantics |
| `propertyNames` in either dialect | Check every object key against its subschema; scan the subschema for unsafe text and unsupported keywords | Keep the constraint | Reject export paths that drop the keyword |
| Other unknown keywords, external refs or unsupported dialect forms | Reject with a fixed safe code | Never offer | No silent constraint loss |

The first fixture corpus will use two synthetic server catalogs: one with a
recursive tree schema and `propertyNames`, one with a nonrecursive local reuse
schema followed by an unsupported schema and a valid tool. Positive instances
include empty and nested objects, escaped-pointer targets, and valid key names.
Negative instances include invalid key names, wrong nested types, a missing
reference, an external reference, a pure alias cycle, unknown keywords in an
unreferenced definition, a bounded-work failure, and malformed/non-JSON
arguments. The registration fixtures will verify both dialect gates and that
a rejected definition does not consume the shared model-facing budget.

Runtime registration is provider-independent. Chat may list an admitted tool
that the active model cannot safely receive. That distinction must remain
visible in status, and no provider support is inferred from successful MCP
discovery or from a local serialization test alone.
