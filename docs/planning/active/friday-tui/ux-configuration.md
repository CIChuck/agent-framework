# Friday Chat CLI configuration extension for TUI settings

**Status:** Additive TUI configuration design accepted by Chuck Russell;
implementation and user acceptance testing remain pending.

**Branch:** `feature/friday-tui`

**Design approval:** The maintainer agreed with the suggested extension and
requested documentation alignment. Accepted scope is the existing presentation
file, optional versioned `tui` namespace, preserved CLI fields/behavior and the
UX option families below. D-87 additionally accepts a TUI-only selected-file
OCR language setting; D-94 accepts optional TUI-only per-file and combined
attachment limits with defaults; D-97 fixes omitted values at 4,000 and 8,000
estimated tokens. The YAML is a design reference; exact field
bounds, reader APIs and construction paths are bound by the later implementation
directive. This design approval does not approve CD-TUI-001 or grant product-code
authority. Later features explicitly deferred below remain deferred.

## 1. Extend the existing presentation file

The maintainer specifically identified the existing Friday Chat CLI configuration
file. Keep `cli-config.yaml`, including custom files selected by `--cli-config`,
as the common presentation file. Preserve explicit file → sibling file → defaults
selection. The earlier separate `tui-config.yaml` suggestion is superseded by
this accepted additive design, not adopted as a second preference source.

Preserve all existing root sections and their current CLI meanings:

| Existing section | Current responsibility | TUI mapping |
| --- | --- | --- |
| `theme` | Semantic error/warning/success/info/muted/highlight Rich styles. | Reuse semantic styles where supported; test the mapping to TUI rendering. |
| `icons` | Status symbols. | Reuse with text labels and an optional TUI ASCII fallback. |
| `prompt` | Prompt/name/separator/continuation styles. | Map applicable labels and editor cues; retain multiline editing. |
| `response` | Assistant prefix/name/separator/text styling. | Map response labels/body while preserving stream content and order. |
| `banner` | CLI greeting/art/version/tips. | Preserve values for CLI; use supported title/version cues in a compact TUI header. |
| `spinner` | Thinking/tool messages and animation/style preferences. | Reuse messages/semantic activity cues where applicable; TUI motion can be reduced independently. |

Do not move these fields under a new `cli:` key, rename them, change their
defaults or require users to migrate existing files. The current framework
[`CLIConfig.from_yaml`](../../../../packages/friday-cli/src/friday_cli/cli_config.py)
selects theme/icons/prompt/spinner; the
[Chat display loader](../../../../packages/friday-chat/src/friday_chat/display.py)
also selects banner/response. Both ignore other root keys today. This supports
an optional `tui:` namespace without changing `friday-cli` source. Malformed YAML
still fails under existing file-loading rules; ignored settings must be valid YAML.

## 2. Accepted UX option direction

The maintainer accepted these UX option families as the design direction.
Implement settings alongside their scoped shell/interaction units and tests;
bind exact fields/defaults and validation in their construction directives.
Additional behavior and the later possibilities below remain separate scope.

