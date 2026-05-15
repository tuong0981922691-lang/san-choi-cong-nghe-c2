# License Decision

## Trạng thái hiện tại

Kho này **chưa có license chính thức** được chọn bởi C2.

Cho đến khi C2 quyết định, toàn bộ nội dung trong kho này thuộc quyền kiểm soát của chủ sở hữu kho.

## Lưu ý với AI tác nhân

AI tác nhân khi tạo công nghệ phải khai báo `license_intent` trong `manifest.yaml`:

```yaml
license_intent: "to-be-decided-by-c2"
```

Hoặc nếu AI muốn đề xuất license cụ thể cho công nghệ của mình, ghi rõ trong `manifest.yaml` và giải thích trong `report.md`.

## Lưu ý với waste items

Waste items phải khai báo `license_status`:
- `"unknown"` — chưa xác định
- `"public-domain"` — miền công cộng
- `"internal-example"` — ví dụ nội bộ
- `"requires-attribution"` — cần ghi nguồn
- `"restricted"` — hạn chế sử dụng

---

*C2 sẽ cập nhật file này khi có quyết định chính thức về license.*
