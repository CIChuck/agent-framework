Friday Chat lacked end-to-end provider-neutral telemetry assembly and reliable
execution correlation. This change wires the existing TelemetryInterface through
Chat, corrects provider ownership and shutdown, adds safe LLM metrics, and
preserves causal execution context across tool, memory, transcript, and background
work. It also aligns workspace support with Python >=3.13.4.

Core TELEM-01–04 are independently verified and accepted. Final product:
`5c3a0e6dc8ba995bad9e7dfb8c574f5dfd335bc8`; acceptance: `4600535`.
See [the acceptance decision](https://github.com/CIChuck/agent-framework/blob/46005353046553477417a730f05ff21ead64a00d/docs/archive/completed/2026/friday-telemetry-rewire-telem-04/README.md)
and [independent VAL-010](https://github.com/CIChuck/agent-framework/blob/46005353046553477417a730f05ff21ead64a00d/docs/planning/active/friday-telemetry-rewire/validation/VAL-010/report.md).

Validation recorded by the independent reviewer: 132 focused, 1,247
Chat/LLM/Telemetry, 3,128 root, and 3,110 owning tests passed with the existing
optional SciPy skip. Source lint and typing passed. Raw root Ruff retains 327
historical findings; it does not pass. The original waiver expired at acceptance.

Telemetry remains opt-in, with custom provider injection and explicit ownership.
Langfuse export, broader headless adoption, remote exporter assembly, OTel Meter
wiring, and persisted diagnostics remain outside this accepted scope. The MCP
upgrade and Langfuse implementation are separate follow-ups.

This draft publishes committed accepted work and its original evidence. Unrelated
local configuration, audit assets, deleted files, and uncommitted follow-up
planning are excluded. The parent board's historical `started` label has closed
construction authority; archive-location housekeeping remains separate because
frozen evidence binds the original paths. No source behavior changes are added
by delivery preparation.
