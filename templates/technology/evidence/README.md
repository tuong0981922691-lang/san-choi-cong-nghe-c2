# Evidence — Bằng Chứng Chạy

## Nội dung bắt buộc

Thư mục này phải chứa ít nhất một trong:

- `run_log.txt` — output của lần chạy thật
- `benchmark.md` — kết quả đo lường hiệu suất
- `test_results.txt` — kết quả chạy test suite

## Định dạng run_log.txt

```
Date: YYYY-MM-DD HH:MM
Command: python src/main.py --input sample.txt
Environment: Python 3.12, Ubuntu 22.04
---
[Output thực tế ở đây]
---
Exit code: 0
```

## Định dạng benchmark.md

So sánh với baseline (nếu có), đơn vị đo rõ ràng, điều kiện đo cụ thể.
