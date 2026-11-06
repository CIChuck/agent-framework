# Friday TUI vision

**Status:** Proposed vision for maintainer review; it does not change the accepted requirements or authorize another construction unit.

**Date:** 2026-10-19

**Initiative:** Friday TUI on `feature/friday-tui`

## Purpose

Friday TUI will make Friday's existing capabilities practical to use in a sustained terminal session. A person should be able to ask Friday for help, see its answer and the work leading to it, use `/` commands, change the active conversational model, and recover from problems without leaving the application. The TUI is an additional way to use Friday, with room for its own commands and richer interactions over time.

The governing product question for each proposed work unit is: **What can a person do or understand in the running TUI after this work that they could not before?** Shared-service work is justified by a specific user workflow or compatibility need, then demonstrated through that workflow. A package that only starts and draws a screen is a construction milestone, not this product.

## Problem statement

Friday already has a maintained conversational command surface, runtime configuration, sessions, tools, and other services. It lacks an independently installed terminal interface that brings these capabilities together in a navigable, inspectable workspace while preserving the existing CLI applications.

The TUI effort has spent substantial time on preparatory service and transcript work while the installed TUI remains a [no-backend shell](../validation/N03A-01-local-checks.md): it does not yet connect to Friday or run `/` commands. The vision re-centers subsequent planning on a complete user journey while retaining the [accepted decisions](../decisions.md) and [existing PRD](../README.md).

## User pain and opportunity

A line-oriented interface makes long responses, command discovery, selected context, and multi-step agent activity harder to follow in one place. Users need to distinguish their prompt from Friday's answer, know when a requested tool actually ran, and see what Friday is doing across internal steps without mistaking a tool request for execution or confusing provider reasoning with the final answer. They should also be able to change the active conversational model between turns instead of relaunching Friday. A full-screen terminal experience can make those distinctions and controls visible while keeping the speed and reach of `/` commands.

## Target users and operators

- **Primary:** People who use Friday in a terminal for conversations, files, and commands, including current Friday Chat users who want the same capabilities in an easier-to-navigate interface.
- **Operators:** People who select Friday's existing runtime configuration, change the active conversational model while idle, monitor activity, diagnose failed operations, and shut down safely.

## Vision statement

**Friday TUI is a standalone, terminal-native home for working with Friday: one readable, interactive place to converse, run and discover `/` commands, add file context, inspect agent and tool activity, change the active conversational model between turns, and remain in control of the session. It uses Friday's existing runtime and configuration while preserving the behavior of Friday Chat and `friday-cli`.**

## Desired outcomes

<a id="v-01"></a>
### V-01 — A complete Friday conversation in one screen

A user starts with an existing runtime configuration, enters or pastes a multiline prompt, receives Friday's response, and continues in the same session. The editor, conversation, context, actions, and status have distinct roles. User and Friday entries have color cues and explicit labels. The latest accepted prompt can remain visible above its scrolling response; browsing older history never forces the view back to the bottom, and a visible `Jump to latest` control restores it.

<a id="v-02"></a>
### V-02 — Commands are first-class and can grow

The user can type, discover, review, and submit the maintained Friday Chat `/` commands and aliases in the TUI, with the same command implementation, effects, errors, and state changes. Friday Chat and the TUI use one UI-neutral command engine; each presents its results in its own interface. The TUI may add its own commands or richer interactions later. Its command experience must not depend on importing or running either CLI package.

<a id="v-03"></a>
### V-03 — The conversational model can change between turns

The user can see and change the active conversational model from within the TUI without relaunching or hand-editing configuration files. The chooser lists `kind: chat` profiles from the loaded `models.yaml` in file order, including eligible profiles not already bound to another service; it excludes embedding profiles and ad hoc provider/model IDs. A change is allowed only while idle, lasts only for this TUI run, and affects future turns of the active conversation, leaving admitted work and other Friday services unchanged. A choice rejected during selection leaves the previous model active; if a provider request through a newly selected model fails, the TUI reports the error and restores the previous model for future turns without resending the failed prompt. Other live runtime-setting controls are outside the first full release. Explicit model selection is distinct from appearance and layout preferences.