| Area | Initial design settings | Limits / later possibilities |
| --- | --- | --- |
| Appearance | Dark/light color scheme for TUI chrome, distinct user/Friday role accents, high contrast and reduced motion. | Role labels and other cues remain visible without color; shared semantic styles retain their meaning. Do not promise automatic terminal-theme detection. |
| Layout | Sidebar visibility/preferred width, editor height and status detail. | Clamp preferences to available size; preserve the 80x24 minimum and responsive collapse rules. Activity is inline within its exchange or tool-command entry, collapsible and internally scrollable on narrow terminals; a new prompt does not auto-collapse older Activity sections. No persistent Activity side pane is a first-release option. Other pane arrangement/persistence can follow later. |
| Editor | Soft wrapping, visible line numbers, tab width. | `Enter` submits, `Ctrl+Enter` inserts a newline and paste never submits automatically. Draft/history persistence is later opt-in scope. |
| Keybindings | Submit, insert newline, help, palette, history, clear-view and graceful Quit. | Detect collisions/reserved editing keys and test actual terminal delivery. There is no second default newline shortcut when `Ctrl+Enter` is unavailable; the focusable Insert newline control is the fallback. Quit always follows safe lifecycle; focusable Submit and Quit controls remain reachable. |
| Output | Markdown display, code wrapping, follow-latest only when at bottom, rendered-history cap, optional timestamps and reasoning visibility. | The latest accepted prompt stays pinned above its scrolling answer, hides during older-history browsing, and returns at the bottom. A visible clickable and keyboard-focusable `Jump to latest` control returns the conversation to the bottom and resumes following. Activity opens on its first entry, then respects user collapse until reopened; its collapsed header counts newly appended entries since collapse, resetting on reopen or display clear, and indicates eviction when applicable. Expanded Activity follows only at its own bottom; its separate `Jump to latest Activity` control or scrolling back down resumes following without moving the conversation. These defaults are not new settings. `reasoning_visibility` sets the startup view; an in-app toggle changes subsequent events without rewriting config or retaining earlier hidden text. Activity is in-process only; neither view changes transcripts, model context, generation or runtime retention. |
| Discovery | Completion on typing, alias/category visibility and palette search preferences. | Selecting a `/` command in the palette fills and focuses an empty editor without executing it. With an unsent draft, ask before replacement; cancel retains it exactly and confirm replaces it without submission. All registered commands remain available through prompt/help; UX preferences cannot enable tools or change command authorization. |
| Status | Optional model-route/maintenance detail and elapsed-time presentation when public events supply it. | Busy, pending Quit and failures stay visible. No new polling of private runtime state or telemetry enablement. |
| Accessibility | Text labels, ASCII symbols, high contrast and reduced motion. | Essential workflows remain keyboard usable and status never depends on color alone. |
| Attachments | Tesseract OCR language codes for PDFs selected in the TUI; default to English. Optional per-file and combined attachment limits with fixed defaults of 4,000 and 8,000 estimated tokens, respectively. | `tui.attachments.ocr_languages` is a proposed list of installed language codes, default `[eng]` (D-87). Validate its shape in TUI configuration; check pack availability when OCR is needed. A missing pack fails that attachment with an actionable error and no silent fallback. D-94 adds two optional, typed limits under `tui.attachments` that govern only D-92/D-93 selected-file admission; D-95 sets estimated tokens as the unit; exact field names, estimator/headroom and allowed override bounds await the construction contract; D-97 fixes omitted values at 4,000/8,000. This does not configure runtime services or change Chat/CLI file commands. |
| Notifications | Later opt-in terminal bell for completion/failure. | No notifications per stream chunk; native desktop integrations require separate scope. |

These settings change TUI presentation, interaction, selected-file OCR or
attachment admission. OCR languages and attachment limits affect only files
selected in the TUI; they do not change Friday runtime configuration. Runtime
models, credentials,
memory paths, provider timeouts, maintenance schedules, tool/MCP enablement,
security policy stay in the runtime configuration. Runtime mode is a launcher
choice: after a config is selected, the TUI defaults to `real` unless
`--runtime fake` is explicit (D-47). It is not a `tui:` presentation setting,
and this TUI default does not alter either CLI.
Settings such as history limits below apply only to rendered UI content, not
session history sent to the model or persistent memory/transcripts.

The [reasoning display option](reasoning-display-requirement.md) is required in
the first TUI release. Its `tui.output.reasoning_visibility` setting defaults
to `hidden` and must not be confused with runtime model-reasoning controls.
The first-release in-app toggle changes only later reasoning events and does
not save a preference or make previously hidden text available.
The pinned prompt is a layout behavior, not a second stored message. Leaving
the bottom pauses following; browsing older exchanges also hides the pin,
while reading its own response keeps it visible. Returning to the bottom by
scrolling or activating `Jump to latest` restores it when a prompt exists and
resumes following. This behavior adds no new configuration field.
The conversation rendered-history cap evicts on-screen messages only. Its
notice directs users to `/transcript` when saved messages are available and
reports honestly when they are not; it adds no `Load older` control. Activity
has separate bounds, and transient Activity/reasoning cannot be recovered
from transcripts.

## 3. Example additive shape

This design reference illustrates the accepted additive shape for a future
extended `cli-config.yaml`. Existing sections remain at the root exactly as
today; the example shows only representative ones. Implementation is pending.

