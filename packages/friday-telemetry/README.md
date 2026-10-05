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
parent IDs per provider. A first child's ID remains public when this composite
has never published it. Reused child IDs and empty composites receive a fresh
opaque composite-owned ID; each child still receives its own ID on end.
Membership is captured when a span starts, so
removing a provider does not strand its span and adding one does not send it a
foreign end. A newly added child receives no parent for a span it never started.
Unknown or repeated ends are no-ops. Event and end payloads are copied per sink.

Published IDs remain reserved for the composite instance's lifetime, including
after a span ends. This prevents a stale end from closing a later span when a
replacement provider reuses an ID. Reservation retains only strings, growing
with the total number of published spans; completed child/provider references
and payloads are released. Use composite instances with a defined runtime
lifetime when cumulative ID retention matters.

Fan-out attempts every child even if another fails, then raises a content-free
aggregate delivery error. A partially failed start closes the children that
opened before raising. An end is attempted once per recorded child; failure is
reported rather than silently treated as success. Exporter retry, OTel context,
and lifecycle behavior are separate contracts.
