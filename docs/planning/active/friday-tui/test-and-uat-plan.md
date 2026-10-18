# Friday TUI incremental test and UAT plan

**Status:** Superseded unit breakdown; continuous testing and UAT remain required.
No product implementation or UAT execution is recorded here.

**Branch:** `feature/friday-tui`

execution_phase: planning; validation_state: not_ready

The [architecture reset](architecture-reset.md) requires new units for an
independent TUI with no CLI-code dependency. TUI-00A/00B and the old dependency
chain below are withdrawn. Keep command-family scenarios as a test inventory,
not an approved execution sequence. Automated Linux checks run during the build;
hands-on macOS UAT runs at applicable milestone gates, and hands-on Linux
terminal UAT is required on the final candidate before first-release acceptance.

The replacement unit plan must schedule the
[user guide and configuration updates](user-guide-requirements.md) alongside
the behavior they describe. Final UAT must include user execution of the guide's
first-launch, configuration-choice, representative-command and safe-Quit steps
on the installed candidate. Documentation defects block the applicable
acceptance gate just as behavior defects do.

## 1. Test while building

The phases in [build-plan.md](build-plan.md) are milestones, not single batches
of implementation followed by testing. Build one bounded, observable unit at a
time. Its directive must bind exact paths, fixture inputs, expected outputs and
state changes, failure cases, test commands and stop conditions before coding.
If a unit cannot be demonstrated and checked independently, split it again.

For every construction unit:

1. Specify expected behavior and meaningful positive, negative and regression
   cases before implementation. Add a reproducing test first for a discovered
   defect; add tests alongside new behavior rather than postponing them.
2. Build the smallest working path using fake providers and disposable stores.
   Check that path immediately, then add its failure, boundary and state cases.
3. Run focused tests, changed-file Ruff/Mypy and unchanged CLI compatibility
   checks. When shared interfaces or dependencies change, rerun the captured
   241-test source profile; expand it only for the affected contracts. Run prior
   applicable TUI tests at each candidate to catch cross-unit regressions.
4. Freeze the candidate and controlling authority; obtain the repository's
   fresh, read-only independent validation. Record exact commands and results.
   A failing or unverified dependency blocks dependent implementation.
5. Where scheduled below, hand that candidate to Chuck Russell or a user he
   designates for UAT in a real terminal. Record the user's actual result and
   explicit checkpoint approval before passing that UAT gate.

Tests for timing/concurrency must use controlled gates and guaranteed teardown,
not sleeps as proof that work started. Test queue saturation and Quit while
output is backpressured so the worker cannot deadlock waiting for an exited UI.
Include ownership, ordering, exactly-once admission and worker termination.

No unit closes on a command name being registered, a screenshot alone, a broad
test count or a promised later test. Required evidence must exercise behavior.
This planning update executes none of the future tests or UAT scenarios below.

## 2. Testable construction units

The following units propose scope, test boundaries and dependencies. Only the
two TUI-00 units have a drafted exact-file directive today. Every later unit
needs its own approved directive before construction. Existing approval gates
are not waived by this breakdown. All unit results currently remain `not_run`.

