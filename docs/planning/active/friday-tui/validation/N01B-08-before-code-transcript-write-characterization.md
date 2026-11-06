# TUI-N01B-08 before-code transcript write characterization

**Status:** Read-only before-code evidence, 2026-10-19. The exact
[CD-TUI-N01B-08](../directives/CD-TUI-N01B-08-neutral-transcript-write-effects.md)
was subsequently approved for its four local source/test paths. The current branch is
`feature/friday-tui` at planning commit `ba609b27`; its product bytes match
the pushed `4a646dc7` source. N01B-07's exact-source Ubuntu gate was
[independently VERIFIED](VAL-N01B-07-postrun-4fc8309d.md), and its push
authority is consumed. Installed TUI terminal UAT is still open.

## Existing write behavior

`FrameworkTranscriptAdapter.record_interaction` in
`packages/friday-chat/src/friday_chat/adapters.py` performs the N01B-07
neutral MCP provenance preflight before touching the store. It then ensures
the session, chooses the next turn number, constructs tool records and a
`TranscriptEntry` with Chat's current messages, model, temperature,
timestamp, latency and metadata. Only the final append/context-log effects
are candidates for N01B-08. Chat still owns session creation, turn numbering,
entry construction and MCP receipt/readback.

The current effect order is exact: await `store.append_entry(entry)`; raise
`RuntimeError("Failed to append transcript entry.")` if it returns `False`;
**then** inspect the current pending context-log tuple; if present, construct
`ContextLogEntry` from the entry/session/turn identity and that tuple, await
`store.store_context_log(log)`, ignore its Boolean return, and clear pending
state; finally set the cached turn number. The pending tuple is read after
the append await, so a callback supplying it to a neutral helper must also
be evaluated after that await.

The SQLite store commits the transcript entry and the raw context log in
separate operations. `append_entry` returns `False` on caught write errors;
`store_context_log` also returns `False` on caught write errors. There is no
cross-write transaction or rollback. The declared `TranscriptStore` protocol
contains `append_entry` but omits `store_context_log`; a narrow structural
write-store protocol in Runtime can express both calls without changing
`friday-transcript` in this unit. Runtime already depends on
`friday-transcript`, and the effect can accept its public models without
importing Chat or CLI.

## Disposable failure and timing probes

Read-only Python probes used fresh temporary SQLite stores and injected
method results. These facts describe current behavior, not a desired
reliability change:

| Injected condition | Observed result |
| --- | --- |
| `append_entry` returns `False` | Exact error `Failed to append transcript entry.`; no entry; pending context retained; cached turn number is `0` after initial count. |
| `store_context_log` returns `False` | Entry remains committed; method returns normally; pending context clears; cached turn number advances to `1`. |
| `store_context_log` raises | Original exception propagates; entry remains committed; pending context and cached turn number remain at their pre-effect values (`("pending", "response")`, `0` in the probe). |
| Pending tuple changes during the append await | The later tuple (`"updated"`) is stored and then cleared. |

This partial-commit behavior is observable and must be preserved by the
extraction. A retry after an exception can encounter the already committed
entry; N01B-08 must not introduce its own retry, deduplication, transaction
or cleanup policy. A later approved unit can revisit those policies.

## Unchanged baseline and next proof

With `UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache`,
`LITELLM_LOCAL_MODEL_COST_MAP=true`, `PYTHONDONTWRITEBYTECODE=1`,
`PYTEST_ADDOPTS='-p no:cacheprovider'` and `uv run --frozen --offline`, five
relevant Chat files passed **113** tests, the direct N01B-07 Runtime file
passed **11**, and unchanged full `friday-cli` passed **155**. These are
separate runs totaling **279 passes**. `uv lock --check --offline` passed
with the same temporary UV cache. No provider or remote service was used.

The proposed N01B-08 unit should add direct Runtime tests for append-only,
append-plus-context, false/exception results and the late pending read. Chat
delegation tests should compare persisted entry/context data and the exact
preflight, session, turn-number, append, context and receipt order through a
disposable store. Full Runtime/Chat and unchanged CLI suites, static checks,
installed Runtime-only and Chat wheel probes, and fresh independent review
remain construction gates under the approved directive. Automated Ubuntu
verification needs a separately authorized push. This characterization is
not implementation, independent validation, UAT or release acceptance.
