# Friday TUI neutral configuration loader contract

**Status:** Implemented as frozen N01A candidate `4a5311f2` under an approved
bounded directive; independent validation BLOCKED on Linux smoke evidence.

**Branch and authority:** `feature/friday-tui`; `granted` for TUI-N01A only

**Original TUI baseline:** `c34269867be50f71923c93c95a63236a35505812`

**Current before-code baseline:** `26f5d090` (N01S identity extraction
independently VERIFIED; no configuration-loader change). The
[N01A characterization](validation/N01A-before-code-characterization.md)
records the current loader's observable behavior.

This is the configuration-loading slice of the [independent TUI plan](replacement-plan.md).
The TUI must use the same Friday Chat runtime files and effective settings
without importing `friday-chat` or `friday-cli` (D-06, D-08). The
[startup contract](startup-bootstrap-contract.md) owns chooser behavior.
Service construction, command effects and resource cleanup need later neutral
contracts; loading a file alone does not make a runnable TUI.

## Before-code source boundary

This table describes the `26f5d090` source before N01A, rather than the
current frozen candidate. Its Chat application loader now delegates to the
neutral Runtime owner.

| Concern | Observed owner and behavior | Consequence |
| --- | --- | --- |
| Chat application YAML | [`friday_chat.config`](../../../../packages/friday-chat/src/friday_chat/config.py) defines the Friday-py-compatible models and `load_friday_py_config()`. It reads one explicit path, validates the MCP reference shape before ordinary environment interpolation, parses the typed sections, emits ordered diagnostics, resolves canonical model-library bindings, and requires either the canonical triplet or legacy `llm.model`. | This is the compatibility baseline that TUI must share through a neutral owner. |
| Headless kernel YAML | [`RuntimeConfig.from_sources()`](../../../../packages/friday-runtime/src/friday_runtime/config.py) merges defaults, YAML, allowed environment overrides and explicit overrides. It has a different allowed-key set, defaults and path policy. | It cannot replace the Chat loader for TUI startup merely because both are in `friday-runtime`. |
| Model library | [`load_model_library()`](../../../../packages/friday-runtime/src/friday_runtime/model_library.py) already lives in `friday-runtime`. Chat calls it with `allow_env_override=False`; a relative catalog path is resolved from the **resolved target** of the selected runtime file. | Keep Chat's catalog, credential and symlink semantics; do not accidentally enable `FRIDAY_MODELS_CONFIG` override through `RuntimeConfig.from_sources()`. |
| Presentation file | [`resolve_display_config()`](../../../../packages/friday-chat/src/friday_chat/display.py) chooses explicit `--cli-config`, otherwise `cli-config.yaml` beside the **supplied path**, otherwise defaults. It activates `friday-cli` display globals. | TUI keeps the file-selection precedence but reads its own `tui:` settings without importing or activating CLI display code. A symlink's presentation sibling is beside the link, while its model library can be beside the target. |
| Live storage and other paths | [`build_runtime()`](../../../../packages/friday-chat/src/friday_chat/runtime.py) captures the process cwd for real assembly. [`resolve_maintenance_layout()`](../../../../packages/friday-chat/src/friday_chat/reorganization/assembly.py) and [`FridayChatMaintenanceLayout.resolve_once()`](../../../../packages/friday-chat/src/friday_chat/reorganization/layout.py) anchor relative maintenance, memory and transcript paths there. | The loader must retain raw path values; the later neutral assembly contract must reproduce the effective paths using the captured launch cwd. |
| Launch mode | [`friday_chat.cli`](../../../../packages/friday-chat/src/friday_chat/cli.py) defaults to fake and lets `FRIDAY_CHAT_RUNTIME` override its flag. D-47 sets a distinct real default for configured interactive TUI startup. | Runtime mode selection belongs to each launcher, outside this YAML loader. Chat's current default and override must remain unchanged. |

The current [configuration reference](../../../../docs/guides/10-configuration.md)
also distinguishes Chat and headless Runtime schemas. Its TUI section and
version metadata require revision with the shipped user guide, not during this
loader-only work unit.

## N01A neutral owner and API

The N01A candidate adds one UI-neutral `friday_runtime.application_config`
module under `friday-runtime`, which already owns the model-library loader.
The public seam is:

```python
def load_application_config(
    path: str | Path,
    *,
    env: Mapping[str, str] | None = None,
    diagnostic_rules: ConfigDiagnosticRules | None = None,
) -> ApplicationConfig: ...
```

