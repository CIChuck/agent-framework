# Friday-LLM Integration Test

Interactive chat CLI for testing the `friday-llm` package.

## Quick Start

```bash
# From the project root
cd tests/integration/llm

# Run the chat CLI
python chat.py
```

## Configuration

Edit `config.yaml` to configure your LLM provider:

### LM Studio (Default)

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Download a model (e.g., Llama 3, Mistral, Phi-3)
3. Start the local server (default port: 1234)
4. Use this config (note the `openai/` prefix - LM Studio uses OpenAI-compatible API):

```yaml
llm:
  model: "openai/local-model"
  api_base: "http://127.0.0.1:1234/v1"
  api_key: "lm-studio"
```

### Ollama

1. Install [Ollama](https://ollama.ai/)
2. Pull a model: `ollama pull llama3`
3. Use this config:

```yaml
llm:
  model: "ollama/llama3"
  api_base: "http://localhost:11434"
  api_key: ""
```

### OpenAI

```yaml
llm:
  model: "gpt-4o-mini"
  api_base: ""  # Uses default OpenAI endpoint
  api_key: "sk-your-api-key-here"
```

### Anthropic

```yaml
llm:
  model: "claude-3-5-sonnet-20241022"
  api_base: ""
  api_key: "sk-ant-your-api-key-here"
```

## Commands

During the chat session:

| Command | Description |
|---------|-------------|
| `exit` or `quit` | End the conversation |
| `clear` | Reset conversation history |
| `history` | Show conversation so far |

## CLI Arguments

```bash
# Use custom config file
python chat.py --config /path/to/config.yaml
```

## Troubleshooting

### "Connection refused" error
- Ensure LM Studio or Ollama server is running
- Check the port number in `config.yaml` matches your server

### "Model not found" error
- Verify the model name matches what your provider expects
- For LM Studio: Check the model is loaded in the UI
- For Ollama: Run `ollama list` to see available models

### Slow responses
- Local models depend on your hardware (GPU recommended)
- Try a smaller model (e.g., Phi-3, Mistral 7B)
- Reduce `temperature` for more deterministic (sometimes faster) responses

## Architecture

```
chat.py
    │
    ▼
LiteLLMService (friday-llm)
    │
    ▼
litellm library
    │
    ▼
LM Studio / Ollama / OpenAI / Anthropic
```

The chat CLI uses `LiteLLMService` from `friday-llm`, which wraps the `litellm` library for multi-provider support. This integration test validates that:

1. Configuration loading works correctly
2. LiteLLMService initializes with custom endpoints
3. Multi-turn conversations maintain context
4. Responses are returned in the expected format
