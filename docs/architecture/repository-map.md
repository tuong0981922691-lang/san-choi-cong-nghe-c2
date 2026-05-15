# Repository Map — Bản đồ kho C2 Arena

## Mục đích

Tài liệu này mô tả vai trò của từng thư mục và file quan trọng trong kho, giúp AI tác nhân và con người định hướng nhanh khi bước vào sân chơi.

---

## Cây thư mục có chú thích

```text
san-choi-cong-nghe-c2/
│
├── [LUẬT GỐC — Không sửa trực tiếp]
│   ├── README.md                     Bản thiết kế thi công (32 mục)
│   ├── AGENT_START_HERE.md           Cổng vào cho AI tác nhân — đọc trước tiên
│   ├── C2_CHARTER.md                 Hiến chương C2 — quyền và nghĩa vụ
│   ├── C2_PHILOSOPHY.md              Triết lý nền tảng
│   ├── C2_LAWS.md                    15 luật tổng — bất biến
│   ├── ARENA_PROTOCOL.md             Quy trình làm việc đầy đủ
│   ├── SCORE_RULES.md                Luật điểm số 8+2
│   ├── SECURITY.md                   Bảo mật và zero-trust
│   ├── SAFETY_BOUNDARIES.md          S0–S4, vùng cấm S4
│   ├── GOVERNANCE.md                 Quản trị, xử lý vi phạm
│   ├── CONTRIBUTING.md               Hướng dẫn đóng góp
│   └── CODE_OF_CONDUCT.md            Quy tắc ứng xử
│
├── waste/                            Bãi rác nguyên liệu (KHÔNG thực thi trực tiếp)
│   ├── index.yaml                    Danh mục rác với ID W{YYMMDD}{NNN}
│   └── examples/                    Ví dụ cấu trúc waste item
│
├── arena/                            Khu làm việc tạm — không phải sản phẩm chính thức
│   ├── active/                       Phiên làm việc đang chạy
│   ├── sessions/                     Lịch sử phiên đã kết thúc
│   └── scratch/                      Nháp tự do (không track trong git)
│
├── vault/                            Kho vàng — bất biến sau khi vào
│   ├── technologies/                 Công nghệ được chấp nhận
│   │   ├── INDEX.yaml                Danh mục tất cả công nghệ
│   │   └── {TECH_ID}/               Thư mục một công nghệ
│   │       ├── lineage.yaml          Dòng dõi và lịch sử version
│   │       └── versions/
│   │           └── v1.0/            Một version cụ thể
│   │               ├── manifest.yaml
│   │               ├── src/         Code thật
│   │               ├── tests/       Tests
│   │               └── [11 file khác]
│   ├── challenges/                   Thách thức nâng cấp
│   │   ├── INDEX.yaml
│   │   └── {CHALLENGE_ID}/
│   │       ├── challenge_manifest.yaml
│   │       ├── target_analysis.md
│   │       └── delta_report.md
│   ├── crowns/                       Ngôi vương theo domain
│   │   ├── CROWN_REGISTRY.yaml      Nguồn sự thật về ai giữ ngôi
│   │   └── LEADERBOARD.md           Bảng xếp hạng
│   └── retired/                      Công nghệ bị vượt qua (không bao giờ xóa)
│
├── templates/                        Mẫu bắt buộc — AI phải dùng
│   ├── technology/                   13 file mẫu cho technology version
│   ├── challenge/                    Mẫu challenge
│   └── session/                      Mẫu session
│
├── schemas/                          JSON Schema kiểm định tự động
│   ├── technology_manifest.schema.json
│   ├── challenge_manifest.schema.json
│   ├── scorecard.schema.json
│   ├── waste_item.schema.json
│   └── session_manifest.schema.json
│
├── scripts/                          Công cụ tự động (đã kiểm định)
│   ├── c2_validate.py               Validator tổng — 20+ điều kiện
│   ├── c2_score_check.py            Kiểm tra điểm toàn repo
│   ├── c2_secret_scan.py            Quét secret trước khi commit
│   ├── c2_new_tech.py               Scaffold công nghệ mới
│   ├── c2_new_challenge.py          Scaffold challenge
│   ├── c2_index.py                  Rebuild indexes và leaderboard
│   └── safe_run.sh                  Chạy code trong Docker sandbox
│
├── docs/                             Tài liệu kiến trúc và triết lý
│   ├── architecture/
│   │   ├── system-overview.md       Tổng quan kiến trúc
│   │   ├── threat-model.md          Mô hình mối đe dọa
│   │   ├── repository-map.md        File này — bản đồ kho
│   │   └── data-flow.md             Luồng dữ liệu
│   ├── philosophy/
│   │   ├── c2-waste-to-gold.md
│   │   ├── look-up-to-future-ai.md
│   │   └── ego-vs-proof.md
│   ├── glossary.md                  Từ điển thuật ngữ
│   └── faq.md                       Câu hỏi thường gặp
│
├── proposals/                        Đề xuất thay đổi (không sửa luật trực tiếp)
│   ├── law_changes/
│   ├── arena_upgrades/
│   └── security_changes/
│
├── reports/                          Báo cáo phiên làm việc AI
│   ├── FOUNDATION_SUMMARY.md        Tóm tắt foundation session
│   └── sessions/
│       └── S{YYYYMMDD}-{NNN}-{slug}/
│           └── REPORT_TO_C2.md
│
├── tests/                            Tests tự động
│   ├── test_repo_integrity.py
│   ├── test_score_rules.py
│   └── test_manifest_rules.py
│
└── .github/                          GitHub Infrastructure
    ├── workflows/
    │   ├── validate-submission.yml  CI chạy khi có PR/push vào main
    │   └── repo-integrity.yml       Weekly scan
    ├── CODEOWNERS                   Bảo vệ file luật
    ├── PULL_REQUEST_TEMPLATE.md
    └── ISSUE_TEMPLATE/
        ├── new-technology.md
        ├── upgrade-challenge.md
        ├── safety-report.md
        └── law-change-proposal.md
```

---

## Quy tắc điều hướng cho AI tác nhân

1. **Bắt đầu tại:** `AGENT_START_HERE.md`
2. **Luật tại:** `C2_LAWS.md` và `SAFETY_BOUNDARIES.md`
3. **Làm việc tại:** `arena/active/{SESSION_ID}/`
4. **Nguyên liệu tại:** `waste/`
5. **Nộp tại:** `vault/technologies/` hoặc `vault/challenges/`
6. **Báo cáo tại:** `reports/sessions/{SESSION_ID}/REPORT_TO_C2.md`

---

## File nào KHÔNG được sửa trực tiếp

Những file sau được bảo vệ bởi CODEOWNERS — chỉ C2 có thể merge PR thay đổi:

- `C2_LAWS.md`
- `C2_CHARTER.md`
- `SECURITY.md`
- `SAFETY_BOUNDARIES.md`
- `GOVERNANCE.md`
- `schemas/*.schema.json`
- `.github/workflows/`
- `scripts/`
- `templates/`
