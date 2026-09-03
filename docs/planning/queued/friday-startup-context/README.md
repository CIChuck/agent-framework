# Build Plan: Friday Framework `friday.md` Startup Context

**Status:** Draft
**Target:** Friday startup context, prompt assembly, and context engineering
**Objective:** Add AGENTS.md-style project instruction loading through a
workspace-level `friday.md` file while preserving prompt precedence, context
budgeting, memory provenance, and runtime package boundaries.

---

## 1. Conversation Snapshot

This plan captures the initial brainstorming for a future `friday.md` feature
and is intended to evolve over time.

Feature intent:

- If a `friday.md` file exists in the root startup directory for Friday, Friday
  loads the file and includes its contents in model context just after the
  system prompt.
- The behavior should resemble AGENTS.md-style project guidance found in many
  agentic coding tools.
- The feature should be compatible with Friday's memory/context engineering
  package and Friday Chat V2 turn processing.

Current recommendation:

- Treat `friday.md` as **startup instruction context**, not ordinary long-term
  memory ingestion.
- Load it from the **Friday startup root** by default.
- Insert it just after the system prompt as a distinct startup-context message or
  static prompt section.
- Make it visible to `/prompt` and `/debug`.
- Add long-term memory ingestion only later as an explicit opt-in, if needed.

## 2. Key Decision: Where `friday.md` Lives

Default location:

```text
<Friday startup root>/friday.md
```

The Friday startup root should mean the working directory from which the Friday
app/runtime is launched, unless explicitly overridden by config.

Example:

```bash
cd /Users/chuckrussell/Dev/gendev/agent-framework
friday-chat --config packages/friday-chat/config.example.yaml
```

Friday should look for:

```text
/Users/chuckrussell/Dev/gendev/agent-framework/friday.md
```

It should not default to looking next to `config.yaml`. Config files may live in
package directories, home config directories, or shared deployment locations.
`friday.md` should describe the active workspace, not the config file location.

## 3. Terminology

| Term | Meaning |
| --- | --- |
| Startup root | The workspace/root directory used to resolve `friday.md` by default |
| Startup context | Prompt-visible content loaded from `friday.md` |
| System prompt | Highest-priority assistant identity, guardrails, and policy prompt |
| Supporting context | Memory/context payload assembled by `friday-memory` |
| Long-term memory ingestion | Persisting content into vector/graph/transcript-backed memory stores |

## 4. Desired Semantics

### 4.1 Prompt Role And Authority

`friday.md` should not silently become a higher-authority system prompt.

Recommended precedence:

1. Repository/platform policy and explicit runtime safety rules.
2. Configured Friday system prompt.
3. Loaded `friday.md` startup context.
4. Retrieved memory/supporting context.
5. Current user request, where it does not conflict with higher-priority
   instructions.

### 4.2 Prompt Placement

The user-facing requirement is "just after the system prompt."

Preferred initial representation:

```python
[
    {"role": "system", "content": base_system_prompt},
    {
        "role": "user",
        "content": "Project instructions from friday.md:\n\n...",
    },
    {"role": "assistant", "content": "[Startup context loaded]"},
    ...
]
```

Reasons:

- Keeps the configured system prompt clean and inspectable.
- Makes `friday.md` prompt-visible before memory and current-turn context.
- Aligns with existing prompt-cache/static-context layout patterns.
- Avoids giving arbitrary workspace Markdown system-level authority by default.

Alternative:

- Append `friday.md` directly to the system message.

This may be considered later if stronger authority is explicitly required, but
it has larger safety and precedence implications.

### 4.3 Memory Behavior

Initial default:

- Do not store `friday.md` in vector memory, graph memory, transcript memory, or
  extraction pipelines as ordinary conversation content.
- Treat it as prompt context loaded from a local instruction file.

Possible future opt-in:

```yaml
chat:
  startup_context:
    ingest_to_memory: false
```

If ingestion is ever enabled, it must include explicit provenance and retention
semantics.

### 4.4 Missing File Behavior

Recommended default:

- Missing `friday.md` is not an error.
- The absence should be visible in debug diagnostics.
- Normal startup should remain quiet unless verbose/debug mode is enabled.

### 4.5 Case And Naming

Default convention:

```text
friday.md
```

Open decision:

- Should `FRIDAY.md` also be recognized for consistency with uppercase
  convention files such as `AGENTS.md`?

