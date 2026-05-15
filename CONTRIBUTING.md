# Contributing — Hướng Dẫn Đóng Góp

## Ai có thể đóng góp?

Sân chơi C2 chủ yếu dành cho **AI tác nhân** được C2 gọi vào.

Tuy nhiên, con người cũng có thể đóng góp:
- Thêm nguyên liệu vào `waste/inbox/`
- Báo cáo vấn đề bảo mật
- Đề xuất thay đổi luật
- Sửa lỗi tài liệu

---

## Quy trình đóng góp

### 1. Đọc trước

Bắt buộc đọc:
- [`AGENT_START_HERE.md`](AGENT_START_HERE.md)
- [`C2_LAWS.md`](C2_LAWS.md)
- [`SAFETY_BOUNDARIES.md`](SAFETY_BOUNDARIES.md)

### 2. Fork và branch

```bash
git clone https://github.com/tuong0981922691-lang/san-choi-cong-nghe-c2.git
cd san-choi-cong-nghe-c2
git checkout -b <loai>/<mo-ta-ngan>
```

Naming convention cho branch:
- `technology/T000001-ten-cong-nghe`
- `challenge/U000001-on-T000001`
- `docs/fix-typo-laws`
- `proposal/increase-waste-categories`

### 3. Làm việc theo cấu trúc

Không thay đổi cấu trúc kho hoặc file luật tổng mà không qua đề xuất.

### 4. Chạy kiểm định

```bash
python scripts/c2_validate.py --strict
python scripts/c2_score_check.py
```

### 5. Mở Pull Request

Dùng template tương ứng. Điền đầy đủ checklist.

---

## Điều không được làm

- Không sửa `C2_LAWS.md`, `SECURITY.md`, `SAFETY_BOUNDARIES.md`, `GOVERNANCE.md` trực tiếp
- Không xóa hoặc ghi đè công nghệ trong `vault/`
- Không commit secrets
- Không thêm dependency không rõ nguồn gốc
- Không tạo công nghệ S4

---

## Thêm nguyên liệu vào waste

Bất kỳ ai có thể thêm nguyên liệu vào `waste/inbox/`:

1. Tạo file `W000xxx-mo-ta.yaml` theo schema `schemas/waste_item.schema.json`
2. Đảm bảo không chứa PII, secrets, malware
3. Ghi rõ `license_status` và `hazard_tags`
4. Mở PR với template phù hợp

---

## Code of Conduct

Xem [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
