# Amendment 001 — isolate Draft-07 validation to MCP 2025

**Status:** approved by Chuck Russell on 2026-10-25 in the conversation;
implementation and validation pending.

**Amends:** [CD-CMD-MCP-001](CD-CMD-MCP-001-compatibility-exception.md).

The approved directive requires 2025 Draft-07 input-schema compatibility while
keeping 2024 behavior unchanged. `CatalogPage.parse` currently receives only a
`modern` boolean, so 2024 and 2025 both arrive as `modern=False`. Selecting
Draft-07 from `$schema` alone in `ToolDefinition.parse` would also change how
2024 catalogs validate explicitly declared Draft-07 schemas. A legal Draft-07
tuple `items` schema, for example, was rejected under the old 2024 validation
path but would become accepted. The current working-tree implementation has
this uncommitted issue; it must be corrected before a candidate is frozen.

Permit one additional production file:
`packages/friday-mcp/src/friday_mcp/client/base.py`. It may pass the already
selected protocol version as a single 2025-compatibility flag to
`CatalogPage.parse`, which passes the flag to `ToolDefinition.parse`. Select
`Draft7Validator` only when that flag is true and the exact Draft-07 URI is
declared. The 2024 path retains its previous `Draft202012Validator.check_schema`
behavior, and the 2026 path retains its strict dialect rejection.

Add one regression test proving a Draft-07 tuple schema is accepted through a
2025 client and still rejected through the 2024 parser, in addition to the
existing 2025/2026 tests. Re-run the approved directive's focused suites,
Ruff, mypy and independent review. No other scope or security rule changes.
