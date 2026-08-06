#!/usr/bin/env zsh
set -euo pipefail

artifact_dir="${ARTIFACT_DIR:-dist/pypi-reservation-0.1.0a0}"
version="${FRIDAY_RESERVATION_VERSION:-0.1.0a0}"
python_bin="${PYTHON_BIN:-python3}"
install_python_bin="${INSTALL_PYTHON_BIN:-python3}"
offline=false
wheel_only=false

while [[ $# -gt 0 ]]; do
  case "$1" in
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
pip_cmd=("${tmpdir}/venv/bin/python" -m pip install --find-links "${artifact_dir}")

if [[ "${offline}" == true ]]; then
  pip_cmd+=(--no-index)
fi

"${pip_cmd[@]}" "friday-chat==${version}"

"${tmpdir}/venv/bin/python" - <<'PY'
import importlib

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

print("imports OK")
PY

"${tmpdir}/venv/bin/friday-chat" --help >/tmp/friday-chat-help.txt
head -n 1 /tmp/friday-chat-help.txt
