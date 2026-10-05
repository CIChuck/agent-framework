# Friday Framework Telemetry

Telemetry package for the Friday Framework.

This package provides telemetry records, interfaces, provider helpers, and
debug/OpenTelemetry-oriented instrumentation support used across Friday
packages.

## Install

```bash
pip install friday-framework-telemetry
```

## Import Package

```python
import friday_telemetry
```

## License

MIT

### Composite span ownership

`CompositeProvider` retains each child's own span ID and translates nested
parent IDs per provider. Its public ID remains the first child's ID; empty
composites generate a local ID. Membership is captured when a span starts, so
removing a provider does not strand its span and adding one does not send it a
foreign end. A newly added child receives no parent for a span it never started.
Unknown or repeated ends are no-ops. Event and end payloads are copied per sink.

Fan-out attempts every child even if another fails, then raises a content-free
aggregate delivery error. A partially failed start closes the children that
opened before raising. An end is attempted once per recorded child; failure is
reported rather than silently treated as success. Exporter retry, OTel context,
and lifecycle behavior are separate contracts.
