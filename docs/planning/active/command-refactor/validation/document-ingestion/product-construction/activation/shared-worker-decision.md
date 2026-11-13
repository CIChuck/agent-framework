# Shared ingestion worker — frontend-neutral process ownership

2026-11-13. Chuck emphasizes a worker process that leaves the main application
responsive and requires ingestion to be reusable by CLI and/or TUI. Optimizing
only for Chat is explicitly rejected. This records shared implementation design,
not production generation, live effects or a new validation project.

## Ownership

- **Tools** owns document conversion/OCR/audit, the owned process/session and
  Docling planning adaptation. It imports no Chat, CLI, TUI, Rich or Textual.
- **Memory** owns common ingestion policy, complete-plan validation and persistence,
  invoking the injected document capability. It imports no frontend or Tools.
- **Core** owns immutable progress/results and worker lifecycle protocols. Workers
  receive no frontend object, terminal output sink, model client or Memory store.
- **LLM** supplies the injected pure local counter/preparation; actual provider
  requests stay outside the conversion worker.
- **Runtime/composition roots** own shared service lifetime. Chat and CLI/Runtime
  call the same capabilities; a future TUI uses those public contracts without
  a Chat import. UI adapters render progress/errors and translate cancellation.

Tools process management and lifecycle semantics are implemented once. Chat's
read request tracking is only an adapter into the shared session; it does not
contain a separate worker implementation. DIContainer.shutdown drains its owned
converter/session service through its existing Runtime shutdown seam. Standalone
headless users use the same explicit close/cancel contract in a finally block.
No new CLI executable, slash registry, TUI package or command-family migration
is created by this requirement.

## Concurrency and resources

Use a fresh worker process for blocking document work; do not rely on threads
for parallel Python bytecode execution. Ordinary GIL-enabled CPython has real
threads, useful for I/O and native work that releases the GIL, but a separate
interpreter has its own GIL. A process still shares machine CPU/RAM/I/O, so it
is not a promise of zero resource impact or OS sandboxing.

One shared converter service owns at most one active document session by default.
Permit one queued request; refuse additional work with a typed busy result before
source I/O/spawn. A cancelled queued request never launches. Capacity spans both
conversion and retained-document planning; no unbounded process-per-command
fan-out or one independent pool per renderer. Do not impose a global singleton:
independent Runtime instances own independent bounded services. Their combined
machine load remains an operator/resource-profile concern.

Progress consists of typed stage/count/code events, not Chat output strings.
The parent owns delivery; the child knows no UI callback. Cancellation discards
late results and waits for owned work to exit, with the same terminate/join
contract in every consumer. Existing timeout/resource-limit acceptance remains
required; no extra model/parity qualification or standalone Docling evaluation
is introduced here.

## Acceptance

The shared headless tests must instantiate Tools and Memory capabilities without
Chat/CLI/TUI imports, ingest a genuine document into a disposable store, and check
structured progress/results. Independently cancel/timeout/drain work through that
same service, including queued cancellation and backpressure. Runtime shutdown
must drain the service. Then Chat verifies its own actual app adapter. A small
renderer-free consumer proves future TUI reuse; it is not a claim of shipping a
TUI or a new CLI command.

Python reference for the GIL distinction:
[threading](https://docs.python.org/3.13/library/threading.html#gil-and-performance-considerations)
and [process-based parallelism](https://docs.python.org/3.13/library/multiprocessing.html).
