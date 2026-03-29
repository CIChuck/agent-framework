# Provider Memory Smoke Experiment

This experiment exercises the real provider-backed direct-agent path plus
archive-time extraction.

It validates:

- `RuntimeKernel` boot and shutdown with Phase 4 runtime YAML
- real provider-backed inference using a dedicated agent LLM service
- archive-time extraction using a different configured extraction LLM service
- embeddings using a separate configured embedding service
- coarse post-turn extraction evidence in graph and vector memory stores

This experiment is intentionally narrow:

- one direct `InteractiveAgent` turn
- `context_strategy: minimal`
- `memory.recall.semantic_retrieval_enabled: false`
- archive extraction enabled

Default runtime persistence paths are declared in:

- `experiments/provider_memory_smoke/config/runtime.yaml`

The checked-in defaults use stable `/tmp` paths so the resulting Chroma/vector
data and runtime artifacts can be inspected after a run. These paths can be
overridden locally in `runtime.local.yaml` if needed.

Run from the repository root:

```bash
uv run python experiments/provider_memory_smoke/run.py
uv run python experiments/provider_memory_smoke/run.py --json
```

Configuration files:

- checked in: `experiments/provider_memory_smoke/config/runtime.yaml`
- checked in scenario input: `experiments/provider_memory_smoke/config/scenario.yaml`
- local secrets overlay: `experiments/provider_memory_smoke/config/runtime.local.yaml`
- example local overlay: `experiments/provider_memory_smoke/config/runtime.local.yaml.example`

The runtime-owned prompt policy lives under `prompting` in
`config/runtime.yaml`. The executed turn input lives in
`config/scenario.yaml`. It is not sourced from code or a fixture file.
`--prompt` and `--agent` remain explicit command-line overrides over the
scenario file.

`runtime.local.yaml` is required for real-provider execution. It is intentionally
untracked and should contain API keys and any machine-local endpoint overrides.

The runner preserves a JSON summary artifact under:

- `experiments/provider_memory_smoke/artifacts/`

The result payload also reports the effective:

- `memory_profile`
- `runtime_data_root`
- `chroma_path`
- runtime base system prompt
- raw user `prompt`
- rendered agent prompt
- composed system prompt
- effective agent profile fields such as role, goal, context strategy, and bound LLM service

The experiment uses coarse extraction assertions:

- non-empty agent response
- at least one extracted entity, insight, or summary

It does not yet assert exact ontology output or exact graph structure.
