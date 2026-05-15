#!/usr/bin/env python3
"""
C2 Index Builder
Rebuild vault/technologies/INDEX.yaml, vault/challenges/INDEX.yaml,
vault/crowns/CROWN_REGISTRY.yaml và LEADERBOARD.md.
"""

import sys
import yaml
import argparse
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).parent.parent
TECH_DIR = REPO_ROOT / "vault" / "technologies"
CHALLENGE_DIR = REPO_ROOT / "vault" / "challenges"
CROWNS_DIR = REPO_ROOT / "vault" / "crowns"

DOMAINS = [
    "algorithm", "ai-tooling", "developer-tool", "data-system",
    "simulation", "security-defense", "creative-media-safe",
    "education", "automation-safe", "architecture-pattern"
]


def load_yaml(path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def rebuild_tech_index():
    entries = []
    if not TECH_DIR.is_dir():
        return entries

    for tech_dir in sorted(TECH_DIR.iterdir()):
        if not tech_dir.is_dir() or tech_dir.name.startswith("."):
            continue
        versions_dir = tech_dir / "versions"
        if not versions_dir.is_dir():
            continue

        lineage = load_yaml(tech_dir / "lineage.yaml") or {}
        latest_version = lineage.get("current_version", "v1")
        manifest_path = versions_dir / latest_version / "manifest.yaml"
        manifest = load_yaml(manifest_path) or {}

        entry = {
            "id": manifest.get("id", tech_dir.name[:7]),
            "slug": manifest.get("slug", tech_dir.name[8:]),
            "title": manifest.get("title", ""),
            "domain": manifest.get("domain", {}).get("primary", "unknown"),
            "status": manifest.get("status", "unknown"),
            "version": latest_version,
            "score": manifest.get("score", {}).get("self_declared_base_score", 0.0),
            "safety_class": manifest.get("safety", {}).get("class", "S1"),
            "created_at": manifest.get("creator", {}).get("created_at", ""),
            "path": str(tech_dir.relative_to(REPO_ROOT)),
        }
        entries.append(entry)

    index_path = TECH_DIR / "INDEX.yaml"
    index_path.write_text(
        yaml.dump({"technologies": entries, "last_updated": str(date.today())},
                  allow_unicode=True, default_flow_style=False),
        encoding="utf-8"
    )
    print(f"[OK] vault/technologies/INDEX.yaml — {len(entries)} entries")
    return entries


def rebuild_challenge_index():
    entries = []
    if not CHALLENGE_DIR.is_dir():
        return entries

    for challenge_dir in sorted(CHALLENGE_DIR.iterdir()):
        if not challenge_dir.is_dir() or challenge_dir.name.startswith("."):
            continue
        manifest_path = challenge_dir / "challenge_manifest.yaml"
        manifest = load_yaml(manifest_path) or {}

        entry = {
            "id": manifest.get("id", ""),
            "target_id": manifest.get("target", {}).get("technology_id", ""),
            "status": manifest.get("status", "proposed"),
            "proposed_delta": manifest.get("score", {}).get("proposed_delta", 0),
            "created_at": manifest.get("created_at", ""),
            "path": str(challenge_dir.relative_to(REPO_ROOT)),
        }
        entries.append(entry)

    index_path = CHALLENGE_DIR / "INDEX.yaml"
    index_path.write_text(
        yaml.dump({"challenges": entries, "last_updated": str(date.today())},
                  allow_unicode=True, default_flow_style=False),
        encoding="utf-8"
    )
    print(f"[OK] vault/challenges/INDEX.yaml — {len(entries)} entries")
    return entries


def rebuild_crown_registry(tech_entries):
    reg_path = CROWNS_DIR / "CROWN_REGISTRY.yaml"
    existing = load_yaml(reg_path) if reg_path.exists() else {}
    domains_data = existing.get("domains", {}) if existing else {}

    # Ensure all domains exist
    for domain in DOMAINS:
        if domain not in domains_data:
            domains_data[domain] = {
                "current_holder": {
                    "technology_id": None,
                    "version": None,
                    "arena_score": 0.0,
                    "since": None,
                },
                "history": []
            }

    # Update current holders based on accepted technologies
    domain_scores = {}
    for entry in tech_entries:
        if entry["status"] == "accepted":
            domain = entry["domain"]
            score = entry.get("score", 0.0)
            if domain not in domain_scores or score > domain_scores[domain]["score"]:
                domain_scores[domain] = {
                    "score": score,
                    "tech_id": entry["id"],
                    "version": entry["version"],
                    "since": entry.get("created_at"),
                }

    for domain, info in domain_scores.items():
        if domain in domains_data:
            domains_data[domain]["current_holder"] = {
                "technology_id": info["tech_id"],
                "version": info["version"],
                "arena_score": info["score"],
                "since": info["since"],
            }

    registry = {
        "last_updated": str(date.today()),
        "domains": domains_data
    }
    CROWNS_DIR.mkdir(parents=True, exist_ok=True)
    reg_path.write_text(
        yaml.dump(registry, allow_unicode=True, default_flow_style=False),
        encoding="utf-8"
    )
    print(f"[OK] vault/crowns/CROWN_REGISTRY.yaml rebuilt")
    return domains_data


def rebuild_leaderboard(tech_entries, domains_data):
    lines = [
        "# Leaderboard — Bảng Xếp Hạng Ngôi Vương C2",
        "",
        f"> Cập nhật: {date.today()}",
        "",
        "## Ngôi vương theo domain",
        "",
        "| Domain | Technology ID | Title | Score | Since |",
        "|--------|--------------|-------|-------|-------|",
    ]

    for domain in DOMAINS:
        d = domains_data.get(domain, {})
        holder = d.get("current_holder", {})
        tech_id = holder.get("technology_id") or "—"
        score = holder.get("arena_score", 0.0)
        since = holder.get("since") or "—"
        title = "—"
        if tech_id != "—":
            for e in tech_entries:
                if e["id"] == tech_id:
                    title = e.get("title", "—")
                    break
        lines.append(f"| {domain} | {tech_id} | {title} | {score} | {since} |")

    lines += [
        "",
        "## Tất cả công nghệ trong vault",
        "",
        "| ID | Title | Domain | Score | Status | Version |",
        "|----|-------|--------|-------|--------|---------|",
    ]

    for e in sorted(tech_entries, key=lambda x: x.get("score", 0), reverse=True):
        lines.append(
            f"| {e['id']} | {e.get('title','—')} | {e.get('domain','—')} "
            f"| {e.get('score',0)} | {e.get('status','—')} | {e.get('version','—')} |"
        )

    if not tech_entries:
        lines.append("| — | (Chưa có công nghệ nào) | — | — | — | — |")

    lines += [
        "",
        "---",
        "",
        "*Điểm tối đa tự thân: 8.0. Ngôi vương là tạm thời.*",
    ]

    lb_path = CROWNS_DIR / "LEADERBOARD.md"
    lb_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] vault/crowns/LEADERBOARD.md rebuilt")


