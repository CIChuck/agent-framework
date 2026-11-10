# Targeted verification diagnostic retest

Diagnostic candidate `3969e4d4438c5a18b3532a73d39d69352d26cda7` is independently
[VERIFIED](verified-report.md). This is an operator retest handoff; the underlying
production failure is still unresolved.

The configured verification routes in the preserved YAML resolve to:

- classifier and researcher: `openrouter/google/gemini-2.5-flash`;
- judge: `openrouter/google/gemini-3.5-flash-lite` (despite its gemini36 alias).

Maintenance falls back to8000 output tokens per request. The LM Studio output
supplied by the maintainer concerns embeddings; it does not establish which
verification role failed. YAML/model/budget settings have not been changed.

Restart Friday Chat through the existing launch workflow so the new source is
loaded. The old running process retains its imported implementation. Then run:

```text
/reorganize --verify --execute
```

This selects only verification, avoiding another full dedupe/prune/synthesize
run. It still executes maintenance: normal recovery snapshots are created and
verification metadata may change on success. Existing rollback/quarantine rules
remain. The agent has not run it or contacted live providers/personal stores.

Retain the new run ID, step results and complete `Error` lines. Failed provider
responses now include role, configured model, schema, available canonical finish
reason, and bounded field/type codes. Values, raw replies and reasoning are
excluded. `model=` identifies the configured route, not an independently
attested upstream serving identity.

`MaintenanceResponseIncompleteError` means an explicit length limit was reported.
`MaintenanceResponseParseError` means enclosing JSON could not be parsed, with
unknown termination still unknown. `MaintenanceResponseValidationError` includes
safe field paths/type codes. Schema and coverage checks remain fail-closed.

The actual production failure and any functional response repair remain open.
Keep populated-meta UAT stopped until verification succeeds; quote/ingest repairs
and human acceptance remain pending. No model/config change or delivery occurred.
