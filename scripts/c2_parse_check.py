#!/usr/bin/env python3
"""
C2 Parse Checker
Kiểm tra tất cả file YAML/JSON trong repo có parse được không.
"""

import sys
import json
from pathlib import Path
import yaml

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).parent.parent
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "env"}

errors = []


def main():
    print("=" * 60)
    print("  C2 YAML/JSON PARSE CHECKER")
    print("=" * 60)

    count = 0
    for p in sorted(REPO_ROOT.rglob("*")):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        rel = p.relative_to(REPO_ROOT)

        if p.suffix in (".yaml", ".yml"):
            try:
                yaml.safe_load(p.read_text(encoding="utf-8"))
                count += 1
            except Exception as e:
                errors.append(f"YAML parse error: {rel}: {e}")
                print(f"  [ERROR] YAML: {rel}: {e}")
        elif p.suffix == ".json":
            try:
                json.loads(p.read_text(encoding="utf-8"))
                count += 1
            except Exception as e:
                errors.append(f"JSON parse error: {rel}: {e}")
                print(f"  [ERROR] JSON: {rel}: {e}")

    print(f"\n  Đã kiểm tra: {count} file YAML/JSON")
    if errors:
        print(f"\n[FAIL] {len(errors)} file lỗi parse.")
        sys.exit(1)
    else:
        print("\n[PASS] Tất cả YAML/JSON parse OK.")
        sys.exit(0)


if __name__ == "__main__":
    main()
