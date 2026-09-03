# Friday Chat Client Lifecycle Remediation

---
title: Friday Chat Client Lifecycle Remediation
initiative: friday-chat-client-lifecycle
document_type: initiative-index
status: draft
created: 2026-09-03
updated: 2026-09-03
next_gate: reproduce and approve bounded remediation
implementation_authority: not granted
---

## Current State

A live Friday Chat `/exit` produced two unclosed `aiohttp.ClientSession`
warnings after the `0.1.0a2` release. No source remediation has been authorized
or implemented.

## Behavioral Authority

The historical Friday Chat V2 behavioral contract requires intentional
background shutdown and final resource cleanup. The completed task list records
that behavior as tested, so the live warning reopens that acceptance condition.

- [Behavioral contract](../../../archive/completed/2026/friday-chat-v2/friday-chat-v2-behavioral-contracts.md)
- [Completed task list](../../../archive/completed/2026/friday-chat-v2/friday-chat-v2-code-generation-task-list.md)

## Next Gate

1. Reproduce under a controlled live-provider exit.
2. Identify the creator and owner of each client session.
3. Decide whether remediation is Friday Chat-only or needs separate Friday LLM
   or Runtime contract authority.
4. Approve a bounded remediation with regression and live-exit validation.

This packet documents priority and authority only. It does not authorize code
changes from this documentation-remediation branch.
