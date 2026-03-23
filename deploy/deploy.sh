#!/bin/bash
# Manual deploy to Vultr VPS
# Usage: ./deploy/deploy.sh [host] [user]
#
# Prerequisites:
#   - SSH key access to the server (ssh-copy-id root@YOUR_IP)
#   - Docker installed on the server (run setup-vultr.sh first)
#
# Examples:
#   ./deploy/deploy.sh                          # uses defaults
#   ./deploy/deploy.sh 107.191.49.133           # custom host
#   ./deploy/deploy.sh 107.191.49.133 ubuntu    # custom host and user

set -euo pipefail

HOST="${1:-${DEPLOY_HOST:?Set DEPLOY_HOST or pass host as first argument}}"
USER="${2:-${DEPLOY_USER:-root}}"
REMOTE_DIR="/opt/clearprice"
BRANCH="${DEPLOY_BRANCH:-master}"

echo "=== Deploying to ${USER}@${HOST} ==="
echo "    Remote dir: ${REMOTE_DIR}"
echo "    Branch: ${BRANCH}"
echo ""

ssh "${USER}@${HOST}" bash -s -- "${REMOTE_DIR}" "${BRANCH}" <<'REMOTE_SCRIPT'
set -euo pipefail
REMOTE_DIR="$1"
BRANCH="$2"

cd "${REMOTE_DIR}" || { echo "Error: ${REMOTE_DIR} not found. Run setup-vultr.sh first."; exit 1; }

echo "--- Pulling latest code (${BRANCH}) ---"
git fetch origin "${BRANCH}"
git checkout "${BRANCH}"
git reset --hard "origin/${BRANCH}"

echo "--- Rebuilding containers ---"
docker compose down
docker compose up -d --build

echo ""
echo "=== Deploy complete ==="
docker compose ps
REMOTE_SCRIPT
