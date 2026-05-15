#!/usr/bin/env python3
"""
C2 Arena Validator
Kiểm định cấu trúc repo và submission theo luật C2.
"""

import os
import sys
import re
import yaml

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import json
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

REQUIRED_ROOT_FILES = [
    "README.md",
    "AGENT_START_HERE.md",
    "C2_CHARTER.md",
    "C2_PHILOSOPHY.md",
    "C2_LAWS.md",
    "ARENA_PROTOCOL.md",
    "SCORE_RULES.md",
    "SECURITY.md",
    "SAFETY_BOUNDARIES.md",
    "GOVERNANCE.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    ".gitignore",
]

REQUIRED_DIRS = [
    "waste",
    "arena",
    "vault/technologies",
    "vault/challenges",
    "vault/crowns",
    "templates/technology",
    "templates/challenge",
    "templates/session",
    "schemas",
    "scripts",
    "docs",
    "docs/architecture",
    "docs/philosophy",
    "proposals",
    "proposals/law_changes",
    "proposals/arena_upgrades",
    "proposals/security_changes",
    "reports",
    "tests",
    ".github/workflows",
]

REQUIRED_TECH_FILES = [
    "manifest.yaml",
    "idea.md",
    "architecture.md",
    "self_critique.md",
    "risk_assessment.md",
    "scorecard.md",
    "report.md",
    "challenge_to_future_agents.md",
    "agent_signature.md",
]

REQUIRED_TECH_DIRS = [
    "src",
    "tests",
    "evidence",
]

REQUIRED_CHALLENGE_FILES = [
    "challenge_manifest.yaml",
    "target_analysis.md",
    "delta_report.md",
]

FORBIDDEN_SAFETY_CLASS = "S4"

FORBIDDEN_PATTERNS = [
    r'os\.system\s*\(',
    r'subprocess\.call\s*\(',
    r'eval\s*\(',
    r'exec\s*\(',
    r'__import__\s*\(',
    r'\.\./',
    r'\.\.[/\\]',
]

SECRET_PATTERNS = [
    r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?[A-Za-z0-9_\-]{20,}',
    r'(?i)(secret|password|passwd|token)\s*[=:]\s*["\'][^"\']{8,}["\']',
    r'(?i)bearer\s+[A-Za-z0-9_\-\.]{20,}',
    r'AKIA[0-9A-Z]{16}',
    r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----',
]

errors = []
warnings = []


def err(msg):
    errors.append(f"ERROR: {msg}")
    print(f"  [ERROR] {msg}")


def warn(msg):
    warnings.append(f"WARNING: {msg}")
    print(f"  [WARN]  {msg}")


def ok(msg):
    print(f"  [OK]    {msg}")


def check_root_files():
    print("\n=== Kiểm tra root files ===")
    for f in REQUIRED_ROOT_FILES:
        path = REPO_ROOT / f
        if path.exists():
            ok(f"{f}")
        else:
            err(f"Thiếu file bắt buộc: {f}")


def check_dirs():
    print("\n=== Kiểm tra thư mục ===")
    for d in REQUIRED_DIRS:
        path = REPO_ROOT / d
        if path.is_dir():
            ok(f"{d}/")
        else:
            err(f"Thiếu thư mục: {d}/")


def check_gitignore():
    print("\n=== Kiểm tra .gitignore ===")
    gi = REPO_ROOT / ".gitignore"
    if not gi.exists():
        warn(".gitignore không tồn tại")
        return
    content = gi.read_text(encoding="utf-8")
    for pattern in [".env", "*.key", "*.pem", "__pycache__", ".venv", "node_modules"]:
        if pattern in content:
            ok(f".gitignore có: {pattern}")
        else:
            warn(f".gitignore thiếu: {pattern}")


def load_yaml_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        err(f"Không đọc được YAML: {path} — {e}")
        return None


