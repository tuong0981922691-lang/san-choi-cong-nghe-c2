# Delta Report — Báo Cáo Cải Thiện

## Tóm tắt

Công nghệ T000000 có điểm yếu X. Bản nâng cấp này vá điểm yếu đó bằng Y.

## So sánh trước và sau

| Hạng mục | Trước (T000000 v1) | Sau (challenge này) | Bằng chứng |
|----------|-------------------|---------------------|------------|
| ... | ... | ... | ... |

## Test so sánh

Chạy: `python -m pytest tests/compare_with_original.py`

Kết quả:
```
[Dán output test vào đây]
```

## Benchmark so sánh (nếu có)

| Metric | Bản gốc | Bản nâng cấp | Cải thiện |
|--------|---------|-------------|----------|
| ... | ... | ... | ... |

## Đề xuất điểm

- Điểm cũ: X.XX
- Delta đề xuất: +X.XX
- Điểm mới đề xuất: X.XX

Lý do: ...

## Không có regression

Tôi xác nhận bản nâng cấp này:
- [ ] Không vi phạm luật tổng C2
- [ ] Không tăng safety class lên S4
- [ ] Không phá chức năng cũ
- [ ] Có test chứng minh chức năng cũ vẫn hoạt động
