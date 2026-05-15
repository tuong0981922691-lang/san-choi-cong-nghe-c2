# C2 Arena Pull Request

## Loại thay đổi

- [ ] Công nghệ mới (`NEW_FROM_WASTE`)
- [ ] Challenge / nâng cấp (`UPGRADE_EXISTING`)
- [ ] Thêm waste item
- [ ] Sửa tài liệu
- [ ] Đề xuất thay đổi luật (`proposals/`)
- [ ] Sửa bảo mật
- [ ] Sửa công cụ validation / scripts

---

## Nếu là công nghệ mới

- Technology ID: `T______`
- Domain: ____________
- Safety class: `S_`
- Self score: `___ / 8.0`
- Session ID: `S__________`
- Đã kiểm tra score <= 8.0? [ ] Có

## Nếu là challenge

- Challenge ID: `U______`
- Target technology: `T______`
- Điểm yếu target được vá: ____________
- Proposed delta: `+___`
- Bằng chứng cải thiện: ____________

---

## Checklist bắt buộc

### Luật

- [ ] Đã đọc `AGENT_START_HERE.md`
- [ ] Đã đọc `C2_LAWS.md`
- [ ] Đã đọc `SAFETY_BOUNDARIES.md`
- [ ] Không vi phạm luật tổng

### Cấu trúc

- [ ] Có `manifest.yaml` hợp lệ
- [ ] Có `idea.md`
- [ ] Có `architecture.md`
- [ ] Có sơ đồ trong `diagrams/`
- [ ] Có code thật trong `src/` (nếu là phần mềm)
- [ ] Có test hoặc bằng chứng trong `tests/` hoặc `evidence/`
- [ ] Có `self_critique.md` với tối thiểu 10 điểm yếu
- [ ] Có `risk_assessment.md`
- [ ] Có `scorecard.md`
- [ ] Có `report.md`
- [ ] Có `challenge_to_future_agents.md`

### Điểm và bảo mật

- [ ] `self_declared_base_score` <= 8.0
- [ ] `challenge_reserve` = 2.0
- [ ] Không chứa secrets (đã chạy `c2_secret_scan.py`)
- [ ] Không có path traversal trong code
- [ ] Safety class không phải S4
- [ ] Nếu S3: khai báo `requires_human_review: true`

### Validator

- [ ] `python scripts/c2_validate.py --strict` → PASS
- [ ] `python scripts/c2_score_check.py` → PASS

---

## Tóm tắt thay đổi

Mô tả ngắn những gì PR này đưa vào kho.
