# TUI-N01B-01 final pre-push candidate review

**Verdict:** `VERIFIED` for the bounded N01B-01 pre-push gate.

**Reviewer:** Fresh-context Codex validation subagent, GPT-6 family (exact build
unavailable), read-only, 2026-10-18 America/New_York. No shared builder context,
source edit, commit or push was permitted. The reviewer independently read the
authority, diff and evidence and reran checks.

**Candidate:** `35e297e850af8fb2a9c54b255dd932062f51730d` on
`feature/friday-tui`, clean at review. **Base:**
`9b24588676c3b84d62c262d4937f4b0d2b39fbfc`. The review covered both
`9b245886..35e297e8` and the final authority/status delta
`edbcee92..35e297e8`. The latter changed controlling authority after the
earlier [pre-push review](VAL-N01B-01-prepush-edbcee92.md), so the earlier
verdict was stale for this candidate. This fresh review replaces it for the
pre-push decision.

## Frozen authority and scope

The reviewer confirmed these SHA-256 values before review:

| Document | SHA-256 |
| --- | --- |
| [Authority manifest](../authority.json) | `16fa4cac57bd05eea90c10aa8a0679f8de648dc9312bca1cbb748ff74eabd1ac` |
| [Approved N01B-01 directive](../directives/CD-TUI-N01B-01-neutral-transcript-query-contracts.md) | `ba55b804a1e94cfd389c822f9f5df3d872800dca445438252b3936795d8cdf06` |
| [Remediation directive](../remediation/REM-TUI-N01B-01-01.md) | `432d97298eac98de7c63627992eedaaf5a86c7a16d764369ed2a5d829e023c3f` |
| [Replacement plan](../replacement-plan.md) | `54a145cd21ac07ba703727b010a470a4d39da93100c465d8c00b6a1ab4eca38d` |
| [Development board](../../../board.yaml) | `ff37c3fe8ca9fb05c54167c5cc18f5f87a67b2c2f32ffb1946905a832618495a` |

The full work-unit diff has exactly the directive's four product/test paths
plus scoped TUI packet, board and generated-dashboard evidence. The final
closeout delta changes documentation and board state only. The neutral Runtime
module preserves the three dataclass shapes and four asynchronous Protocol
signatures. The Chat facade exports those same objects by identity while
retaining the Chat-owned export result. No `friday-cli`, TUI, package metadata,
lock or workflow path changed. The board, manifest and packet agree that the
initiative remains `started`, the corrected unit has pre-push verification,
and a further push is a separate gate.

## Independent checks

These commands ran at the candidate with `UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache`,
`PYTHONDONTWRITEBYTECODE=1`, `PYTEST_ADDOPTS='-p no:cacheprovider'`, and
`LITELLM_LOCAL_MODEL_COST_MAP=true` for the pytest invocations:

```bash
uv run --frozen --no-sync pytest -q packages/friday-runtime/tests_runtime/test_transcript_views.py packages/friday-chat/tests_chat/test_transcript_query_facade.py packages/friday-chat/tests_chat/test_transcript_production_commands.py packages/friday-chat/tests_chat/test_transcript_export_commands.py packages/friday-chat/tests_chat/test_session_identity.py packages/friday-cli/tests_cli
uv run --frozen --no-sync pytest -q --tb=line packages/friday-runtime/tests_runtime
uv run --frozen --no-sync pytest -q --tb=line packages/friday-chat/tests_chat
uv run --frozen --no-sync ruff check packages/friday-runtime/src/friday_runtime/transcript_views.py packages/friday-chat/src/friday_chat/transcripts.py packages/friday-runtime/tests_runtime/test_transcript_views.py packages/friday-chat/tests_chat/test_transcript_query_facade.py
uv run --frozen --no-sync ruff format --check packages/friday-runtime/src/friday_runtime/transcript_views.py packages/friday-chat/src/friday_chat/transcripts.py packages/friday-runtime/tests_runtime/test_transcript_views.py packages/friday-chat/tests_chat/test_transcript_query_facade.py
uv run --frozen --no-sync mypy packages/friday-runtime/src/friday_runtime/transcript_views.py packages/friday-chat/src/friday_chat/transcripts.py packages/friday-runtime/tests_runtime/test_transcript_views.py packages/friday-chat/tests_chat/test_transcript_query_facade.py
uv lock --check --offline
uv run --frozen --no-sync python scripts/friday-dev-board.py validate
uv run --frozen --no-sync python scripts/friday-dev-board.py render --check
```

Results: **179** focused/protected CLI tests, **339** full Runtime tests,
**848** full Chat tests with five skips and one existing deprecation warning;
Ruff, format, Mypy, lock, board and dashboard all passed. Initial full-suite
attempts in the default sandbox failed only where fixtures bound to
`127.0.0.1`; permitted local-loopback reruns passed. Both diff ranges passed
`git diff --check`.

The reviewer independently built fresh Runtime and Chat wheels offline and
installed them into a fresh Python 3.13 venv using local dependency wheels:

```bash
uv build --offline --wheel --package friday-framework-runtime --out-dir /private/tmp/friday-tui-n01b01-independent-review-wheel
uv build --offline --wheel --package friday-chat --out-dir /private/tmp/friday-tui-n01b01-independent-review-wheel
uv venv --offline --python 3.13 /private/tmp/friday-tui-n01b01-independent-review-venv
uv pip install --offline --python /private/tmp/friday-tui-n01b01-independent-review-venv/bin/python --find-links /private/tmp/friday-tui-n01b01-wheels /private/tmp/friday-tui-n01b01-independent-review-wheel/friday_framework_runtime-0.1.0a4-py3-none-any.whl
uv pip check --python /private/tmp/friday-tui-n01b01-independent-review-venv/bin/python
uv pip install --offline --python /private/tmp/friday-tui-n01b01-independent-review-venv/bin/python --find-links /private/tmp/friday-tui-n01b01-wheels /private/tmp/friday-tui-n01b01-independent-review-wheel/friday_chat-0.1.0a4-py3-none-any.whl
uv pip check --python /private/tmp/friday-tui-n01b01-independent-review-venv/bin/python
```

Runtime-only installation had 111 compatible packages and no
installed `friday_chat` or `friday_cli`. Its neutral import did not load either
frontend; the Runtime wheel contained `transcript_views.py` and declared no
Chat or CLI dependency. After installing Chat, 127 packages were compatible;
all four facade object identities and historical
`friday_chat.transcripts` pickle-global lookups resolved. The isolated
neutral-import probe omitted the LiteLLM local cost-map setting, so LiteLLM
logged a failed remote map lookup before using its local fallback; no provider
was called.

The repository-wide documentation-lifecycle check still reports six links in
the unchanged telemetry `VAL-001/report.md`; its SHA-256 at base and candidate
is `7f59d23203f78e1696d040cc87c29e53e7051dcc0f4da7166cd7ea6e02b08c9b`.
All ten Markdown files changed in the reviewed work-unit diff had valid local
links. The full command evidence and before/after comparison are also recorded
in the [builder's local-check report](N01B-01-local-checks.md).

## Remaining gates

No N01B-01 exact-source Ubuntu workflow or installed terminal UAT has run.
The local origin-tracking ref was `315a30e4`; a live remote query failed due
to DNS access, so this review makes no claim about current remote state.
`VERIFIED` is only the pre-push work-unit gate. It grants no push, maintainer
acceptance, PR, merge, release or deployment authority. This report was added
after the successful review as review evidence only; it changes no governed
product or authority file.
