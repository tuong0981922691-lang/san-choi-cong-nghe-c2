# Vault — Kho Vàng Công Nghệ C2

## Mục đích

Đây là nơi lưu trữ công nghệ đã được kiểm định và chấp nhận vào sân chơi C2.

## Cấu trúc

```text
vault/
  technologies/   — Công nghệ đã được accept
    T000001-slug/ — Mỗi technology có ID + slug
      lineage.yaml
      versions/
        v1/       — Version đầu tiên
  challenges/     — Challenge nâng cấp
    U000001-on-T000001/
  crowns/         — Ngôi vương theo domain
    CROWN_REGISTRY.yaml
    LEADERBOARD.md
  retired/        — Công nghệ đã bị vượt qua hoặc vi phạm
```

## Luật vault

- Không xóa công nghệ đã accept
- Không sửa nội dung trực tiếp — tạo version mới
- Nâng cấp qua challenge có lineage
- Công nghệ bị vượt: trạng thái `superseded`, không bị xóa
- Công nghệ vi phạm luật: chuyển sang `retired/` với nhãn `VIOLATION`

## Cập nhật index

```bash
python scripts/c2_index.py --rebuild
```
