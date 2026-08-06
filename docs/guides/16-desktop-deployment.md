# Friday Agent Framework

## Desktop Deployment With uv

**Framework Version:** v0.1.0 alpha
**Last Updated:** 2026-07-22

---

## Overview

This guide describes how to deploy Friday Chat on a desktop machine with
Astral's `uv` package manager. It covers macOS, Linux, and Windows.

Friday Chat has two desktop execution modes:

- **Persistent tool install:** `uv tool install friday-chat`, then run
  `friday-chat`.
- **Wrapper launcher:** keep no persistent Friday executable and run
  `uvx friday-chat` through a small shell or PowerShell launcher.

The current alpha and the planned first-run experience differ:

- **Current alpha:** create config files yourself and run
  `friday-chat --config <path> --runtime real`.
- **Planned state:** run `friday-chat init`, `friday-chat doctor`, then
  `friday-chat`.

The package environment created by `uvx` is temporary. Do not put editable
configuration, API keys, memory state, transcripts, Chroma/vector data, logs, or
caches inside the installed package or temporary tool environment.

---

## Recommended Paths

Use stable user-owned paths for configuration and runtime data. Do not create
runtime state under the `uv` tool install directory or a temporary `uvx`
environment.


| Purpose | macOS and Linux | Windows |
| --- | --- | --- |
| Main config | `~/.config/friday/config.yaml` | `%APPDATA%\Friday\config.yaml` |
| CLI display config | `~/.config/friday/cli-config.yaml` | `%APPDATA%\Friday\cli-config.yaml` |
| User data root | `~/.local/share/friday/` | `%LOCALAPPDATA%\Friday\` |
| Cache | `~/.cache/friday/` | `%LOCALAPPDATA%\Friday\cache\` |

Recommended user data subfolders:

| Subfolder | Purpose |
| --- | --- |
| `vector/` | Vector memory persistence. The current template uses this for Chroma-backed memory state. |
| `exports/` | Transcript database files and exported conversation artifacts. |
| `backups/` | Optional memory backup output. |
| `quarantine/` | Sanitized or quarantined tool output when security storage policy requires it. |
| `reorganization_logs/` | Memory maintenance and reorganization logs. |
| `speech/` | Optional speech model files or provider runtime assets. |
| `cache/` | Download/cache/runtime scratch data. On macOS and Linux this should live under `~/.cache/friday/`, not the user data root. |


Recommendation:

- Use XDG-style paths on macOS and Linux.
- Use Windows app-data paths on Windows.
- Implement future path resolution with `platformdirs` so the app can resolve
  native OS paths consistently.
- Keep `--config` as the highest-priority override for reproducible runs.

Current config lookup should be treated as explicit:

```bash
friday-chat --config ~/.config/friday/config.yaml --runtime real
```

Planned config lookup order:

1. `--config /path/to/config.yaml`
2. `FRIDAY_CONFIG=/path/to/config.yaml`
3. OS user config directory
4. built-in package templates

---

## Config Template Baseline

Friday Chat already has two example config files that should be treated as the
baseline for user customization:

- `config.example.yaml`: the main runtime, model, memory, tool, transcript,
  telemetry, finance, security, session, and speech configuration template.
- `cli-config.example.yaml`: the terminal display, banner, prompt, response,
  icon, and spinner configuration template.

Installed users should edit copies of these files, not the package templates
themselves.

Installed-package behavior:

1. Ship the templates inside the wheel as package resources:

   ```text
   site-packages/friday_chat/config_templates/config.example.yaml
   site-packages/friday_chat/config_templates/cli-config.example.yaml
   ```

   The exact `site-packages` parent directory is managed by `uv` and varies by
   operating system, Python version, and whether the user ran `uvx`,
   `uv tool install`, or `uv run --with`. The stable import-resource path is:

   ```text
   friday_chat.config_templates/config.example.yaml
   friday_chat.config_templates/cli-config.example.yaml
   ```

2. `friday-chat init` copies those package-resource templates into the user
   config directory:

   ```text
   ~/.config/friday/config.yaml
   ~/.config/friday/cli-config.yaml
   ```

   On Windows:

   ```text
   %APPDATA%\Friday\config.yaml
   %APPDATA%\Friday\cli-config.yaml
   ```

3. Users customize the copied files in the user config directory.

To print the template directory from an installed or temporary Friday Chat
environment:

```bash
uv run --with friday-chat python -c "from importlib.resources import files; print(files('friday_chat.config_templates'))"
```

Use this path for inspection only. Edit the copies under the user config
directory.

Alpha artifact note:

- The source checkout also contains docs-facing copies at
  `packages/friday-chat/config.example.yaml` and
  `packages/friday-chat/cli-config.example.yaml`.
- Rebuilt and future `friday-chat` wheels should include the package-resource
  copies under `friday_chat/config_templates/`.
- Already-built alpha artifacts from before the package-resource change may not
  include these templates.
- Until `friday-chat init` is implemented, users should use the manual copy
  commands in Step 4 and Step 5 to copy package-resource templates into the
  user config directory. If they are working from a source checkout, they may
  also copy the docs-facing examples directly.

---

## Step 1: Install uv

Install `uv` with the official standalone installer.

macOS and Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If `curl` is unavailable:

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart your terminal, then verify:

```bash
uv --version
uvx --version
```

If installed tools are not on your `PATH`, run:

```bash
uv tool update-shell
```

Restart the terminal again after updating shell configuration.

---

## Step 2: Create Config Directories

macOS and Linux:

```bash
mkdir -p ~/.config/friday
mkdir -p ~/.local/share/friday/vector
mkdir -p ~/.local/share/friday/exports
mkdir -p ~/.local/share/friday/backups
mkdir -p ~/.local/share/friday/quarantine
mkdir -p ~/.local/share/friday/reorganization_logs
mkdir -p ~/.local/share/friday/speech
mkdir -p ~/.cache/friday
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$env:APPDATA\Friday" | Out-Null
New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\Friday\vector" | Out-Null
New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\Friday\exports" | Out-Null
New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\Friday\backups" | Out-Null
New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\Friday\quarantine" | Out-Null
New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\Friday\reorganization_logs" | Out-Null
New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\Friday\speech" | Out-Null
New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\Friday\cache" | Out-Null
```

The current source template uses relative `.friday/...` paths. For installed
desktop use, replace those relative paths with stable user data paths before
running Friday Chat.

---

## Step 3: Configure API Keys

Do not put literal API keys in `config.yaml`. Store secrets in environment
variables and reference them from YAML with `${NAME}` placeholders.

The current Friday config shape commonly uses `FRIDAY_*` variables:


| Variable                      | Used for                                  |
| ----------------------------- | ----------------------------------------- |
| `FRIDAY_LLM_API_KEY`          | Primary chat model provider               |
| `FRIDAY_EMBEDDING_API_KEY`    | Embedding provider, if separate from chat |
| `FRIDAY_SERPER_API_KEY`       | Optional web search tools                 |
| `FRIDAY_LANGFUSE_PUBLIC_KEY`  | Optional telemetry                        |
| `FRIDAY_LANGFUSE_SECRET_KEY`  | Optional telemetry                        |
| `FRIDAY_ELEVENLABS_API_KEY`   | Optional speech output                    |
| `FRIDAY_PICOVOICE_ACCESS_KEY` | Optional speech input                     |


macOS and Linux, current shell:

```bash
export FRIDAY_LLM_API_KEY="..."
export FRIDAY_EMBEDDING_API_KEY="..."
```

macOS and Linux, persistent shell profile:

```bash
printf '\nexport FRIDAY_LLM_API_KEY="..."\n' >> ~/.zshrc
printf 'export FRIDAY_EMBEDDING_API_KEY="..."\n' >> ~/.zshrc
source ~/.zshrc
```

Use `~/.bashrc` instead of `~/.zshrc` when Bash is your login shell.

Windows PowerShell, current shell:

```powershell
$env:FRIDAY_LLM_API_KEY = "..."
$env:FRIDAY_EMBEDDING_API_KEY = "..."
```

Windows PowerShell, persistent user environment:

```powershell
[Environment]::SetEnvironmentVariable("FRIDAY_LLM_API_KEY", "...", "User")
[Environment]::SetEnvironmentVariable("FRIDAY_EMBEDDING_API_KEY", "...", "User")
```

Open a new terminal after setting persistent Windows environment variables.

---

## Step 4: Create `config.yaml`

Create the main Friday config file from the installed package template.

Current manual copy command for macOS and Linux:

```bash
uv run --with friday-chat python - <<'PY'
from importlib.resources import files
from pathlib import Path

