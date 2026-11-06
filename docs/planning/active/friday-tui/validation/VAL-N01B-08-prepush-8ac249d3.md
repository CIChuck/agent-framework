# TUI-N01B-08 independent local candidate review

**Verdict:** `VERIFIED` for the bounded N01B-08 **local** work unit. No
source or test finding requires remediation.

**Reviewer and mode:** Fresh-context Codex validation subagent, read-only
full work-unit review on 2026-10-19; exact model version was not exposed.
There was no shared builder context. The reviewer did not edit, commit or
push. The handoff named exact authority, candidate and base commits,
required checks and known baseline limits without builder conclusions.

**Authority base and frozen candidate:** `0268ec33` to clean
`8ac249d3ad694d886a7b11acf69d2ec2cc817d51` on `feature/friday-tui`.
The exact diff has four approved Runtime/Chat source/test paths and seven
scoped planning/evidence paths. It has no package metadata, lock, workflow,
script, `friday-cli` or other product-source change.

The reviewer matched these SHA-256 values at the frozen candidate:

| Controlling file | SHA-256 |
| --- | --- |
| `AGENTS.md` | `02c6360f0e2532a3ea761d7ae228fb105231c60d447146ead69c01c6ff99d152` |
| `docs/reference/policies/repository-engineering-policy.md` | `17b830b8990f74d1b0a25a46fc2cf2f62249f4e0d668f45b96cfe03a6cc76aff` |
| `docs/reference/policies/development-task-lifecycle.md` | `7087fb62381cc8a46128bc6745476d1aa08e1d577b4c73340760657ae834fe2a` |
| `docs/reference/policies/independent-validation-policy.md` | `4d951418e0f0c96a4c87d4b8a07cb4025dd94738da50893d19a6d2b7a7f82f4a` |
| `docs/planning/active/friday-tui/authority.json` | `76c8f1fe829068052e7b67063ba13c1ce83a48ca1b251a99691ec3526f27ddfb` |
| `docs/planning/active/friday-tui/directives/CD-TUI-N01B-08-neutral-transcript-write-effects.md` | `fbb5a93aaec274cac05442976333c0ebf30b1c37f2c53911b81ca8075c6c77e7` |
| `docs/planning/active/friday-tui/replacement-plan.md` | `e0b45d2c4adec6d23e9c94307f6edfabd21016ed73f7ae492a7a4f20ae27c840` |

The reviewer read [the directive](../directives/CD-TUI-N01B-08-neutral-transcript-write-effects.md),
[authority](../authority.json), [replacement plan](../replacement-plan.md),
[before-code characterization](N01B-08-before-code-transcript-write-characterization.md),
[builder checks](N01B-08-local-checks.md), policy and source/tests. The
neutral helper imports public transcript models without Chat/CLI and moves
only entry append and optional context-log effects. It preserves the exact
false-append error, late pending read, ignored false context result and
exception/cancellation propagation without rollback or retry. Chat keeps
preflight, session and turn policy, entry construction, pending-state
clearing, cached-turn advancement and MCP receipt readback.

Independent offline checks passed with
`UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache`,
`LITELLM_LOCAL_MODEL_COST_MAP=true`, `PYTHONDONTWRITEBYTECODE=1`,
`PYTEST_ADDOPTS='-p no:cacheprovider'` and `uv run --frozen --offline`:

| Gate | Independent result |
| --- | --- |
| Two new and protected N01B-07 tool-record test files | 34 passed. |
| Full Runtime | 402 passed. |
| Full Chat | 880 passed, five skipped, one existing deprecation warning. |
| Unchanged full `friday-cli` | 155 passed. |
| Scoped Ruff, new-file format check and targeted Mypy | Passed on the four changed source/test paths. |
| Offline lock, board/dashboard, authority JSON, links and diff check | Passed; board has 34 tasks, 408 local links across five changed Markdown files resolved. |
| Built wheels and installed probes | 17 wheels built; changed wheel members match checkout; isolated Runtime-only and Chat probes passed with 111 and 127 compatible packages respectively. |

Runtime and Chat full-suite fixtures used synthetic loopback bind access;
no live provider was used. `python -I` in the Runtime-only installed
environment confirmed Chat and CLI unavailable and unloaded. The separate
installed Chat probe persisted entry/context facts, verified MCP receipt
readback and rejected unsafe preflight. `uv pip check` passed in both
environments. Repository-wide `ruff check .` remains red with 534 findings
outside the four changed paths (533 under `docs/`, one in unchanged CLI);
the scoped gate is clean.

**Planning advisory:** [The replacement plan](../replacement-plan.md) still
says the candidate “awaits a stable commit” at line 348, although the
reviewed commit exists. This is a status-prose correction, not a product
finding. Because the replacement plan is controlling authority, any
post-verdict correction requires a fresh read-only review of that authority
delta before claiming a final current-authority closeout.

This verdict closes only the exact four-path N01B-08 **local candidate at
its reviewed authority revision**. A separately authorized non-force push
would be needed for exact-source Ubuntu verification. Installed macOS/Linux
TUI terminal UAT, controlled real-provider/tool tests, later neutral
transcript writer units, initiative acceptance, PR, merge and release
remain open.
