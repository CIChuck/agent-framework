---
title: "Getting Started"
description: "Install Friday, run your first agent, and understand the core concepts in minutes."
weight: 1
---

Welcome to Friday Framework. This section walks you through installation, your first agent run, and the foundational concepts you need to be productive.

## What You'll Do

1. Install Friday from PyPI
2. Configure a basic agent with your choice of LLM provider
3. Run your first conversation
4. Verify memory persistence across sessions
5. Explore the interactive CLI

By the end, you'll have a working Friday agent that remembers conversations, learns from interactions, and demonstrates genuine memory persistence.

---

## Prerequisites

### System Requirements

- **Python 3.10 or higher** (3.11+ recommended)
- **4GB RAM minimum** (16+GB recommended for local LLMs)
- **macOS, Linux, or Windows** (WSL2 recommended for Windows)
- **Internet connection** (for cloud LLM providers) or local Ollama instance

### Required Knowledge

- Basic Python experience (ability to run scripts, understand basic syntax)
- Familiarity with terminal/command line
- API keys for your chosen LLM provider (or Ollama installed locally)

### LLM Provider Options

You'll need **at least one** of the following:

**Cloud Providers (Recommended for Getting Started):**
- **OpenAI**: Get API key from [platform.openai.com](https://platform.openai.com) - Models: GPT-4o, GPT-4o-mini
- **Anthropic**: Get API key from [console.anthropic.com](https://console.anthropic.com) - Models: Claude 3.5 Sonnet, Claude 3 Haiku
- **Google AI**: Get API key from [ai.google.dev](https://ai.google.dev) - Models: Gemini 2.5 Pro, Gemini 2.5 Flash
- **OpenRouter**: Get API key from [openrouter.ai](https://openrouter.ai) - Access to 100+ models with single key

**Local Option (No API Keys Required):**
- **Ollama**: Install from [ollama.ai](https://ollama.ai) - Models: Llama 3, Mistral, and more
  - Requires 8GB+ RAM, GPU recommended but not required
  - Run: `ollama pull llama3` to download the model

---

## Next Steps

- **[Installation](/docs/getting-started/installation/)** — Install the packages and set your API keys
- **[Quick Start](/docs/getting-started/quick-start/)** — Build and run your first memory-persistent agent
