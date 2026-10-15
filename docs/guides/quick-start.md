---
title: Friday Chat client quick start
description: Install the complete framework from a clone or PyPI, configure model roles and memory embeddings, and launch repeatable terminal chat sessions.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# Friday Chat client quick start

This guide takes you from installation to a repeatable **Friday Chat** session,
with your own runtime, model and terminal configuration. Choose one installation
path, then follow the shared configuration steps:

| Use case | Starting point | Installation path |
| --- | --- | --- |
| **UC1** | You cloned this repository and want the complete local workspace | [Install from a clone](#uc1-install-from-a-clone) |
| **UC2** | You want the published framework in an existing Python environment/project | [Install from PyPI](#uc2-install-from-pypi) |

Both paths finish with the same three `.yml` files and a Bash launcher modeled
on [`scripts/run-friday-chat-example.sh`](../../scripts/run-friday-chat-example.sh).
The maintained interactive executable is **`friday-chat`**, supplied by the
`friday-chat` distribution and imported as `friday_chat`. The separate `friday`
entry point in `friday-framework-cli` is a placeholder in this release; use
`friday-chat` for these instructions.

The examples target **0.1.0a3**. Installing the entire framework includes optional
packages and adapters; it does not activate tools, speech or external services.
The initial configuration enables real conversation and memory, with tools and
speech disabled. Chat's orchestration and speech adapters remain deterministic
even in real mode; these instructions do not establish live audio or specialist
agent execution. See [capability status](FRIDAY-FEATURES.md).

## Prerequisites and decisions

Before a real session, you need:

1. **Python 3.13.4 or newer**, an isolated virtual environment, and pip or uv.
   Check the patch version with `python --version`. UC1 also needs Git and uv.
2. **A running chat-model server and an embedding-model server.** One Ollama
   or LM Studio installation can serve both. Friday does not download or start
   those models for you. Choose local models your machine can run concurrently
   or accept the extra load/unload latency.
3. **Exact server model identifiers**, available context sizes, and any required
   credentials. A model's repository/download name can differ from its API ID.
   Use the server's model listing rather than guessing.
4. **A writable client directory** for configuration, transcripts, vector data,
   graph data and recovery records. Keep it stable between launches.
5. **A model-role plan.** At minimum, real canonical startup needs the primary
   chat service, extraction and four maintenance roles. The examples define all
   roles, sharing one chat profile initially, plus a separate embedding profile.
6. **A supported shell.** Commands and the launcher below target Bash on
   macOS/Linux. WSL is an option for a Bash workflow on Windows; native
   PowerShell needs an equivalent launcher and `.venv\Scripts\friday-chat.exe`.

The complete installation can bring native/platform dependencies for optional
adapters, especially audio. Consult the relevant package README if installation
fails there. Core Chat does not require a microphone, Docker, a paid provider,
or a telemetry account. If you want the smaller standard framework installation,
use `friday-framework==0.1.0a3` without `[all]`; it still includes Chat. This guide's
full-install commands deliberately use `[all]` or all workspace packages/extras.

## UC1: install from a clone

Run these commands in the parent directory where you want the checkout:

```bash
git clone https://github.com/CIChuck/agent-framework.git
cd agent-framework
python3.13 --version
uv sync --python 3.13 --all-packages --all-extras --locked
source .venv/bin/activate
python --version
friday-chat --version
friday-chat --help
```

Verify the installed interpreter is at least **3.13.4**, and the checkout and
reported Friday version match the **0.1.0a3** basis of this guide. If your branch
is newer, consult its matching guides. The Python minor selector `3.13` lets uv
select an available compatible patch; it is not a request for Python 3.13.0.

`--all-packages` selects the entire workspace; `--all-extras` includes optional
dependencies; `--locked` preserves the checked-in dependency resolution and fails
rather than silently updating it. Workspace packages are editable: this
`.venv/bin/friday-chat` uses the cloned source. You do not also need a PyPI
installation in that environment. See [uv workspace behavior](https://docs.astral.sh/uv/concepts/projects/workspaces/).

Keep the terminal at the repository root for the next step. The client files
will live inside `.friday/chat-client/`, which this repository already ignores.
The existing repository example launcher points to broad example configuration
and a machine-local environment file. It is useful as a pattern; the dedicated
launcher below uses your own files and avoids editing distributed templates.

Continue with [Create your client directory](#create-your-client-directory).

## UC2: install from PyPI

Activate your **existing compatible virtual environment**, then choose **one**
method below. Run commands from your own application/project directory, outside
the Friday source checkout. Keep the Friday distribution cohort on one version.

### Option A: pip in an existing virtual environment

```bash
python --version
python -m pip --version
python -m pip install "friday-framework[all]==0.1.0a3"
python -m pip check
friday-chat --version
friday-chat --help
```

`python -m pip` binds installation to the selected interpreter. The aggregate
`friday-framework[all]` installs the framework's optional package groups and
`friday-chat`; a separate `pip install friday_chat` is unnecessary. There is no
`friday_framework` module to import: the root distribution is metadata-only.

### Option B: uv add in an existing uv project

Use this when your application has a `pyproject.toml` and uv-managed dependencies.
Activate its Python >=3.13.4 environment first; `--active` explicitly selects that
active environment rather than silently choosing a different project `.venv`.

```bash
python --version
uv add --active "friday-framework[all]==0.1.0a3"
friday-chat --version
friday-chat --help
```

This updates your project's dependency declaration, lockfile and selected
project environment. For a **bare virtual environment without a uv project**,
use pip above, or `uv pip install --python "$VIRTUAL_ENV/bin/python"
"friday-framework[all]==0.1.0a3"`; `uv add` is a project operation. Do not run
`uv init` inside the Friday monorepo to set up an independent installed client.
See [uv environments](https://docs.astral.sh/uv/pip/environments/) and
[active project environments](https://docs.astral.sh/uv/concepts/projects/config/).

Keep this environment activated and remain in your application directory for
the shared steps. Installed wheels include templates as package resources, but
you do not need a `packages/` directory or the repository's scripts to run Chat.
You will create the following smaller, complete configuration yourself.

## Create your client directory

For either use case, run from the chosen checkout/application root, with the
correct environment still activated:

```bash
CLIENT_DIR="$PWD/.friday/chat-client"
mkdir -p "$CLIENT_DIR"
```

Use a new directory for this walkthrough. If these filenames already exist,
back them up and reconcile their contents instead of overwriting them. Keep the
`CLIENT_DIR` variable in this terminal while following the remaining steps.
Your finished layout will be:

```text
<checkout-or-application>/
├── .venv/                         # or your existing environment elsewhere
└── .friday/chat-client/
    ├── config.yml                 # Chat runtime settings and role bindings
    ├── models.yml                 # endpoint, credential references and profiles
    ├── cli.yml                    # terminal appearance and progress messages
    ├── friday.env                 # selected executable and process environment
    ├── run-friday-chat.sh          # your launcher
    └── data/                      # created as the real runtime writes state
        ├── vector/                # Chroma collections
        ├── graph.json             # graph sibling of vector/
        ├── transcripts/
        │   └── friday_transcripts.sqlite
        ├── recovery/
        └── reorganization_logs/
```

In UC2, add `.friday/` to **your application's** `.gitignore` if it is not already
ignored. `friday.env` is executable shell input; keep it private and source only
a file you control. Real conversation and extracted data also need appropriate
retention and backup. The guide uses synthetic values for setup.

### Understand the three configuration files

| File | Owner | What belongs here |
| --- | --- | --- |
| `config.yml` | `friday_chat.config.load_friday_py_config()` | Role bindings, memory paths/budgets, identity, extraction, tools and optional integrations |
| `models.yml` | `friday.model-library/v1` | Server addresses, credential references, exact model identities and shared generation defaults |
| `cli.yml` | Friday CLI display resolver | Colors, banner, response styling and progress messages |

`.yml` and `.yaml` are both YAML filenames. The explicit launch arguments below
select the `.yml` files. Without `--cli-config`, automatic sibling lookup looks
for **`cli-config.yaml`**, not `cli.yml`; otherwise it uses built-in defaults.
There is no implicit discovery of this runtime file and no `init` or `doctor`
subcommand in alpha3. A headless `RuntimeConfig` file has a different schema;
use the **Chat** schema shown here.

## Prepare local model serving

Choose **Ollama or LM Studio**. Start the server before the live preflight and
real Chat launch. All examples use the **OpenAI-compatible** interface; Friday
stores the base address in `api_base`, even though the OpenAI SDK calls its
corresponding setting `base_url`.

### Ollama

Install [Ollama](https://ollama.com/download), then make these example models
available locally:

```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
ollama list
```

These are reproducible example identities, not a model-quality ranking. You can
substitute another instruction model and embedding model after updating their
profiles. [Qwen2.5](https://ollama.com/library/qwen2.5:7b-instruct) is the chat
example; [nomic-embed-text](https://ollama.com/library/nomic-embed-text) is an
embedding-only example, not a conversational model.

If Ollama is not already running as an application/service, start it in another
terminal with a context capacity matching this guide:

```bash
OLLAMA_CONTEXT_LENGTH=8192 ollama serve
```

For an existing managed server, configure that server's environment and restart
it as described in the [Ollama FAQ](https://docs.ollama.com/faq#how-can-i-specify-the-context-window-size).
Do not start a second server on an occupied port. Changing an environment
variable only in the Friday shell does not reconfigure an already running server.

The local compatible base address is `http://127.0.0.1:11434/v1`. Keep `/v1`;
do not use Ollama's native `/api` path in these profiles. The local server ignores
the required client key value; the example supplies `local-only`. Cloud-backed
Ollama routes have different credential requirements. See
[Ollama OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility).

### LM Studio

Install [LM Studio](https://lmstudio.ai/), download an instruction/chat model
and a separate text-embedding model, and make both available to its local server.
In the **Developer** view, start the server and copy the exact API model IDs.
Set the chat model's served context to at least **8192 tokens** for this example;
download size, quantization and context length must fit your machine.

The examples use `http://127.0.0.1:1234/v1`. Configure the actual port if yours
differs. If authentication is enabled, use the server's actual token rather than
`local-only`. See [LM Studio server setup](https://lmstudio.ai/docs/developer/core/server)
and [embedding endpoint](https://lmstudio.ai/docs/developer/openai-compat/embeddings).
Do not substitute LM Studio's separate native REST address/route into these
OpenAI-compatible profiles.

For either server, listing IDs is a **live local request**:

```bash
# Ollama; change 11434 to 1234 for an unauthenticated LM Studio server.
curl --fail --silent --show-error http://127.0.0.1:11434/v1/models
```

For an authenticated server, use its documented authentication when listing
models. Confirm that the chat ID and embedding ID below are actually served.
A downloaded file by itself is not proof of an available API route.

## Write models.yml: endpoints and model profiles

Save **one** of the following complete examples as `$CLIENT_DIR/models.yml`.
They expose the same two profile names, so `config.yml` works with either.
A profile is a reusable model definition; a service is a runtime role bound to
that definition. Ten services can share two profiles without ten model downloads.

### Complete Ollama model library

```yaml
schema: friday.model-library/v1
credentials:
  local:
    env: FRIDAY_LOCAL_MODEL_KEY
endpoints:
  local:
    api_base: http://127.0.0.1:11434/v1
    provider: openai_compatible
    serving_engine: ollama
    default_credential: local
    resilience:
      max_retries: 2
      timeout_seconds: 120
profiles:
  local_chat:
    kind: chat
    endpoint: local
    dialect: openai_chat_completions
    model: openai/qwen2.5:7b
    model_target:
      model_id: qwen2.5:7b
      family: qwen2_5
      revision: replace-with-your-installed-ollama-model-digest
    generation:
      sampling:
        temperature: 0.2
      max_tokens: 2048
  local_embedding:
    kind: embedding
    endpoint: local
    dialect: openai_embeddings
    model: openai/nomic-embed-text
    model_target:
      model_id: nomic-embed-text
      family: nomic_embed
      revision: replace-with-your-installed-embedding-model-digest
    embedding_options:
      batch_size: 16
      cache_size: 100
```

Replace `revision` with the actual model digest/revision recorded for your
installation. It is provenance metadata, not a command that downloads or pins
a model inside the server. If your server lists a different tag, change both
`model` and `model_target.model_id` to match it.

`openai/` is LiteLLM's routing prefix for this compatible interface; it does not
mean these requests go to OpenAI's hosted service. The explicit `api_base`
selects your local server. The wire model ID is the corresponding server ID
without that routing prefix. Do not put the `openai/` prefix into `model_id`.

### Complete LM Studio model library

This example assumes the server lists `qwen2.5-7b-instruct` and
`text-embedding-nomic-embed-text-v1.5`. **Replace those IDs with the exact IDs
from your server**, including both each `model` suffix and `model_id`. Replace
the revision values with your downloaded artifact/revision information.

```yaml
schema: friday.model-library/v1
credentials:
  local:
    env: FRIDAY_LOCAL_MODEL_KEY
endpoints:
  local:
    api_base: http://127.0.0.1:1234/v1
    provider: openai_compatible
    serving_engine: lm_studio
    default_credential: local
    resilience:
      max_retries: 2
      timeout_seconds: 120
profiles:
  local_chat:
    kind: chat
    endpoint: local
    dialect: openai_chat_completions
    model: openai/qwen2.5-7b-instruct
    model_target:
      model_id: qwen2.5-7b-instruct
      family: qwen2_5
      revision: replace-with-your-installed-lm-studio-chat-revision
    generation:
      sampling:
        temperature: 0.2
      max_tokens: 2048
  local_embedding:
    kind: embedding
    endpoint: local
    dialect: openai_embeddings
    model: openai/text-embedding-nomic-embed-text-v1.5
    model_target:
      model_id: text-embedding-nomic-embed-text-v1.5
      family: nomic_embed
      revision: replace-with-your-installed-lm-studio-embedding-revision
    embedding_options:
      batch_size: 16
      cache_size: 100
```

### Model-library options that matter first

| Setting | Meaning and setup rule |
| --- | --- |
| `credentials.local.env` | **Name** of a process variable, never the token itself; the launcher exports its value |
| `api_base` | Full compatible base including `/v1`; use a separate endpoint definition if embeddings are hosted elsewhere |
| `provider`, `serving_engine`, `dialect` | Transport/capability identity; keep the values consistent with the route you selected |
| `model` / `model_target` | Routing model plus exact served identity, family and recorded revision; an arbitrary friendly label does not load a server model |
| `timeout_seconds`, `max_retries` | Shared transport resilience; role-specific `resilience_overrides` can replace these |
| `generation.sampling.temperature` | Shared chat default; role overrides below make extraction/maintenance less variable |
| `generation.max_tokens` | Response cap; it is not the model's total context size or an embedding dimension |
| `embedding_options` | Embedding batch size and process cache size; these do not change vector dimension |

Canonical model-library schemas reject unknown fields. Add only supported
provider/generation controls; copying a provider's native JSON options into a
profile can fail validation or exceed that route's capabilities. The examples
omit reasoning controls to avoid assuming a particular model's reasoning API.
For other hosted/mixed endpoints, see [configuration reference](10-configuration.md).

## Write config.yml: runtime, roles and memory

Save this **complete Chat configuration** as `$CLIENT_DIR/config.yml`.
It works with either model library above after your model IDs are correct.
It binds all documented model roles explicitly; the first session needs only
one actual chat model plus one actual embedding model.

```yaml
model_library:
  path: ./models.yml

llm_pool:
  default_service: chat
  services:
    chat:
      profile: local_chat
    extraction:
      profile: local_chat
      generation_overrides:
        sampling:
          temperature: 0.0
        max_tokens: 2048
    synthesizer:
      profile: local_chat
      generation_overrides:
        sampling:
          temperature: 0.0
    classifier:
      profile: local_chat
      generation_overrides:
        sampling:
          temperature: 0.0
    researcher:
      profile: local_chat
    judge:
      profile: local_chat
      generation_overrides:
        sampling:
          temperature: 0.0
    compaction:
      profile: local_chat
      generation_overrides:
        sampling:
          temperature: 0.0
    passage_router:
      profile: local_chat
      generation_overrides:
        sampling:
          temperature: 0.0
        max_tokens: 512
    smart_file_summarizer:
      profile: local_chat
    smart_file_synthesizer:
      profile: local_chat

embedding_pool:
  default_service: memory
  services:
    memory:
      profile: local_embedding
    maintenance:
      profile: local_embedding

llm:
  max_retries: 0

chat:
  user_name: User
  assistant_name: Friday
  system_prompt: You are Friday, a careful and helpful assistant.

logging:
  level: WARNING
  extraction_debug: false
  extraction_rejections: false
  tools_debug: false

extraction:
  llm_service: extraction
  interval: 3
  ontology:
    node_types:
      person:
        description: A named person
        examples: [Alex]
      project:
        description: A named project
        examples: [Orchid]
    edge_relations:
      association: [WORKS_ON, RELATED_TO]
    min_label_length: 2
    max_label_length: 80

memory:
  persist_directory: ./data/vector
  collection_name: chat_long_term
  context_window: 8192
  output_buffer: 2048
  max_history_turns: 12
  consolidate_after_turns: 15
  token_estimator:
    strategy: approx
    approx_chars_per_token: 4.0
    approx_overhead_pct: 0.15
  retrieval:
    short_term_collection: chat_short_term
    long_term_collection: chat_long_term
    decayed_collection: chat_decayed
    short_term_min_similarity: 0.5
    long_term_min_similarity: 0.7
    default_n_results: 5
  supporting_context:
    budget_ratio: 0.25
    section_priority: [known_facts, insights, summaries, tools, passages, state]
    max_items:
      known_facts: 20
      insights: 10
      summaries: 5
      passages: 3
      tools: 0
  compaction:
    enabled: true
    llm_service: compaction
    compaction_threshold: 0.85
    critical_threshold: 0.95
    target_utilization: 0.7
    cooldown_turns: 3
  passage_router:
    enabled: false
    llm_service: passage_router
  priming:
    enabled: true
    previous_sessions: 2
    previous_session_turns: 8
    token_budget: 1500

transcript:
  export_directory: ./data/transcripts
  capture_raw_prompts: false

maintenance:
  backup_directory: ./data/recovery
  llm:
    synthesizer:
      llm_service: synthesizer
    classifier:
      llm_service: classifier
    researcher:
      llm_service: researcher
    judge:
      llm_service: judge
  embedding:
    embedding_service: maintenance
  logging:
    log_directory: ./data/reorganization_logs

lifecycle:
  enabled: true

session:
  flush_on_exit: true
  lifecycle_on_exit: true
  reorganize_on_exit: false

smart_file:
  default_add_to_context: true
  default_store_to_memory: false
  llm:
    summarizer:
      llm_service: smart_file_summarizer
    synthesizer:
      llm_service: smart_file_synthesizer

tools:
  enabled: false
speech:
  enabled: false
telemetry:
  enabled: false
langfuse:
  enabled: false
```

### Required and optional model roles

| Service name in the example | Used for | Startup/activation rule |
| --- | --- | --- |
| `chat` | Foreground conversation | Selected by `llm_pool.default_service`; required for real Chat |
| `extraction` | Structured entities, relationships, insights and turn summaries | Real maintenance assembly constructs the extractor; define it even before its first scheduled call |
| `synthesizer` | Memory synthesis | Maintenance roles are resolved during real startup, even with reorganization-on-exit disabled |
| `classifier` | Classifying claims for maintenance | Same startup requirement |
| `researcher` | Maintenance evidence/research processing | Same startup requirement; a role name alone does not grant web access |
| `judge` | Maintenance verification/judgment | Same startup requirement |
| `compaction` | Summarizing context when its budget is pressured | Used when `memory.compaction.enabled` is true, as above |
| `passage_router` | Deciding whether retrieved passages belong in context | Conditional on `memory.passage_router.enabled`; off above |
| `smart_file_summarizer` | Summarizing large file sections | Used when a `SmartFileReadTool` is registered/constructed; tools are off above |
| `smart_file_synthesizer` | Combining those section summaries | Same smart-file prerequisite |
| Embedding `memory` | Embedding ingestion and similarity queries | Selected by `embedding_pool.default_service` in real Chat assembly |
| Embedding `maintenance` | Explicit reorganization embedding provider | Selected by `maintenance.embedding.embedding_service`; kept compatible with `memory` |

These service names are local configuration keys, not models you must download
separately. `local_chat` and `local_embedding` are the reusable profile keys in
`models.yml`. To use a different extraction model, add a second **chat** profile
there and change only `llm_pool.services.extraction.profile`. Do the same for any
role requiring a larger/faster model or a different endpoint. Change a role's
`generation_overrides` or `resilience_overrides` in its service binding; endpoint
defaults remain shared. Never bind an embedding profile to a chat service.

All three canonical sections—`model_library`, `llm_pool`, `embedding_pool`—must
appear together. Every declared service is resolved when the configuration
loads, including roles not yet enabled. Remove unused hosted bindings or supply
their selected credentials; disabling a feature does not excuse an unresolved
model-library credential. A missing maintenance service can prevent startup;
a caught optional adapter error can instead appear as a runtime gap. Configuration
success alone is not proof that every secondary adapter is functioning.

### Runtime options and path rules

- `model_library.path` is resolved relative to **config.yml**. Keep `models.yml`
  beside it, or use an absolute path. This differs from data paths.
- Memory/transcript/recovery paths above are relative to the **process working
  directory**. The launcher changes to the client directory before Chat starts.
  If you launch directly from elsewhere, use absolute data paths or perform that
  same `cd`; otherwise you can accidentally select a different empty store.
- `context_window: 8192` is Friday's context budget. Configure at least that
  capacity on the model server; Friday does not resize the server's model context.
  `output_buffer: 2048` reserves response room. Keep the model's output cap and
  budget aligned, then tune history/supporting context to your workload.
- `llm.max_retries: 0` disables Chat's additional whole-turn retry loop;
  endpoint/service transport retries still apply. This avoids multiplying two
  retry layers. An optional `llm.timeout_seconds` sets the foreground turn
  timeout and the primary request timeout; secondary services retain their own
  resolved resilience settings. Increase time budgets deliberately for slow
  local inference rather than adding retry layers.
- `extraction.interval: 3` schedules extraction every three turns. `0` means every
  turn; `-1` disables interval-triggered extraction. Extraction also participates
  in configured exit flushing, so an interval setting alone is not a universal
  no-model-calls switch. JSON-producing extraction quality matters independently
  of conversational fluency; the built-in prompt is used when none is supplied.
- `lifecycle.enabled` selects persistent graph/lifecycle services. Vector memory,
  transcripts and graph memory are different stores. Compaction is opt-in here;
  its role can make extra model calls when budget thresholds are reached.
- `session.flush_on_exit` lets pending extraction settle; `reorganize_on_exit`
  remains false for this initial setup. Exit normally rather than killing the
  process while writes/background work are active.
- `capture_raw_prompts: false` avoids opting into raw prompt capture; transcript
  records still contain conversation content. It is not a global privacy switch.
- Tools, speech and telemetry are off independently. Full installation does not
  supply credentials or permission to activate them. Optional Langfuse backend
  work remains queued; the legacy callback configuration is a separate path.

These are initial settings, not a complete catalog of every advanced memory,
security, tool or MCP option. Continue with [configuration](10-configuration.md),
[memory](04-adaptive-memory.md) and [memory budgeting](memory-management-guidelines.md)
after the first working session.

## Embedding setup: how memory gets its vectors

The chat model generates text; an embedding model converts text into a numeric
vector so memory can find related records. Installing Chroma or choosing an
embedding-looking name does not provide that model. It must be available at an
endpoint that actually implements embeddings.

The examples make the route explicit:

```text
models.yml: profiles.local_embedding
    ↓
config.yml: embedding_pool.services.memory.profile = local_embedding
    ↓
config.yml: embedding_pool.default_service = memory
    ↓
real Chat's embedding adapter → memory ingestion and retrieval
```

In alpha3 real Chat assembly, the **pool default** selects the regular embedding
adapter. A standalone `embedding.embedding_service` entry does not override that
selection. Explicit maintenance uses its separate
`maintenance.embedding.embedding_service` reference; this guide binds both to
the same profile to keep the stored vector space consistent.

### What you must keep compatible

| Item | Why it matters |
| --- | --- |
| Actual embedding model and revision | Stored and query vectors must come from the same compatible embedding space |
| Vector dimension | The server determines the returned vector length; changing it can make an existing Chroma collection incompatible |
| Preprocessing and model task-prefix conventions | These affect similarity; validate the chosen model's retrieval behavior rather than assuming any same-sized vector is interchangeable |
| All three collection names and persistence directory | They select your existing short-term, long-term and decayed collections; changing them can look like missing memory |
| Maintenance embedding binding | Synthesized/maintenance records must remain compatible with ordinary memory queries |

There is **no `dimensions` setting** in alpha3's canonical `embedding_options`.
The supported options here are `batch_size` and `cache_size`; neither changes the
vector length. Friday's Chat adapter does not configure a query/document prefix
policy in this example. If your selected embedding model requires task-specific
preprocessing, verify that your serving/integration path provides it; do not
invent a YAML field to request it. The small live probe below checks availability
and vector length, not retrieval quality.

Before replacing an embedding model, stop the old client, retain a consistent
backup and the source records, choose a **new persistence directory and new
collection names**, and re-embed/reingest the intended content through a supported
workflow. Do not point an incompatible model at an existing collection, even if
it happens to return the same dimension. Changing `revision` in YAML does not
migrate existing vectors. Keep existing data until you have verified the new
retrieval behavior. See [memory recovery and operations](04-adaptive-memory.md).

## Write cli.yml: terminal presentation

Save this **complete display configuration** as `$CLIENT_DIR/cli.yml`:

```yaml
theme:
  error: bold red
  warning: bold yellow
  success: bold green
  info: bold blue
  muted: dim
  highlight: bold cyan
icons:
  error: X
  warning: '!'
  success: OK
  info: i
banner:
  enabled: true
  style: panel
  title: Friday
  subtitle: '{assistant_name} CLI'
  show_version: true
  border_style: cyan
  tips_enabled: false
prompt:
  style: bold cyan
  name_style: bold cyan
  separator_style: white
  continuation_style: dim
response:
  prefix: true
  name_style: bold green
  separator_style: green
  text_style: white
spinner:
  spinner_type: dots
  text_style: dim
  spinner_style: cyan
  randomize: false
  thinking_messages: [Thinking...]
  tool_messages: [Working...]
```

`theme` and `icons` set terminal styles; `banner` controls the startup display;
`response` controls the assistant prefix/colors; `spinner` supplies wait-state
presentation. The Chat identity still comes from `config.yml`. In alpha3 the
Chat input adapter formats its prompt as `<user_name>: `; declaring prompt styles
does not change that text. Spinner/tool messages do not enable tools.

This file contains no model endpoints, credentials, memory paths or command
permissions. An invalid/missing **explicit** file is an error. If you prefer
built-in styling, omit `--cli-config` from your launcher; remember the sibling
`cli-config.yaml` lookup described above.

## Create friday.env and the launcher

### Capture the correct installed executable

With the UC1 or UC2 environment still activated, create `friday.env` automatically.
This **offline setup command** uses that interpreter's scripts directory and
refuses to overwrite an existing environment file:

```bash
export CLIENT_DIR
python - <<'PY'
import os
import shlex
import sysconfig
from pathlib import Path

client_dir = Path(os.environ["CLIENT_DIR"])
executable = Path(sysconfig.get_path("scripts")) / "friday-chat"
if not executable.is_file():
    raise SystemExit(f"Friday Chat is not installed in this interpreter: {executable}")
env_file = client_dir / "friday.env"
with env_file.open("x", encoding="utf-8") as stream:
    stream.write(f"export FRIDAY_CHAT_BIN={shlex.quote(str(executable))}\n")
    stream.write("export FRIDAY_LOCAL_MODEL_KEY=local-only\n")
env_file.chmod(0o600)
print(f"Created {env_file}; executable: {executable}")
PY
```

The resulting shell file resembles:

```bash
export FRIDAY_CHAT_BIN='/absolute/path/to/your/environment/bin/friday-chat'
export FRIDAY_LOCAL_MODEL_KEY='local-only'
```

Keep `local-only` for an explicitly local server that accepts an unused client
key. For an authenticated LM Studio/server route, edit that value privately to
its real token. `credentials.local.env` in `models.yml` names this variable;
it does not embed its value. Avoid publishing the file or displaying real tokens
in diagnostics. Recreate/update the executable path if you move the environment.

Chat does **not automatically load `.env` files**. The launcher deliberately
sources `friday.env`. Ordinary `${VARIABLE}` strings in runtime YAML are expanded
before validation, including strings in disabled sections; every such variable
must be supplied. The canonical credential `env:` value above is a literal
reference resolved for each declared service. CLI display YAML is not the place
for environment-variable substitution or provider secrets.

### Save run-friday-chat.sh

Save this **complete script** as `$CLIENT_DIR/run-friday-chat.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

CLIENT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-real}"
if [[ "$#" -gt 1 ]] || [[ "$MODE" != real && "$MODE" != fake ]]; then
  echo "Usage: $0 [real|fake]" >&2
  exit 2
fi

for name in friday.env config.yml models.yml cli.yml; do
  if [[ ! -f "${CLIENT_DIR}/${name}" ]]; then
    echo "Missing client file: ${CLIENT_DIR}/${name}" >&2
    exit 1
  fi
done

cd "$CLIENT_DIR"
source "${CLIENT_DIR}/friday.env"
: "${FRIDAY_CHAT_BIN:?Set FRIDAY_CHAT_BIN in friday.env}"
if [[ "$FRIDAY_CHAT_BIN" != /* || ! -x "$FRIDAY_CHAT_BIN" ]]; then
  echo "FRIDAY_CHAT_BIN must be an absolute executable path." >&2
  exit 1
fi

# The environment takes precedence over --runtime in alpha3: set both explicitly.
export FRIDAY_CHAT_RUNTIME="$MODE"
exec "$FRIDAY_CHAT_BIN" \
  --runtime "$MODE" \
  --config "${CLIENT_DIR}/config.yml" \
  --cli-config "${CLIENT_DIR}/cli.yml"
```

Then make it executable:

```bash
chmod u+x "$CLIENT_DIR/run-friday-chat.sh"
```

This script works from another working directory because it locates its own
files and changes to their directory before starting Chat. It selects the saved
virtual-environment executable without requiring activation on later launches.
Its default is **real**; the first verification below deliberately passes
`fake`. It normalizes `FRIDAY_CHAT_RUNTIME` so an inherited value cannot silently
change the selected mode. It does not start model servers or install/update any
packages. The only optional positional argument is `real` or `fake`.

## Validate configuration before calling models

Run this **offline** check from the same activated installation environment:

```bash
cd "$CLIENT_DIR"
source ./friday.env
python - <<'PY'
from pathlib import Path
from friday_chat.config import load_friday_py_config
from friday_chat.display import resolve_display_config

config = load_friday_py_config(Path("config.yml"))
display = resolve_display_config(
    config_path=Path("config.yml"), cli_config_path=Path("cli.yml")
)
print("Chat services:", ", ".join(config.llm_service_specs))
print("Embedding services:", ", ".join(config.embedding_service_specs))
print("Display source:", display.source)
print("Configuration parsed and model bindings resolved; no model call made.")
PY
```

Expect ten chat service names, embedding services `memory, maintenance`, and
`Display source: explicit`. This verifies syntax, schema, selected credential
references and profile resolution. It does **not** contact the server, validate
model availability, test extraction quality or guarantee runtime readiness.

Check the terminal flow independently of providers:

```bash
"$CLIENT_DIR/run-friday-chat.sh" fake
```

Enter a short greeting, then `/q` to exit. Fake mode supplies deterministic
responses. Canonical configuration still loads, so its declared credential
references must resolve; it does not require real model connectivity. Fake mode
is not proof of persistence or semantic recall.

### Live preflight for chat and embeddings

After starting your local server, run this **live local check** from the client
directory and activated environment. It reads the selected profiles rather than
hardcoding a different model or endpoint. It sends synthetic text to both APIs:

```bash
cd "$CLIENT_DIR"
source ./friday.env
python - <<'PY'
import asyncio
from pathlib import Path
from friday_chat.config import load_friday_py_config
from friday_llm import (
    ChatCompletionRequest, LiteLLMEmbeddingService, LiteLLMService,
    close_litellm_async_clients,
)

async def main() -> None:
    config = load_friday_py_config(Path("config.yml"))
    chat_spec = config.llm_service_specs[config.llm_pool.default_service]
    embedding_spec = config.embedding_service_specs[config.embedding_pool.default_service]
    chat = LiteLLMService.from_spec(chat_spec)
    embedding = LiteLLMEmbeddingService.from_spec(embedding_spec)
    try:
        reply = await chat.chat_completion_request(ChatCompletionRequest(
            messages=({"role": "user", "content": "Say hello in one short sentence."},)
        ))
        if not reply.content:
            raise RuntimeError("Chat server returned no text content")
        vector = await embedding.embed_query("The Orchid project uses a green notebook.")
        if not vector:
            raise RuntimeError("Embedding server returned an empty vector")
        print("Chat reply:", reply.content)
        print("Embedding vector length:", len(vector))
    finally:
        await close_litellm_async_clients()

asyncio.run(main())
PY
```

A nonempty response and numeric vector confirm basic connectivity for those
routes. Repeat setup for any role you later bind to a different profile. A model
can chat successfully yet produce malformed extraction JSON or have inadequate
context capacity. This preflight does not certify those behaviors. For hosted
profiles it becomes a provider call with that provider's data/cost implications.

## Start and verify real sessions

Launch with the configured local models running:

```bash
"$CLIENT_DIR/run-friday-chat.sh" real
```

For a first synthetic conversation, introduce a distinctive fact such as
“The Orchid project uses a green notebook,” ask a follow-up, and continue for
at least three turns so interval-based extraction can run. Wait for responses
and exit normally. Background work can make additional chat/embedding requests;
the endpoint must remain available while it settles.

Start the script again for another chat session. Each launch gets a new session
identity; the same stable data paths retain the transcript/vector/graph stores.
Previous-session context/priming is not an exact continuation of the old live
session. Check saved records independently of whether a model happens to recall
the fact. The guide's `priming` settings limit how much prior context is selected.

Use the existing [CLI reference as further reference](09-cli-reference.md) for
session/history/transcript inspection, memory/context diagnostics, session
management and other chat commands. It describes the commands and their side
effects; this quick start intentionally does not repeat that catalog.

For a direct equivalent to the script, run from the client directory:

```bash
cd "$CLIENT_DIR"
source ./friday.env
FRIDAY_CHAT_RUNTIME=real "$FRIDAY_CHAT_BIN" \
  --runtime real --config "$CLIENT_DIR/config.yml" --cli-config "$CLIENT_DIR/cli.yml"
```

On later days you can use the launcher's **absolute path**, for example
`/your/application/.friday/chat-client/run-friday-chat.sh real`, without first
activating the environment. `CLIENT_DIR` is only a convenience variable in the
setup terminal; it is not automatically preserved in a new shell.

### What to verify before adding features

| Check | Evidence to look for |
| --- | --- |
| Installation | Correct `friday-chat` version and intended environment path |
| Runtime/model files | All ten chat bindings and two embedding bindings resolve; real mode selected |
| Chat | A live response from the intended server/model |
| Memory | Successful extraction and nonempty stored records; no adapter-gap/extraction failures |
| Restart | Earlier transcript/records accessible with the same data paths |
| Retrieval | The relevant record appears in selected context, not just somewhere in storage |
| Shutdown | Background extraction/write work settles without lifecycle errors |

If an endpoint is unreachable, check its server process, port, `/v1` base and
exact model ID. A 401 usually means its selected credential is wrong or absent.
An unknown service/profile means the role keys do not match. A schema error can
mean a legacy/headless setting was placed in Chat YAML. A new empty store often
means you changed cwd, a directory or a collection name. Do not delete live
SQLite/Chroma lock files or reset data as a setup repair.

After this baseline works, enable one optional integration at a time using
[tools](05-tools.md), [MCP client setup](17-mcp-client.md), or
[advanced integration](11-advanced-topics.md). For deeper configuration and
recovery, see [configuration reference](10-configuration.md) and
[troubleshooting](13-troubleshooting.md).

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
