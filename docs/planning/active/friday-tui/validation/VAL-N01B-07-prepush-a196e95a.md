# TUI-N01B-07 independent local candidate review

**Verdict:** `VERIFIED` for the bounded N01B-07 local work unit. No finding
requires a source change.

**Reviewer and mode:** Fresh-context Codex validation subagent, read-only
full work-unit review on 2026-10-19; exact model version was not exposed.
There was no shared-context exception. The handoff supplied the exact
authority, directive, candidate and diff, acceptance checks and known
baseline limits without builder reasoning. The reviewer did not edit,
commit or push.

**Authority base and candidate:** `f78ab6aa` to clean
`a196e95ab17120b6ee9d86d88ee9283485e1eb4f` on `feature/friday-tui`.
The reviewer checked the board, authority JSON, [approved exact
directive](../directives/CD-TUI-N01B-07-neutral-transcript-tool-records.md),
[before-code characterization](N01B-07-before-code-transcript-tool-record-characterization.md),
[builder checks](N01B-07-local-checks.md), policy and exact diff. The diff
contains the four named Runtime/Chat source/test paths and seven scoped TUI
planning, board and dashboard paths. No metadata, lock, workflow, script,
`friday-cli` or other product source changed.

The frozen candidate contains these controlling files and SHA-256 values:

| Controlling file | SHA-256 |
| --- | --- |
| `AGENTS.md` | `02c6360f0e2532a3ea761d7ae228fb105231c60d447146ead69c01c6ff99d152` |
| `docs/reference/policies/repository-engineering-policy.md` | `17b830b8990f74d1b0a25a46fc2cf2f62249f4e0d668f45b96cfe03a6cc76aff` |
| `docs/reference/policies/development-task-lifecycle.md` | `7087fb62381cc8a46128bc6745476d1aa08e1d577b4c73340760657ae834fe2a` |
| `docs/reference/policies/independent-validation-policy.md` | `4d951418e0f0c96a4c87d4b8a07cb4025dd94738da50893d19a6d2b7a7f82f4a` |
| `docs/planning/active/friday-tui/authority.json` | `f1cb05b86d319e08edcd85668b77d02b8f0f3e64d1f50ab961c828f6b76cd931` |
| `docs/planning/active/friday-tui/directives/CD-TUI-N01B-07-neutral-transcript-tool-records.md` | `abcf5057f8d2b482317919762c883c20d5572c9a955db861fa3408778dcada70` |
| `docs/planning/active/friday-tui/replacement-plan.md` | `afd8a664b026573ad3e2cf1844640fae7006c21b05ba82eabf3b7949b69d7f51` |

The new [neutral Runtime module](../../../../../packages/friday-runtime/src/friday_runtime/transcript_tool_records.py)
preserves MCP preflight predicates, errors, correlation, call IDs, argument
copies and result fields. [Chat delegation](../../../../../packages/friday-chat/src/friday_chat/adapters.py)
still validates before session/store access and constructs models after
session and turn-number setup. Chat retains entry persistence, context-log
order and MCP receipt readback; CLI behavior and code remain unchanged.

The reviewer independently passed 16 new tests, full Runtime (393), full
Chat (871 passed, five skipped), unchanged full `friday-cli` (155), scoped
Ruff and Mypy, offline lock, board validation (34 tasks), current dashboard,
authority JSON parse, 388 changed-document local links and whitespace
checks. All 17 wheels built. Runtime and Chat wheel source bytes matched the
checkout. Isolated installed-wheel probes passed with 111 compatible
Runtime-only packages and 127 after Chat installation; Runtime-only had no
Chat or CLI package. Initial sandboxed Runtime and Chat fixture runs hit
existing `127.0.0.1` bind restrictions; the complete offline suites passed
with synthetic loopback access. The whole Chat adapter's formatter diff
was identical at authority base and candidate.

The package-suite results are reproducible with offline
`uv run --frozen --offline pytest` on
`packages/friday-runtime/tests_runtime`, `packages/friday-chat/tests_chat`
and `packages/friday-cli/tests_cli`, respectively; the Runtime and Chat
synthetic HTTP/MCP fixtures need loopback bind access. The neutral and Chat
installed probes and wheel-byte hashes are specified in the linked
[builder checks](N01B-07-local-checks.md). The policy and source scope can
be rechecked with `git diff f78ab6aa..a196e95a --name-only`,
`uv run --frozen --offline python scripts/friday-dev-board.py validate`,
`uv run --frozen --offline python scripts/friday-dev-board.py render --check`,
`uv lock --check --offline` and `git diff --check f78ab6aa..a196e95a`.

This verdict closes only the N01B-07 **local** work unit. Exact-source Ubuntu
verification needs a separately authorized non-force push of frozen source.
Installed macOS/Linux TUI terminal UAT, controlled real-provider/tool
testing, later transcript persistence, full initiative acceptance, PR,
merge and release remain separate gates. Post-verdict board and packet
reconciliation must not alter the reviewed four product/test paths.
