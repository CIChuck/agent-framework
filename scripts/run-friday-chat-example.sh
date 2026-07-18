#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

ENV_FILE="${REPO_ROOT}/scripts/source-friday-chat-example-env.sh"
CONFIG_FILE="${REPO_ROOT}/packages/friday-chat/config.example.yaml"
CLI_CONFIG_FILE="${REPO_ROOT}/packages/friday-chat/cli-config.example.yaml"
FRIDAY_CHAT="${REPO_ROOT}/.venv/bin/friday-chat"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing environment file: ${ENV_FILE}" >&2
  exit 1
fi

if [[ ! -x "${FRIDAY_CHAT}" ]]; then
  echo "Missing Friday Chat executable: ${FRIDAY_CHAT}" >&2
  echo "Run: uv sync --all-extras" >&2
  exit 1
fi

cd "${REPO_ROOT}"
source "${ENV_FILE}"
if [[ -f "${CLI_CONFIG_FILE}" ]]; then
  exec "${FRIDAY_CHAT}" \
    --runtime real \
    --config "${CONFIG_FILE}" \
    --cli-config "${CLI_CONFIG_FILE}" \
    "$@"
fi

exec "${FRIDAY_CHAT}" --runtime real --config "${CONFIG_FILE}" "$@"
