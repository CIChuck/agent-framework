# Build Plan: Friday Web Chat

**Status:** Draft
**Target:** Browser-based Friday Chat experience
**Objective:** Expose Friday Chat-like behavior through a web browser while
preserving the existing Friday package boundaries, runtime composition, memory
context engineering, transcript persistence, tool safety, and streaming turn
semantics.

---

## 1. Conversation Snapshot

This plan captures the initial architecture discussion for a future browser
interface and is intended to evolve over time.

Current direction:

- Build a dedicated web app layer over the same runtime and chat services.
- Do not shell out to the CLI.
- Keep `friday-chat` and `friday-runtime` as reusable service layers.
- Add a backend package for HTTP/SSE/WebSocket APIs.
- Add a React-like browser frontend for the user experience.

Initial recommendation:

```text
packages/
  friday-chat/        # existing chat/session/turn/tool-loop app logic
  friday-runtime/     # service composition
  friday-memory/      # memory/context
  friday-tools/       # tools
  friday-transcript/  # transcript persistence
  friday-web/         # new FastAPI backend for browser clients
apps/
  friday-web-ui/      # React/Vite frontend, if repo structure allows app dirs
```

If the project should keep all deployable code under `packages/`, an alternate
shape is:

```text
packages/friday-web/
  src/friday_web/
    app.py
    api/
    sessions.py
    streaming.py
    schemas.py
    auth.py
  web/
    package.json
    src/
```

The preferred default is a Python backend package plus a separate frontend app,
if repository policy allows that structure.

## 2. Goals

- Provide a browser-based chat workspace with Friday Chat-like behavior.
- Reuse existing Friday services instead of duplicating prompt, memory, tool,
  transcript, or runtime logic.
- Support streamed assistant output and turn lifecycle events.
- Preserve memory/context visibility through structured debug APIs.
- Preserve tool safety and sanitization behavior.
- Support local-first usage initially, with a path to authenticated remote
  deployment.

## 3. Non-Goals

- Do not replace `friday-chat` CLI behavior.
- Do not build a marketing site or landing page.
- Do not execute tools in the browser.
- Do not expose secrets or raw provider config to the browser.
- Do not bypass existing memory, transcript, or tool-loop contracts.
- Do not introduce a second prompt-construction system specific to the web UI.

## 4. Proposed Architecture

### 4.1 Package Responsibilities

| Package | Responsibility |
| --- | --- |
| `friday-web` | HTTP APIs, session API, streaming API, auth boundary, browser-safe schemas |
| `friday-web-ui` | Browser presentation and interaction layer |
| `friday-chat` | Turn processing, command semantics, tool-loop-facing app contracts |
| `friday-runtime` | Runtime service construction and lifecycle |
| `friday-memory` | Retrieval, context assembly, prompt layout, memory maintenance |
| `friday-tools` | Native tool implementations and tool registry behavior |
| `friday-transcript` | Persistent conversation/session records and exports |
| `friday-core` | Shared protocols, typed contracts, security primitives |

The web backend should be a presentation/API layer over existing runtime
services. Browser clients should not directly own LLM, memory, transcript, or
tool execution concerns.

### 4.2 Backend

Recommended backend framework:

- FastAPI

Reasons:

- Already appears in the repository dependency set through `friday-cli`.
- Supports typed request/response models.
- Supports SSE and WebSocket patterns.
- Fits Python package boundaries and existing async service code.

Candidate backend package:

```text
packages/friday-web/
  pyproject.toml
  src/friday_web/
    __init__.py
    app.py
    config.py
    dependencies.py
    security.py
    schemas.py
    sessions.py
    streaming.py
    api/
      __init__.py
      health.py
      sessions.py
      messages.py
      tools.py
      memory.py
      transcripts.py
      config.py
```

### 4.3 Frontend

Recommended frontend stack:

- React
- Vite
- TypeScript

The UI should be a real chat workspace:

- conversation pane with streamed assistant output
- message composer
- session list/sidebar
- tool activity panel
- context/prompt/debug inspector
- transcript export controls
- memory summaries/entities views
- runtime status panel
- cancellation and retry controls

