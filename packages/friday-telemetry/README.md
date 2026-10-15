# Friday Telemetry

Provider-neutral event/span contracts, local recorders, validated instrumentation helpers and optional owned OpenTelemetry exporters. Applications select providers and control their lifetime.

**Distribution:** [friday-framework-telemetry](https://pypi.org/project/friday-framework-telemetry/) · **Import:** `friday_telemetry`
**Python:** 3.13.4+ · **Status:** alpha · **License:** MIT

## Installation

```bash
python -m pip install "friday-framework-telemetry==0.1.0a3"
```

Friday distributions use the same release version; keep internal Friday dependencies aligned.

## Quick start: record an event locally

```python
from friday_telemetry import DebugTelemetryRecorder

recorder = DebugTelemetryRecorder()
span = recorder.start_span("example.operation")
recorder.capture_event("example.completed", {"count": 1})
recorder.end_span(span, {"outcome": "succeeded"})
print(recorder.get_event("example.completed"))
```

The event data includes `count: 1`. This recorder retains data in process memory; it is a debugging/test facility, not a durable or bounded production exporter. Never pass secrets or raw application content assuming the recorder will redact them.

## Providers and lifecycle

| API | Responsibility |
| --- | --- |
| `TelemetryInterface` | Injectable event/span contract |
| `DebugTelemetryRecorder` | Local white-box inspection |
| `CompositeProvider` | Fan-out while preserving child span ownership |
| `create_telemetry`, `ManagedTelemetry` | Explicit owned provider construction, flush and shutdown |
| `OpenTelemetryProvider` | Optional SDK-backed tracing |
| `SafeLLMTelemetry`, `MCPEvent`, `ExecutionEvent` | Closed validated instrumentation families |

A managed local provider needs no exporter SDK:

```python
from friday_telemetry import TelemetryFactoryConfig, create_telemetry

with create_telemetry(TelemetryFactoryConfig(provider="debug")) as owned:
    owned.telemetry.capture_event("example.completed", {"count": 1})
    result = owned.flush(1000)
    print(result.status)
```

The factory defaults to disabled. Callers close handles they create; consumers borrowing `TelemetryInterface` must not close the caller's provider. Composite membership and each child's span identity are captured when a span starts. Unknown/repeated ends are no-ops; fan-out failures are reported after attempting children. Composite public IDs stay reserved for its lifetime, so that reservation set grows across completed spans; use a defined provider lifetime.

## OpenTelemetry

```bash
python -m pip install "friday-framework-telemetry[otel]==0.1.0a3"
```

Use `TelemetryFactoryConfig(provider="otel", otel=OTelConfig(...))` to choose an exporter explicitly. The owned provider does not install a global tracer. Missing requested SDK/exporter support fails explicitly; installing the extra alone does not enable an exporter or wire Runtime/Chat automatically.

The validated SDK/API profile is 1.39.1; broader metadata lower bounds do not assert compatibility with every SDK version. The exporter supports console and explicitly configured OTLP/gRPC destinations. Remote collection requires verified TLS; insecure collection is restricted to explicit literal-loopback endpoints. Inherited OTEL/GRPC, proxy and certificate overrides are rejected by the owned factory. No HTTP exporter, custom credential headers, automatic instrumentation or ambient context bridge is promised. `snapshot()`, `flush()` and `shutdown()` report categorical failures/timeouts rather than treating attempted delivery as success. Shutdown/flush budgets are capped at five seconds.

## Content and integration boundaries

- Closed LLM/MCP/execution payloads contain bounded counts, timings, categories and generated opaque correlation identifiers. Raw prompts, responses, reasoning, schemas, tool payloads and credentials are excluded from those schemas.
- Generic `capture_event` values are caller data; string validation is not redaction. Historical LLM/memory helpers retain raw-content compatibility behavior and are outside the closed-schema guarantee.
- Friday Chat has separate default-disabled YAML assembly, safe local diagnostics, turn correlation and caller-owned injection. Headless adoption of the newer factory/correlation path is separate work.
- Langfuse integration remains separately queued. Legacy LLM callback support and the `langfuse` extra do not constitute a completed provider-neutral Langfuse backend.

For full limits and trust contracts, consult the factory, lifecycle and event-model source linked below.

## Development

Work from the monorepo root after the [shared contributor setup](https://github.com/CIChuck/agent-framework/blob/master/README.md#development).
Run the focused suite:

```bash
uv run --no-sync pytest packages/friday-telemetry/tests_telemetry -q
```

## Documentation and support

[Chat telemetry](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-chat/README.md) · [Owned provider factory](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-telemetry/src/friday_telemetry/factory.py) · [Lifecycle contracts](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-telemetry/src/friday_telemetry/lifecycle.py) · [Source](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-telemetry/src/friday_telemetry) · [Issues](https://github.com/CIChuck/agent-framework/issues) · [Contributing](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md)

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).
