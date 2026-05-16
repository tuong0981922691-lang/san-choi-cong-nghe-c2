#!/usr/bin/env python3
"""
C2 Arena Validator
Kiểm định cấu trúc repo và submission theo luật C2.
"""

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
import jsonschema

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
    "LICENSE_DECISION.md",
    ".gitignore",
]

REQUIRED_DIRS = [
    ".github",
    ".github/workflows",
    ".github/ISSUE_TEMPLATE",
    "docs",
    "docs/architecture",
    "docs/philosophy",
    "waste",
    "waste/inbox",
    "waste/normalized",
    "waste/quarantine",
    "arena",
    "arena/active",
    "arena/sessions",
    "vault",
    "vault/technologies",
    "vault/challenges",
    "vault/crowns",
    "vault/retired",
    "templates",
    "templates/technology",
    "templates/challenge",
    "templates/session",
    "schemas",
    "scripts",
    "proposals",
    "proposals/law_changes",
    "proposals/arena_upgrades",
    "proposals/security_changes",
    "reports",
    "tests",
]

REQUIRED_DOC_FILES = [
    "docs/architecture/system-overview.md",
    "docs/architecture/threat-model.md",
    "docs/architecture/repository-map.md",
    "docs/architecture/data-flow.md",
    "docs/philosophy/c2-waste-to-gold.md",
    "docs/philosophy/look-up-to-future-ai.md",
    "docs/philosophy/ego-vs-proof.md",
    "docs/glossary.md",
    "docs/faq.md",
    "reports/FOUNDATION_SUMMARY.md",
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
    "diagrams",
    "src",
    "tests",
    "evidence",
]

REQUIRED_CHALLENGE_FILES = [
    "challenge_manifest.yaml",
    "target_analysis.md",
    "upgrade_plan.md",
    "delta_report.md",
    "self_critique.md",
    "risk_assessment.md",
    "report.md",
]

REQUIRED_CHALLENGE_DIRS = [
    "src",
    "tests",
    "evidence",
]

