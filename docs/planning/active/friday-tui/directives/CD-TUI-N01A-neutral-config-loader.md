# CD-TUI-N01A: neutral application configuration loader

**Status:** Proposed for maintainer approval; **not** a construction grant.

**Initiative/unit:** `friday-tui` / TUI-N01A

**Branch/before-code source:** `feature/friday-tui` / `26f5d090`

**Current authority:** `design_only`; `product_code_generation_authorized:
false`. TUI-N01S was independently `VERIFIED`, but its grant does not extend
to this unit. Construction requires the maintainer's explicit approval of
this exact directive and a matching `granted` board/authority-manifest update
before any product-code edit, per [AGENTS.md](../../../../../AGENTS.md).

## Purpose and observable result

Give an independently installed future `friday-tui` the same Friday Chat
runtime-file schema, interpolation, diagnostics and canonical model-library
resolution through `friday_runtime.application_config`, without importing
`friday-chat` or `friday-cli`. Keep current `friday_chat.config` callers on a
thin compatibility facade with unchanged Chat and `friday-cli` behavior.
This unit loads configuration only. It does not launch a TUI or assemble a
runtime service.

The [neutral loader contract](../neutral-config-loader-contract.md),
[before-code characterization](../validation/N01A-before-code-characterization.md),
[replacement plan](../replacement-plan.md) and current [authority
manifest](../authority.json) control the work. If they disagree with this
directive or current source, stop and reconcile before editing code.

## Exact change boundary

Permitted product and test paths:

1. Add `packages/friday-runtime/src/friday_runtime/application_config.py` as
   the single owner of the moved typed application models, parser,
   diagnostics and `load_application_config()`.
2. Edit `packages/friday-chat/src/friday_chat/config.py` into a compatibility
   facade, retaining Chat-specific traceability data and its public loader.
3. Edit `packages/friday-runtime/pyproject.toml` to declare direct
   `pydantic>=2.0` and `pyyaml>=6.0.0` dependencies; update only the resulting
   `friday-framework-runtime` dependency entry in `uv.lock`.
4. Add `packages/friday-runtime/tests_runtime/test_application_config.py`
   for neutral loading, failures, paths, dependency/import isolation and
   no-service-effect tests.
5. Add `packages/friday-chat/tests_chat/test_config_facade.py` for same-object
   re-exports, `__all__`, Chat rule monkeypatching, traceability, legacy
   import/pickle lookup and before/after paired results.

Scoped planning state/evidence may be updated under
`docs/planning/active/friday-tui/`, the TUI task/events in
`docs/planning/board.yaml`, and its generated dashboard. Existing tests are
comparison fixtures; do not rewrite them to make the extraction pass. No
edits to `packages/friday-cli`, Chat CLI/display/runtime/command modules,
`friday_runtime.config.RuntimeConfig`, `friday_runtime.model_library`, other
package metadata, package versions, templates or TUI implementation. If the
work needs another path, change this directive and seek renewed approval
before editing it.

## Public API and compatibility contract

- `friday_runtime.application_config` exposes
  `load_application_config(path: str | Path, *, env: Mapping[str, str] | None
  = None, diagnostic_rules: ConfigDiagnosticRules | None = None) ->
  ApplicationConfig`. It exposes `ApplicationConfig`,
  `ApplicationConfigError`, `ConfigDiagnosticRules`, `ConfigDiagnostic`, the
  section models and the section constants used by Chat. `ConfigDiagnosticRules`
  is a frozen, slot-based value containing `deprecated_keys` and
  `renamed_keys` mappings; it takes read-only snapshots of supplied mappings.
  Omitting it uses the current default key mappings. The neutral module has
  no import of or declared dependency on either frontend.
- Keep one concrete `FridayChatConfig` model and one concrete
  `FridayChatConfigError` exception in the neutral owner, with
  `ApplicationConfig`/`ApplicationConfigError` aliases to those class objects.
  Chat re-exports the same objects under its current names. Preserve the
  existing class names, model fields/defaults/validators and public methods.
  The owning `__module__` changes; old Chat module import and historical
  pickle global lookup must work. Do not claim byte-for-byte module metadata
  identity.
- `friday_chat.config.load_friday_py_config(path, *, env=None)` keeps its
  signature and delegates to `load_application_config()`. Each call constructs
  rules from the **current** Chat module `DEPRECATED_CONFIG_KEYS` and
  `RENAMED_CONFIG_KEYS` dictionaries so replacement monkeypatches and in-place
  mutations affect the next Chat call exactly as before. Keep Chat's current
  `__all__`, and importable `ChatTelemetryConfig`, `FlexibleConfigSection`,
  `ProviderConfig` and `ENV_PATTERN`. Keep `CONFIG_TRACEABILITY` and
  copy-returning `get_config_traceability()` in Chat with existing ownership
  strings. Do not add a neutral-to-Chat import or duplicate the schema.