`ApplicationConfig` is one typed model, not a second schema copied from Chat.
It retains the currently accepted sections, defaults, strict-versus-flexible
nested validation, ordered `ConfigDiagnostic` values, resolved LLM and
embedding service specs, and model methods used by Chat. A neutral
`ApplicationConfigError` expresses the same load failures. Preserve the
existing concrete class names `FridayChatConfig` and `FridayChatConfigError`
in the neutral owner and expose `ApplicationConfig` and
`ApplicationConfigError` as aliases of those **same class objects**. This
keeps existing Chat type names and exception identity while giving the TUI
neutral import names. Their owning `__module__` changes to
`friday_runtime.application_config`; test old Chat imports and historical
pickle global lookup. A discovered supported serialization dependency on the
old module identity stops the extraction for an explicit compatibility fix.

`ConfigDiagnosticRules` is a frozen, slot-based value with
`deprecated_keys: Mapping[str, str]` and
`renamed_keys: Mapping[str, str]`. Construction snapshots both mappings into
read-only copies, so a caller cannot change a load's rules after passing the
value. With `diagnostic_rules=None`, the neutral loader uses the current Chat
default mappings. The Chat facade builds a fresh rules value on **each**
`load_friday_py_config()` call from its current module-level
`DEPRECATED_CONFIG_KEYS` and `RENAMED_CONFIG_KEYS`. This preserves both
replacement monkeypatches and in-place edits without a reverse Runtime-to-Chat
import. Neither frontend parses warning text to infer diagnostic state.

`friday-runtime` must declare `pydantic>=2.0` and `pyyaml>=6.0.0` as direct
dependencies in its own package metadata; it already declares `friday-llm`.
The lockfile and installed wheel metadata must reflect that closure. The
neutral module must have no frontend import or presentation side effect.

`friday_chat.config` remains a compatibility facade. Existing imports,
`FridayChatConfig`, `FridayChatConfigError`, `load_friday_py_config(path,
*, env=None)`, exported section types, constants and `get_config_traceability()`
must continue to work. Preserve the current `__all__` and the additional
importable `ChatTelemetryConfig`, `FlexibleConfigSection`, `ProviderConfig`
and `ENV_PATTERN` names. The facade delegates without copying the schema or
parser. Re-export the neutral model, error and section classes as the existing
Chat names; the Chat and Runtime imports must identify the same objects. Keep
Chat-specific traceability ownership strings and the copy-returning
`get_config_traceability()` in the facade. Preserve Chat exception messages,
cause/context, diagnostic order and existing public method behavior.

`friday-tui` imports only the neutral API and owns its config-error presentation.
Neither frontend may parse the other's rendered warning/error text to infer
state. The TUI maps typed diagnostics to its own view; Chat retains its current
`Config warning [path]` and `Config error:` behavior.

## Loading and path semantics to preserve

1. The selected runtime path is explicit. The loader performs no automatic
   cwd/home/config-directory discovery, file creation or rewriting. The TUI
   chooser and explicit `--config` route both pass the selected path to this
   same full loader after selection. The separate D-62 startup replay path
   bypasses configured loading and uses an isolated fake replay service.
2. An omitted `env` uses the process environment at load time, as Chat does;
   a supplied mapping is used as supplied, without eagerly reading unrelated
   entries. Ordinary `${NAME}` values are interpolated recursively before
   typed validation, including values in unknown top-level sections. Missing
   names fail loading. Do not implicitly load `.env`.
3. MCP credential references and remote field shape are checked before generic
   interpolation. Streamable-HTTP server fields that are currently literal
   remain literal; enabled connection assembly resolves named credentials
   later. Preserve this order and the absence of secret values in diagnostics.
4. Unknown top-level sections are diagnosed and omitted, not made fatal by
   adopting the headless kernel parser. Preserve accepted legacy and canonical
   YAML, warning order, defaults, field-set-sensitive LLM migration behavior,
   canonical-triplet requirements and selected-service credential resolution.
5. Pass the selected runtime path through to `load_model_library()` so a
   relative `model_library.path` resolves beside the selected file's resolved
   target. For D-60 symlinks, that can differ from the directory containing
   the link. Keep `allow_env_override=False` for this Chat-compatible loader.
