#!/usr/bin/env python3
"""
C2 New Technology Scaffold
Tạo cấu trúc thư mục công nghệ mới từ template.
"""

import os
import sys
import shutil
import argparse
import yaml
from pathlib import Path
from datetime import date

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).parent.parent
TEMPLATE_DIR = REPO_ROOT / "templates" / "technology"
VAULT_DIR = REPO_ROOT / "vault" / "technologies"

VALID_DOMAINS = [
    "algorithm", "ai-tooling", "developer-tool", "data-system",
    "simulation", "security-defense", "creative-media-safe",
    "education", "automation-safe", "architecture-pattern"
]


def next_tech_id():
    existing = []
    if VAULT_DIR.is_dir():
        for d in VAULT_DIR.iterdir():
            if d.is_dir():
                m = d.name[:7]
                if m.startswith("T") and m[1:].isdigit():
                    existing.append(int(m[1:]))
    next_num = max(existing, default=0) + 1
    return f"T{next_num:06d}"


def scaffold(tech_id, slug, domain, mode, session_id):
    tech_slug = f"{tech_id}-{slug}"
    dest = VAULT_DIR / tech_slug

    if dest.exists():
        print(f"[ERROR] Đã tồn tại: {dest}")
        sys.exit(1)

    version_dir = dest / "versions" / "v1"
    version_dir.mkdir(parents=True)

    # Copy template files
    for item in TEMPLATE_DIR.rglob("*"):
        if item.is_file():
            rel = item.relative_to(TEMPLATE_DIR)
            target = version_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)

    # Create lineage.yaml
    lineage = {
        "id": tech_id,
        "slug": slug,
        "current_version": "v1",
        "versions": ["v1"],
        "derived_from": [],
        "superseded_by": None,
    }
    (dest / "lineage.yaml").write_text(
        yaml.dump(lineage, allow_unicode=True, default_flow_style=False),
        encoding="utf-8"
    )

    # Update manifest.yaml
    manifest_path = version_dir / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["id"] = tech_id
    manifest["slug"] = slug
    manifest["title"] = slug.replace("-", " ").title()
    manifest["mode"] = mode
    manifest["creator"]["created_at"] = str(date.today())
    manifest["creator"]["session_id"] = session_id
    manifest["domain"]["primary"] = domain
    manifest_path.write_text(
        yaml.dump(manifest, allow_unicode=True, default_flow_style=False),
        encoding="utf-8"
    )

    print(f"[OK] Scaffold tạo tại: {dest.relative_to(REPO_ROOT)}")
    print(f"     ID: {tech_id}")
    print(f"     Slug: {slug}")
    print(f"     Domain: {domain}")
    print(f"     Mode: {mode}")
    print(f"\nBước tiếp theo:")
    print(f"  1. Chỉnh sửa {dest.relative_to(REPO_ROOT)}/versions/v1/")
    print(f"  2. Điền idea.md, architecture.md, src/, tests/, evidence/")
    print(f"  3. Tự phản biện trong self_critique.md (tối thiểu 10 điểm)")
    print(f"  4. Chạy: python scripts/c2_validate.py --strict")
    print(f"  5. Chạy: python scripts/c2_score_check.py")


def main():
    parser = argparse.ArgumentParser(description="C2 New Technology Scaffold")
    parser.add_argument("--id", type=str, help="Technology ID (tự động nếu bỏ trống)")
    parser.add_argument("--slug", type=str, required=True, help="Technology slug (e.g. my-algorithm)")
    parser.add_argument("--domain", type=str, default="algorithm",
                        choices=VALID_DOMAINS, help="Primary domain")
    parser.add_argument("--mode", type=str, default="NEW_FROM_WASTE",
                        choices=["NEW_FROM_WASTE", "UPGRADE_EXISTING"])
    parser.add_argument("--session", type=str, default="S00000000-000",
                        help="Session ID")
    args = parser.parse_args()

    tech_id = args.id if args.id else next_tech_id()
    slug = args.slug.lower().replace(" ", "-").replace("_", "-")
    scaffold(tech_id, slug, args.domain, args.mode, args.session)


if __name__ == "__main__":
    main()
