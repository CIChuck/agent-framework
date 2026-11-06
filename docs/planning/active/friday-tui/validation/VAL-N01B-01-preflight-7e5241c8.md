# TUI-N01B-01 independent pre-push review: first candidate

**Verdict:** `CHANGES_REQUESTED` (historical first-candidate result).

**Reviewer/mode:** Fresh-context Codex validation subagent (GPT-6; exact build
unavailable), read-only, 2026-10-18 America/New_York. No candidate file was
changed by the reviewer.

**Candidate/base:** `7e5241c8611c41475b7730ff84005c4bb7561dd6` /
`9b24588676c3b84d62c262d4937f4b0d2b39fbfc`; complete diff range
`9b245886..7e5241c8`. Candidate worktree was clean.

**Authority checked:** [authority manifest](../authority.json) at candidate
SHA-256 `a6b831f86f2c1a69ae2c6579f407023700d317f0048de612b2ef155feb8445db`;
[CD-TUI-N01B-01](../directives/CD-TUI-N01B-01-neutral-transcript-query-contracts.md)
at candidate SHA-256
`ba55b804a1e94cfd389c822f9f5df3d872800dca445438252b3936795d8cdf06`.
The reviewer also read `AGENTS.md`, repository independent-validation policy,
the replacement plan, architecture boundaries, before-code characterization
and [builder report](N01B-01-local-checks.md). Both supplied hashes matched.

## Findings

1. **N01B01-01 — Medium; authority-document conflict.**
   `replacement-plan.md` lines 3-6 and its current-construction-gate section
   around lines 348-378 still say N01A review is pending, authority is
   N01A-only and later units are design-only. The approved N01B-01 directive,
   authority manifest and board instead authorize this exact unit. This
   violates the [independent-validation policy's authority reconciliation
   and documentation requirements](../../../../reference/policies/independent-validation-policy.md)
   and could misdirect the next unit. Correct both plan locations to record
   closed N01A and approved N01B-01 under validation, retaining the boundary
   against later subunits. Compare revised text with manifest and board, then
   rerun board validation and dashboard check. Documentation-only; no
   configuration or product-code effect.
2. **N01B01-02 — Low; required command evidence missing.** The
   [local-check report](N01B-01-local-checks.md) records outcomes but omits
   exact after-code test, static, build and install commands required by
   [directive verification item 4](../directives/CD-TUI-N01B-01-neutral-transcript-query-contracts.md).
   Add command lines and environment settings, including the 171-to-179
   comparison and local-loopback limitation, so the builder checks are
   reproducible. Verify that each required gate is represented. Evidence-only
   correction; no configuration or product-code effect.

## Checks and limit

The reviewer found the product diff confined to the four authorized
source/test paths. The moved dataclass fields and async signatures matched
the before-code source; Chat re-exported the identical four objects, retained
`TranscriptExportResult`, and left query and export implementations untouched.
Independent focused testing passed **179** tests. Separate full runs passed
**Runtime 339**, **Chat 848 with five skips**, and **CLI 155**. Ruff, Mypy,
lock, board, dashboard and `git diff --check` passed. Fresh Runtime and Chat
wheels built offline; a fresh Python 3.13 environment installed Runtime with
neither frontend present or importable, then confirmed installed Chat object
identity and all four historical pickle global lookups. Sandboxed loopback
fixture binds failed before candidate code ran; reruns with local loopback
permitted passed.

This verdict covers the **pre-push** candidate. Exact-source N01B-01 Ubuntu
execution still needs a separately authorized push. Installed terminal UAT and
full TUI acceptance remain later gates. A corrected authority document
changes the candidate and requires a fresh independent review; this historical
first-candidate verdict cannot be promoted to `VERIFIED`.
