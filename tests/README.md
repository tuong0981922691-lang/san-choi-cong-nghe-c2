# Tests — Kiểm Thử Tính Toàn Vẹn Repo

## Mục đích

Các test này kiểm tra tính toàn vẹn cấu trúc của repo C2 Arena, không phải test công nghệ cụ thể.

## Chạy tests

```bash
python -m pytest tests/ -v
```

## Nội dung

- `test_repo_integrity.py` — Kiểm tra root files, thư mục bắt buộc, index files
- `test_manifest_rules.py` — Kiểm tra schema và luật manifest cho mọi technology
- `test_score_rules.py` — Kiểm tra luật điểm (score <= 8.0, challenge delta hợp lệ)
