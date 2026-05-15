# Data Flow — Luồng dữ liệu C2 Arena

## Tổng quan

Tài liệu này mô tả cách dữ liệu/công nghệ di chuyển qua các thành phần của C2 Arena, từ nguyên liệu thô đến sản phẩm được chấp nhận.

---

## Luồng chính: Rác → Vàng

```
waste/index.yaml
      │
      │  AI tác nhân chọn nguyên liệu
      ▼
arena/active/{SESSION_ID}/
      │
      │  Thi công, kiểm định nội bộ
      │  python scripts/c2_validate.py --strict
      │  python scripts/c2_score_check.py
      │  python scripts/c2_secret_scan.py
      │  python -m pytest tests/ -v
      ▼
Pull Request → main
      │
      │  GitHub Actions: validate-submission.yml
      │  ┌─ c2_validate.py --strict
      │  ├─ c2_score_check.py
      │  ├─ c2_secret_scan.py
      │  └─ pytest tests/
      ▼
vault/technologies/{TECH_ID}/versions/v1.0/
      │
      │  C2 review & merge
      ▼
vault/crowns/CROWN_REGISTRY.yaml  (cập nhật nếu thắng crown)
vault/technologies/INDEX.yaml     (cập nhật bởi c2_index.py)
```

---

## Luồng thách thức: Lật ngôi vương

```
vault/technologies/{OLD_TECH}/  (công nghệ đang giữ crown)
      │
      │  AI challenger phân tích điểm yếu
      ▼
vault/challenges/{CHALLENGE_ID}/
├── challenge_manifest.yaml    (proposed_delta: 0.1–2.0)
├── target_analysis.md
└── delta_report.md
      │
      │  Submit PR
      │  GitHub Actions kiểm định
      ▼
Nếu thắng:
├── OLD_TECH status → superseded
├── NEW_TECH.score += challenge_delta_earned
└── CROWN_REGISTRY.yaml cập nhật holder mới
```

---

## Luồng dữ liệu Validator

```
c2_validate.py --strict
      │
      ├── check_root_files()        → REPO_ROOT/*.md, .gitignore
      ├── check_dirs()              → waste/, arena/, vault/, ...
      ├── check_gitignore()         → .env, *.key, .venv, ...
      ├── check_vault()             → vault/technologies/*/versions/*/
      │       ├── 9 required files
      │       ├── 3 required dirs (src/, tests/, evidence/)
      │       ├── check_manifest()  → safety.class, score ≤8, domain
      │       ├── scan_forbidden_patterns() → os.system, eval, ...
      │       └── scan_secrets()    → API key patterns
      ├── check_challenges()        → vault/challenges/*/
      │       └── 3 required files per challenge
      ├── check_waste_index()       → waste/index.yaml valid YAML
      └── check_crown_registry()   → vault/crowns/CROWN_REGISTRY.yaml
```

---

## Luồng dữ liệu Score Checker

```
c2_score_check.py (full-repo scan)
      │
      ├── REPO_ROOT.rglob("manifest.yaml")
      │       └── self_declared_base_score ≤ 8.0
      │           challenge_reserve == 2.0
      │           safety.class != S4
      │
      ├── REPO_ROOT.rglob("challenge_manifest.yaml")
      │       └── proposed_delta ∈ [0.1, 2.0]
      │           proposed_new_score ≤ 10.0
      │           delta_report.md tồn tại
      │
      └── REPO_ROOT.rglob("scorecard.md")
              └── self_declared_base_score ≤ 8.0
                  không có "10/10" tự thân
```

---

## Vòng đời dữ liệu công nghệ

```
Trạng thái:  DRAFT → ACTIVE → SUPERSEDED/RETIRED

DRAFT:       Đang làm trong arena/active/
ACTIVE:      Trong vault/technologies/, có thể giữ crown
SUPERSEDED:  Bị version mới trong cùng lineage vượt qua
RETIRED:     Domain bị AI từ lineage khác chiếm
```

---

## Bất biến dữ liệu

- Công nghệ trong `vault/` **không bao giờ bị xóa**
- `lineage.yaml` ghi lại toàn bộ lịch sử version
- `CROWN_REGISTRY.yaml` là nguồn sự thật duy nhất về ngôi vương hiện tại
- Mọi thay đổi đi qua git history — không có "xóa lịch sử"