6. Preserve raw relative memory, transcript, maintenance and workflow values
   for later assembly. The real assembly path uses the captured launch cwd;
   the loader does not reinterpret these values relative to the config file.
   The presentation sibling lookup uses the supplied config path's parent,
   not the model-library path anchor.
7. Full loading may read the chosen YAML, referenced model library and selected
   environment values, but it creates no provider client, runtime service,
   persistent store or terminal UI. Shallow chooser listing and Refresh must
   remain separate and cannot call this full loader.

The existing full loader uses `yaml.safe_load()` without a new size, alias or
depth limit. N01A must preserve that behavior; adding a new full-loader parser
policy would change Chat. The separately scoped chooser shallow reader needs
its own bounds and symlink/error contract in TUI-N03A.

For this unit, failure categories are the **observed Python outcomes**, not a
new tagged error taxonomy. Missing files, malformed YAML, non-mapping roots,
missing `${NAME}` values, typed validation failures and canonical resolution
failures keep their current `FridayChatConfigError` messages and chaining.
An empty YAML document reaches the existing missing-`llm.model` error. File
read, permission and decoding errors currently propagate as their native
`OSError`/`UnicodeError` subclasses; N01A must not silently wrap them.
Chooser-versus-explicit-path error presentation belongs to TUI-N03A.

Mode selection is not part of this API. Chat retains its existing fake default
and `FRIDAY_CHAT_RUNTIME` behavior. The TUI ignores that Chat-specific variable
for mode selection: configured interactive startup defaults to real and its
own explicit `--runtime fake` selects fake (D-47, D-61). The first-release TUI
has no runtime-mode environment override. Ordinary configuration-value
interpolation and credential lookup through the loader still use the supplied
environment; D-61 changes only launcher mode selection.

## Testable construction slices

| Slice | Work and evidence gate |
| --- | --- |
| C0: characterization | Freeze disposable legacy, canonical and example-file fixtures with explicit environment mappings. Record current Chat load results, model/service specs, diagnostics, exception types/messages, and path anchors before source movement. Include symlinked config with separate link and target directories, unknown/deprecated keys, missing placeholders, invalid MCP references, malformed/non-mapping YAML and missing files. Record that the headless `RuntimeConfig` loader gives a different result for a Chat-only section. |
| TUI-N01A: neutral loader plus Chat facade | Extract one schema/parser into `friday-runtime`, preserve public Chat imports and diagnostic-rule monkeypatch behavior, and compare the neutral result against the frozen Chat fixtures. Assert no `friday_chat`/`friday_cli` imports from the neutral module, no CLI display globals touched, no service/store construction, and no source-file mutation. Run Chat config/CLI and `friday-cli` regression tests. Build/install wheels outside the checkout and inspect declared dependency closure. |
| TUI-N01B: neutral effect/resource primitives | Bound separately by command family; it must not be hidden inside config migration. Check typed effects and Chat/CLI regressions after each change. |
| TUI-N01C: neutral assembly | After required primitives exist, compose real and explicit fake runtime services from the neutral config. Compare effective model/service, storage, workflow, tool, transcript and cleanup behavior on disposable fixtures. Do not substitute `RuntimeKernel` alone for Chat parity; a separate exact directive and failure-injection tests are required. |
| TUI-N03A: launcher/chooser | Full validation calls the neutral loader only after a chosen or explicit path. Check D-47 through D-61 recovery, link and mode-isolation cases; keep the initial candidate check shallow. With `FRIDAY_CHAT_RUNTIME=fake` or an invalid value in the process environment, omitted TUI `--runtime` still selects real; explicit TUI fake still selects fake. Chat's existing override remains unchanged. An invalid chosen file stays in the chooser, while invalid explicit `--config` exits nonzero. |

At before-code revision `26f5d090`, 369 focused Chat, Runtime and
`friday-cli` tests passed. The
[before-code characterization](validation/N01A-before-code-characterization.md)
records synthetic legacy/canonical, error, diagnostic, symlink and parser
observations. These are **before-code** evidence, not verification of an
extraction or TUI. The exact N01A source/test/package boundary and after-code
checks are in [CD-TUI-N01A](directives/CD-TUI-N01A-neutral-config-loader.md),
which is approved for this unit only. The
[local candidate checks](validation/N01A-local-checks.md) and the independent
[BLOCKED report](validation/VAL-N01A-neutral-config-loader.md) leave the
required Linux smoke open. Chooser parser bounds, link-listing policy and
assembly/resource-close interfaces remain later, separately directed units.
