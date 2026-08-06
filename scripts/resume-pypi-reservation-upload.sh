#!/usr/bin/env zsh
set -euo pipefail

artifact_dir="${ARTIFACT_DIR:-dist/pypi-reservation-0.1.0a0}"
delay_seconds="${PYPI_UPLOAD_DELAY_SECONDS:-60}"
version="${FRIDAY_RESERVATION_VERSION:-0.1.0a0}"

if [[ -z "${TWINE_USERNAME:-}" || -z "${TWINE_PASSWORD:-}" ]]; then
  print -u2 "TWINE_USERNAME and TWINE_PASSWORD must be set before running this script."
  print -u2 "For PyPI API tokens, use TWINE_USERNAME=__token__."
  exit 1
fi

remaining_packages=(
  friday_framework
)

for package_base in "${remaining_packages[@]}"; do
  print "UPLOAD ${package_base}"
  uv run --with twine twine upload \
    --non-interactive \
    --disable-progress-bar \
    "${artifact_dir}/${package_base}-${version}"*

  sleep "${delay_seconds}"
done