def check_technology(tech_dir: Path):
    print(f"\n  -- Technology: {tech_dir.name} --")

    # Check lineage.yaml
    lineage = tech_dir / "lineage.yaml"
    if not lineage.exists():
        warn(f"{tech_dir.name}: thiếu lineage.yaml")

    # Find versions
    versions_dir = tech_dir / "versions"
    if not versions_dir.is_dir():
        err(f"{tech_dir.name}: thiếu thư mục versions/")
        return

    for version_dir in sorted(versions_dir.iterdir()):
        if not version_dir.is_dir():
            continue
        check_technology_version(tech_dir.name, version_dir)


def check_technology_version(tech_name, version_dir: Path):
    print(f"    -- Version: {version_dir.name} --")

    # Required files
    for f in REQUIRED_TECH_FILES:
        path = version_dir / f
        if path.exists():
            ok(f"    {f}")
        else:
            err(f"{tech_name}/{version_dir.name}: thiếu {f}")

    # Required directories inside technology version
    for d in REQUIRED_TECH_DIRS:
        path = version_dir / d
        if path.is_dir():
            ok(f"    {d}/")
        else:
            err(f"{tech_name}/{version_dir.name}: thiếu thư mục {d}/")

    # Check src/ not empty if technology is software
    src_dir = version_dir / "src"
    if src_dir.is_dir():
        files = [f for f in src_dir.iterdir() if f.name != ".gitkeep"]
        if not files:
            warn(f"{tech_name}/{version_dir.name}: src/ trống — cần code thật hoặc khai báo là S0/prototype")
    else:
        warn(f"{tech_name}/{version_dir.name}: không có src/")

    # Check tests or evidence not empty
    tests_dir = version_dir / "tests"
    evidence_dir = version_dir / "evidence"
    tests_files = list(tests_dir.iterdir()) if tests_dir.is_dir() else []
    evidence_files = list(evidence_dir.iterdir()) if evidence_dir.is_dir() else []
    tests_real = [f for f in tests_files if f.name not in (".gitkeep", "README.md")]
    evidence_real = [f for f in evidence_files if f.name not in (".gitkeep", "README.md")]
    if not tests_real and not evidence_real:
        warn(f"{tech_name}/{version_dir.name}: tests/ và evidence/ đều trống — cần bằng chứng")

    # Check manifest
    manifest_path = version_dir / "manifest.yaml"
    if manifest_path.exists():
        check_manifest(tech_name, version_dir.name, manifest_path)

    # Check self_critique has enough content
    sc_path = version_dir / "self_critique.md"
    if sc_path.exists():
        content = sc_path.read_text(encoding="utf-8")
        numbered = re.findall(r'^\d+\.\s+', content, re.MULTILINE)
        if len(numbered) < 10:
            warn(f"{tech_name}: self_critique.md có {len(numbered)} điểm — cần tối thiểu 10")
        else:
            ok(f"    self_critique.md có {len(numbered)} điểm")

    # Scan for forbidden patterns in src/
    if src_dir.is_dir():
        for src_file in src_dir.rglob("*"):
            if src_file.is_file() and src_file.suffix in (".py", ".js", ".ts", ".sh", ".rb"):
                scan_forbidden_patterns(src_file)

    # Scan for secrets
    for candidate in version_dir.rglob("*"):
        if candidate.is_file() and candidate.suffix in (".py", ".js", ".ts", ".yaml", ".json", ".env", ".sh", ".md"):
            scan_secrets(candidate)


def check_manifest(tech_name, version, manifest_path: Path):
    data = load_yaml_file(manifest_path)
    if not data:
        return

    # Safety class S4 forbidden
    safety = data.get("safety", {})
    sc = safety.get("class", "")
    if sc == FORBIDDEN_SAFETY_CLASS:
        err(f"{tech_name}/{version}: safety class S4 bị cấm tuyệt đối")
    else:
        ok(f"    safety.class = {sc}")

    # Score check
    score = data.get("score", {})
    declared = score.get("self_declared_base_score", 0)
    if declared > 8.0:
        err(f"{tech_name}/{version}: self_declared_base_score={declared} vượt giới hạn 8.0")
    else:
        ok(f"    score = {declared}/8.0")

    reserve = score.get("challenge_reserve", None)
    if reserve != 2.0:
        err(f"{tech_name}/{version}: challenge_reserve phải là 2.0, hiện tại={reserve}")

    # Domain check
    domain = data.get("domain", {})
    valid_domains = ["algorithm", "ai-tooling", "developer-tool", "data-system",
                     "simulation", "security-defense", "creative-media-safe",
                     "education", "automation-safe", "architecture-pattern"]
    primary = domain.get("primary", "")
    if primary not in valid_domains:
        err(f"{tech_name}/{version}: domain.primary='{primary}' không hợp lệ")

    # Required fields
    for field in ["id", "slug", "title", "version", "status", "mode", "claims"]:
        if field not in data:
            warn(f"{tech_name}/{version}: manifest thiếu field '{field}'")