The frontend should remain a presentation layer. Prompt construction, memory
retrieval, tool execution, transcript writes, sanitization, and provider calls
stay on the backend.

## 5. API Sketch

Initial HTTP/SSE API:

```text
GET    /api/health
POST   /api/sessions
GET    /api/sessions
GET    /api/sessions/{session_id}
DELETE /api/sessions/{session_id}
POST   /api/sessions/{session_id}/messages
GET    /api/sessions/{session_id}/events
POST   /api/sessions/{session_id}/cancel
GET    /api/sessions/{session_id}/transcript
GET    /api/sessions/{session_id}/context
GET    /api/sessions/{session_id}/prompt
GET    /api/tools
POST   /api/tools/{tool_name}/run
GET    /api/config/effective
```

Streaming:

- Start with Server-Sent Events for assistant output and turn events.
- Add WebSocket support later if bidirectional live controls become necessary.

Candidate event types:

```text
turn.started
assistant.delta
tool.call.started
tool.call.completed
tool.call.failed
memory.retrieved
context.prepared
turn.completed
turn.failed
turn.cancelled
heartbeat
```

## 6. Session Model

Open decision:

- one runtime per server,
- one runtime per user,
- one runtime per browser session,
- or one shared runtime with per-session state.

Initial recommendation:

- Local-first phase: one backend runtime with multiple isolated chat sessions.
- Remote/authenticated phase: runtime/session isolation must be revisited based
  on user identity, provider credentials, tool access, and memory tenancy.

Session state should include:

- session id
- user id or local anonymous identity
- runtime profile
- transcript session id
- current turn state
- cancellation token
- active tools
- loaded startup context metadata, including any future `friday.md`
- memory/context debug metadata

## 7. Security Considerations

The browser changes the threat model. A local CLI user is not equivalent to a
remote web client.

Required security decisions:

- local-only trusted mode vs authenticated remote mode
- CORS defaults
- CSRF protection for browser sessions
- secret redaction in effective config APIs
- tool execution permissions
- shell/file/network tool restrictions
- per-session cancellation and timeout behavior
- transcript and memory access controls
- prompt/debug visibility controls

Initial recommendation:

- Phase 1 is local-only and binds to `127.0.0.1`.
- Remote deployment requires explicit auth and tightened tool-safety defaults.

## 8. Tooling And Memory Compatibility

### 8.1 Tool Execution

The web backend should call the same tool-loop path used by Friday Chat.

Required behavior:

- tool schemas are selected through existing registry/context logic
- tool calls execute server-side
- tool output is sanitized before model feedback
- tool results are included in transcript/context logs
- browser receives structured tool events, not raw unsafe internals

### 8.2 Memory And Context

The web backend should expose memory and context through structured read APIs.

Required behavior:

- prompt/context debug views reflect the actual prompt sent to the model
- memory retrieval metadata is visible where safe
- transcript and memory records distinguish web-origin turns from CLI-origin
  turns
- future `friday.md` startup context appears in prompt/debug views if loaded

### 8.3 Transcript

The backend should persist web turns through `friday-transcript`.

Required behavior:

- web sessions create transcript sessions
- streamed turns finalize into immutable transcript entries
- exports use existing transcript exporters where possible
- raw prompt capture remains governed by config

## 9. Candidate Implementation Phases

### Phase 1: Backend Skeleton With Fake Runtime

Goal:

- Create a `friday-web` backend package with a typed API over fake services.

Work:

- Add package metadata and workspace registration.
- Add FastAPI app factory.
- Add health endpoint.
- Add session create/list/get/delete endpoints.
- Add message endpoint with fake streamed events.
- Add package tests using fake runtime services.

Acceptance:

- `uv run pytest packages/friday-web/tests_web` passes.
- `uv run python -c "from friday_web import create_app; print('OK')"` passes.
- No real LLM, memory, tool, or network provider is required.

### Phase 2: Real Friday Runtime Integration

Goal:

- Wire the backend to real Friday runtime and Friday Chat turn processing.

Work:

- Build runtime dependency lifecycle for FastAPI startup/shutdown.
- Create per-session Friday Chat state.
- Route message requests through `TurnProcessor` or a shared service contract.
- Stream assistant deltas and lifecycle events.
- Persist transcript entries.