REQUIRED_TEMPLATE_TECH_FILES = [
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

REQUIRED_TEMPLATE_CHALLENGE_FILES = [
    "challenge_manifest.yaml",
    "target_analysis.md",
    "upgrade_plan.md",
    "delta_report.md",
    "self_critique.md",
    "risk_assessment.md",
    "report.md",
]

REQUIRED_TEMPLATE_SESSION_FILES = [
    "session_manifest.yaml",
    "working_notes.md",
    "decision_log.md",
    "REPORT_TO_C2.md",
]

FORBIDDEN_SAFETY_CLASS = "S4"

FORBIDDEN_PATTERNS = [
    r'os\.system\s*\(',
    r'subprocess\.call\s*\(',
    r'subprocess\.run\s*\(',
    r'subprocess\.Popen\s*\(',
    r'os\.popen\s*\(',
    r'pty\.spawn\s*\(',
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

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "env"}

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


def check_doc_files():
    print("\n=== Kiểm tra doc files bắt buộc ===")
    for f in REQUIRED_DOC_FILES:
        path = REPO_ROOT / f
        if path.exists():
            ok(f"{f}")
        else:
            err(f"Thiếu doc file bắt buộc: {f}")


def check_gitignore():
    print("\n=== Kiểm tra .gitignore ===")
    gi = REPO_ROOT / ".gitignore"
    if not gi.exists():
        err(".gitignore không tồn tại")
        return
    content = gi.read_text(encoding="utf-8")
    for pattern in [".env", "*.key", "*.pem", "__pycache__", ".venv", "node_modules", ".idea/"]:
        if pattern in content:
            ok(f".gitignore có: {pattern}")
        else:
            warn(f".gitignore thiếu: {pattern}")


_schema_cache: dict = {}


def load_schema(schema_name: str):
    """Load và cache JSON schema từ thư mục schemas/."""
    if schema_name in _schema_cache:
        return _schema_cache[schema_name]
    schema_path = REPO_ROOT / "schemas" / schema_name
    if not schema_path.exists():
        warn(f"Schema file không tồn tại: schemas/{schema_name}")
        return None
    data = load_json_file(schema_path)
    if data is not None:
        _schema_cache[schema_name] = data
    return data


def validate_against_schema(data: dict, schema_name: str, context: str) -> bool:
    """Validate dict data theo JSON schema. Trả về True nếu hợp lệ."""
    schema = load_schema(schema_name)
    if schema is None:
        warn(f"{context}: không load được schema {schema_name} — bỏ qua validate")
        return True
    try:
        jsonschema.validate(instance=data, schema=schema)
        ok(f"    schema OK ({schema_name})")
        return True
    except jsonschema.ValidationError as e:
        err(f"{context}: vi phạm schema '{schema_name}' — {e.message} (path: {list(e.absolute_path)})")
        return False
    except jsonschema.SchemaError as e:
        err(f"{context}: lỗi schema '{schema_name}' — {e.message}")
        return False


def load_yaml_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        err(f"YAML parse lỗi: {path} — {e}")
        return None


def load_json_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        err(f"JSON parse lỗi: {path} — {e}")
        return None


def check_all_yaml_json():
    print("\n=== Kiểm tra YAML/JSON parse toàn repo ===")
    count_ok = 0
    for item in sorted(REPO_ROOT.rglob("*")):
        if not item.is_file():
            continue
        if any(part in SKIP_DIRS for part in item.parts):
            continue
        if item.suffix in (".yaml", ".yml"):
            try:
                yaml.safe_load(item.read_text(encoding="utf-8"))
                count_ok += 1
            except Exception as e:
                err(f"YAML parse lỗi: {item.relative_to(REPO_ROOT)} — {e}")
        elif item.suffix == ".json":
            try:
                json.loads(item.read_text(encoding="utf-8"))
                count_ok += 1
            except Exception as e:
                err(f"JSON parse lỗi: {item.relative_to(REPO_ROOT)} — {e}")
    ok(f"Đã parse {count_ok} file YAML/JSON không lỗi")


def check_templates():
    print("\n=== Kiểm tra templates ===")
    tech_tmpl = REPO_ROOT / "templates" / "technology"
    for f in REQUIRED_TEMPLATE_TECH_FILES:
        p = tech_tmpl / f
        if p.exists():
            ok(f"templates/technology/{f}")
        else:
            err(f"templates/technology: thiếu {f}")

    ch_tmpl = REPO_ROOT / "templates" / "challenge"
    for f in REQUIRED_TEMPLATE_CHALLENGE_FILES:
        p = ch_tmpl / f
        if p.exists():
            ok(f"templates/challenge/{f}")
        else:
            err(f"templates/challenge: thiếu {f}")

    sess_tmpl = REPO_ROOT / "templates" / "session"
    for f in REQUIRED_TEMPLATE_SESSION_FILES:
        p = sess_tmpl / f
        if p.exists():
            ok(f"templates/session/{f}")
        else:
            err(f"templates/session: thiếu {f}")


def check_technology(tech_dir: Path):
    print(f"\n  -- Technology: {tech_dir.name} --")
    lineage = tech_dir / "lineage.yaml"
    if not lineage.exists():
        warn(f"{tech_dir.name}: thiếu lineage.yaml")
    else:
        load_yaml_file(lineage)

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

    for f in REQUIRED_TECH_FILES:
        path = version_dir / f
        if path.exists():
            ok(f"    {f}")
        else:
            err(f"{tech_name}/{version_dir.name}: thiếu {f}")

    for d in REQUIRED_TECH_DIRS:
        path = version_dir / d
        if path.is_dir():
            ok(f"    {d}/")
        else:
            err(f"{tech_name}/{version_dir.name}: thiếu thư mục {d}/")

    src_dir = version_dir / "src"
    if src_dir.is_dir():
        files = [f for f in src_dir.iterdir() if f.name != ".gitkeep"]
        if not files:
            warn(f"{tech_name}/{version_dir.name}: src/ trống — cần code thật")
    else:
        warn(f"{tech_name}/{version_dir.name}: không có src/")

    tests_dir = version_dir / "tests"
    evidence_dir = version_dir / "evidence"
    tests_real = [f for f in tests_dir.iterdir() if f.name not in (".gitkeep", "README.md")] if tests_dir.is_dir() else []
    evidence_real = [f for f in evidence_dir.iterdir() if f.name not in (".gitkeep", "README.md")] if evidence_dir.is_dir() else []
    if not tests_real and not evidence_real:
        warn(f"{tech_name}/{version_dir.name}: tests/ và evidence/ đều trống — cần bằng chứng")

    manifest_path = version_dir / "manifest.yaml"
    if manifest_path.exists():
        check_manifest(tech_name, version_dir.name, manifest_path)

    sc_path = version_dir / "self_critique.md"
    if sc_path.exists():
        content = sc_path.read_text(encoding="utf-8")
        numbered = re.findall(r'^\d+\.\s+', content, re.MULTILINE)
        if len(numbered) < 10:
            warn(f"{tech_name}: self_critique.md có {len(numbered)} điểm — cần tối thiểu 10")
        else:
            ok(f"    self_critique.md có {len(numbered)} điểm")

    if src_dir.is_dir():
        for src_file in src_dir.rglob("*"):
            if src_file.is_file() and src_file.suffix in (".py", ".js", ".ts", ".sh", ".rb"):
                scan_forbidden_patterns(src_file)

    for candidate in version_dir.rglob("*"):
        if candidate.is_file() and candidate.suffix in (".py", ".js", ".ts", ".yaml", ".json", ".env", ".sh", ".md"):
            scan_secrets(candidate)


def check_manifest(tech_name, version, manifest_path: Path):
    data = load_yaml_file(manifest_path)
    if not data:
        return

    # Schema validation thực sự
    validate_against_schema(data, "technology_manifest.schema.json", f"{tech_name}/{version}")

    safety = data.get("safety", {})
    sc = safety.get("class", "")
    if sc == FORBIDDEN_SAFETY_CLASS:
        err(f"{tech_name}/{version}: safety class S4 bị cấm tuyệt đối")
    else:
        ok(f"    safety.class = {sc}")

    score = data.get("score", {})
    declared = score.get("self_declared_base_score", 0)
    try:
        declared = float(declared)
    except (TypeError, ValueError):
        err(f"{tech_name}/{version}: self_declared_base_score không phải số: {declared!r}")
        return
    if declared > 8.0:
        err(f"{tech_name}/{version}: self_declared_base_score={declared} vượt giới hạn 8.0")
    else:
        ok(f"    score = {declared}/8.0")

    reserve = score.get("challenge_reserve", None)
    if reserve != 2.0:
        err(f"{tech_name}/{version}: challenge_reserve phải là 2.0, hiện tại={reserve}")

    domain = data.get("domain", {})
    valid_domains = ["algorithm", "ai-tooling", "developer-tool", "data-system",
                     "simulation", "security-defense", "creative-media-safe",
                     "education", "automation-safe", "architecture-pattern"]
    primary = domain.get("primary", "")
    if primary not in valid_domains:
        err(f"{tech_name}/{version}: domain.primary='{primary}' không hợp lệ")

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
        for d in REQUIRED_CHALLENGE_DIRS:
            path = c / d
            if path.is_dir():
                ok(f"    {d}/")
            else:
                err(f"{c.name}: thiếu thư mục {d}/")
        cm = c / "challenge_manifest.yaml"
        if cm.exists():
            cm_data = load_yaml_file(cm)
            if cm_data:
                validate_against_schema(cm_data, "challenge_manifest.schema.json", c.name)


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
    args = parser.parse_args()

    print("=" * 60)
    print("  C2 ARENA VALIDATOR v2")
    print("=" * 60)

    check_root_files()
    check_dirs()
    check_doc_files()
    check_gitignore()
    check_all_yaml_json()
    check_templates()
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
