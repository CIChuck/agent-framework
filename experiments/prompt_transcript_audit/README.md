# Prompt Transcript Audit Experiment

This experiment is the deterministic validation harness for the Phase 5-A
prompting and transcript contract.

It validates:

- runtime `prompting.base_system_prompt` loading
- agent-owned prompt fragment loading from agent YAML
- centralized prompt composition before inference
- transcript-backed episodic storage
- transcript entry persistence with prompt metadata
- `context_log` persistence and linkage to the transcript entry
- scenario input loaded from `config/scenario.yaml`, not hardcoded in code

This experiment is intentionally deterministic:

- one direct `InteractiveAgent` turn
- no provider dependency
- no archive extraction
- fake LLM response with stable output

Run from the repository root:

```bash
uv run python experiments/prompt_transcript_audit/run.py
uv run python experiments/prompt_transcript_audit/run.py --json
```

Configuration files:

- checked in runtime contract: `experiments/prompt_transcript_audit/config/runtime.yaml`
- checked in scenario input: `experiments/prompt_transcript_audit/config/scenario.yaml`

The result payload reports the layered prompt and persistence audit:

- runtime base system prompt
- rendered agent prompt
- composed system prompt
- transcript session system prompt
- transcript entry persistence and provenance
- whether prompt metadata was persisted on the transcript entry
- whether `context_log` was captured
- whether the stored system prompt matches the composed prompt
- whether the stored raw response matches the deterministic agent response

Artifacts are written under:

- `experiments/prompt_transcript_audit/artifacts/`

This experiment is the recommended first-line validation for Phase 5-A. Use
`provider_memory_smoke` when you need the real provider-backed integration path.