<a id="v-04"></a>
### V-04 — Friday's work is understandable while it happens

The user sees ordered, in-process Activity across model steps and actual tool execution, including parameters passed, actor, and status. A request rejected before execution is clearly `Not run`; automatic tool-result payloads are not dumped into the conversation. Optional display of provider-supplied reasoning is available in the first release, separate from the final answer and hidden by default. The interface does not invent reasoning when a provider supplies none.

<a id="v-05"></a>
### V-05 — Context is deliberate and visible

The user can browse and select supported files, see what is attached, remove or refresh them, and know when extraction fails. Selected content, including supported document formats and scanned-PDF text through Tesseract, reaches Friday's next eligible model turn; a filename alone is not an attachment. The TUI distinguishes temporary selected-file context from Friday memory and persisted transcripts.

<a id="v-06"></a>
### V-06 — The user stays in control

Essential workflows work from the keyboard, with visible pointer-accessible controls where specified. Submitting, inserting a newline, scrolling, help, command discovery, errors, recovery, and graceful Quit have predictable behavior. Provider/runtime failures preserve a recoverable initial prompt without losing a newer draft; after executed tools, they leave a truthful incomplete turn and its completed effects visible. A stalled operation has a separate, warned Force quit path; normal Quit waits for a safe stopping point and cleanup.

<a id="v-07"></a>
### V-07 — Friday compatibility and configuration continuity

The TUI is independently installable and uses Friday's existing runtime files, service behavior, and storage interpretation. It does not depend on Friday Chat or `friday-cli`; both existing applications retain their current behavior. TUI-only presentation preferences and explicit live runtime actions remain separate so changing the interface cannot silently change Friday's runtime policy.

<a id="v-08"></a>
### V-08 — A usable, verified release

People can install and operate the TUI on macOS and Linux using a user-oriented guide and configuration reference. Automated checks, hands-on terminal UAT, and a controlled real-provider/tool run demonstrate the shipped behavior. A shell or isolated technical component is a milestone, not release acceptance.

<a id="v-09"></a>
### V-09 — Startup replay remains usable

A user can request Friday's existing file-based replay at TUI startup, inspect a clear success or failure result, and quit without entering an interactive conversation. This separate startup route preserves the accepted read-only result and error behavior while interactive `/replay` remains a maintained slash command.

## Observable success criteria

