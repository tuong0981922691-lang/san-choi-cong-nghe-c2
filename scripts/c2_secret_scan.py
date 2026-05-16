#!/usr/bin/env python3
"""
C2 Secret Scanner
Quét repo tìm secrets tiềm ẩn trước khi commit.
"""

import sys
import re
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).parent.parent

SECRET_PATTERNS = [
    (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?[A-Za-z0-9_\-]{20,}', "API Key"),
    (r'(?i)(secret[_-]?key|secret)\s*[=:]\s*["\'][^"\']{8,}["\']', "Secret Key"),
    (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\'][^"\']{4,}["\']', "Password"),
    (r'(?i)(token|auth[_-]?token|access[_-]?token)\s*[=:]\s*["\'][^"\']{10,}["\']', "Token"),
    (r'(?i)bearer\s+[A-Za-z0-9_\-\.]{20,}', "Bearer Token"),
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key"),
    (r'(?i)aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["\']?[A-Za-z0-9+/]{40}', "AWS Secret"),
    (r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----', "Private Key"),
    (r'(?i)github[_-]?token\s*[=:]\s*["\']?ghp_[A-Za-z0-9]{36}', "GitHub Token"),
    (r'ghp_[A-Za-z0-9]{36}', "GitHub Personal Token"),
    (r'(?i)sk-[A-Za-z0-9]{32,}', "OpenAI API Key"),
]

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "env"}
SKIP_FILES = {"c2_secret_scan.py"}

TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".env",
    ".sh", ".bash", ".md", ".txt", ".cfg", ".ini", ".toml",
    ".html", ".css", ".jsx", ".tsx", ".rb", ".go", ".rs", ".java"
}

found = []


def scan_file(path: Path):
    if path.name in SKIP_FILES:
        return
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        for pattern, label in SECRET_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                rel = path.relative_to(REPO_ROOT)
                found.append((str(rel), label))
                print(f"  [POTENTIAL SECRET] {label} in {rel}")
    except Exception:
        pass


def main():
    print("=" * 60)
    print("  C2 SECRET SCANNER")
    print("=" * 60)
    print(f"  Scanning: {REPO_ROOT}")
    print()

    for item in REPO_ROOT.rglob("*"):
        if item.is_file():
            skip = False
            for skip_dir in SKIP_DIRS:
                if skip_dir in item.parts:
                    skip = True
                    break
            if not skip:
                scan_file(item)

    print()
    print("=" * 60)
    if found:
        print(f"  [WARN] Tìm thấy {len(found)} file có thể chứa secrets.")
        print("  Kiểm tra thủ công trước khi commit!")
        for path, label in found:
            print(f"    - {label}: {path}")
        sys.exit(1)
    else:
        print("  [OK] Không tìm thấy secret nào.")
        sys.exit(0)


if __name__ == "__main__":
    main()
