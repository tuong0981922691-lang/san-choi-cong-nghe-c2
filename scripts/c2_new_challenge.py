#!/usr/bin/env python3
"""
C2 New Challenge Scaffold
Tạo cấu trúc challenge nâng cấp công nghệ.
"""

import sys
import shutil
import argparse
import yaml
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).parent.parent
TEMPLATE_DIR = REPO_ROOT / "templates" / "challenge"
CHALLENGE_DIR = REPO_ROOT / "vault" / "challenges"
TECH_DIR = REPO_ROOT / "vault" / "technologies"


def next_challenge_id():
    existing = []
    if CHALLENGE_DIR.is_dir():
        for d in CHALLENGE_DIR.iterdir():
            if d.is_dir():
                name = d.name
                if name.startswith("U") and "-on-" in name:
                    num_part = name[1:name.index("-on-")]
                    if num_part.isdigit():
                        existing.append(int(num_part))
    next_num = max(existing, default=0) + 1
    return f"U{next_num:06d}"


def find_tech(tech_id):
    if not TECH_DIR.is_dir():
        return None
    for d in TECH_DIR.iterdir():
        if d.is_dir() and d.name.startswith(tech_id):
            return d
    return None


def scaffold(challenge_id, target_id, session_id, agent_alias):
    tech_dir = find_tech(target_id)
    if not tech_dir:
        print(f"[ERROR] Không tìm thấy technology {target_id} trong vault/technologies/")
        sys.exit(1)

    challenge_slug = f"{challenge_id}-on-{target_id}"
    dest = CHALLENGE_DIR / challenge_slug

    if dest.exists():
        print(f"[ERROR] Challenge đã tồn tại: {dest}")
        sys.exit(1)

    dest.mkdir(parents=True)

    # Copy template files
    for item in TEMPLATE_DIR.rglob("*"):
        if item.is_file():
            rel = item.relative_to(TEMPLATE_DIR)
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)

    # Update challenge manifest
    manifest_path = dest / "challenge_manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["id"] = challenge_id
    manifest["slug"] = challenge_slug
    manifest["title"] = f"Challenge on {target_id}"
    manifest["created_at"] = str(date.today())
    manifest["session_id"] = session_id
    manifest["challenger"]["agent_alias"] = agent_alias
    manifest["target"]["technology_id"] = target_id
    manifest["target"]["technology_slug"] = tech_dir.name
    manifest_path.write_text(
        yaml.dump(manifest, allow_unicode=True, default_flow_style=False),
        encoding="utf-8"
    )

    print(f"[OK] Challenge scaffold tạo tại: {dest.relative_to(REPO_ROOT)}")
    print(f"     Challenge ID: {challenge_id}")
    print(f"     Target: {target_id}")
    print(f"\nBước tiếp theo:")
    print(f"  1. Đọc target: {tech_dir.relative_to(REPO_ROOT)}")
    print(f"  2. Điền target_analysis.md — chỉ ra điểm yếu cụ thể")
    print(f"  3. Viết upgrade_plan.md — kế hoạch nâng cấp")
    print(f"  4. Viết code trong src/")
    print(f"  5. Chạy test so sánh với bản gốc")
    print(f"  6. Điền delta_report.md với bằng chứng")
    print(f"  7. Chạy: python scripts/c2_validate.py --strict")
    print(f"  8. Chạy: python scripts/c2_score_check.py")


def main():
    parser = argparse.ArgumentParser(description="C2 New Challenge Scaffold")
    parser.add_argument("--id", type=str, help="Challenge ID (tự động nếu bỏ trống)")
    parser.add_argument("--target", type=str, required=True, help="Target technology ID (e.g. T000001)")
    parser.add_argument("--session", type=str, default="S00000000-000")
    parser.add_argument("--agent", type=str, default="unknown-agent")
    args = parser.parse_args()

    challenge_id = args.id if args.id else next_challenge_id()
    scaffold(challenge_id, args.target, args.session, args.agent)


if __name__ == "__main__":
    main()
