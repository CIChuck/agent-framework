# REM-009 Implementation Report — WS-08 Documentation Correction

- Date: 2026-09-29
- Status: Corrected builder candidate; independent review pending
- Branch: `feature/friday-mcp-ws08-docs`
- Original WS-08 base: `d9eb81d`
- VAL-017 reviewed candidate: `f8970313655e6e18b39d14dc1f151b5a7b5aaa33`
- Corrected documentation candidate: `08141407f7a7c3ca37174c8950bf552180df47c8`
- Remediation authority: [REM-009 directive](../remediation/REM-009-directive.md)
- Historical finding authority: [VAL-017 report](../validation/VAL-017-report.md)

The correction changes exactly four paths in the approved 11-path WS-08
documentation manifest: `docs/guides/17-mcp-client.md`,
`docs/guides/10-configuration.md`, `docs/guides/13-troubleshooting.md` and
`packages/friday-runtime/README.md`. The original candidate, VAL-017 report
and evidence remain intact. No runtime source, tests, schema, templates,
package metadata or unrelated local paths changed.

| Finding | Correction and local evidence |
| --- | --- |
| VAL-017-F01 | The main guide now states that an optional peer's connection failure is diagnostic but a pinned missing `include_tools` name independently fails registration with `missing_include`. A separate selected-mode example uses `include_categories: [mcp]` and warns that it admits all valid discovered MCP tools. The configuration summary, troubleshooting table and Runtime README carry the same distinction. A local provider start-and-register probe registered the good strict and category examples; a missing optional peer failed with `missing_include` under strict selection and continued under category selection; a missing required peer failed. |
| VAL-017-F02 | The configuration summary now names both selected-mode admission rules: canonical `include_tools` names and `include_categories: [mcp]`. A category-only config parsed through both Runtime and Chat and registered the repo-local probe tool without a name include. |

The scratch probe `/private/tmp/ws08_rem009_probe.py` parsed all four guide YAML
snippets and both distributed template copies through Runtime and Chat MCP
configuration models. It used only the repository's local synthetic stdio peer
or a missing local command, and stopped owned peers. Its exact outcome was
`strict good: registered; category good: registered; strict optional missing:
missing_include; category optional missing: continued; category required
missing: failed`. No live provider, network, credential or external delivery
was used.

`pytest -q` on the four affected Runtime/Chat config, turn-budget and memory
modules passed 92 tests. `scripts/check-documentation-lifecycle.py` passed
with 374 Markdown files, and board `validate` and `render --check` passed.
`git diff --check` passed. The unchanged package/integration results and
nonzero broad Chat result remain recorded in the original
[WS-08 implementation report](WS-08-implementation-report.md) and independent
[VAL-017 report](../validation/VAL-017-report.md); this documentation-only
correction did not alter their test inputs.

These are builder checks, not an independent verdict. A fresh read-only
reviewer must check the correction delta and the complete original WS-08
aggregate before closeout. VAL-017 remains CHANGES_REQUESTED for the old
candidate and is superseded only for decisions on the corrected candidate.