| Unit | Demonstrable increment | Tests required before dependent work | Dependency / user checkpoint |
| --- | --- | --- | --- |
| TUI-00A | Pure display configuration reader | Explicit/sibling/default paths; invalid config; fresh values; unchanged CLI config/console identity; current resolver behavior. CD1-01..03 and CD1-09. | G0 approval; no standalone TUI UAT because this is an API. |
| TUI-00B | Public shutdown report | Normal exit, EOF, startup/operation/cleanup failure, cancellation, immutability and per-run reset; unchanged cleanup/exception/telemetry behavior. CD1-04..09; retain 00A coverage. | Verified 00A; no standalone TUI UAT because this is an API. |
| TUI-01A | Installable bootstrap with help/version and fake startup diagnostics | Resources, metadata/internal pins, full workspace dependency resolution, no-service help/version, CFG-01..06 runtime parity plus UXCFG-01..08 presentation-file compatibility, CLI with/without dependency overlay and no global console changes. Enumerate registration/helper changes in its directive. | Verified 00B. |
| TUI-01B | Backend worker and bounded input/output bridges | Runtime constructed/used/closed on owning loop; ordered output; saturation/backpressure; busy rejection retains draft; EOF wakeup; error propagation; no leaked worker or client. | Verified 01A. |
| TUI-01C | First usable editor/conversation shell | Multiline/paste, one accepted submit per action, focus, `/help`, `/history`, `/cls`, idle Quit and startup-failure view through the real adapters with fake runtime. | Verified 01B; UAT-01 before G1. |
| TUI-02A | Session commands (7 canonical) | Equivalent history, variables, clear versus clear-view, aliases and exit effects on fresh fixtures; invalid input. Reuse applicable shell cases. | G1; UAT-02A. |
| TUI-02B | Memory inspection/context commands (12) | Metadata/argument families, diagnostics, context and unavailable-service results; expected session/output effects. | Verified 02A; UAT-02B. |
| TUI-02C | Memory priming/compaction/reset (3) | Disposable before/after stores, scope of each reset option, error paths, admission and no duplicate effects. | Verified 02B; UAT-02C. |
| TUI-02D | Transcript/export/replay commands (5) | Isolated session identity, export formats/content/paths, interactive replay reset behavior, separate startup replay view and invalid files/delays. | Verified 02C; UAT-02D. |
| TUI-02E | File read/ingest commands (2) | Temporary text/table inputs, arguments/limits, missing/malformed input, ingest effects and UI responsiveness during gated slow reads. | Verified 02D; UAT-02E. |
| TUI-02F1 | `/lifecycle` | Existing stats/flush/optimize and execution-intent semantics on disposable stores, progress and failure outcomes. | Verified 02E. |
| TUI-02F2 | `/migrate` | Existing stats/force/execute behavior, resulting state, errors and admission; no developer-store migration. | Verified 02F1. |
| TUI-02F3 | `/reorganize` and recovery | Existing dry-run/execute, stage/skip flags, recovery artifacts and exclusive admission; inject failed stages in disposable fixtures. | Verified 02F2; UAT-02F after all three maintenance units. |
| TUI-02G | Tool commands (6) | Selection/injection/budget/manual execution, JSON/input errors, unavailable capabilities and exactly-once tool effects using local stubs. | Verified 02F3; UAT-02G. |
| TUI-02H | Security commands (4) | Config/inspection/test/injection cases, literal untrusted output and current unavailable/error behavior; no live unsafe tool execution. | Verified 02G; UAT-02H. |
| TUI-02I | Speech commands (2) | Opt-in/mode/provider/voice behavior, fake audio/provider paths, unavailable-service and current `once`/`loop` results. Do not invent looping beyond current handler behavior. | Verified 02H; UAT-02I. |
| TUI-02J | Agent/workflow commands (6), `@agent` and `!` routes | Selection/delegation/status, workflow run/approve/skip, fake runtime effects; preserve disabled-by-default shell behavior. | Verified 02I; UAT-02J before G2. |
| TUI-03A | Streaming/progress during slow work | Ordered chunks/final output, no duplicates, saturation, scroll/edit responsiveness and busy admission; provider fallback/errors. | G2. |
| TUI-03B | Active-operation graceful Quit | Controlled generation/tool/replay/read/ingest/maintenance gates; close admission, finish admitted operation, EOF/cleanup and terminal ownership; repeated/racing Quit. | Verified 03A. |
| TUI-03C | Failure and cleanup visibility | Startup/run/cleanup failures, public outcome mapping, retained failure view, persistence/recovery artifacts and no leaked owned worker/client. | Verified 03B; UAT-03 before G3. |
| TUI-04A | Command extension and discovery | Test-only module registration, help/completion/palette, collision rejection, isolated CLI defaults and unchanged inherited behavior. | G3. |
| TUI-04B | Keyboard/layout polish | History draft retention, focus, copy/literal output, resize/Unicode/scroll and below-minimum Quit; real key delivery on both terminals. | Verified 04A; UAT-04 before G4. |
| TUI-05A | Clean installed candidate and compatibility | Wheel/sdist/resources, full workspace/install checks, internal version pins/docs URL, outside-checkout startup, and CLI with/without TUI on both targets. | G4. |
| TUI-05B | Final acceptance candidate and handoff | Complete AC-01..15 evidence, cumulative regression results, aggregate independent validation, UAT evidence/defect reconciliation and user docs. No new behavior hidden in closeout. | Verified 05A; UAT-05 before G5 completion proposal. |

There are 24 proposed units. TUI-02A..J partition the 50 canonical commands;
F1..F3 are the three maintenance commands. The memory inspection unit contains
the `memory` category except `/prime`, `/compact` and `/reset`, which belong to
02C. The other units follow the categories in
[the registry inventory](validation/command-matrix.json): session; transcript;
files; tools; security; speech; and orchestration plus workflow. Every alias,
argument/choice and additional route remains required in the
[command matrix](command-matrix.md). Construction directives must bind exact
PAR case IDs and may subdivide further; they cannot omit difficult commands.
The [unit-to-case map](validation/test-unit-map.json) assigns each current PAR
row and its aliases to exactly one parity unit, all marked `not_run`.

TUI-01A performs the minimum complete package/registration/dependency checks
when the package is first added. TUI-05A repeats the full installed compatibility
matrix on the finished candidate; packaging is not left untested until closeout.