```yaml
theme:
  error: "bold red"
  warning: "bold yellow"
  success: "bold green"
  info: "bold blue"
  muted: "dim"
  highlight: "bold cyan"

response:
  prefix: true
  name_style: "bold bright_green"
  separator_style: "bright_green"
  text_style: "bright_green"

tui:
  schema_version: 1
  appearance:
    color_scheme: dark
    high_contrast: false
    reduced_motion: false
  layout:
    sidebar_visible: true
    sidebar_width: 28
    editor_height: 5
  editor:
    soft_wrap: true
    line_numbers: false
    tab_width: 4
  keybindings:
    submit: enter
    insert_newline: ctrl+enter
    quit: ctrl+q
    command_palette: ctrl+p
  output:
    render_markdown: true
    wrap_code: false
    auto_scroll: when_at_bottom
    max_rendered_messages: 500
    reasoning_visibility: hidden
  discovery:
    completion_on_typing: true
    show_aliases: true
  attachments:
    ocr_languages: [eng]
```

`tui` absent means TUI defaults; an existing CLI file works without additions.
The example omits the two accepted attachment-limit fields until their exact
names are bound. D-95 fixes their unit as estimated tokens; D-96 makes omitted
defaults model-independent; D-97 sets them to 4,000 per file and 8,000
combined.
The finished configuration guide must show both fields with valid values and
defaults before release.
When present, the accepted namespace declares `schema_version: 1`; TUI defaults
fill omitted supported options. TUI-specific values take precedence only for
their own TUI-owned properties. They do not overwrite shared semantic
styles or introduce runtime defaults. Existing root settings still drive
applicable semantic colors, icons, labels and activity messages.

The proposed `tui.attachments.ocr_languages` defaults to `[eng]` and selects
one or more Tesseract language packs the user installed separately. The TUI
validates the setting's shape when loading configuration and checks requested
packs when OCR is needed. Missing packs yield a named attachment error, not a
silent English fallback; embedded-text and other file attachment remain usable.
The exact allowed-code syntax and bounds belong to the OCR construction
directive.

The two attachment limits are optional TUI-only fields with defaults
(D-94). D-95 sets estimated tokens as their unit. D-96/D-97 keep omitted
defaults fixed at 4,000 per file and 8,000 combined across providers and
models, even when context-window metadata is known; explicit valid values
override them. Exactly-at-limit content is admitted; larger content is
rejected. Exact names, estimator, headroom and allowed override bounds remain
contract work. The TUI must validate them
before runtime services start, then apply custom values only to
selected-file admission under D-92/D-93; it must not alter model limits,
runtime configuration or CLI file-reading behavior. D-98/D-99 add a separate
budget check for every assembled conversational model request, with one
eligible older-turn compaction recovery attempt. This uses the existing
runtime `memory.compaction.enabled` and service configuration; the TUI adds
no new compaction setting and does not enable it implicitly. Compaction may
make separate model calls and persist memory changes.

Root `theme` defines semantic text styles; `tui.appearance.color_scheme` selects
TUI background/chrome. High contrast is a view adaptation that must preserve
status distinctions and report unsupported style mapping once at startup.
Legacy banner art or a CLI spinner may have no literal widget equivalent;
preserve CLI behavior and document the TUI mapping. Do not silently claim identical
rendering across the two UX environments.

## 4. Loading, validation and ownership

- Keep the current CLI activation resolver's API, values, side effects and
  errors unchanged. CLI ignores the additional `tui` namespace, including
  well-formed YAML whose TUI-only values it does not understand.
- The TUI reads the same selected presentation file through its own parser or a
  UI-neutral configuration contract. It must not import Chat or CLI loaders or
  activate CLI globals. Bind its exact API and startup error handling in the
  replacement construction plan. The former Chat pure-reader proposal and
  CD-TUI-001 are withdrawn.
- Validate the TUI namespace's schema version, keys, types, enum values, numeric
  bounds and keybinding conflicts. Reject unsupported versions or runtime-setting
  injection actionably before runtime service construction. Do not impose this
  new TUI validation on existing CLI startup.
- Validate the OCR-language list's type and syntax as a TUI-only field. Check
  installed language-pack availability only when an attachment needs OCR,
  so the rest of the TUI remains usable without those packs.
- Validate omitted/default and custom attachment limits, including type and
  numeric bounds, as TUI-only fields before runtime services start. Invalid
  TUI values produce actionable TUI errors while the CLI ignores those valid
  YAML fields as it does other `tui` settings.