def next_id(kind):
    if kind == "technology":
        existing = []
        if TECH_DIR.is_dir():
            for d in TECH_DIR.iterdir():
                if d.is_dir() and d.name[1:7].isdigit() and d.name.startswith("T"):
                    existing.append(int(d.name[1:7]))
        return f"T{(max(existing, default=0)+1):06d}"
    elif kind == "challenge":
        existing = []
        if CHALLENGE_DIR.is_dir():
            for d in CHALLENGE_DIR.iterdir():
                if d.is_dir() and d.name.startswith("U"):
                    part = d.name[1:d.name.index("-on-")] if "-on-" in d.name else d.name[1:7]
                    if part.isdigit():
                        existing.append(int(part))
        return f"U{(max(existing, default=0)+1):06d}"
    return None


def main():
    parser = argparse.ArgumentParser(description="C2 Index Builder")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild tất cả indexes")
    parser.add_argument("--next-id", type=str, choices=["technology", "challenge"],
                        help="In ra ID tiếp theo")
    args = parser.parse_args()

    if args.next_id:
        print(next_id(args.next_id))
        return

    if args.rebuild:
        print("Rebuilding C2 indexes...")
        tech_entries = rebuild_tech_index()
        rebuild_challenge_index()
        domains_data = rebuild_crown_registry(tech_entries)
        rebuild_leaderboard(tech_entries, domains_data)
        print("\n[DONE] Tất cả indexes đã được rebuild.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
