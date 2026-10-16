# Friday Optimization

A reserved experimental namespace for future DSPy-based memory and context optimization. This package is **scaffolding**, not a working optimizer.

**Distribution:** [friday-framework-optimization](https://pypi.org/project/friday-framework-optimization/) · **Import:** `friday_opt`
**Python:** 3.13.4+ · **Status:** alpha · **License:** MIT

## Installation

```bash
python -m pip install "friday-framework-optimization==0.1.0a3"
```

Friday distributions use the same release version; keep internal Friday dependencies aligned.

## Current implementation status

The `friday_opt` package currently contains docstring-only modules:

| Module | Intended area; not implemented |
| --- | --- |
| `signatures.query_gen` | Memory-search query generation |
| `signatures.summarization` | Memory summarization |
| `compilers.optimize_context` | Context-prompt optimization |

The distribution declares DSPy and Friday Memory dependencies, but exposes no implemented optimizer, compiler, runnable training pipeline, or stable optimization API. There is no optimization quick start to run. Installing this package does not improve model prompts or enable optimization in Runtime/Chat.

Use the implemented memory/context and LLM APIs for application work. Contributors should agree on a concrete optimization contract, dataset/evaluation method and execution authority before adding functionality; do not infer implementation from the module names or dependency declarations.

## Development

Work from the monorepo root after the [shared contributor setup](https://github.com/CIChuck/agent-framework/blob/master/README.md#development).
There is no package-local test suite yet. Start with an import check:

```bash
uv run --no-sync python -c "import friday_opt"
```

This import check verifies packaging only, not optimization functionality. There is no package-local test suite or evaluator yet.
## Documentation and support

[Implemented memory APIs](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-memory/README.md) · [Implemented LLM APIs](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-llm/README.md) · [Source](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-optimization/src/friday_opt) · [Issues](https://github.com/CIChuck/agent-framework/issues) · [Contributing](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md)

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).
