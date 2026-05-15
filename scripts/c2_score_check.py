#!/usr/bin/env python3
"""
C2 Score Checker
Kiểm tra điểm tự chấm không vượt 8.0 và challenge delta hợp lệ.
Quét toàn bộ repo, không chỉ vault/.
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


def extract_score_from_scorecard(path: Path):
    """Tìm dòng 'self_declared_base_score:' trong scorecard.md"""
    try:
        content = path.read_text(encoding="utf-8")
        match = re.search(r'self_declared_base_score\s*:\s*([0-9]+\.?[0-9]*)', content)
        if match:
            return float(match.group(1))
    except Exception as e:
        warn(f"Không đọc được {path}: {e}")
    return None


def check_manifest_file(manifest_path: Path):
    """Kiểm tra một file manifest.yaml bất kỳ trong repo."""
    rel = manifest_path.relative_to(REPO_ROOT)
    try:
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return

        score_block = data.get("score", {})
        if not score_block:
            return

        declared = score_block.get("self_declared_base_score", None)
        reserve = score_block.get("challenge_reserve", None)

        if declared is not None:
            if declared > MAX_SELF_SCORE:
                err(f"{rel}: self_declared_base_score={declared} > 8.0 — VI PHẠM LUẬT C2")
            else:
                ok(f"{rel}: base_score = {declared}/8.0")

        if reserve is not None and reserve != REQUIRED_RESERVE:
            err(f"{rel}: challenge_reserve={reserve} phải là 2.0")

        safety = data.get("safety", {})
        if isinstance(safety, dict) and safety.get("class") == "S4":
            err(f"{rel}: safety class S4 bị cấm tuyệt đối")

    except Exception as e:
        warn(f"Lỗi đọc manifest {rel}: {e}")


def check_challenge_manifest_file(manifest_path: Path):
    """Kiểm tra một file challenge_manifest.yaml."""
    rel = manifest_path.relative_to(REPO_ROOT)
    try:
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return

        score_block = data.get("score", {})
        if not score_block:
            return

        delta = score_block.get("proposed_delta", None)
        new_score = score_block.get("proposed_new_score", None)

        if delta is not None:
            if delta < MIN_CHALLENGE_DELTA:
                err(f"{rel}: proposed_delta={delta} < 0.1 — không đủ để lật ngôi")
            elif delta > MAX_CHALLENGE_DELTA:
                err(f"{rel}: proposed_delta={delta} > 2.0 — vượt giới hạn thách thức")
            else:
                ok(f"{rel}: delta = +{delta}")

            delta_report = manifest_path.parent / "delta_report.md"
            if not delta_report.exists():
                err(f"{rel}: có proposed_delta nhưng thiếu delta_report.md")

        if new_score is not None and new_score > 10.0:
            err(f"{rel}: proposed_new_score={new_score} > 10.0")

    except Exception as e:
        warn(f"Lỗi đọc challenge manifest {rel}: {e}")


def check_scorecard_file(scorecard_path: Path):
    """Kiểm tra một file scorecard.md."""
    rel = scorecard_path.relative_to(REPO_ROOT)
    score = extract_score_from_scorecard(scorecard_path)
    if score is None:
        return

    if score > MAX_SELF_SCORE:
        err(f"{rel}: khai báo {score} > 8.0 — VI PHẠM LUẬT C2")
    else:
        ok(f"{rel}: score = {score}/8.0")

    try:
        content = scorecard_path.read_text(encoding="utf-8")
        if re.search(r'\b10\s*/\s*10\b|\b10\.0\s*/\s*10\b', content):
            first_200 = content.lower()[:200]
            if "challenge" not in first_200 and "example" not in first_200 and "template" not in first_200:
                err(f"{rel}: chứa '10/10' như điểm tự thân — vi phạm")
    except Exception:
        pass


def scan_repo():
    print("\n=== Quét toàn bộ repo ===")
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
    print("  C2 SCORE CHECKER (full-repo scan)")
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
