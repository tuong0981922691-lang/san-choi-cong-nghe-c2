# Tests — Hướng dẫn

Thư mục này chứa tests cho code trong `../src/` của challenge.

## Yêu cầu

- Ít nhất một test file chạy được
- Tests phải kiểm chứng **cụ thể** rằng phương án nâng cấp tốt hơn target
- Có thể là unit tests, integration tests, hoặc benchmark tests

## Ví dụ cấu trúc

```text
tests/
├── README.md                (file này)
├── test_{tên_chức_năng}.py  — Unit tests
├── test_benchmark.py        — Benchmark so sánh với target
└── test_regression.py       — Đảm bảo tính năng cũ không bị phá
```

## Chạy tests

```bash
python -m pytest tests/ -v
```

## Kết quả phải lưu vào

`../evidence/test_results.txt`

```bash
python -m pytest tests/ -v 2>&1 | tee ../evidence/test_results.txt
```