template = files("friday_chat.config_templates").joinpath("config.example.yaml")
target = Path.home() / ".config" / "friday" / "config.yaml"
target.parent.mkdir(parents=True, exist_ok=True)

if target.exists():
    print(f"exists: {target}")
else:
    target.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"created: {target}")
PY
```

Current manual copy command for Windows PowerShell:

```powershell
$script = @'
from importlib.resources import files
from pathlib import Path
import os

template = files("friday_chat.config_templates").joinpath("config.example.yaml")
target = Path(os.environ["APPDATA"]) / "Friday" / "config.yaml"
target.parent.mkdir(parents=True, exist_ok=True)

if target.exists():
    print(f"exists: {target}")
else:
    target.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"created: {target}")
'@

uv run --with friday-chat python -c $script
```

Then edit the copied config.

macOS and Linux:

```bash
$EDITOR ~/.config/friday/config.yaml
```

Windows PowerShell:

```powershell
notepad "$env:APPDATA\Friday\config.yaml"
```

The installed package template should be the baseline. The following starter
snippet shows the current Friday-style section names and the expected
environment-variable placeholder pattern:

```yaml
# Friday Chat desktop configuration.
# Keep secrets in environment variables, not in this file.

logging:
  level: INFO
  extraction_debug: false
  extraction_rejections: true
  extraction_rejections_file: .friday/extraction_rejections.log
  tools_debug: false