If both are supported, precedence must be explicit.

## 5. Configuration Shape

Candidate config:

```yaml
chat:
  startup_context:
    enabled: true
    instruction_file: friday.md
    root: null
    max_tokens: 4096
    missing: silent
    reload: startup
    include_in_prompt_debug: true
    ingest_to_memory: false
```

Field meanings:

| Field | Meaning |
| --- | --- |
| `enabled` | Enables or disables startup-context loading |
| `instruction_file` | Relative or absolute file path; default `friday.md` |
| `root` | Optional root override; default current startup directory |
| `max_tokens` | Maximum prompt budget for loaded file content |
| `missing` | `silent`, `debug`, or `warn` behavior when file is absent |
| `reload` | `startup`, `per_turn`, or future `watch` |
| `include_in_prompt_debug` | Whether `/prompt` and `/debug` show loaded content/path |
| `ingest_to_memory` | Future opt-in; should default false |

## 6. Repository Insertion Points

Likely packages/files:

| Area | Candidate location |
| --- | --- |
| Typed config | `packages/friday-chat/src/friday_chat/config.py` and/or `friday-runtime` config |
| File loading | New app/runtime startup-context helper |
| Prompt assembly | `packages/friday-chat/src/friday_chat/turns/processor.py` |
| Context architecture | `packages/friday-memory/src/friday_memory/context/layout.py` / `ContextAssembler` |
| Debug commands | `packages/friday-chat/src/friday_chat/commands/registry.py` |
| Session metadata | Transcript/session creation in Friday Chat adapters/runtime |
| Tests | `packages/friday-chat/tests_chat` and possibly `packages/friday-memory/tests_memory` |

Important existing behavior:

- Friday Chat currently builds model messages in turn processing using the
  configured `chat.system_prompt`, retrieved memories, tool context, current
  query, and turn count.
- `friday-memory` has a `PromptArchitect` that models system prompt, history,
  static context, dynamic context, and supporting context.
- Any final design should avoid duplicating prompt layout rules across packages.

## 7. Design Considerations

### 7.1 Startup Root Resolution

Default:

- Use the process working directory at Friday startup.

Config override:

```yaml
chat:
  startup_context:
    root: /absolute/workspace/path
```

Open question:

- Should Friday search upward from the startup directory until it finds
  `friday.md`, or should it only check the root exactly?

Root-only is simpler and safer for v1. Upward search can be added later if
there is a clear need.

### 7.2 Multi-Workspace Behavior

If Friday later supports changing active workspaces mid-session, the
`friday.md` behavior needs a clear rule:

- keep startup context fixed for the session, or
- reload when workspace root changes.

Initial recommendation:

- Keep it fixed for the session.

### 7.3 Reload Behavior

Initial recommendation:

- Load once at startup.

Potential later modes:

- `per_turn`: re-read before every turn.
- `watch`: reload when file mtime changes.

Startup-only is deterministic and easier to test.

### 7.4 Token Budgeting

`friday.md` should have a bounded prompt budget.

Possible policies:

- fail if the file exceeds budget,
- truncate with warning/diagnostic,
- summarize later using memory/context machinery.

Initial recommendation:

- Truncate to `max_tokens` with a debug-visible diagnostic.
- Do not summarize automatically in v1, because summarization would require an
  LLM call during startup and could distort instruction text.

### 7.5 Security

Treat `friday.md` as local workspace instruction content, but not as system
policy.

Requirements:

- Do not let `friday.md` override explicit runtime safety constraints.
- Show the source path in debug diagnostics.
- Avoid automatically storing secrets from `friday.md` into memory.
- Preserve prompt-injection mitigations for external content.

### 7.6 Transcript And Raw Prompt Capture

If `friday.md` is prompt-visible, it should be reflected in raw prompt capture
when raw prompts are enabled.

Session metadata should record:

- whether startup context was loaded,
- source path,
- content hash,
- truncation status,
- token estimate.

This gives reproducibility without necessarily storing the full file content in
session metadata.

## 8. Candidate Implementation Phases

### Phase 1: Friday Chat Startup Context

Goal:

- Implement root-level `friday.md` loading for Friday Chat V2.

Work:

- Add typed `chat.startup_context` config.
- Resolve startup root and instruction file path.
- Load file once at startup.
- Include loaded content after the system prompt in model messages.
- Expose source path and load status in `/debug` and `/prompt`.
- Add tests for present, missing, disabled, relative path, absolute path, and
  truncation cases.

