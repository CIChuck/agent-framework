# Friday Chat user acceptance testing roadmap

Status: executed by Chuck Russell against the corrected DIAG-001 candidate;
maintainer-reported overall **PASS** on 2026-11-09 ([acceptance](../approval/diagnostics-acceptance.md)).
Original preparation status (historical): all cases NOT RUN.
Prepared: 2026-11-08. Intended tester: Chuck Russell.

Use this roadmap after the completed DIAG-001 candidate has passed its automated
tests and independent reviews. It covers the six diagnostics, accepted
help/exit/display/history behavior and the basic interactive Chat experience.
It supports bounded user acceptance; it is not the complete remaining command
family or full-refactor acceptance matrix.

Related documents: [packet index](../README.md),
[DIAG contract](../diagnostics-command-contract.md),
[construction directive](../directives/CD-CMD-DIAG-001-context-diagnostics.md),
[test strategy](../test-strategy.md) and
[current checkpoint](../next-phase.md).

## Before you begin

- [ ] Obtain the candidate's automated test report, independent review results,
  known limitations and exact installed launch command.
- [ ] Use the completed candidate's installed environment, with a disposable UAT
  configuration, memory session and export folder.
- [ ] Record the environment below. Use the same model/configuration and terminal
  when comparing performance with a previous version.
- [ ] For a quick interface pass, fake mode is useful. Assess real conversation
  quality, retrieval integration and model latency with the configured real
  runtime; canned fake responses are not evidence for those checks.

| Run information | Value |
| --- | --- |
| Run ID / date | |
| Tester | |
| Candidate commit / installed version | |
| Comparison version, if any | |
| Installed launch command | |
| Runtime: fake or real | |
| Provider / model | |
| Configuration path | |
| Memory test data / session | |
| Export directory | |
| Telemetry enabled / disabled | |
| OS / terminal / terminal dimensions | |

Commands beginning with `/` below are entered at the Chat prompt. Launch and
restart Chat using the supplied candidate launch command.

**Fresh session** means a newly launched process. **Populated session** means
a session with at least two completed conversational turns. For a repeatable
real-model setup, send:

```text
My test marker is BLUE-OTTER-47. Reply with OK.
What is my test marker?
```

The second answer should identify the marker when testing a real model. Record
conversation-quality failures separately from command or rendering failures.
Cases UAT-05 through UAT-11 may share a populated session. Use a fresh session
when reproducing a failure; run clear and exit cases separately.

## Individual acceptance checklist

- [ ] **UAT-01 — Startup and first impression**

    **Steps:** Launch a fresh session. Inspect the startup display and first
    input prompt before entering anything.

    **Expected:** The configured banner and information appear once, the prompt
    is readable, and the cursor is correctly positioned. No stray escape codes,
    unexplained traceback or startup output obscures the prompt.

    **Look / feel / performance:** Record time from launch to usable prompt.
    Note clutter, spacing, contrast and whether startup feels ready or stalled.

- [ ] **UAT-02 — Conversation and streaming**

    **Steps:** Send the two setup messages. Then request a longer answer, such
    as “Explain the test marker in five short paragraphs.”

    **Expected:** The real-model conversation retains the marker; responses
    appear once with correct speaker labels. With streaming enabled, text
    arrives progressively and Chat returns cleanly to the input prompt.

    **Look / feel / performance:** Record time to first visible response and
    total completion time. Note long pauses, duplicated text or uneven display.
    Compare cold and warmed-up model runs separately.

- [ ] **UAT-03 — Help and discoverability**

    **Steps:** Run `/help`, `/help context` and `/help debug-retrieval`.

    **Expected:** Command grouping, descriptions, usage and arguments are
    readable. Focused help describes the selected command. Literal angle
    brackets and flags remain visible, and long help can be scrolled normally.

    **Look / feel / performance:** Judge whether you can find a command without
    already knowing its syntax. Note excessive wrapping or noticeable delay.

- [ ] **UAT-04 — Conversation history**

    **Steps:** Complete several exchanges, including a multiline response, then
    run `/history`.

    **Expected:** User and assistant messages appear once in chronological
    order, with preserved contents, indentation and line breaks.

    **Look / feel / performance:** Check whether exchanges are easy to scan and
    whether a longer history makes the command or terminal noticeably slower.

