#!/usr/bin/env python3
"""
C2 Score Checker
Kiểm tra điểm tự chấm không vượt 8.0 và challenge delta hợp lệ.
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


def check_technology_scores():
    print("\n=== Kiểm tra điểm công nghệ ===")
    tech_base = REPO_ROOT / "vault" / "technologies"
    if not tech_base.is_dir():
        ok("vault/technologies/ trống")
        return

    for tech_dir in sorted(tech_base.iterdir()):
        if not tech_dir.is_dir():
            continue
        versions_dir = tech_dir / "versions"
        if not versions_dir.is_dir():
            continue
        for version_dir in sorted(versions_dir.iterdir()):
            if not version_dir.is_dir():
                continue
            check_version_score(tech_dir.name, version_dir)


def check_version_score(tech_name, version_dir: Path):
    # Check manifest score
    manifest = version_dir / "manifest.yaml"
    if manifest.exists():
        try:
            data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
            score_block = data.get("score", {})
            declared = score_block.get("self_declared_base_score", None)
            reserve = score_block.get("challenge_reserve", None)

            if declared is not None:
                if declared > MAX_SELF_SCORE:
                    err(f"{tech_name}/{version_dir.name}: manifest score {declared} > 8.0 — VI PHẠM LUẬT C2")
                else:
                    ok(f"{tech_name}/{version_dir.name}: manifest score = {declared}/8.0")

            if reserve is not None and reserve != REQUIRED_RESERVE:
                err(f"{tech_name}/{version_dir.name}: challenge_reserve={reserve} phải là 2.0")

        except Exception as e:
            warn(f"Lỗi đọc manifest {manifest}: {e}")

    # Check scorecard.md
    scorecard = version_dir / "scorecard.md"
    if scorecard.exists():
        score = extract_score_from_scorecard(scorecard)
        if score is not None:
            if score > MAX_SELF_SCORE:
                err(f"{tech_name}/{version_dir.name}: scorecard.md khai báo {score} > 8.0 — VI PHẠM LUẬT C2")
            else:
                ok(f"{tech_name}/{version_dir.name}: scorecard score = {score}/8.0")

            # Check for "10/10" claims in scorecard
            content = scorecard.read_text(encoding="utf-8")
            if re.search(r'\b10\s*/\s*10\b|\b10\.0\s*/\s*10\b', content):
                if "challenge" not in content.lower()[:200]:
                    err(f"{tech_name}: scorecard.md chứa '10/10' như điểm tự thân — vi phạm")


def check_challenge_scores():
    print("\n=== Kiểm tra điểm challenge ===")
    challenge_base = REPO_ROOT / "vault" / "challenges"
    if not challenge_base.is_dir():
        ok("vault/challenges/ trống")
        return

    for challenge_dir in sorted(challenge_base.iterdir()):
        if not challenge_dir.is_dir():
            continue
        manifest_path = challenge_dir / "challenge_manifest.yaml"
        if not manifest_path.exists():
            warn(f"{challenge_dir.name}: thiếu challenge_manifest.yaml")
            continue

        try:
            data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            score_block = data.get("score", {})
            delta = score_block.get("proposed_delta", None)
            new_score = score_block.get("proposed_new_score", None)

            if delta is not None:
                if delta < MIN_CHALLENGE_DELTA:
                    err(f"{challenge_dir.name}: proposed_delta={delta} < 0.1 — không đủ để lật ngôi")
                elif delta > MAX_CHALLENGE_DELTA:
                    err(f"{challenge_dir.name}: proposed_delta={delta} > 2.0 — vượt giới hạn thách thức")
                else:
                    ok(f"{challenge_dir.name}: delta = +{delta}")

            if new_score is not None and new_score > 10.0:
                err(f"{challenge_dir.name}: proposed_new_score={new_score} > 10.0")

            # Require delta_report.md if delta > 0
            if delta and delta > 0:
                delta_report = challenge_dir / "delta_report.md"
                if not delta_report.exists():
                    err(f"{challenge_dir.name}: có proposed_delta nhưng thiếu delta_report.md")
                else:
                    ok(f"{challenge_dir.name}: delta_report.md tồn tại")

        except Exception as e:
            warn(f"Lỗi đọc challenge manifest {challenge_dir.name}: {e}")


def main():
    print("=" * 60)
    print("  C2 SCORE CHECKER")
    print("=" * 60)

    check_technology_scores()
    check_challenge_scores()

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