### Shared runtime configuration parity in TUI-01A

Bind these cases in the startup unit's exact directive. They are future cases,
all `not_run`; the new requirement does not add an independent runtime loader.

| Case | Required observable behavior |
| --- | --- |
| CFG-01 | One unchanged main YAML/model catalog works through both launch adapters using the shared loader/factory, with equivalent typed settings, model/service bindings and storage identity under the same environment/cwd. Record no resolved credential values. |
| CFG-02 | Missing/malformed config, model references and required environment values retain shared validation rules; display the failure before constructing runtime services. |
| CFG-03 | Existing fake/real defaults and `FRIDAY_CHAT_RUNTIME` precedence match; file selection introduces no TUI runtime override or implicit `FRIDAY_CONFIG`/OS-directory lookup. |
| CFG-04 | In two controlled launch directories, absolute configured storage paths retain identity; relative paths match current CLI behavior for each cwd, while model-library paths remain relative to the main YAML. No TUI-only cwd change or rebasing occurs. |
| CFG-05 | Runtime files work without a `tui` namespace in the existing CLI presentation file. Optional namespaced settings affect only appearance/interaction; attempted model, credential, memory-path, service or runtime-mode overrides are rejected by the TUI presentation contract. |
| CFG-06 | Version/replay/configured-startup precedence matches Chat. Startup replay does not load an ignored missing config or reject supplied runtime/display flags; its existing default fake-runtime behavior is retained. |

UAT-01 checks selection/validation of the same files in both frontends; UAT-05
confirms installed startup and durable store identity using explicit absolute
paths from different launch directories on each target. These cases support
AC-14. Automatic discovery or setup requires separate shared-contract approval.

The [accepted existing-file UX extension design](ux-configuration.md) adds UXCFG-01..08:
old-file defaults, added-namespace CLI compatibility, file selection, visible
setting effects, TUI-only schema errors, runtime isolation, pure reads and schema
evolution. Bind parsing in TUI-01A and interaction cases to the widgets as built.
UAT-01 uses unchanged and extended CLI files, UAT-04 checks preference effects
and UAT-05 repeats common-file compatibility in installed environments. All
future TUI settings cases remain `not_run`; existing-loader probes are separate.

## 3. UAT checkpoints and executable user scenarios

UAT means a real user exercises a working candidate in a real terminal. The
builder prepares reproducible steps, isolated fixtures and expected outcomes;
Chuck Russell or his designated user performs and approves the checkpoint.
Headless tests, scripted PTY checks and independent technical review support UAT
but do not substitute for that user's assessment.

At each applicable construction checkpoint, run macOS Terminal.app user UAT and
automated Linux checks, recording actual environments and key settings. Arrange
hands-on Linux terminal UAT on the final candidate before first-release
acceptance. An unavailable required target is `blocked`, not a pass. The revised
plan must bind precise target versions and scenarios before construction.

There are five user approval checkpoints (UAT-01 through UAT-05), with 14
scenario groups below. Every group is `not_run`; none records user signoff.
UAT-02A..J are rolling demonstrations as each command family becomes usable;
record user results during construction and approve the combined UAT-02 at G2.
Internal construction units require automated checks and independent review;
the five milestone gates are the user checkpoint approval boundaries. A blocking
UAT finding stops affected dependent work whenever it is discovered.

