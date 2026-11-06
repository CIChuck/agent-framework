# TUI-N01B-09 before-code transcript session-ensure characterization

**Status:** Read-only before-code evidence, 2026-10-19. The exact
[CD-TUI-N01B-09](../directives/CD-TUI-N01B-09-neutral-transcript-session-ensure.md)
is proposed only and needs separate maintainer approval before source or
test edits. The branch is `feature/friday-tui` at planning base `78aad114`;
its product bytes match pushed `c4a5faa6`. N01B-08's exact-source Ubuntu
gate was [independently VERIFIED](VAL-N01B-08-postrun-3a5e05cf.md), and
its one push is consumed. Installed TUI terminal UAT remains open.

## Existing session behavior

`FrameworkTranscriptAdapter.record_interaction` in
`packages/friday-chat/src/friday_chat/adapters.py` performs the neutral MCP
provenance preflight before touching the transcript store. It then calls
`_ensure_session`, `_next_turn_number`, constructs the Chat-specific entry
and tool records, and delegates append/context-log effects to Runtime.
N01B-09 can isolate only `_ensure_session`'s get-or-create effect. Turn
numbering, entry construction, receipt readback and finalization remain in
Chat for later bounded units.

`_ensure_session` awaits `store.get_session(self.session_id)`. If any
`TranscriptSession` is returned, it stops without creating or changing that
session, even when the session is ended or contains an older configuration
snapshot. On a miss, Chat constructs a new `TranscriptSession` with the
current session ID, `config.chat.user_name`, `config.llm.model or
"unknown"`, and `config.chat.system_prompt`. Chat evaluates
`config.model_dump(mode="json", exclude={"tools": {"providers": {"mcp"}}})`
only on that miss. The omission of the MCP provider stanza applies to a
**new** Chat diagnostic snapshot; existing snapshots are not rewritten.
The model supplies its own start time and default aggregates. Chat awaits
`store.create_session(session)` and ignores its Boolean result.

The SQLite store returns `False` for an integrity or caught operational
write error. `_ensure_session` does not retry, reopen, repair, roll back,
re-read after a race or convert a false result into an exception. A raised
get/create exception or cancellation propagates. `get_session` reads by
session ID without filtering ended or archived sessions.

## Disposable behavior probes

Read-only Python probes used fresh temporary SQLite stores and fake stores.
They describe current behavior, including existing limitations:

| Condition | Observed result |
| --- | --- |
| Missing session | Persisted identity, user, model, system prompt and JSON configuration snapshot match Chat inputs; repeated ensure keeps the original start time. |
| Existing historical session | Stored model and snapshot remain unchanged; the Chat snapshot factory is not evaluated. |
| Ended session with same ID | Session remains ended; no reopen or replacement. |
| `create_session` returns `False` | `_ensure_session` returns normally and no session row is created. A later `record_interaction` reaches the existing `Failed to append transcript entry.` error with no entry and cached count `0`. |
| `get_session` or `create_session` raises or is cancelled | The same exception or cancellation propagates; no new recovery policy runs. |

Existing MCP transcript tests also protect the new-session snapshot's
complete MCP-stanza omission, preservation of other provider shape, and
unchanged historical snapshots. N01B-09 must preserve those fields and
timing while exposing the get-or-create effect to a neutral caller.

## Unchanged baseline and next proof

With `UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache`,
`LITELLM_LOCAL_MODEL_COST_MAP=true`, `PYTHONDONTWRITEBYTECODE=1`,
`PYTEST_ADDOPTS='-p no:cacheprovider'` and `uv run --frozen --offline`, a
selected Chat transcript/session run passed **41** tests with eight
deselected, protected Chat/Runtime/Transcript files passed **29**, and the
unchanged full `friday-cli` suite passed **155**. These separate runs
total **225 passes**. `uv lock --check --offline` passed. No live provider
or remote service was used.

The proposed unit should add direct Runtime fake-store tests for the lazy
session factory, existing/ended sessions, false create, raised and
cancelled get/create. Chat delegation tests should compare disposable
SQLite session fields and snapshots, the preflight-to-append order, and
the unchanged false-create path. Full Runtime/Chat and unchanged CLI
suites, static checks, installed Runtime-only and Chat wheel probes, and
fresh independent review remain construction gates. Automated Ubuntu
verification needs a separately authorized push. This characterization
is not implementation, independent validation, UAT or acceptance.