Acceptance:

- Browser/API message flow uses the same prompt and tool loop as Friday Chat.
- Transcript persistence works for web-origin turns.
- Runtime shutdown releases resources.

### Phase 3: Tool, Memory, And Debug APIs

Goal:

- Expose browser-safe tool, memory, context, prompt, and transcript controls.

Work:

- Add `/api/tools`.
- Add optional `/api/tools/{tool_name}/run` with safety controls.
- Add `/api/sessions/{session_id}/context`.
- Add `/api/sessions/{session_id}/prompt`.
- Add transcript export endpoints.
- Add tests for redaction and access controls.

Acceptance:

- Browser-visible debug output matches actual model payloads.
- Secrets are redacted.
- Tool outputs remain sanitized.

### Phase 4: React/Vite Frontend

Goal:

- Build a usable browser chat workspace.

Work:

- Create frontend app structure.
- Add session sidebar and conversation view.
- Add streamed output rendering.
- Add message composer, cancel, and retry controls.
- Add tool activity panel.
- Add context/prompt/debug inspector.
- Add transcript export controls.

Acceptance:

- Local developer can run backend and frontend together.
- Streamed assistant output appears incrementally.
- Tool and debug panels reflect backend events.
- UI works on desktop and mobile viewport basics.

### Phase 5: Auth And Deployment Hardening

Goal:

- Define local vs remote deployment security boundaries.

Work:

- Add local-only default bind behavior.
- Add optional auth mode.
- Add CSRF/CORS policy.
- Add config redaction tests.
- Add tool permission tests for risky tools.

Acceptance:

- Local mode is easy to run.
- Remote mode cannot be accidentally exposed with permissive tool access.
- Effective config APIs never leak provider keys.

### Phase 6: Update User And Developer Guides

Goal:

- Document browser-based Friday usage before the feature is considered complete.

Work:

- Update `docs/guides/02-getting-started.md` with local web startup commands.
- Update `docs/guides/09-cli-reference.md` or add an adjacent web reference
  section describing web-specific commands and APIs.
- Update `docs/guides/10-configuration.md` with web backend configuration,
  bind/auth settings, streaming settings, and redaction behavior.
- Update `docs/guides/11-advanced-topics.md` with architecture, session
  isolation, streaming, tool safety, and deployment modes.
- Update `docs/guides/13-troubleshooting.md` with startup, streaming, auth,
  CORS, transcript, and tool-execution troubleshooting.

Acceptance:

- Guides explain how to run the web backend and frontend locally.
- Guides distinguish CLI, web, and runtime responsibilities.
- Guides document local-only vs remote deployment security expectations.
- Web implementation is not considered complete until guide updates are done.

## 10. Open Questions

- Should the frontend live under `apps/friday-web-ui/` or inside
  `packages/friday-web/web/`?
- Should `friday-web` depend on `friday-chat`, or should common app services be
  extracted into a shared package first?
- Is SSE sufficient for Phase 1, or do we need WebSockets immediately?
- What is the default runtime isolation model: per backend, per user, or per
  browser session?
- Should browser clients be allowed to run arbitrary `/run-tool` equivalents?
- Should prompt/debug APIs be enabled by default, admin-only, or local-only?
- Should web sessions share CLI transcript storage by default?
- Should this app support multiple workspaces in one backend process?
- Should speech support be included in the web UI, or deferred?

## 11. Initial Validation Targets

```bash
uv run pytest packages/friday-web/tests_web
uv run mypy packages/friday-web
uv run ruff check packages/friday-web
git diff --check -- docs/guides
git diff --check
```

When frontend code exists:

```bash
npm test
npm run lint
npm run build
```

Repo-wide validation should be run after framework validation gate restoration:

```bash
uv run pytest
uv run mypy packages tests main.py
uv run ruff check .
```

## 12. Completion Criteria

- A browser client can create a Friday session and send messages.
- Assistant output streams to the browser.
- Web turns use the same runtime, memory, prompt, tool-loop, and transcript
  behavior as Friday Chat.
- Tool activity and memory/context debug data are available through safe
  structured APIs.
- Local-only security defaults are documented and enforced.
- User and developer guides are updated before closeout.