llm:
  api_base: https://api.moonshot.ai/v1
  api_key: ${FRIDAY_LLM_API_KEY}
  model: moonshot/kimi-k3
  temperature: 1
  top_p: 0.95
  top_k: 40
  max_tokens: 20000
  max_retries: 3
  timeout_seconds: 120.0
  thinking: true

embedding:
  api_base: https://api.openai.com/v1
  api_key: ${FRIDAY_EMBEDDING_API_KEY}
  model: text-embedding-3-small
  timeout_seconds: 60.0

extraction:
  model: openai/qwen3.6-35b-a3b-mlx
  api_base: http://127.0.0.1:1234/v1
  api_key: lm-studio
  temperature: 0.0
  max_tokens: 4000
  timeout_seconds: 90.0
  interval: 3
  rejection_log: .friday/vector/extraction_rejections.log
  ontology:
    node_types:
      person:
        description: A human individual
      organization:
        description: A company, institution, or group
      technology:
        description: A software tool, language, framework, or hardware
      location:
        description: A physical or virtual place
      product:
        description: A named product, service, or system
      document:
        description: A named document, spec, or reference
    edge_relations:
      association:
        - RELATES_TO
        - PART_OF
      usage:
        - USES
        - DEPENDS_ON

memory:
  collection_name: friday_memory
  persist_directory: ~/.local/share/friday/vector
  context_window: 128000
  output_buffer: 20000
  max_history_turns: 20
  consolidate_after_turns: 8
  retrieval:
    enabled: true
    max_items: 8
  supporting_context:
    enabled: true
  cache:
    enabled: true
  priming:
    enabled: true

transcript:
  export_directory: ~/.local/share/friday/exports
  capture_raw_prompts: false

chat:
  user_name: User
  assistant_name: Friday
  system_prompt: You are Friday.

maintenance:
  backup_directory: ~/.local/share/friday/backups
  pruning:
    enabled: false
  synthesis:
    enabled: false
  fact_checking:
    enabled: false
  llm: {}
  prompts: {}

lifecycle:
  enabled: false

smart_file:
  auto_chunk_threshold: 12000
  chunk_size: 4000
  chunk_overlap: 400
  default_add_to_context: true
  default_store_to_memory: true
  llm: {}
  prompts: {}

tools:
  enabled: true
  loop:
    enabled: true
  registry: {}
  context: {}

web:
  serper_api_key: null
  reader: {}

langfuse:
  enabled: false
  public_key: null
  secret_key: null

finance:
  massive:
    enabled: false

security:
  sanitization:
    enabled: true

session:
  run_maintenance_on_exit: false

speech:
  enabled: false
```

Windows users should adjust the path values if the current runtime does not
expand `~` as expected. Use absolute paths such as:

```yaml
memory:
  persist_directory: C:\Users\YOUR-NAME\AppData\Local\Friday\vector

transcript:
  export_directory: C:\Users\YOUR-NAME\AppData\Local\Friday\exports
```

---

## Step 5: Create `cli-config.yaml`

Create the optional terminal display config from the installed package template.
It should live next to `config.yaml` so Friday Chat can auto-discover it.

Current manual copy command for macOS and Linux:

```bash
uv run --with friday-chat python - <<'PY'
from importlib.resources import files
from pathlib import Path

template = files("friday_chat.config_templates").joinpath(
    "cli-config.example.yaml"
)
target = Path.home() / ".config" / "friday" / "cli-config.yaml"
target.parent.mkdir(parents=True, exist_ok=True)

if target.exists():
    print(f"exists: {target}")
else:
    target.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"created: {target}")
PY
```

Current manual copy command for Windows PowerShell:

```powershell
$script = @'
from importlib.resources import files
from pathlib import Path
import os

