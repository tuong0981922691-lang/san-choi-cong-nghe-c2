#!/usr/bin/env bash
# C2 Safe Run — Chạy code công nghệ trong môi trường cách ly 2 tầng
# Tầng 1: build image với mạng để cài requirements.txt
# Tầng 2: thực thi RUN_CMD với --network none (không mạng)
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
echo "  C2 SAFE RUN (2-stage sandbox)"
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
  echo "[INFO] Docker khả dụng. Chạy 2-stage sandbox..."

  # Tên image tạm duy nhất cho lần chạy này
  IMAGE_TAG="c2-sandbox-$$"

  # -----------------------------------------------------------
  # TẦNG 1: Build image — CÓ mạng — cài requirements.txt
  # -----------------------------------------------------------
  echo "[INFO] Tầng 1: build image + pip install (có mạng)..."
  docker build --quiet --tag "$IMAGE_TAG" - <<DOCKERFILE
FROM python:3.12-slim
WORKDIR /work
COPY . /work/
RUN if [ -f requirements.txt ]; then \
      pip install --no-cache-dir -r requirements.txt -q; \
    else \
      echo "Không có requirements.txt — bỏ qua pip install"; \
    fi
DOCKERFILE
  # Note: COPY không dùng được với stdin Dockerfile nếu không có context.
  # Dùng cách thay thế: build với context từ FULL_PATH
  docker rmi "$IMAGE_TAG" -f 2>/dev/null || true

  docker build --quiet --tag "$IMAGE_TAG" "$FULL_PATH" \
    --file - <<DOCKERFILE
FROM python:3.12-slim
WORKDIR /work
COPY . /work/
RUN if [ -f requirements.txt ]; then \
      pip install --no-cache-dir -r requirements.txt -q; \
    else \
      echo "Khong co requirements.txt, bo qua pip install"; \
    fi
DOCKERFILE

  echo "[INFO] Tầng 1 xong. Image: $IMAGE_TAG"

  # -----------------------------------------------------------
  # TẦNG 2: Run — KHÔNG mạng — thực thi RUN_CMD
  # -----------------------------------------------------------
  echo "[INFO] Tầng 2: thực thi với --network none..."
  docker run --rm \
    --network none \
    --cpus "1.0" \
    --memory "512m" \
    --read-only \
    --tmpfs /tmp:rw,noexec,nosuid,size=64m \
    "$IMAGE_TAG" \
    sh -c "$RUN_CMD"
  EXIT_CODE=$?

  # Dọn image tạm
  docker rmi "$IMAGE_TAG" -f 2>/dev/null || true

else
  # -----------------------------------------------------------
  # Fallback: không có Docker — chạy trực tiếp, cảnh báo rủi ro
  # -----------------------------------------------------------
  echo "[WARN] Docker không khả dụng. Chạy trực tiếp — RỦI RO CAO HƠN."
  echo "[WARN] Chỉ chạy code bạn đã đọc và hiểu."
  echo ""
  read -r -p "Tiếp tục? (yes/no): " confirm
  if [ "$confirm" != "yes" ]; then
    echo "Hủy."
    exit 0
  fi
  cd "$FULL_PATH"
  if [ -f requirements.txt ]; then
    pip install --no-cache-dir -r requirements.txt -q
  fi
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