- [ ] **UAT-05 — Context display**

    **Steps:** In a populated session, run `/context`, then `/context --debug`.

    **Expected:** Existing context is displayed, and the second command adds a
    character count. These commands do not generate another assistant answer.
    The count describes the base context text, not a token count.

    **Look / feel / performance:** Inspect section boundaries, line wrapping and
    the usefulness of the debug block. Record command response time.

- [ ] **UAT-06 — Prompt inspection**

    **Steps:** After a conversational turn, run `/prompt`.

    **Expected:** The displayed prompt has recognizable configured system and
    user content. It describes the stored last prompt or documented fallback,
    with intact line breaks and no duplicated sections.

    **Look / feel / performance:** Check whether a large prompt remains readable
    and whether the distinction between prompt content and Chat's input prompt
    is clear.

- [ ] **UAT-07 — Debug information**

    **Steps:** Run `/debug` in a fresh session, then again after a conversation.

    **Expected:** An empty state is reported clearly when no information exists.
    Recorded fields have readable labels and values. When execution telemetry
    is available, the last-turn information describes a completed turn.

    **Look / feel / performance:** Note confusing labels, duplicate entries,
    stale-looking information or delay. Missing optional telemetry should not
    be mistaken for a successful telemetry capture.

- [ ] **UAT-08 — Budget information**

    **Steps:** Run `/debug-budget` and compare its values with the UAT
    configuration.

    **Expected:** `context_window` and `output_buffer` reflect the configured
    values. Preserved behavior renders zero or unavailable values as `unknown`.
    This command reports configuration, not a recalculated remaining budget.

    **Look / feel / performance:** Check whether labels are understandable and
    output is immediate enough for routine inspection.

- [ ] **UAT-09 — Timing information**

    **Steps:** Run `/timing` after a short response and again after a longer one.

    **Expected:** Timing labels, seconds and precision are readable and values
    are plausible. These describe conversational turns, not the execution
    time of `/timing` itself. An empty state before a turn is understandable.

    **Look / feel / performance:** Compare the displayed data with your observed
    wait. Record discrepancies without assuming every metric measures the same
    interval as your stopwatch.

- [ ] **UAT-10 — Retrieval diagnostics**

    **Steps:** Run `/debug-retrieval` without a query. Then query a known term
    from the disposable UAT data, such as `/debug-retrieval BLUE-OTTER-47` if
    that marker is present in the prepared retrieval data.

    **Expected:** Missing input produces a usage or specific runtime-availability
    message. A valid query is echoed with a result count and readable previews.
    Count describes all returned snippets; at most ten previews are displayed.
    A prepared no-result case is understandable. No unrelated assistant answer
    is generated.

    **Look / feel / performance:** Record retrieval response time separately
    from local diagnostic commands. Judge preview relevance, truncation and
    whether the output helps explain what was retrieved.

- [ ] **UAT-11 — Context and prompt file exports**

    **Steps:** Run `/context --debug --file` and `/prompt --file`. Open the
    reported files. Complete another turn, repeat the exports and reopen them.

    **Expected:** The configured folder contains `friday_context.txt` and
    `friday_prompt.txt`. Each file matches its displayed body, including the
    context debug block but excluding the export footer. Repeating the export
    overwrites the fixed file with current content. The reported path is usable.

    **Look / feel / performance:** Check encoding, Unicode, line breaks and
    discoverability of the destination. Record export time and unexpected files.

- [ ] **UAT-12 — Clear the display without clearing history**

    **Steps:** In a populated session, run `/cls`, then `/history`. Repeat with
    `/clearscreen`.

    **Expected:** The screen clears cleanly, the input prompt remains usable,
    and conversation history remains available. No replacement conversation
    message is needed to prove the screen was cleared.

    **Look / feel / performance:** Check cursor position, residual screen text,
    flicker and whether you can type immediately afterward.

- [ ] **UAT-13 — Clear conversation history**

    **Steps:** Run `/history`, `/clear`, then `/history`. Send a new message.

    **Expected:** Chat confirms the clear, then reports
    `No conversation history.` New conversation works normally. Screen clearing
    is separate; this case does not require `/clear` to erase terminal output.
    Diagnostic snapshots may still describe the last completed turn.

    **Look / feel / performance:** Judge confirmation clarity and responsiveness.
    This case checks the session-clear procedure, not deletion of every
    persistent store.

