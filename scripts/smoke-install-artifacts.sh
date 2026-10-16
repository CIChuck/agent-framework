#!/usr/bin/env zsh
set -euo pipefail

artifact_dir="${ARTIFACT_DIR:-dist/friday-package-cohort-0.1.0a3}"
version="${FRIDAY_RESERVATION_VERSION:-0.1.0a3}"
distribution="${FRIDAY_SMOKE_DISTRIBUTION:-friday-chat}"
import_package="${FRIDAY_SMOKE_IMPORT:-friday_chat}"
console_script="${FRIDAY_SMOKE_CONSOLE:-friday-chat}"
python_bin="${PYTHON_BIN:-python3}"
install_python_bin="${INSTALL_PYTHON_BIN:-python3}"
offline=false
wheel_only=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --artifact-dir)
      artifact_dir="$2"
      shift 2
      ;;
    --version)
      version="$2"
      shift 2
      ;;
    --package)
      distribution="$2"
      shift 2
      ;;
    --import-package)
      import_package="$2"
      shift 2
      ;;
    --console-script)
      console_script="$2"
      shift 2
      ;;
    --offline)
      offline=true
      shift
      ;;
    --wheel-only)
      wheel_only=true
      shift
      ;;
    *)
      print -u2 "unknown argument: $1"
      exit 2
      ;;
  esac
done

tmpdir="$(mktemp -d /private/tmp/friday-wheel-smoke.XXXXXX)"
print "smoke venv: ${tmpdir}"

