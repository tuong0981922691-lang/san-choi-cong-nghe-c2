#!/usr/bin/env python3
"""
C2 Score Checker v2
Quét toàn repo. Không cho lách điểm bằng string, 10/10, hoặc YAML lỗi.
"""

import sys
import re
import yaml

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
MAX_SELF_SCORE = 8.0
REQUIRED_RESERVE = 2.0
MIN_CHALLENGE_DELTA = 0.1
MAX_CHALLENGE_DELTA = 2.0

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "env"}

FORBIDDEN_SELF_CLAIM_PATTERNS = [
    (r'\b10\s*/\s*10\b', "10/10 tự thân"),
    (r'\b10\.0\s*/\s*10\b', "10.0/10 tự thân"),
    (r'\b100\s*/\s*100\b', "100/100 tự thân"),
    (r'(?i)perfect\s+score', "perfect score"),
    (r'(?i)ho[aà]n\s+h[aả]o\s+tuy[eệ]t\s+[dđ][oô]i', "hoàn hảo tuyệt đối"),
]

errors = []
warnings = []


def err(msg):
    errors.append(msg)
    print(f"  [ERROR] {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"  [WARN]  {msg}")


def ok(msg):
    print(f"  [OK]    {msg}")


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def parse_score(value, field_name, context):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        err(f"{context}: {field_name}={value!r} không phải số hợp lệ — vi phạm")
        return None


def check_manifest_file(manifest_path: Path):
    rel = manifest_path.relative_to(REPO_ROOT)
    try:
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        err(f"{rel}: YAML parse lỗi — {e}")
        return
    if not isinstance(data, dict):
        return

    score_block = data.get("score", {})
    if not isinstance(score_block, dict) or not score_block:
        return

    declared = parse_score(score_block.get("self_declared_base_score"), "self_declared_base_score", rel)
    reserve = score_block.get("challenge_reserve", None)

    if declared is not None:
        if declared > MAX_SELF_SCORE:
            err(f"{rel}: self_declared_base_score={declared} > 8.0 — VI PHẠM LUẬT C2")
        else:
            ok(f"{rel}: base_score = {declared}/8.0")

    if reserve is not None:
        reserve_float = parse_score(reserve, "challenge_reserve", rel)
        if reserve_float is not None and reserve_float != REQUIRED_RESERVE:
            err(f"{rel}: challenge_reserve={reserve_float} phải là 2.0")

    safety = data.get("safety", {})
    if isinstance(safety, dict) and safety.get("class") == "S4":
        err(f"{rel}: safety class S4 bị cấm tuyệt đối")


def check_challenge_manifest_file(manifest_path: Path):
    rel = manifest_path.relative_to(REPO_ROOT)
    try:
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        err(f"{rel}: YAML parse lỗi — {e}")
        return
    if not isinstance(data, dict):
        return

    score_block = data.get("score", {})
    if not isinstance(score_block, dict) or not score_block:
        return

    delta = parse_score(score_block.get("proposed_delta"), "proposed_delta", rel)
    new_score = parse_score(score_block.get("proposed_new_score"), "proposed_new_score", rel)

    if delta is not None:
        if delta < MIN_CHALLENGE_DELTA:
            err(f"{rel}: proposed_delta={delta} < 0.1 — không đủ để lật ngôi")
        elif delta > MAX_CHALLENGE_DELTA:
            err(f"{rel}: proposed_delta={delta} > 2.0 — vượt giới hạn thách thức")
        else:
            ok(f"{rel}: delta = +{delta}")

        delta_report = manifest_path.parent / "delta_report.md"
        if delta > 0 and not delta_report.exists():
            err(f"{rel}: có proposed_delta > 0 nhưng thiếu delta_report.md")

    if new_score is not None and new_score > 10.0:
        err(f"{rel}: proposed_new_score={new_score} > 10.0")


def check_scorecard_file(scorecard_path: Path):
    rel = scorecard_path.relative_to(REPO_ROOT)
    try:
        content = scorecard_path.read_text(encoding="utf-8")
    except Exception as e:
        warn(f"Không đọc được {rel}: {e}")
        return

    match = re.search(r'self_declared_base_score\s*:\s*([0-9]+\.?[0-9]*)', content)
    if match:
        score = parse_score(match.group(1), "self_declared_base_score", rel)
        if score is not None:
            if score > MAX_SELF_SCORE:
                err(f"{rel}: khai báo {score} > 8.0 — VI PHẠM LUẬT C2")
            else:
                ok(f"{rel}: score = {score}/8.0")

    first_300 = content.lower()[:300]
    is_law_doc = any(kw in first_300 for kw in ["forbidden", "bị cấm", "vi phạm", "không được", "example", "template"])

    for pattern, label in FORBIDDEN_SELF_CLAIM_PATTERNS:
        if re.search(pattern, content):
            if not is_law_doc:
                err(f"{rel}: chứa '{label}' như điểm tự thân — vi phạm")


def scan_repo():
    print("\n=== Quét toàn bộ repo (full-repo scan) ===")
    manifests_found = 0
    challenges_found = 0
    scorecards_found = 0

    for item in sorted(REPO_ROOT.rglob("*")):
        if not item.is_file():
            continue
        if should_skip(item):
            continue

        if item.name == "manifest.yaml":
            manifests_found += 1
            check_manifest_file(item)
        elif item.name == "challenge_manifest.yaml":
            challenges_found += 1
            check_challenge_manifest_file(item)
        elif item.name == "scorecard.md":
            scorecards_found += 1
            check_scorecard_file(item)

    ok(f"Đã quét: {manifests_found} manifest.yaml, {challenges_found} challenge_manifest.yaml, {scorecards_found} scorecard.md")


def main():
    print("=" * 60)
    print("  C2 SCORE CHECKER v2 (full-repo, anti-lach)")
    print("=" * 60)

    scan_repo()

    print("\n" + "=" * 60)
    print(f"  Kết quả: {len(errors)} lỗi, {len(warnings)} cảnh báo")
    print("=" * 60)

    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
        print("\n[FAIL] Score check thất bại.")
        sys.exit(1)
    else:
        print("\n[PASS] Score check thành công.")
        sys.exit(0)


if __name__ == "__main__":
    main()
