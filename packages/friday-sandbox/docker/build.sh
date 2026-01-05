#!/bin/bash
# Build the Friday Sandbox Python Docker image
#
# Usage:
#   ./build.sh           # Build with default tag
#   ./build.sh v1.0.0    # Build with specific version tag
#
# Ref: docs/specs/sandbox_specifications.md - Section 9: Docker Image

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="friday-sandbox-python"
VERSION="${1:-latest}"

echo "Building Friday Sandbox Python image..."
echo "  Image: ${IMAGE_NAME}:${VERSION}"

docker build \
    -t "${IMAGE_NAME}:${VERSION}" \
    -f "${SCRIPT_DIR}/Dockerfile.python" \
    "${SCRIPT_DIR}"

# Also tag as latest if version was specified
if [ "${VERSION}" != "latest" ]; then
    docker tag "${IMAGE_NAME}:${VERSION}" "${IMAGE_NAME}:latest"
    echo "  Also tagged as: ${IMAGE_NAME}:latest"
fi

echo ""
echo "Build complete!"
echo ""
echo "Test the image with:"
echo "  docker run --rm ${IMAGE_NAME}:${VERSION} python -c 'print(\"Hello from Friday Sandbox!\")'"
