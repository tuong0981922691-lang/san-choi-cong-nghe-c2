# Scripts

## Công cụ C2 Arena

| Script | Mô tả |
|--------|-------|
| `c2_validate.py` | Kiểm định toàn bộ repo và submission |
| `c2_score_check.py` | Kiểm tra điểm tự chấm không vượt 8.0 |
| `c2_new_tech.py` | Scaffold thư mục công nghệ mới từ template |
| `c2_new_challenge.py` | Scaffold thư mục challenge mới |
| `c2_index.py` | Rebuild index files và leaderboard |
| `c2_secret_scan.py` | Quét secrets tiềm ẩn trong repo |
| `safe_run.sh` | Chạy code công nghệ trong sandbox cách ly |

## Cách dùng

```bash
# Kiểm định toàn bộ
python scripts/c2_validate.py --strict

# Kiểm tra điểm
python scripts/c2_score_check.py

# Tạo công nghệ mới
python scripts/c2_new_tech.py --id T000001 --slug my-tech --domain algorithm

# Tạo challenge mới
python scripts/c2_new_challenge.py --id U000001 --target T000001

# Rebuild index
python scripts/c2_index.py --rebuild

# Quét secrets
python scripts/c2_secret_scan.py

# Chạy sandbox
bash scripts/safe_run.sh vault/technologies/T000001-my-tech/versions/v1
```

## Yêu cầu

- Python 3.9+
- PyYAML: `pip install pyyaml`
- jsonschema (tùy chọn): `pip install jsonschema`