- Separate namespaces let a CLI user carry TUI settings without loading Textual
  or changing the CLI. New TUI fields receive typed defaults and behavior tests;
  incompatible TUI schema changes require explicit version/migration design.
- Loading never rewrites the file. Future preference editing/saving must be an
  explicit user action, preserve unrelated root/namespaced content and comments,
  handle concurrent file changes and use an atomic write; it is outside the
  current construction scope. Do not mutate installed templates or user files
  during startup.

## 5. Tests while building and UAT

Bind parsing cases in replacement unit TUI-N03A and visible widget effects in
their owning UI units; preserve CLI regression tests. All future cases below
remain `not_run`.

| Case | Required evidence |
| --- | --- |
| UXCFG-01 | Existing files without `tui` retain the same CLI values/rendering and produce documented TUI defaults. |
| UXCFG-02 | Adding the example `tui` section preserves CLI theme/icons/prompt/spinner/banner/response values and rendered output; CLI imports no Textual/TUI code. |
| UXCFG-03 | Explicit/sibling/default selection is unchanged; both frontend readers use the intended common file. No separate TUI settings lookup or override file is introduced. |
| UXCFG-04 | Supported TUI settings have visible tested effects. Exercise layout collapse, `Enter` submit, `Ctrl+Enter` newline where delivered distinctly, focusable action fallbacks, multiline paste without submit and safe remapping through actual UI interactions; physical macOS/Linux terminal UAT distinguishes event simulation from delivered keys. Also exercise output cap with an older-message eviction notice and saved/unavailable transcript cases, pinned latest prompt over its scrolling response, pause following when away from bottom, pin hiding during older-exchange browsing, clickable and keyboard-focusable `Jump to latest`, return-by-scrolling and resumed following, hidden/shown reasoning and its forward-only in-app toggle with provider-exposed text, user/Friday role-color distinction in dark/light/high-contrast modes, discovery and accessibility. |
| UXCFG-05 | Invalid TUI types/keys/version and binding collisions give actionable TUI errors before services start; existing CLI still ignores that valid-YAML namespace. Malformed YAML preserves the current whole-file failure behavior. |
| UXCFG-06 | Presentation settings cannot override runtime/model/credential/storage/security or destructive-command behavior. Render limits do not change persisted transcript/memory or backend history. |
| UXCFG-07 | Pure reads preserve CLI config/console identity and never rewrite files; repeated loads return fresh typed values and leave existing templates/config unchanged. |
| UXCFG-08 | Missing/partial namespaces apply deterministic defaults; extension registration/discovery continues to work; unsupported legacy style mappings are diagnosed without per-chunk warning noise. |
| UXCFG-09 | Omitted OCR-language setting selects English; a valid list of installed languages reaches Tesseract for selected-file OCR. Invalid type/syntax is a TUI configuration error; unavailable requested packs fail OCR attachment by name without silent fallback. Existing CLI ignores this valid-YAML `tui` field and retains its original behavior. |
| UXCFG-10 | Omitted per-file and combined attachment-limit settings use typed defaults of 4,000 and 8,000 estimated tokens, respectively; valid custom values change only TUI D-92/D-93 admission outcomes. Count complete formatted model-input text, including labels/OCR/formulas, with deterministic estimator boundary tests. Omitted limits yield those same values and admission outcomes across different or unknown model context metadata; switching models does not recalculate them. Test below/at/above 4,000 and 8,000 with a deterministic estimator; D-98/D-99 gate a whole conversational request and permit one eligible runtime-configured older-turn compaction attempt before a final overage result. Invalid type/range fails TUI configuration before runtime services start. The same valid-YAML file leaves CLI configuration, reader behavior and runtime model limits unchanged; neither frontend rewrites it. Installed macOS/Linux checks confirm the documented defaults and custom values. |

The [replacement plan](replacement-plan.md#4-verification-and-uat-gates)
controls the UAT schedule. The first-shell macOS UAT checks one unchanged
CLI file and one extended copy through both frontends. Later macOS UAT
exercises dark/light/contrast/motion, layout, multiline/paste, remapped keys,
fallback controls, scrolling, discovery and readable status. Final installed
UAT repeats those workflows on macOS and Linux. Automated configuration
parsing alone is not UX acceptance.
