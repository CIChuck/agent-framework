# TUI-N01A local construction checks

**Date/branch:** 2026-10-18; `feature/friday-tui`.

**State:** Locally checked N01A candidate for a frozen commit and
fresh-context independent validation. The exact candidate hash is supplied
with the review dispatch. This report is not `VERIFIED`, TUI UAT,
maintainer acceptance or delivery authorization.

The candidate moves the existing Chat application schema and file loader into
`friday_runtime.application_config`, keeps `friday_chat.config` as a facade,
and declares Runtime's direct Pydantic/PyYAML dependencies. The scope is the
six product/test/metadata/lockfile paths named by
[CD-TUI-N01A](../directives/CD-TUI-N01A-neutral-config-loader.md). No
`friday-cli`, Chat launcher/display/runtime/command, TUI or other product
module changed. The approved N01S identity result remains separate.

## Behavior and regression evidence

- The 34 moved model/section classes and seven untouched parser helpers are
  AST-identical to the approved before-code Chat source. Only the loader
  entry point, rule injection and private diagnostic-rule lookup changed.
  The Chat traceability map and original `__all__` remain in the facade.
- New neutral/facade tests cover default and snapshotted diagnostic rules,
  replacement and in-place Chat rule edits, class/error identity, historical
  Chat pickle-global lookup, legacy and packaged canonical YAML parity,
  diagnostic order, raw paths, symlink-target catalog anchoring, ignored
  `FRIDAY_MODELS_CONFIG`, error type/message/chaining, native read errors,
  no source-file mutation and neutral import isolation. Existing Chat suites
  retain MCP validation/interpolation ordering and typed LLM migration cases.
- Full Runtime suite: **334 passed**. Full Chat suite: **839 passed,
  5 skipped** with one existing deprecation warning. Unchanged
  `friday-cli` suite: **155 passed**. Cross-package telemetry, MCP and
  integration configuration callers: **113 passed**. Suites with local HTTP
  fixtures required permitted loopback binding; sandbox-only runs failed at
  socket creation before assertions, and the same suites passed when rerun
  with loopback enabled.
- Changed-file Ruff and Mypy pass. `uv lock --check --offline`, package
  metadata validation for all 17 projects, board validation, generated
  dashboard check and `git diff --check` pass.

## Installed-package evidence

Built Runtime and Chat wheels plus their local Friday dependency wheels. A
fresh disposable Python 3.13 venv outside the checkout resolved and installed
the Runtime wheel with its declared dependencies. Its wheel metadata contains
direct `pydantic>=2.0` and `pyyaml>=6.0.0` requirements and no Chat/CLI
requirement. Before Chat installation, the installed neutral module loaded
from that venv; neither `friday_chat` nor `friday_cli` was installed or loaded.

The same disposable venv then installed the Chat wheel and dependencies.
`uv pip check` found **127 compatible installed packages**. The installed
Chat facade and neutral API returned the same class/error objects, typed
values and resolved service specs for a synthetic legacy file and the
wheel-packaged canonical example. No real provider credential or provider
request was used. Both checkout and installed `friday-chat --version` report
`0.1.0a4`; `--help` exits zero with the same options. The existing `friday
--help` import failure (`friday_cli.main.app` absent) remains in both
environments and was not changed under this directive.

## Remaining gate

The neutral test module is runnable on Linux, but no Linux execution was
available for this candidate. The host is macOS; both configured Docker
contexts have no running daemon, and the installed Docker app could not be
launched because its executable is missing. The automated Linux smoke in
CD-TUI-N01A therefore remains **unverified**. The independent reviewer must
assess this limit against the directive and must not report Linux coverage or
final TUI acceptance. Hands-on macOS/Linux terminal UAT is scheduled for
later visible TUI and final installed-candidate gates.

The repository-wide documentation lifecycle checker still reports six
pre-existing broken absolute links in the unrelated telemetry `VAL-001`
review report. The N01A packet introduces no new broken links.