- [ ] **UAT-14 — Mistakes and recovery**

    **Steps:** Enter `/not-a-command`, followed by a valid command and a normal
    conversational message. Also revisit the missing-query retrieval case.

    **Expected:** Unknown commands and missing input receive understandable
    responses. Subsequent commands and conversation work without restarting.

    **Look / feel / performance:** Assess whether the message tells you enough
    to recover and whether the terminal remains clean and responsive.

- [ ] **UAT-15 — Layout, Unicode and long text**

    **Steps:** Try accented characters, emoji, multiline pasted text and a long
    response. Inspect `/history`, `/help` and `/prompt` with a narrow and a wide
    terminal.

    **Expected:** Input submission is predictable; supported multiline input
    retains its intended content. No missing text, duplicated prefixes, stray
    escape sequences or misplaced prompt. Resizing leaves output usable.

    **Look / feel / performance:** Record wrapping, spacing, contrast, scrolling,
    paste behavior and any lag. Note the exact terminal dimensions for failures.

- [ ] **UAT-16 — Repeated use and responsiveness**

    **Steps:** In the same populated session, repeat `/help`, `/history`,
    `/context`, `/debug` and `/timing` about ten times.

    **Expected:** No increasing delay, duplicate output, unexplained assistant
    responses or degrading prompt behavior. Each command remains usable.

    **Look / feel / performance:** Compare early and late response times.
    Measure retrieval, exports and model generation separately rather than
    combining them with local display commands.

- [ ] **UAT-17 — Exit and interruption**

    **Steps:** In separate sessions try `/q`, `/quit`, `/exit` and Ctrl+C at the
    input prompt. In another session interrupt one active response.

    **Expected:** Normal exits and idle interruption shut down cleanly and
    restore terminal input. For active interruption, record whether the turn
    cancels or the app exits; either outcome must leave the terminal usable,
    without a hung process or unexplained traceback.

    **Look / feel / performance:** Record shutdown time, confusing exit output
    and whether a clean relaunch succeeds.

## Performance and usability assessment

The following is a **proposed manual UAT target**, not an established benchmark
or construction requirement: local commands with ordinary output should usually
respond in under one second. Confirm or revise that target when the candidate
and baseline environment are available.

Record startup, local commands, retrieval, exports, first visible model response
and total generation time separately. Compare the same model/configuration,
similar data sizes and cold versus warmed-up runs. Large output and provider
latency should be identified rather than silently averaged together.

For look and feel use a simple scale: **1** difficult to use, **3** usable with
friction, **5** clear and comfortable. A score is supporting feedback; it does
not override a functional failure.

## Results register

Leave unchecked cases as **NOT RUN**. For executed cases record **PASS**,
**FAIL** or **QUESTION**; use **BLOCKED** when a prerequisite prevents execution.
A checked box means the case was executed, not necessarily that it passed.

| Case | Status | Look / feel (1–5) | Timing | Finding / evidence |
| --- | --- | --- | --- | --- |
| UAT-01 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |
| UAT-02 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |
| UAT-03 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |
| UAT-04 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |
| UAT-05 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |
| UAT-06 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |
| UAT-07 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |
| UAT-08 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |
| UAT-09 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |
| UAT-10 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |
| UAT-11 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |
| UAT-12 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |
| UAT-13 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |
| UAT-14 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |
| UAT-15 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |
| UAT-16 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |
| UAT-17 | PASS (maintainer-reported) | not supplied | not supplied | Overall maintainer report 2026-11-09; no per-case detail supplied |

Copy this record for each failure, question or detailed observation:

```text
Case / finding ID:
Candidate / run ID:
Status: PASS / FAIL / QUESTION / BLOCKED
Runtime / model:
Setup and exact input:
Expected:
Actual:
Look / feel: 1–5
Elapsed time / measurement:
Repeatable: always / intermittent / once
Screenshot or terminal excerpt:
Area to investigate: interface / command / model / runtime / environment / unknown
Notes:
```

## Acceptance handoff

- [ ] Reconcile all executed, blocked and unrun cases with the automated report.
- [ ] Record functional failures separately from usability preferences and
  performance observations.
- [ ] Reproduce failures and retest any corrected candidate's affected cases.
- [ ] Summarize remaining limitations, questions and deferred improvements.
- [ ] Record the maintainer's explicit bounded acceptance decision separately
  from execution results and independent review scores.

This document records no test success or approval in advance. It does not amend
the proposed contract/directive or authorize implementation, later-family work,
full-refactor acceptance or external delivery.
