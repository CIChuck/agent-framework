# Friday LLM 0.1.0a1 Wire Investigation

- Date: 2026-08-27
- Candidate: `friday-framework-llm==0.1.0a1`
- LiteLLM: `1.94.1`
- Deterministic transport: real LiteLLM OpenAI-compatible client to a controlled
  loopback HTTP server
- Live target: unavailable at `127.0.0.1:1234` during this pass

## Primary Sources

- [LiteLLM completion input parameters](https://docs.litellm.ai/docs/completion/input)
  documents standard parameters, supported-parameter inspection, strict
  unsupported-parameter behavior, and provider-specific parameters.
- [LiteLLM release index](https://github.com/BerriAI/litellm-docs/blob/main/release_notes/index.md)
  identifies the stable line used for the exact selected dependency.
- [Qwen3.8-27B model card](https://huggingface.co/Qwen/Qwen3.8-27B/blob/main/README.md)
  documents `enable_thinking`, `reasoning_effort`, `preserve_thinking`, and
  framework-specific sampling recommendations.
- [LM Studio OpenAI-compatible Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions)
  is the release-one endpoint dialect.
- [LM Studio native chat](https://lmstudio.ai/docs/developer/rest/chat) documents
  native reasoning and sampling controls, but that endpoint is explicitly
  deferred from this release.

Model-card recommendations are evidence inputs, not Friday defaults.

## LiteLLM Inspection

`litellm.get_supported_openai_params()` for an OpenAI-compatible Qwen route
reports the standard OpenAI Chat fields but not Qwen chat-template controls.
LiteLLM 1.94.1's OpenAI-compatible path merges registered provider-specific
parameters into final request JSON. Friday therefore supplies only a bounded,
translator-owned `extra_body`; it does not enable LiteLLM's process-global
drop/modify policy and does not expose arbitrary `extra_body` publicly.

The initial `1.98.0` candidate was rejected. On Python 3.10 it imports
`NotRequired` from `typing`, where that name is unavailable, and Friday fails
during import. Stable `1.94.1` imports on the declared Python floor and retains
the deterministic field merge required by this release.

## Captured Final JSON

The test server receives final HTTP JSON after LiteLLM translation. Captures use
only the fixed prompt identifier `fixed synthetic prompt` and placeholder
credentials. They are asserted in
`packages/friday-llm/tests_llm/test_wire_capture.py`; raw payload artifacts are
not retained.

| Friday intent | LiteLLM input location | Final HTTP JSON | Classification |
| --- | --- | --- | --- |
| provider default | no reasoning override | no `thinking` or `chat_template_kwargs` | emitted absence |
| disabled | `extra_body.chat_template_kwargs.enable_thinking=false` | `chat_template_kwargs.enable_thinking=false` | emitted |
| enabled | `extra_body.chat_template_kwargs.enable_thinking=true` | `chat_template_kwargs.enable_thinking=true` | emitted |
| effort `xhigh`, `medium`, `low` | `extra_body.chat_template_kwargs.reasoning_effort` | same nested field/value | emitted |
| preserve | `extra_body.chat_template_kwargs.preserve_thinking` | same nested field/value | emitted |
| temperature/top-p/presence/frequency penalty | standard LiteLLM kwargs | standard root fields | emitted |
| top-k | `extra_body.top_k` | root `top_k` | emitted |
| min-p | `extra_body.min_p` | root `min_p` | emitted |
| repetition penalty | normalized `repetition_penalty` to `extra_body.repeat_penalty` | root `repeat_penalty` | emitted |
| Qwen reasoning budget | rejected during Friday preflight | no HTTP request | unsupported |

Streaming and non-streaming requests contain byte-equivalent normalized fields;
streaming adds only `stream=true` and `stream_options.include_usage=true`.
Credentials, Friday's `drop_params` setting, and internal retry metadata do not
appear in final JSON.

The observed final wire shape does not prove that LM Studio or the model honored
a field. Every result above remains `emitted`, not `acknowledged` or
`behaviorally_observed`.

## Capability Records Frozen From This Evidence

- `dialect:openai_chat_completions@1`: standard sampling and token limit.
- `engine:lm_studio@1`: reasoning mode/effort/preserve and LM Studio sampling
  field transport.
- `model_family:qwen3_8@1`: Qwen effort values and explicit unsupported budget.
- Exact model revision: supplied explicitly by the operator and retained in
  diagnostics; live behavioral authority remains pending until the target is
  available.

The composition lattice is conservative: unsupported wins, unknown remains
unknown unless an operator declaration safely refines it, constraints
intersect, and empty intersections fail before I/O. Operator declarations
cannot override unsupported claims or widen built-in constraints.

## Baseline And Consumer Inventory

Before implementation, the package used `friday-framework-llm==0.1.0a0`,
LiteLLM `1.81.3`, a legacy default temperature of `0.7`, a legacy
`thinking={"type":"disabled"}` request, and text-only streaming. The focused
baseline was 116 passing package tests.

All current downstream callers are legacy-compatible validation consumers. The
main future typed-adoption points are Friday Chat adapters/runtime factories,
Friday Runtime dependency assembly, and Friday Memory maintenance/context/
ingestion factories. Friday Agent, Friday Tools, telemetry examples, and the
top-level integration suites also exercise the legacy methods. No consumer was
modified in this component release.

## Live Gate

The readiness probe to `http://127.0.0.1:1234/v1/models` returned connection
refused. The opt-in matrix exists in `test_live_lmstudio.py`, but no live model,
LM Studio fingerprint, accepted-control result, tool result, or behavioral
comparison was fabricated. Live completion remains a release blocker.