- Preserve legacy and canonical YAML acceptance, defaults, strict/flexible
  nested validation, diagnostics and their order, safe validation-error text,
  MCP credential-reference checks before interpolation, literal remote MCP
  fields, field-set-sensitive LLM migration, selected model/embedding service
  specs and `allow_env_override=False` for model-library lookup. Supplied
  `env` is used as supplied; omitted `env` reads process environment at load
  time. Unknown top-level fields are diagnosed and removed after recursive
  interpolation. Do not load `.env`, select a runtime mode or add a new
  full-loader YAML size/alias/depth policy.
- Pass the selected runtime path to the model-library loader. Relative
  library paths follow the selected file's resolved target when it is a
  symlink. Leave raw relative memory, transcript, maintenance and workflow
  paths unchanged for later assembly under the captured launch cwd. Neither
  loader creates services, stores, provider clients, a terminal UI or files.
- Preserve error type, message, `__cause__` and `__context__` for the
  characterized missing, malformed, non-mapping, empty, missing-variable,
  typed-validation and canonical-service cases. Native file read/permission
  and Unicode errors currently propagate; do not normalize them here.
  Preserve the current diagnostic/error redaction and the current model
  representation behavior. In particular, resolved service specs stay
  excluded from `repr`; do not claim that all legacy model fields are
  redacted there.

## Construction and verification gates

1. Before edits, rerun or retain the exact synthetic cases and 369-test
   result in the [characterization](../validation/N01A-before-code-characterization.md).
   Freeze the Chat expected typed dumps, diagnostics, resolved spec fields,
   exception shape and symlink target behavior in disposable test fixtures.
   No real provider or credential is needed.
2. Move the implementation once, then compare the neutral and Chat APIs on
   the same legacy, canonical, packaged-example and negative fixtures.
   Include a symlink whose link and target directories have different
   same-named catalogs; pass `FRIDAY_MODELS_CONFIG` pointing to the wrong
   one and prove it is ignored. Check Chat rule replacement and in-place
   mutation, ordered diagnostics, unknown-field interpolation, raw relative
   paths, empty document, native read error, malformed YAML chaining,
   invalid MCP reference before environment access, service spec resolution,
   error redaction and both import/class identities. Assert file inputs are
   unchanged and no provider/store/terminal was constructed.
3. Run the focused suites named in the characterization, all unchanged
   `packages/friday-cli/tests_cli` tests, and the full Chat and Runtime
   package suites. Compare `friday-chat --version`/`--help` and the known
   existing `friday --help` outcome to the baseline; do not repair that CLI
   entry point in this unit. Run Ruff, Mypy, `git diff --check`, board
   validation and dashboard check on the affected scope. A failure or a
   changed baseline needs investigation, not an unrecorded test rewrite.
4. Build the Runtime and Chat wheels; inspect the Runtime wheel's
   `Requires-Dist` for its direct parser/model dependencies and absence of
   Chat/CLI. Install candidates outside the checkout into a disposable
   environment with declared dependencies, then verify that importing the
   neutral module loads no Chat/CLI module and Chat's installed facade
   identifies the same model/error objects. Record any dependency-resolution
   limitation rather than calling a workspace-only import an installed
   closure check. Automate the neutral smoke on Linux as part of the rolling
   cross-platform checks. This loader-only unit has no terminal user UAT;
   macOS/Linux user UAT remains a first-shell and final-candidate gate.
5. Commit a stable candidate only after local checks. Give a fresh-context,
   read-only independent validator the exact directive/authority, candidate
   commit/diff, comparison fixtures and check results. A changed candidate
   needs a fresh review. `VERIFIED` closes only the N01A validation gate;
   it does not accept, publish or release the TUI.

Stop if Chat or `friday-cli` behavior changes, neutral imports acquire a
frontend dependency, old supported serialization fails, the parser's
effective behavior changes, a secret enters diagnostics, direct dependency
closure cannot be shown, or the change needs another source path. Do not
start chooser parsing, UI configuration, service assembly or command work
under N01A.

**Approval fields:** Maintainer approval/date/evidence pending. The current
board and authority manifest remain `design_only` until that approval is
explicitly recorded.
