#!/usr/bin/env bash
# C2 Safe Run — Chạy code công nghệ trong môi trường cách ly
# Usage: bash scripts/safe_run.sh vault/technologies/T000001-slug/versions/v1

set -euo pipefail

TARGET="${1:-}"

if [ -z "$TARGET" ]; then
  echo "Usage: bash scripts/safe_run.sh <technology-version-dir>"
  echo "Example: bash scripts/safe_run.sh vault/technologies/T000001-my-tech/versions/v1"
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FULL_PATH="$REPO_ROOT/$TARGET"

if [ ! -d "$FULL_PATH" ]; then
  echo "[ERROR] Thư mục không tồn tại: $FULL_PATH"
  exit 1
fi

MANIFEST="$FULL_PATH/manifest.yaml"
if [ ! -f "$MANIFEST" ]; then
  echo "[ERROR] Thiếu manifest.yaml trong $FULL_PATH"
  exit 1
fi

echo "=================================================="
echo "  C2 SAFE RUN"
echo "  Target: $TARGET"
echo "=================================================="

# Đọc run_command từ manifest (cần python + pyyaml)
RUN_CMD=$(python3 -c "
import yaml, sys
with open('$MANIFEST') as f:
    m = yaml.safe_load(f)
print(m.get('execution', {}).get('test_command', 'python -m pytest tests -v'))
" 2>/dev/null || echo "python -m pytest tests -v")

echo "  Run command: $RUN_CMD"
echo ""

# Kiểm tra Docker
if command -v docker &>/dev/null; then
  echo "[INFO] Docker khả dụng. Chạy trong Docker sandbox..."
  docker run --rm \
    --network none \
    --cpus "1.0" \
    --memory "512m" \
    --read-only \
    --tmpfs /tmp:rw,noexec,nosuid,size=64m \
    -v "$FULL_PATH":/work:ro \
    -w /work \
    python:3.12-slim \
    sh -c "pip install -r requirements.txt -q 2>/dev/null || true; $RUN_CMD"
  EXIT_CODE=$?
else
  echo "[WARN] Docker không khả dụng. Chạy trực tiếp — RỦI RO CAO HƠN."
  echo "[WARN] Chỉ chạy code bạn đã đọc và hiểu."
  echo ""
  read -r -p "Tiếp tục? (yes/no): " confirm
  if [ "$confirm" != "yes" ]; then
    echo "Hủy."
    exit 0
  fi
  cd "$FULL_PATH"
  eval "$RUN_CMD"
  EXIT_CODE=$?
fi

echo ""
echo "=================================================="
if [ $EXIT_CODE -eq 0 ]; then
  echo "  [PASS] Exit code: 0"
else
  echo "  [FAIL] Exit code: $EXIT_CODE"
fi
echo "=================================================="
exit $EXIT_CODE
