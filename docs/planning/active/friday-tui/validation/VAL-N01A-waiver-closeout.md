# VAL-N01A: closeout review under maintainer Linux deferral

**Outcome:** VERIFIED for TUI-N01A only. Automated Linux smoke was expressly
deferred for this work-unit closeout; it was not run or passed.

**Reviewer:** `/root/n01a_waiver_validation`, separate fresh-context Codex
GPT-6-family agent (exact variant unavailable).

**Date/mode:** 2026-10-18; read-only work-unit review of the unchanged
product candidate and the bounded authority amendment.

**Candidate:** `4a5311f2340adfbbf9cd5c4289db325e6b420b6b` against base
`ab56cbc61ac8f9ec54fc8d6e0b1753fe18411332`. Product diff:
`git diff ab56cbc61ac8f9ec54fc8d6e0b1753fe18411332..4a5311f2340adfbbf9cd5c4289db325e6b420b6b`.
Amended authority revision: `cfbc4a9599177983cadbce898fc8760d149edd2f`.
The intervening `4a5311f2..cfbc4a95` diff changes ten planning/evidence
files and no product source, tests, metadata or lockfile. The shared worktree
was clean during review; the reviewer made no edit.

The reviewer checked `AGENTS.md`, repository engineering/lifecycle and
independent-validation policies, the current manifest and directive, the
candidate diff and the prior [BLOCKED report](VAL-N01A-neutral-config-loader.md).
At the reviewed authority revision, SHA256 values were:

- `authority.json`: `bfe91deca9ccd5ebd0b0a6d421ae149e02ed2574d3fd4ca0aee3762be5c14ee1`;
- `directives/CD-TUI-N01A-neutral-config-loader.md`:
  `372e6fad7f81cc8529806572e1060202e03b804c256103ac94c83eb0a1a1fe1a`;
- `replacement-plan.md`:
  `aec3a03adf63d34ed34c2333074ca65bb6fced06eba10cc615a1357ccffc0650`;
- `docs/planning/board.yaml`:
  `1dac02a080681a5cb2585829255c3e24ff4b05f7c9f340548071aa5aff122035`.

Chuck Russell's instruction, "Let's postpone testing on Linux for now. Close
N01A," is recorded as a maintainer-approved waiver of only the automated
Linux smoke as an N01A verification prerequisite in the
[amended directive](../directives/CD-TUI-N01A-neutral-config-loader.md).
The independent reviewer confirmed that the waiver applies to the frozen
candidate, leaves every other N01A criterion intact, and retains automated
Linux testing and final installed-candidate Linux UAT before first TUI release
acceptance. The earlier `BLOCKED` report is preserved as historical evidence;
this fresh review supplies the governing N01A verdict.

The reviewer independently rechecked **390 focused tests**, board validation
(34 tasks), dashboard, offline lock, changed-file Ruff, two-source Mypy and
`git diff --check`; all passed. AST comparison found 42 shared definitions
with only the intended diagnostic-rule function changed. The six permitted
product paths are byte-unchanged since the frozen candidate. The prior full
read-only review records passing full Runtime (**334**), full Chat (**839,
5 skipped**), unchanged `friday-cli` (**155**), cross-package (**280**) and
installed-wheel/import checks. No other finding or blocked N01A criterion
remains under the approved waiver.

This result closes only N01A validation. It does not establish whole-TUI
completion, user UAT, maintainer acceptance of the initiative, Linux
coverage, or authority to push, merge, publish or release. Subsequent
board/manifest edits only close N01A code authority and record this verdict;
they do not alter the reviewed candidate or waiver.
