# FridayV2 Framework Upgrade Log

This document records framework package changes discovered while building
FridayV2. During the first FridayV2 parity pass, existing framework packages are
frozen so FridayV2 can be compared against the reference CLI at
`tests/integration/memory/friday.py` without moving the baseline.

## Freeze Directive

FridayV2 must be implemented as an app layer over the existing framework
packages. Do not modify existing framework package source or tests during the
FridayV2 parity implementation pass.

Frozen packages:

- `packages/friday-agent`
- `packages/friday-cli`
- `packages/friday-core`
- `packages/friday-finance`
- `packages/friday-llm`
- `packages/friday-mcp`
- `packages/friday-memory`
- `packages/friday-moltbook`
- `packages/friday-runtime`
- `packages/friday-sandbox`
- `packages/friday-speech`
- `packages/friday-telemetry`
- `packages/friday-tools`
- `packages/friday-transcript`

Allowed implementation targets:

- `packages/friday-chat/`
- `packages/friday-chat/tests_chat/`
- Workspace metadata required to register and run `packages/friday-chat`.
- FridayV2 planning documents under `docs/planning/`.

If FridayV2 exposes a missing capability, bug, type contract problem, or
awkward interface in a frozen framework package, do not patch that package
during the parity pass. Record the requested framework change below with source
evidence, impact, the FridayV2 workaround, and suggested follow-up tests. A
secondary framework-upgrade pass can then improve the framework package content
without weakening the FridayV2-to-`friday.py` comparison.

## Entry Template

```text
## FU-000: Short Title

Status: proposed | accepted | deferred | resolved
Discovered During: FridayV2 phase or test
Framework Package: packages/friday-...
Requested Change:
Reason:
Impact If Not Changed:
FridayV2 Workaround:
Compatibility Risk:
Suggested Follow-Up Tests:
Source Evidence:
```

## Upgrade Items

No framework upgrade items have been recorded yet.