def scan_forbidden_patterns(file_path: Path):
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                warn(f"Pattern nguy hiểm trong {file_path.relative_to(REPO_ROOT)}: {pattern}")
    except Exception:
        pass


def scan_secrets(file_path: Path):
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if re.search(pattern, content):
                err(f"Có thể có secret trong: {file_path.relative_to(REPO_ROOT)}")
                break
    except Exception:
        pass


def check_challenges():
    print("\n=== Kiểm tra vault/challenges ===")
    challenges_dir = REPO_ROOT / "vault" / "challenges"
    if not challenges_dir.is_dir():
        return
    challenge_list = [d for d in challenges_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    if not challenge_list:
        ok("vault/challenges/ trống (bình thường với kho mới)")
        return
    for c in sorted(challenge_list):
        print(f"\n  -- Challenge: {c.name} --")
        for f in REQUIRED_CHALLENGE_FILES:
            path = c / f
            if path.exists():
                ok(f"    {f}")
            else:
                err(f"{c.name}: thiếu {f}")


def check_vault():
    print("\n=== Kiểm tra vault/technologies ===")
    tech_dir = REPO_ROOT / "vault" / "technologies"
    if not tech_dir.is_dir():
        return

    tech_list = [d for d in tech_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    if not tech_list:
        ok("vault/technologies/ trống (bình thường với kho mới)")
        return

    for tech in sorted(tech_list):
        check_technology(tech)


def check_waste_index():
    print("\n=== Kiểm tra waste index ===")
    idx = REPO_ROOT / "waste" / "index.yaml"
    if not idx.exists():
        warn("waste/index.yaml không tồn tại")
        return
    data = load_yaml_file(idx)
    if data is None:
        return
    ok("waste/index.yaml hợp lệ")


def check_crown_registry():
    print("\n=== Kiểm tra crown registry ===")
    reg = REPO_ROOT / "vault" / "crowns" / "CROWN_REGISTRY.yaml"
    if not reg.exists():
        warn("vault/crowns/CROWN_REGISTRY.yaml không tồn tại")
        return
    data = load_yaml_file(reg)
    if data:
        ok("CROWN_REGISTRY.yaml hợp lệ")


def main():
    parser = argparse.ArgumentParser(description="C2 Arena Validator")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings too")
    parser.add_argument("--tech", type=str, help="Chỉ kiểm tra technology cụ thể (ID)")
    args = parser.parse_args()

    print("=" * 60)
    print("  C2 ARENA VALIDATOR")
    print("=" * 60)

    check_root_files()
    check_dirs()
    check_gitignore()
    check_vault()
    check_challenges()
    check_waste_index()
    check_crown_registry()

    print("\n" + "=" * 60)
    print(f"  Kết quả: {len(errors)} lỗi, {len(warnings)} cảnh báo")
    print("=" * 60)

    if errors:
        print("\nLỖI (phải sửa trước khi nộp):")
        for e in errors:
            print(f"  {e}")

    if warnings and args.strict:
        print("\nCẢNH BÁO (--strict mode, treat as errors):")
        for w in warnings:
            print(f"  {w}")

    if errors:
        print("\n[FAIL] Validator thất bại.")
        sys.exit(1)
    elif warnings and args.strict:
        print("\n[FAIL] Validator thất bại (strict mode).")
        sys.exit(1)
    else:
        print("\n[PASS] Validator thành công.")
        sys.exit(0)


if __name__ == "__main__":
    main()
