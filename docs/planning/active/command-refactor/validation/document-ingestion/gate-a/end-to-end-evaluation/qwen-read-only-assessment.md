# Qwen comparison — read-only serving observations

Chuck proposes a larger-context test and reports Qwen already loaded. On
2026-11-12 at22:58 UTC, one read-only `lms ps --json` and one native
`GET /api/v1/models` observation identify two loaded instances:
`qwen3-embedding-4b-mlx` and `qwen3-embedding-4b-mlx:2`.
Both report context40960 and ttlMs=null; native API classifies their model as
`type: llm`, formatMLX. Nomic remains classified `embedding`.

These are serving metadata observations, not actual embedding qualification.
No inference request, model load/unload, server restart, settings or production
change occurred. The two additional read-only observations are separate from
the frozen Nomic experiment's57-request receipt, with no increase in its172
vectors or41556 prepared tokens. They are recorded as two read-only observations,
not a newly qualified inference budget or proof of internal CLI transport count.
The original experiment budget/receipts are unchanged, not reset or extended.

The [official Qwen3-Embedding-4B model card](https://huggingface.co/Qwen/Qwen3-Embedding-4B)
specifies32K context and up to2560 output dimensions, with task instructions for
retrieval queries and plain document inputs. The reported40960 runtime setting
does not prove that embedding capacity. LM Studio documents separate model
[type metadata](https://lmstudio.ai/docs/developer/rest/list) and
[embedding handles](https://lmstudio.ai/docs/python/embedding).

Before a larger-context comparison: qualify that the exact deployment is exposed
through the embedding interface, bind its actual artifact/tokenizer/preparation
and effective limit, then use a separately recorded bounded test profile/window.
Use the same documents, initially512 tokens for comparison, then larger budgets;
fresh Qwen-only stores; actual Friday-LLM vectors; dimensions/latency/retrieval
checks. Keep Nomic evidence separate. No production default selection or model
management is authorized by this factual observation, and no claim is made that
all MLX models lack embedding support.
