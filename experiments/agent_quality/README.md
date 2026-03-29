# Agent Quality Experiment

This experiment smoke-tests the Phase 4 direct-agent runtime path.

It validates:

- `RuntimeKernel` boot and shutdown
- YAML agent loading
- runtime agent factory/registry wiring
- session initialization
- one single-step `InteractiveAgent` execution

Default mode is deterministic and does not require external LLM credentials.

Run from the repository root:

```bash
uv run python experiments/agent_quality/run.py
uv run python experiments/agent_quality/run.py --json
```

Runtime configuration is declared in:

- `experiments/agent_quality/config/runtime.yaml`

The runner only applies ephemeral temp-path overrides and deterministic test
double wiring on top of that declarative runtime contract.
