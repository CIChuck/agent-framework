# TUI-N03A-01 before-code package and shell characterization

**Status:** Read-only planning evidence for a proposed, unapproved
construction directive. No TUI package or UI code exists yet.
**Branch/source:** `feature/friday-tui` at
`adfb92e6b100bda46a4215183f4942b947b0460c`.
**Maintainer direction:** After N01B-09 local and exact-source Ubuntu gates
were independently VERIFIED, Chuck Russell asked when TUI package work would
begin, then replied “proceed” to the proposal to make it the next
construction unit.

`packages/friday-tui/` does not exist. The root workspace already declares
`packages/*` as members; the new package will need its own `pyproject.toml`,
source, tests and lock entry. No root dependency or import from Chat/CLI is
needed merely to make the independent TUI installable. The current
`uv.lock` has no `textual` package entry. The accepted [product goal](../README.md)
requires Textual, independent installation and unchanged `friday-cli` and
`friday-chat` behavior. The [screen contract](../screen-layout.md) defines
the first visible zones and Enter/Ctrl+Enter controls. The
[replacement plan](../replacement-plan.md) identifies TUI-N03A and N03B,
but its full N03A row also includes configuration discovery and service
startup. Those are separate from the narrow first visible-shell subunit.

The current neutral `friday_runtime.application_config.load_application_config`
can validate the established YAML shape. Chat-equivalent real/fake service
assembly still lives in `friday_chat.runtime.build_runtime`; the headless
`RuntimeKernel` uses a distinct `RuntimeConfig` path. An initial TUI shell
must therefore not silently use either Chat code or a different config path
to claim working prompt/runtime parity. Configuration chooser, runtime
construction and prompt execution need later exact directives.

Current unchanged baselines on 2026-10-19:

- `uv run pytest packages/friday-cli/tests_cli -q`: **155 passed**.
- `uv run pytest packages/friday-chat/tests_chat/test_cli.py
  packages/friday-chat/tests_chat/test_config_facade.py
  packages/friday-chat/tests_chat/test_app_lifecycle.py -q`: **50 passed**.
- `uv run python scripts/friday-dev-board.py validate`: **34 tasks**.
- `UV_CACHE_DIR=/private/tmp/friday_tui_n03a01_uv_cache uv lock --check
  --offline`: existing lock **resolved 213 packages** without edits. The
  default `uv lock` cache path was restricted in this sandbox, so this
  check used a disposable cache outside the repository.

[Textual 8.2.8 on PyPI](https://pypi.org/project/textual/) declares Python
3.13 support and was the latest listed release at this planning check.
The official [testing guide](https://textual.textualize.io/guide/testing/)
documents headless `App.run_test()`/Pilot checks, and the official
[TextArea guide](https://textual.textualize.io/widgets/text_area/) confirms
multiline editing support. These sources support a first local dependency
resolution proposal, not an installed TUI or physical terminal-key result.

The next testable unit should deliver `friday-tui --help` and `--version`
without service startup, plus a launchable development shell with the
accepted screen zones, draft editor and accessible controls. A Submit
attempt without a connected runtime must retain the draft and explain the
unavailable action. A test-injected handler may prove exactly-once UI
submission, but the executable must not fabricate a Friday answer or claim
runtime integration. Installed macOS terminal UAT, Linux terminal UAT,
all `/` command parity, live provider/tool behavior and release remain open.