template = files("friday_chat.config_templates").joinpath(
    "cli-config.example.yaml"
)
target = Path(os.environ["APPDATA"]) / "Friday" / "cli-config.yaml"
target.parent.mkdir(parents=True, exist_ok=True)

if target.exists():
    print(f"exists: {target}")
else:
    target.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"created: {target}")
'@

uv run --with friday-chat python -c $script
```

Then edit the copied display config.

macOS and Linux:

```bash
$EDITOR ~/.config/friday/cli-config.yaml
```

Windows PowerShell:

```powershell
notepad "$env:APPDATA\Friday\cli-config.yaml"
```

The installed package template should be the baseline. The following starter
snippet shows the expected display customization shape:

```yaml
theme:
  error: "bold red"
  warning: "bold yellow"
  success: "bold green"
  info: "bold blue"
  muted: "dim"
  highlight: "bold cyan"

icons:
  error: "X"
  warning: "!"
  success: "OK"
  info: "i"

banner:
  enabled: true
  style: "ascii"
  title: "Friday"
  subtitle: "{assistant_name} CLI"
  show_version: true
  border_style: "bright_cyan"
  title_style: "bold cyan"
  subtitle_style: "dim white"
  version_style: "dim cyan"
  tips_enabled: true
  tips_title: "Tips for getting started:"
  tips:
    - "Ask questions, edit files, or run commands."
    - "Be specific for the best results."
    - "`/help` for more information."

prompt:
  style: "bold cyan"
  name_style: "bold cyan"
  separator_style: "white"
  continuation_style: "gray"

response:
  prefix: true
  name_style: "bold bright_green"
  separator_style: "bright_green"
  text_style: "bright_green"

spinner:
  spinner_type: "dots12"
  text_style: "bold green"
  spinner_style: "bright white"
  randomize: true
  thinking_messages:
    - "Thinking..."
    - "Working..."
  tool_messages:
    - "Using tools..."
    - "Checking context..."
```

When `friday-chat` is started with `--config`, it automatically looks for a
sibling `cli-config.yaml` in the same directory. Use `--cli-config` only when
the display config lives elsewhere.

---

## Step 6: Install The Friday Chat Executable

Use this path when you want a persistent local `friday-chat` command.

Publication note:

- This command requires the `friday-chat` distribution and its Friday framework
  dependencies to be available on PyPI.
- During an alpha reservation or pre-publication window, run from a source
  checkout with `uv run friday-chat --config <path> --runtime real` instead.

```bash
uv tool install friday-chat
uv tool update-shell
```

Restart your terminal, then verify:

```bash
friday-chat --version
friday-chat --help
```

To install a specific alpha version:

```bash
uv tool install friday-chat==0.1.0a0
```

Current alpha run command:

macOS and Linux:

```bash
friday-chat --config ~/.config/friday/config.yaml --runtime real
```

Windows PowerShell:

```powershell
friday-chat --config "$env:APPDATA\Friday\config.yaml" --runtime real
```

Alternative with environment variables:

macOS and Linux:

```bash
export FRIDAY_CONFIG="$HOME/.config/friday/config.yaml"
export FRIDAY_CHAT_RUNTIME=real
friday-chat --config "$FRIDAY_CONFIG"
```

Windows PowerShell:

```powershell
$env:FRIDAY_CONFIG = "$env:APPDATA\Friday\config.yaml"
$env:FRIDAY_CHAT_RUNTIME = "real"
friday-chat --config "$env:FRIDAY_CONFIG"
```

---

## Step 7: Create A Wrapper Launcher For `uvx`

Use this path when you do not want to install a persistent Friday executable.
The wrapper invokes `uvx friday-chat` and points it at stable user config.

macOS and Linux launcher:

```bash
mkdir -p ~/.local/bin
$EDITOR ~/.local/bin/friday-chat-uvx
```

Paste:

```bash
#!/usr/bin/env bash
set -euo pipefail

export FRIDAY_CONFIG="${FRIDAY_CONFIG:-$HOME/.config/friday/config.yaml}"
export FRIDAY_CHAT_RUNTIME="${FRIDAY_CHAT_RUNTIME:-real}"

exec uvx friday-chat --config "$FRIDAY_CONFIG" --runtime "$FRIDAY_CHAT_RUNTIME" "$@"
```

Make it executable:

```bash
chmod +x ~/.local/bin/friday-chat-uvx
```

Run:

```bash
friday-chat-uvx
```

Windows PowerShell launcher:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\bin" | Out-Null
notepad "$env:USERPROFILE\bin\friday-chat-uvx.ps1"
```

Paste:

```powershell
$ErrorActionPreference = "Stop"

if (-not $env:FRIDAY_CONFIG) {
    $env:FRIDAY_CONFIG = Join-Path $env:APPDATA "Friday\config.yaml"
}

if (-not $env:FRIDAY_CHAT_RUNTIME) {
    $env:FRIDAY_CHAT_RUNTIME = "real"
}

uvx friday-chat --config $env:FRIDAY_CONFIG --runtime $env:FRIDAY_CHAT_RUNTIME @args
```

Run:

```powershell
& "$env:USERPROFILE\bin\friday-chat-uvx.ps1"
```

If PowerShell blocks local scripts, allow scripts for the current user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

## Step 8: Planned First-Run Flow

The planned desktop experience should remove the manual file creation steps:

```bash
uvx friday-chat init
uvx friday-chat doctor
uvx friday-chat
```

Planned command responsibilities:

| Command | Responsibility |
| --- | --- |
| `init` | Write editable `config.yaml` and `cli-config.yaml` into the user config directory |
| `doctor` | Validate config, required environment variables, data paths, optional dependencies, and safe provider reachability checks |
| `friday-chat` | Start the app using the resolved config |

Expected missing-config failure:

```text
No Friday config found.
Run: uvx friday-chat init
Config path: ~/.config/friday/config.yaml
```

Implementation requirements for this planned flow:

- Package templates must ship inside `friday_chat` as package resources.
- `init` should copy `config.example.yaml` to `config.yaml` and
  `cli-config.example.yaml` to `cli-config.yaml` in the user config directory.
- `init` should report the installed package-resource source and the editable
  destination path for each copied file.
- `uvx` must never depend on files in the source checkout.
- User config and data must live outside the temporary tool environment.
- `FRIDAY_CONFIG` should work as an override.
- `--config` should remain the most explicit override.
- `doctor` should report missing environment variables without printing secret
  values.

---

## Step 9: Verify The Deployment

Check the executable:

```bash
friday-chat --version
friday-chat --help
```

Check required environment variables without printing their values:

macOS and Linux:

```bash
test -n "${FRIDAY_LLM_API_KEY:-}" && echo "FRIDAY_LLM_API_KEY is set"
```

Windows PowerShell:

```powershell
if ($env:FRIDAY_LLM_API_KEY) { "FRIDAY_LLM_API_KEY is set" }
```

Run the current alpha:

macOS and Linux:

```bash
friday-chat --config ~/.config/friday/config.yaml --runtime real
```

Windows PowerShell:

```powershell
friday-chat --config "$env:APPDATA\Friday\config.yaml" --runtime real
```

Run through the `uvx` launcher:

macOS and Linux:

```bash
friday-chat-uvx --version
```

Windows PowerShell:

```powershell
& "$env:USERPROFILE\bin\friday-chat-uvx.ps1" --version
```

---

## Troubleshooting

### `uv` or `uvx` is not found

Run:

```bash
uv tool update-shell
```

Then restart the terminal. Confirm the install location with:

```bash
uv tool dir --bin
```

### `friday-chat` is not found after `uv tool install`

Run:

```bash
uv tool list
uv tool update-shell
```

Restart the terminal and try again.

### The app exits with config errors

Confirm the config path exists:

macOS and Linux:

```bash
ls -l ~/.config/friday/config.yaml
```

Windows PowerShell:

```powershell
Test-Path "$env:APPDATA\Friday\config.yaml"
```

Then run with an explicit config path:

```bash
friday-chat --config /path/to/config.yaml --runtime real
```

### Environment placeholders fail to resolve

The config loader expands `${VARIABLE_NAME}` placeholders from the process
environment. Set the missing variable in the same terminal before starting
Friday, or set it persistently and open a new terminal.

Do not paste secret values into diagnostics, issue reports, or committed files.

### `uvx friday-chat` downloads packages every time

`uvx` uses isolated environments and may refresh or recreate them. For repeated
daily use, prefer:

```bash
uv tool install friday-chat
```

Use the `uvx` wrapper when you want an always-fresh launcher or do not want a
persistent Friday command installed.

---

## References

- uv installation: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
- uv tool commands: [https://docs.astral.sh/uv/reference/cli/#uv-tool](https://docs.astral.sh/uv/reference/cli/#uv-tool)
- Installed Friday Chat config template:
  `friday_chat.config_templates/config.example.yaml`
- Installed Friday Chat CLI display template:
  `friday_chat.config_templates/cli-config.example.yaml`
- Source checkout config template:
  `packages/friday-chat/config.example.yaml`
- Source checkout CLI display template:
  `packages/friday-chat/cli-config.example.yaml`