Acceptance:

- A root-level `friday.md` appears in the model prompt immediately after the
  system prompt.
- Missing file does not fail startup by default.
- Disabled config prevents loading.
- `/prompt` and `/debug` show startup-context state.

### Phase 2: Context Engineering Integration

Goal:

- Move the concept from Friday Chat-specific message assembly into the shared
  prompt/context architecture where appropriate.

Work:

- Decide whether `PromptArchitect` should accept a `startup_context` block.
- Ensure cached and non-cached prompt layouts place startup context after the
  system prompt.
- Ensure fixed-cost and dynamic-budget calculations include startup context.
- Add package-level tests in `friday-memory` if the layout engine owns the
  behavior.

Acceptance:

- Startup context placement is consistent in cached and non-cached layouts.
- Budget calculations include startup-context tokens.
- Friday Chat does not duplicate logic that belongs in `friday-memory`.

### Phase 3: Optional Memory Ingestion

Goal:

- Define an opt-in path for storing `friday.md` into memory if needed.

Work:

- Define provenance metadata for instruction-file ingestion.
- Decide target stores: vector only, graph extraction, transcript metadata, or
  a separate instruction-source record.
- Add retention and refresh rules.
- Keep ingestion disabled by default.

Acceptance:

- Ingestion is explicit and provenance-rich.
- Startup prompt context and long-term memory ingestion remain separate
  concepts.

### Phase 4: Update User And Developer Guides

Goal:

- Document `friday.md` startup-context behavior before the feature is considered
  complete.

Work:

- Update `docs/guides/02-getting-started.md` with the basic `friday.md`
  convention and where the file lives relative to the Friday startup root.
- Update `docs/guides/09-cli-reference.md` with startup-root behavior, any CLI
  flags or diagnostics added for startup context, and `/prompt` or `/debug`
  visibility.
- Update `docs/guides/10-configuration.md` with `chat.startup_context` config,
  including `enabled`, `instruction_file`, `root`, `max_tokens`, missing-file
  behavior, reload behavior, and memory-ingestion defaults.
- Update `docs/guides/13-troubleshooting.md` with missing file, wrong root,
  truncation, prompt visibility, and precedence troubleshooting.

Acceptance:

- The guides explain that `<Friday startup root>/friday.md` is the default
  location.
- The guides distinguish prompt startup context from long-term memory ingestion.
- The guides document precedence relative to the configured system prompt,
  retrieved memory, and current user request.
- The guides show at least one minimal `friday.md` example.
- The `friday.md` implementation is not considered complete until these guide
  updates are done.

## 9. Open Questions

- Should Friday search only `<startup_root>/friday.md`, or search upward from
  the startup root?
- Should subdirectory-specific `friday.md` files be supported later?
- Should `FRIDAY.md` be accepted as an alias?
- If both `friday.md` and `FRIDAY.md` exist, which wins?
- Should missing files be silent, debug-only, or warning-level by default?
- Should file changes reload during a running session?
- Should `friday.md` be included as a separate message, or appended to the
  system message?
- Should `friday.md` ever be allowed to change safety-sensitive behavior?
- Should config allow arbitrary instruction file names, or should the convention
  remain fixed?

## 10. Initial Validation Targets

```bash
uv run pytest packages/friday-chat/tests_chat
uv run pytest packages/friday-memory/tests_memory/test_context
uv run mypy packages/friday-chat packages/friday-memory
uv run ruff check packages/friday-chat packages/friday-memory
git diff --check -- docs/guides
git diff --check
```

Repo-wide validation should be run after framework validation gate restoration:

```bash
uv run pytest
uv run mypy packages tests main.py
uv run ruff check .
```

## 11. Completion Criteria

- A root-level `friday.md` can be loaded from the Friday startup root.
- Loaded `friday.md` content appears just after the system prompt in the model
  prompt path.
- Missing files, disabled config, truncation, prompt debug visibility, and
  startup-root overrides are tested.
- `friday.md` is not ingested into long-term memory by default.
- `docs/guides/02-getting-started.md`, `docs/guides/09-cli-reference.md`,
  `docs/guides/10-configuration.md`, and
  `docs/guides/13-troubleshooting.md` are updated before closeout.
