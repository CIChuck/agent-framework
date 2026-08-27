#!/usr/bin/env zsh
set -euo pipefail

artifact_dir="${ARTIFACT_DIR:-dist/pypi-reservation-0.1.0a0}"
version="${FRIDAY_RESERVATION_VERSION:-0.1.0a0}"
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
        ReasoningConfig,
        ReasoningMode,
        TransportTarget,
    )

    async def fake_completion(**kwargs):
        expected = {"enable_thinking": False}
        actual = kwargs.get("extra_body", {}).get("chat_template_kwargs")
        if actual != expected:
            raise RuntimeError(f"unexpected translated reasoning fields: {actual!r}")
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
        finally:
            litellm.acompletion = original

    asyncio.run(smoke_typed_request())
    LiteLLMService(model_name="gpt-4")
    print("typed fake-transport and legacy constructor smokes OK")
PY

"${tmpdir}/venv/bin/python" -m pip check

if [[ -n "${console_script}" ]]; then
  "${tmpdir}/venv/bin/${console_script}" --help >"${tmpdir}/console-help.txt"
  head -n 1 "${tmpdir}/console-help.txt"
fi
