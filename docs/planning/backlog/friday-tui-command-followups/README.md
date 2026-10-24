# Friday TUI command follow-ups

**Status:** Backlog; no implementation authority

**Date:** 2026-10-22

**Source:** Maintainer review of the [scored command inventory](../../active/command-refactor/command-inventory.md).

The [separate shared-command refactor](../../active/command-refactor/README.md)
migrates the current retained commands with their existing
behavior. A change to command behavior, syntax, or user interaction needs its own
later decision and bounded work item. This packet records those follow-ups; it
does not change the [accepted first-release command matrix](../../active/command-refactor/command-matrix.md)
or the deferred [Friday TUI gate](../../deferred/friday-tui/README.md).
The six selected command retirements are part of the shared command
refactor plan rather than this follow-up backlog.

| ID | Follow-up | Question or review outcome needed |
| --- | --- | --- |
| CMD-F01 | Restore an earlier transcript session through `/sessions`. | Define session activation, context/history restoration, persistence and failure behavior. The current first-release decision only permits listing, inspection and export. |
| CMD-F02 | Reassess Friday's security guardrails and commands. | Map configuration, actual coverage and limits across Core, agent, Chat native tools, MCP, memory and transcript paths; assess `/security`, `/security-config`, `/security-test` and the retiring `/inject-payload` against prompt-injection and malicious-output threats. Decide later whether any retained behavior should change. |
| CMD-F03 | Reassess framework workflows and the `/workflow` command. | Map the current subcommands and flat/canonical execution paths, agent orchestration, approval and state behavior. Decide what complete workflow support should mean before proposing enhancements. |
| CMD-F04 | Consider confirmation for `/clear` and `/reset`. | Define prompts in each interactive frontend, partial/full reset scope, cancel and non-interactive behavior. Preserve current behavior during command migration. |
| CMD-F05 | Repair ingested-source listing and define source validation. | Decide what `/list-ingested` must list from persistent metadata and what validation covers before changing ingestion or listing behavior. |
| CMD-F06 | Improve diagnostic presentation. | Review `/debug-budget` and `/debug-retrieval` readability and minimal interaction without changing their meaning during migration. |
| CMD-F07 | Improve `/tools` presentation. | Retain the current read-only listing during migration; separately design clearer discovery of loaded, valid tools. |
| CMD-F08 | Evaluate explicit file-to-context attachment from a slash command. | Preserve display-only `/read` during migration; decide syntax, attachment lifetime and Chat/TUI scope separately. |
| CMD-F09 | Reassess `/migrate` after the first TUI version. | Retain the current `/migrate` command in the first TUI version. Decide any later retirement against actual storage-migration needs. |
| CMD-F10 | Evaluate command consolidation proposals C-01 through C-06. | Preserve current command names, aliases, syntax and effects during the refactor. Later evaluate the six scored proposals independently, including compatibility for old names and any session-restoration dependency. |

The maintainer asked to disregard the inventory comment about transcript model
identification; it creates no backlog item here. Promotion of any row requires a
separate scoped plan and the ordinary board authority gates.
