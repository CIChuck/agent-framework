# TUI-CI01 first-candidate independent preflight

**Outcome:** `CHANGES_REQUESTED` on 2026-10-18. Historical review of the
first candidate; a corrected candidate requires a fresh review.

**Reviewer:** fresh-context, read-only agent
`/root/tui_ci01_independent_review` (model/version not exposed to the
controller). This report transcribes the reviewer's final verdict; the
reviewer did not edit the candidate.

**Authority and candidate:** board unit TUI-CI01, approved
[`CD-TUI-CI01-linux-actions.md`](../directives/CD-TUI-CI01-linux-actions.md),
and [`authority.json`](../authority.json). Construction base
`d69c1d72fb841e4b3e51683ef16d7dcd4eac1f00`; reviewed commit
`7d97aacdd11c3cdf9903b52866a6896a21302e3e`; diff
`d69c1d72..7d97aacd`. At the reviewed revision, SHA-256 hashes were:

- `board.yaml`: `102d70a467475f385865061169e32ca1de7a876dcec3f4618f35ba6ba5371d96`
- `authority.json`: `0cbb3d3457926ef8a8229619e8fd79e703973ff1a98582a5a56f34eb654bbbe9`
- `CD-TUI-CI01-linux-actions.md`: `fd3e847928093a9e904575d80e17900c54504961dd9ef9a754b2d64a84d289f4`
- TUI packet `README.md`: `e7577b182bc808efe903c46bed912a0ab1159c8dba7ff3a5607f8afcda36a089`

**Review mode and checks:** full read-only preflight of the frozen eight-path
diff and current authority. All eight paths were within approved scope. The
reviewer ran board validation (34 tasks), dashboard check, `git diff --check`,
YAML parsing, Bash syntax, and embedded Python parsing; these passed. The
reviewer inspected the local test record but did not rerun package suites.
No Linux Actions run existed.

## Findings

- **CI01-01 — High, workflow cannot start.** In
  `.github/workflows/friday-tui-linux.yml` at commit `7d97aacd`,
  `jobs.n01a-linux.env` set `WHEEL_DIR` and `RUNTIME_VENV` with
  `${{ runner.temp }}`. GitHub excludes the `runner` context at job-level
  `env`, although it permits it at step-level `env`. This violates the
  directive's required runnable Ubuntu workflow. Move both expressions to
  consuming steps and check expression availability as well as syntax.
  [GitHub context availability](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts).
- **CI01-02 — Medium, source commit absent from PR log.** The reviewed
  version step printed only `git rev-parse HEAD`. On `pull_request`, default
  checkout tests a synthetic merge commit. The directive requires logging
  the source commit and tying Linux evidence to the candidate. Record the
  PR head SHA beside the tested checkout SHA; use the push SHA for pushes.
  Keep the merge checkout. Verify the expression and log command.
  [GitHub pull-request checkout behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).

**Disposition:** Both findings are assigned exactly once in the
`RD-TUI-CI01-01` remediation addendum to the approved directive. This first
candidate is rejected for decision purposes. Package boundaries and
documentation placement are unchanged. A new commit and independent review
are required; a successful Ubuntu run remains pending and terminal UAT is a
separate final-candidate gate.
