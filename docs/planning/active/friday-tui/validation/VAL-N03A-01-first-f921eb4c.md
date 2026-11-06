# Independent first-candidate review: TUI-N03A-01

**Verdict:** `CHANGES_REQUESTED`.
**Candidate:** `f921eb4c380822879363f8331d54438ce7048640` against
`44359d22f769c41a129eb7483d5c95b71187cde9`.
**Review mode:** Fresh-context, read-only independent validator on the exact
approved [N03A-01 directive](../directives/CD-TUI-N03A-01-installable-shell.md)
and [authority manifest](../authority.json). This first verdict remains
historical after any correction.

The validator found the changed paths within scope and independently passed
11 TUI, 155 CLI and 50 selected Chat tests, focused Ruff/format/Mypy, offline
lock and board validation. Its independently built and freshly installed
Python 3.13 wheel passed entry-point, shell/quit, resource, dependency and
Chat/CLI isolation checks. No product code defect was demonstrated.

| Finding | Evidence and required disposition |
| --- | --- |
| N03A01-VAL-01 (medium, packet state) | The [packet index](../README.md) still said N03A-01 awaited approval, had no TUI package and was in `planning`, while [authority](../authority.json), [execution log](../execution-log.md) and the candidate said approved and implemented. The [replacement plan](../replacement-plan.md) also retained a current proposed/unimplemented next-gate claim. Reconcile current-state labels and fields under [REM-TUI-N03A-01-01](../remediation/REM-TUI-N03A-01-01.md), then seek fresh review. |
| N03A01-VAL-02 (high, required terminal UAT) | The directive requires macOS terminal observation of physical Ctrl+Enter delivery, pointer actions, live resize, visual layout, focus, paste and Quit. The [builder report](N03A-01-local-checks.md) records PTY smoke only. Hands-on results on the frozen candidate are required before the bounded shell milestone is complete; headless and PTY checks cannot substitute. No app defect is established by this missing observation. |

The initiative remains `started`. This verdict grants no acceptance, push,
PR, merge, release or later runtime/command work.