- An installed `friday-tui` starts on supported macOS and Linux terminals with the same Friday runtime files and service interpretation as Friday Chat, offers an existing-file chooser when no runtime path is given, and makes its active mode and startup failures clear. Its presentation preferences extend the common `cli-config.yaml` through optional TUI settings without changing existing CLI settings or defaults.
- In an installed run, a person can select a real runtime configuration, submit a prompt, see Friday's answer in the conversation, and use the same active session for subsequent prompts and commands. A no-backend screen or fake-only demonstration does not meet this criterion.
- In that running session, a person can inspect and change the active conversational model from loaded `kind: chat` profiles while idle. The TUI confirms the effective choice; future turns of the active conversation use it without a relaunch, while other model bindings remain as configured. A rejected selection leaves the previous choice active; a provider request failure through a newly selected model restores the previous choice for future turns, shows the error, and leaves deliberate retry to the person. Busy-time requests do not queue or alter admitted work, and a relaunch returns to the configured model.
- Every command and alias in the maintained [command baseline](../command-handoff.md#command-matrix) runs through the shared command implementation and has tested TUI behavior for valid input, invalid input, relevant unavailable services, results, and effects. A name appearing in help is not enough. Changes to the shared command set are tested through both frontends, while TUI-only commands can be added independently.
- A representative multi-step tool run shows ordered Activity that distinguishes requested, running, completed, failed, and rejected-before-run work; it shows the actual arguments passed, keeps automatic tool results out of chat, and presents any provider-supplied reasoning separately when the user enables it. The final answer remains readable.
- Representative text, PDF, DOCX, and XLSX selections supply real extracted content to a model turn; scanned PDFs use the documented Tesseract prerequisite. Attachment failures are visible and do not silently add incomplete content.
- Keyboard and pointer interaction, scrolling, resizing, safe Quit, failure recovery, and terminal restoration pass automated checks and hands-on macOS and Linux terminal UAT. A controlled installed run with a real provider and executing tool is part of first-release acceptance.
- Existing Friday Chat and `friday-cli` behavior and standalone installation remain unchanged with and without the TUI installed. The shipped TUI has a user-oriented guide and updated configuration guidance verified against its actual behavior.
- Startup `--replay FILE` shows the accepted read-only file/count result or actionable file/error result until Quit, with no interactive session or in-process retry.

These are product-level release outcomes. The [vision-traceable PRD](../prd/README.md) groups them; detailed accepted cases remain in the [parent requirements](../README.md), [screen proposal](../screen-layout.md), [reasoning requirement](../reasoning-display-requirement.md), [Activity requirement](../tool-activity-requirement.md), and [guide requirement](../user-guide-requirements.md).

## Non-goals

- The TUI does not replace, refactor, or change the current `friday-cli` feature set or behavior. Friday Chat is the command-parity reference, not a TUI dependency or backend.
- The TUI does not create a second runtime configuration dialect or use appearance and layout settings to change model, memory, tool, credential, storage, or security policy. Explicit in-session model selection has its own validated behavior and visible effect. The first full release has no active-workspace switch or additional live runtime-setting editor.
- The first release does not treat a partial command set, static shell, or infrastructure-only package as a complete TUI. Conversely, future TUI-only `/` commands need not be added to Friday Chat or `friday-cli` by default.
- Provider reasoning visibility does not cause the provider to produce reasoning, and a token count is not reasoning text. Activity is an in-process view, not a new transcript or export format. Automatic tool-result payloads are not part of the scrolling conversation.
- Browsing a file does not edit it, ingest it into memory, or switch transcript sessions. The optional `!<command>` shell route is deferred from the first full release; launcher flags, including startup replay, are separate surfaces from the `/` command growth goal.

## Assumptions

- The initial experience is for one person operating a local terminal session. Multi-user or remote-session needs have not been established and should be evaluated separately if they become a target use case.
- Reasoning text availability is outside the TUI's control; assume a provider may expose text, a token count, or neither. The TUI can offer visibility over text actually supplied but cannot promise its availability for every model.

## Constraints

- The [accepted decision register](../decisions.md) remains the first-full-release scope unless the maintainer explicitly revises it. Full maintained-command parity, Activity, optional reasoning display, selected-file context, live conversational-model selection, startup replay, and user documentation remain release requirements even when delivered through smaller milestones. D-110–D-122 settle the live-control, failure-recovery, staging, replay, shell-route, and UAT questions; D-123 requires a single shared command implementation; D-121 supersedes D-115.
- The TUI is an independently installable package. It neither imports nor depends on `friday-chat` or `friday-cli`; maintained commands and other shared capabilities are supplied through UI-neutral Friday packages. Existing CLI packages continue to operate without the TUI installed.
- The same runtime configuration files, service behavior, and storage interpretation must work across Friday Chat and the TUI. TUI-only presentation settings may extend the common CLI presentation file without changing its existing meanings or defaults. In-session model selection must use explicit Friday runtime capabilities and must not silently rewrite the shared configuration files or change either CLI's behavior.
- macOS Terminal.app on arm64 and Ubuntu 24.04 GNOME Terminal on x86_64 are the physical first-full-release UAT targets. Test the full layout at 120×30, minimum usable layout at 80×24, and below-minimum resize with Quit reachable. Actual `Ctrl+Enter` delivery varies by terminal; a visible Insert newline control is required where the shortcut is unavailable. Tesseract is separately installed when scanned-PDF OCR is needed. The accepted screen behavior and hands-on UAT remain release gates; a construction milestone cannot waive them.
- No calendar release date or broader platform commitment has been accepted. Preview alphas may deliver tested subsets with honest scope labels; a later first full release must meet the complete accepted baseline. An integrated startup-to-answer milestone should provide early evidence of user value, but it is not full-release acceptance.

## Security and governance considerations

The TUI must preserve Friday's existing tool authorization and runtime security decisions; showing a control or Activity entry grants no new execution authority. The accepted first-release Activity view shows tool parameters as passed without TUI-specific sensitive-value filtering, within explicit display bounds. Shown reasoning and Activity remain bounded, transient UI state rather than being added to normal transcripts, exports, memory, telemetry, or logs by default. User-facing documentation should explain what a shared or recorded terminal may expose. Work-unit approval, independent validation, UAT, and maintainer acceptance remain separate gates under the repository lifecycle policy.

## Testability implications

Each construction increment should have an observable user behavior, a failure or recovery case, and regression evidence for affected Chat and `friday-cli` paths. The first meaningful integrated milestone is **choose a valid configuration → start Friday → submit a prompt → see a response through Friday's runtime → quit safely** in the installed TUI. A following end-to-end milestone should change the active conversational model while idle and prove its effect on a future turn without disturbing other services. Command families and the accepted interaction, Activity, reasoning, and file-context requirements can then be demonstrated in bounded user workflows. Headless tests and automated Linux checks support these milestones; physical terminal UAT and a real-provider/tool run remain necessary for full-release acceptance. Bind the exact provider and executing tool at a pre-UAT gate. The current shell's physical macOS UAT is still open.

## Phase boundaries

- **Current shell:** Proves installation and basic terminal controls only. Its physical macOS UAT remains open; it is not a working Friday session.
- **Next integrated milestone:** Prove the startup-to-answer journey through Friday's runtime in the installed TUI. This is the first user-visible capability, not first-release completion.
- **Next live-model milestone:** Change the active conversational model while idle in a running session, then verify its effect on a future turn and both selection and later provider-failure behavior.
- **Preview alphas:** Deliver tested, labeled subsets under a separate phase plan; each preview states what is implemented and does not claim full-release acceptance.
- **First full release:** Meet all accepted command-parity and experience requirements, including live conversational-model selection, startup replay, compatibility checks, user documentation, and macOS/Linux UAT. Bind the real provider/tool before final UAT. Later TUI-only `/` commands and other enhancements remain separately scoped work.

## Risks

- The accepted first-release scope is large. Without user-visible milestones, service extraction and detailed edge-case design can consume effort without producing a useful TUI.
- Migration from Chat-owned handlers to a shared command engine could change Chat behavior or leave frontend state/effects inconsistent. Characterize each command before extraction and test the same implementation through both frontends; name-only registration or matching output text cannot prove parity.
- Terminal behavior differs across platforms and applications, especially key delivery, paste, mouse interaction, resize, color, and recovery after failure.
- Showing unfiltered tool parameters can expose sensitive values to anyone who sees or records the terminal. Transient display limits and clear documentation matter.
- A provider may omit reasoning text, and some runtime events needed for truthful Activity may not yet be available through UI-neutral services. The TUI must report what actually happened rather than infer it from display text.
- Model changes can affect provider availability and context limits. Implementation must uphold the settled idle-only, future-turn fallback rules and distinguish rejected selection from a provider error after selection, without automatically resending a failed turn.

## Open questions

No unresolved product-scope question blocks this vision draft. Friday Chat's `/set` only changes scoped variables, so slash-command parity alone does not provide live conversational-model selection. The exact real provider and executing tool remain to be bound at the accepted pre-UAT gate. The separate phase plan must map tested preview alphas to requirements without diluting first-full-release acceptance.

## Recommended next review

Review the [vision-traceable PRD](../prd/README.md) against the settled
model-selection behavior, startup replay, and deferred shell route. Keep accepted
decisions unless explicitly changed. Once the PRD is accepted, revise the
[replacement plan](../replacement-plan.md) around user-visible, testable
milestones. The first revised milestone should prove an installed end-to-end
Friday conversation, followed by live conversational-model selection. This proposed vision
itself grants no code, push, release, or acceptance authority.