| Checkpoint | User actions and observable success | Gate |
| --- | --- | --- |
| UAT-01: first shell | Start fake mode; type and paste a multiline prompt; verify Enter does not submit, F2 and the focused Submit button each submit once; use help/history/clear-view by keyboard; quit and use the restored terminal. Select the same unchanged runtime/presentation files used by the CLI; also try a display-file copy with the proposed tui namespace; repeat with invalid config and inspect the shared validation error before services start. | G1 |
| UAT-02A: session | Set/show a variable; create history; compare `/cls` with `/clear`; discover and run an alias; verify idle `/q` cleanup and terminal restoration. | Rolling UAT-02; signoff at G2 |
| UAT-02B: memory inspection | Inspect memory/context/diagnostics using seeded fixtures; compare displayed results to fixture expectations; try an invalid argument and an unavailable capability without losing the editor. | Rolling UAT-02; signoff at G2 |
| UAT-02C: memory changes | Prime/compact/reset only a disposable seeded store; confirm command scope, actual resulting state and readable failures. Never interpret a visible success message alone as persistence evidence. | Rolling UAT-02; signoff at G2 |
| UAT-02D: transcripts/replay | Select the intended session, export and inspect its file; run interactive replay; launch isolated startup replay and verify its retained result view; try a missing input file. | Rolling UAT-02; signoff at G2 |
| UAT-02E: files | Read/ingest a temporary file with line options; compare result/store content; keep editing/scrolling during a controlled slow read; try an unreadable input. | Rolling UAT-02; signoff at G2 |
| UAT-02F: maintenance | Compare dry-run/stats with explicit execute on disposable stores; inspect before/after results; trigger a controlled failed reorganization and follow its existing recovery path without duplicate execution. | Rolling UAT-02; signoff at G2 |
| UAT-02G: tools | Discover/select/run a local stub tool once; inspect captured invocation/result; enter malformed JSON and an unavailable tool; verify editor and session remain usable. | Rolling UAT-02; signoff at G2 |
| UAT-02H: security | Inspect/change a fixture setting, run deterministic security checks and display injected text literally; compare actual capability/error behavior with the CLI fixture. | Rolling UAT-02; signoff at G2 |
| UAT-02I: speech | Exercise speech controls and both speech-test modes in a prepared fake-service fixture; compare the actual single `speak` invocation with current CLI behavior, then Quit; verify unavailable-provider feedback. This does not claim real microphone/audio/provider acceptance. | Rolling UAT-02; signoff at G2 |
| UAT-02J: orchestration | Select/delegate to a fake agent; run/approve/skip a seeded workflow; inspect backend state; exercise `@agent`, an invalid command and disabled `!` input. | G2 |
| UAT-03: long work and failure | Watch controlled streaming/progress while editing/scrolling; attempt a busy submit; request Quit during each slow-operation family; see pending status, one completed effect and cleanup before terminal release. Inject a cleanup failure, inspect failure/recovery evidence and acknowledge only after worker termination. | G3 |
| UAT-04: discovery and interaction | In an explicitly identified test fixture, discover/use an added command without UI dispatch changes; confirm it does not leak to normal CLI/default builds. Compare dark/light, contrast/motion, editor and output preferences from the same CLI presentation file; use remapped keys and keyboard fallbacks; resize through 120x30, 80x24 and below minimum; verify readable output and reachable Quit. | G4 |
| UAT-05: installed end-to-end | Install identified artifacts in disposable environments outside the checkout on both targets; verify help/version/config and a full conversation → command → export → restart/read → Quit workflow. Use the same runtime files in CLI and TUI from two launch directories with absolute storage paths; confirm identical intended stores and compare normal CLI use before/after TUI installation; review setup/command docs and rerun earlier high-risk scenarios against the final candidate. | G5 |

All 50 commands and their argument families require automated parity evidence;
manual UAT adds representative real-user workflows, destructive-operation checks
and usability judgment. Each checkpoint's prepared script must name exact
commands, fixture paths and expected state/output from its directive. Missing
scripts or unspecified expected outcomes block that checkpoint.

Base UAT uses fake providers and disposable local stores. Before final acceptance,
reconcile each optional integration's claimed support against executed evidence.
If acceptance requires real model/audio/remote-MCP services, obtain the specific
service, cost and state authority and execute that profile; otherwise record the
explicitly accepted limitation. Do not describe fake-service results as live
integration acceptance. Current planning authority authorizes no live UAT run.

## 4. Evidence, defects and signoff

For every automated unit, record its ID, base/candidate commit, authority hashes,
test/fixture profile, command results, protected CLI comparison, independent
review and outstanding defects. Store actual run records under `validation/`.

For every UAT scenario, capture:

```text
checkpoint / scenario ID:
candidate commit and installed artifact hashes (if applicable):
tester and date:
OS / architecture / terminal version / key settings / dimensions:
fixture and runtime mode (no secrets):
exact actions and expected output/state:
actual result and evidence paths:
result: not_run | passed | failed | blocked
defect IDs / affected acceptance criteria:
user checkpoint approval: pending | approved (by whom, when, exact scope)
```

A test pass is not automatically user approval. Failed or blocked required UAT
prevents the associated gate from passing. Record defect reproduction, severity,
affected units and a bounded remediation scope; do not lower expectations to
close the checkpoint. Fix, rerun affected automated/UAT scenarios and revalidate
the changed candidate/authority under repository policy.

Any candidate change requires an impact assessment and a new evidence mapping;
rerun affected UAT rather than carrying prior approval forward silently. Final
UAT must identify the actual final candidate and artifacts. All required cases
must pass, with any residual limitation or deferral explicitly accepted by the
maintainer. No unresolved CLI compatibility, data-loss, duplicate-execution,
unsafe-shutdown or essential-keyboard defect may pass the planned exit criteria.

G5 requires both aggregate `VERIFIED` technical evidence and approved final UAT.
These permit a completion proposal; only the maintainer records final task
acceptance. Neither UAT approval nor technical verification grants publication.
