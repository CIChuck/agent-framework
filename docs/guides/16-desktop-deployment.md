---
title: Desktop deployment with uv
description: Install a pinned Chat executable, keep configuration/state outside tool environments and launch explicitly.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# Desktop deployment with uv

This guide installs the terminal application on a user-owned machine. It is
not a background daemon or graphical desktop application. Use Python 3.13.4+
and **`friday-chat==0.1.0a3`**. First run the [offline quick start](02-getting-started.md#run-an-offline-chat-session)
before connecting models or existing state.

## Choose an installation mode

| Mode | Command | Environment lifetime |
| --- | --- | --- |
| Persistent tool | `uv tool install --python 3.13 "friday-chat==0.1.0a3"` | Managed installation with an executable on the tools PATH |
| On-demand tool | `uvx --python 3.13 --from "friday-chat==0.1.0a3" friday-chat --help` | Isolated managed tool environment; uv can cache/reuse it |
| Application venv | [pip/venv setup](02-getting-started.md#prerequisites-and-installation) | Explicit environment you own |

`uvx` is `uv tool run`; its environment is disposable from the application's
perspective, but it does not necessarily download packages on every invocation.
Never put editable configuration, keys, vector data or transcripts inside a
managed tool environment. See the official [uv tools documentation](https://docs.astral.sh/uv/concepts/tools/).

Install uv using [its official installation instructions](https://docs.astral.sh/uv/getting-started/installation/)
for your platform. After installation:

```bash
uv --version
uv python install 3.13
uv tool install --python 3.13 "friday-chat==0.1.0a3"
uv tool dir --bin
friday-chat --version
friday-chat --help
```

If needed, `uv tool update-shell` configures the tools PATH; restart the terminal
after a shell configuration change. No provider request is needed for version/help.

## Stable paths

The following are **operator-selected conventions**, not automatic Chat lookup:

| Purpose | macOS/Linux example | Windows example |
| --- | --- | --- |
| Editable configuration | `~/.config/friday/` | `%APPDATA%\Friday\` |
| Persistent data | `~/.local/share/friday/` | `%LOCALAPPDATA%\Friday\` |
| Cache/scratch | `~/.cache/friday/` | `%LOCALAPPDATA%\Friday\cache\` |

Keep install, config, workspace and state roles distinct. Headless Runtime has
additional root containment rules; these path conventions alone are not a
complete `RuntimeConfig`. Keep stores and exports outside the repository and
outside uv's managed package directories.

## Copy and edit configuration

Use the installed `friday_chat.config_templates` resources, which are included
in alpha3. The [getting-started copy script](02-getting-started.md#prepare-a-real-session)
creates a new directory without overwriting existing files. You can run that
script with an explicit interpreter environment, for example after saving it
as `copy_templates.py`:

```bash
uv run --no-project --python 3.13 --with "friday-chat==0.1.0a3" python copy_templates.py
```

Review the copied templates or use [the smaller canonical configuration](10-configuration.md#canonical-model-library).
The broad template contains multiple providers, optional placeholders, legacy
Langfuse enablement and raw-content retention choices. Remove/rebind unused
services and placeholders rather than supplying unnecessary credentials.

Set absolute memory/export/log paths in the main YAML. Model-library relative
paths resolve against that YAML file; other Chat paths can depend on process
cwd. Edit the display file only for terminal appearance. Keep credentials in
the process environment or your secret-management system; Chat does not load
`.env` automatically.

No `friday-chat init`, `doctor`, automatic `FRIDAY_CONFIG` lookup or implicit OS
config-directory search is implemented. Always pass the intended `--config`.

## Launch explicitly

These are **live launch commands** once you have configured models and state.
macOS/Linux, with the convention above:

```bash
friday-chat --config "$HOME/.config/friday/config.yaml" --cli-config "$HOME/.config/friday/cli-config.yaml" --runtime real
```

Windows PowerShell:

```powershell
friday-chat --config "$env:APPDATA\Friday\config.yaml" --cli-config "$env:APPDATA\Friday\cli-config.yaml" --runtime real
```

For an on-demand launch, use the same arguments after
`uvx --python 3.13 --from "friday-chat==0.1.0a3" friday-chat`.
Ensure `FRIDAY_CHAT_RUNTIME` is unset or intentionally selected: it takes
precedence over the command's `--runtime` argument.

A wrapper may supply these explicit paths, but should not contain credentials,
overwrite configuration, migrate stores or silently switch runtime mode.
GUI/launcher environments may lack variables present in your terminal; configure
their environment deliberately. Use a stable working directory or absolute
data paths so launching from another folder cannot select a different store.

## Verify the installation in stages

1. Run version/help and a new offline fake session.
2. Load the intended config/model library without constructing services.
3. Run a real session against your selected chat and embedding routes.
4. Inspect `/sessions`, `/transcript`, `/memory` and the configured data paths.
5. Exit normally, then restart and verify durable records independently of model
   recollection. Enable optional tools/MCP only after their separate checks.

Chat's current speech and orchestration adapters remain deterministic even in
real mode. The standalone Speech package and headless agent APIs have separate
setup; do not use Chat command success as proof of live audio or specialist agents.

## Upgrade and rollback

Pin the intended version explicitly. Before changing versions, stop owned work,
save configuration and take a supported consistent backup of persistent data.
Validate the candidate with disposable state before opening an existing store.
Replacing an executable is not a store migration or proof of format compatibility.

Do not clean uv environments as a way to repair state. Cache cleanup, package
updates and data recovery have different effects. Restoring an older application
may also require its compatible configuration/state snapshot.

## Troubleshooting launch problems

| Symptom | Check |
| --- | --- |
| Executable missing | `uv tool dir --bin`, shell PATH and selected environment |
| Config missing | Explicit absolute path, spelling and user permissions |
| Credential reference missing | Launcher process environment and unused ordinary placeholders |
| Wrong runtime mode | `FRIDAY_CHAT_RUNTIME` precedence |
| New empty memory on restart | cwd-dependent paths, changed config or selected session |
| Audio command appears successful without sound | Chat still uses its deterministic speech adapter; use the standalone package/harness |

See [troubleshooting](13-troubleshooting.md) for model, storage and cleanup failures.

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