if [[ "${wheel_only}" == true ]]; then
  target_dir="${tmpdir}/target"
  mkdir -p "${target_dir}"
  "${install_python_bin}" -m pip install \
    --quiet \
    --no-deps \
    --no-index \
    --target "${target_dir}" \
    "${artifact_dir}"/*.whl

  PYTHONPATH="${target_dir}:${PYTHONPATH:-}" "${python_bin}" - <<'PY'
import importlib
import importlib.metadata

modules = [
    "friday_core",
    "friday_telemetry",
    "friday_llm",
    "friday_transcript",
    "friday_memory",
    "friday_agent",
    "friday_runtime",
    "friday_cli",
    "friday_tools",
    "friday_chat",
]

for module in modules:
    importlib.import_module(module)

entry_points = importlib.metadata.distribution("friday-chat").entry_points
if not any(entry_point.name == "friday-chat" for entry_point in entry_points):
    raise SystemExit("friday-chat console entry point missing from wheel metadata")

print("wheel-only imports OK")
PY
  exit 0
fi

"${python_bin}" -m venv "${tmpdir}/venv"
pip_cmd=("${tmpdir}/venv/bin/python" -m pip install --quiet --find-links "${artifact_dir}")

if [[ "${offline}" == true ]]; then
  pip_cmd+=(--no-index)
fi

"${pip_cmd[@]}" "${distribution}==${version}"

FRIDAY_SMOKE_DISTRIBUTION="${distribution}" \
FRIDAY_SMOKE_IMPORT="${import_package}" \
"${tmpdir}/venv/bin/python" - <<'PY'
import asyncio
import importlib
import importlib.metadata
import os
import re
import tempfile
from pathlib import Path
from types import SimpleNamespace

distribution = os.environ["FRIDAY_SMOKE_DISTRIBUTION"]
import_package = os.environ["FRIDAY_SMOKE_IMPORT"]
importlib.import_module(import_package)
installed_version = importlib.metadata.version(distribution)
print(f"{distribution}=={installed_version} import OK")

if distribution == "friday-framework-llm":
    import litellm
    from friday_llm import (
        ChatCompletionRequest,
        GenerationOverrides,
        LiteLLMService,
        ModelTarget,
        NamedToolChoice,
        NamedToolChoiceFunction,
        ReasoningConfig,
        ReasoningMode,
        TransportTarget,
    )

    async def fake_completion(**kwargs):
        if kwargs.get("tools"):
            if kwargs.get("tool_choice") != "required":
                raise RuntimeError("LM Studio named tool choice was not translated")
            tool_names = [tool["function"]["name"] for tool in kwargs["tools"]]
            if tool_names != ["selected"]:
                raise RuntimeError(f"unexpected selected tool schemas: {tool_names!r}")
        else:
            expected = {"enable_thinking": False}
            actual = kwargs.get("extra_body", {}).get("chat_template_kwargs")
            if actual != expected:
                raise RuntimeError(
                    f"unexpected translated reasoning fields: {actual!r}"
                )
        message = SimpleNamespace(content="ok", reasoning_content=None, tool_calls=[])
        return SimpleNamespace(
            choices=[SimpleNamespace(message=message, finish_reason="stop")],
            model="qwen3.8-27b-mlx",
            usage=None,
        )

    async def smoke_typed_request():
        original = litellm.acompletion
        litellm.acompletion = fake_completion
        try:
            service = LiteLLMService(
                model_name="openai/qwen3.8-27b-mlx",
                transport_target=TransportTarget(
                    provider="openai_compatible",
                    dialect="openai_chat_completions",
                    serving_engine="lm_studio",
                ),
                model_target=ModelTarget(
                    model_id="qwen3.8-27b-mlx",
                    family="qwen3_8",
                    revision="artifact-smoke-1",
                ),
            )
            response = await service.chat_completion_request(
                ChatCompletionRequest(
                    messages=({"role": "user", "content": "fixed"},),
                    overrides=GenerationOverrides(
                        reasoning=ReasoningConfig(mode=ReasoningMode.DISABLED)
                    ),
                )
            )
            if response.content != "ok":
                raise RuntimeError("typed fake-transport smoke returned wrong content")
            await service.chat_completion_request(
                ChatCompletionRequest(
                    messages=({"role": "user", "content": "fixed"},),
                    tools=(
                        {
                            "type": "function",
                            "function": {
                                "name": "other",
                                "parameters": {"type": "object"},
                            },
                        },
                        {
                            "type": "function",
                            "function": {
                                "name": "selected",
                                "parameters": {"type": "object"},
                            },
                        },
                    ),
                    tool_choice=NamedToolChoice(
                        function=NamedToolChoiceFunction(name="selected")
                    ),
                )
            )
        finally:
            litellm.acompletion = original

    asyncio.run(smoke_typed_request())
    LiteLLMService(model_name="gpt-4")
    print("typed fake-transport and legacy constructor smokes OK")
elif distribution == "friday-chat":
    import importlib.resources

    import litellm
    import yaml
    import friday_chat
    from friday_chat.adapters import build_framework_chat_model
    from friday_chat.config import load_friday_py_config

    if friday_chat.__version__ != installed_version:
        raise RuntimeError(
            "friday_chat.__version__ does not match installed metadata: "
            f"{friday_chat.__version__!r} != {installed_version!r}"
        )

    template = importlib.resources.files("friday_chat.config_templates").joinpath(
        "config.example.yaml"
    )
    models_template = importlib.resources.files(
        "friday_chat.config_templates"
    ).joinpath("models-config.example.yaml")
    model_data = yaml.safe_load(models_template.read_text(encoding="utf-8"))
    for credential in model_data.get("credentials", {}).values():
        os.environ.setdefault(credential["env"], "artifact-smoke-secret")
    config_text = template.read_text(encoding="utf-8")
    for env_name in set(re.findall(r"\$\{([A-Z][A-Z0-9_]*)\}", config_text)):
        os.environ.setdefault(env_name, "artifact-smoke-value")
    with tempfile.TemporaryDirectory() as directory:
        template_directory = Path(directory)
        config_path = template_directory / "config.example.yaml"
        models_path = template_directory / "models-config.example.yaml"
        config_path.write_text(config_text, encoding="utf-8")
        models_path.write_text(
            models_template.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        template_config = load_friday_py_config(config_path)
    if template_config.diagnostics:
        raise RuntimeError("packaged Friday Chat template emitted config diagnostics")

    async def fake_chat_completion(**kwargs):
        if kwargs.get("model") != "moonshot/kimi-k3":
            raise RuntimeError(f"unexpected model: {kwargs.get('model')!r}")
        if "top_p" in kwargs:
            raise RuntimeError(f"unexpected top_p: {kwargs.get('top_p')!r}")
        if "top_k" in kwargs.get("extra_body", {}):
            raise RuntimeError(
                f"unexpected top_k: {kwargs.get('extra_body', {}).get('top_k')!r}"
            )
        message = SimpleNamespace(
            content="ok",
            reasoning_content=None,
            provider_specific_fields={
                "reasoning_content": "private artifact-smoke reasoning"
            },
            tool_calls=[],
        )
        usage = SimpleNamespace(
            prompt_tokens=1,
            completion_tokens=1,
            total_tokens=2,
            completion_tokens_details=None,
        )
        return SimpleNamespace(
            choices=[SimpleNamespace(message=message, finish_reason="stop")],
            model="kimi-k3",
            usage=usage,
        )

    async def smoke_chat_adapter():
        original = litellm.acompletion
        litellm.acompletion = fake_chat_completion
        try:
            response = await build_framework_chat_model(template_config).complete(
                [{"role": "user", "content": "fixed"}]
            )
            if response.content != "ok":
                raise RuntimeError("Friday Chat typed adapter returned wrong content")
            if response.reasoning_content != "private artifact-smoke reasoning":
                raise RuntimeError("provider reasoning metadata was not normalized")
        finally:
            litellm.acompletion = original

    asyncio.run(smoke_chat_adapter())
    print("packaged config and typed Friday Chat fake-transport smokes OK")
PY

"${tmpdir}/venv/bin/python" -m pip check

if [[ -n "${console_script}" ]]; then
  "${tmpdir}/venv/bin/${console_script}" --help >"${tmpdir}/console-help.txt"
  head -n 1 "${tmpdir}/console-help.txt"
  "${tmpdir}/venv/bin/${console_script}" --version
fi
