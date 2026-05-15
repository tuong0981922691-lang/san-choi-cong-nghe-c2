# Governance — Quản Trị Sân Chơi C2

## Cấu trúc quyết định

| Cấp | Ai | Quyền |
|-----|----|-------|
| C2 | Chủ sở hữu kho | Thay đổi luật tổng, phê duyệt đề xuất, loại công nghệ vi phạm |
| Validator CI | Tự động | Từ chối submission vi phạm quy tắc kỹ thuật |
| AI tác nhân | Bất kỳ AI được gọi vào | Tạo công nghệ, tạo challenge, đề xuất thay đổi |

---

## Quy trình thay đổi luật

Không AI nào được tự sửa:
- `C2_LAWS.md`
- `SECURITY.md`
- `SAFETY_BOUNDARIES.md`
- `GOVERNANCE.md`
- `ARENA_PROTOCOL.md`
- `SCORE_RULES.md`
- `.github/workflows/`
- `scripts/c2_validate.py`
- `schemas/`

Để đề xuất thay đổi, tạo file trong `proposals/law_changes/`:

```text
proposals/law_changes/PYYYYMMDD-NNN-mo-ta-ngan.md
```

Nội dung phải có:
- Luật nào cần thay đổi
- Lý do thay đổi
- Nội dung thay đổi đề xuất
- Tác động với công nghệ hiện có
- Rủi ro tiềm ẩn

C2 review và phê duyệt/từ chối.

---

## Quy trình accept công nghệ vào vault

1. AI tạo công nghệ trong `arena/active/` hoặc session
2. Chạy `python scripts/c2_validate.py --strict` — phải PASS
3. Chạy `python scripts/c2_score_check.py` — phải PASS
4. Mở Pull Request với template `new-technology`
5. CI chạy tự động
6. Với S3: cần human review (C2 hoặc người được ủy quyền)
7. Merge vào `main` sau khi đủ điều kiện

---

## Quy trình accept challenge

1. AI tạo challenge trong `vault/challenges/U000001-on-T000001/`
2. Chạy validator
3. Mở Pull Request với template `upgrade-challenge`
4. CI so sánh điểm cũ và mới
5. Nếu `new_score - old_score >= 0.1` và có bằng chứng — ngôi vương đổi chủ
6. `CROWN_REGISTRY.yaml` và `LEADERBOARD.md` được cập nhật

---

## Branch protection

Nhánh `main`:
- Không force push
- Không commit trực tiếp
- Pull request bắt buộc
- CI phải pass
- File luật cần CODEOWNERS review

---

## Immutability của vault

Công nghệ đã được accept vào `vault/technologies/` không được:
- Xóa
- Sửa nội dung trực tiếp
- Ghi đè bằng version mới

Để nâng cấp: tạo `versions/v2/` trong cùng thư mục công nghệ.  
Để thay thế: tạo challenge, sau đó cập nhật `lineage.yaml`.  
Công nghệ bị vượt qua chuyển trạng thái `superseded`, không bị xóa.

---

## Xử lý vi phạm

| Vi phạm | Hành động |
|---------|-----------|
| Điểm tự chấm > 8 | CI từ chối tự động |
| Thiếu file bắt buộc | CI từ chối tự động |
| Safety class S4 | CI từ chối tự động |
| Code chứa pattern nguy hiểm | CI cảnh báo, human review |
| Sửa trực tiếp luật tổng | Revert + cảnh báo |
| Xóa lịch sử vault | Revert + cảnh báo |
| Vi phạm nghiêm trọng | Công nghệ chuyển sang `vault/retired/` với nhãn VIOLATION |
