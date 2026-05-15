# Tests

## Chạy tests

```bash
python -m pytest tests -v
```

## Cấu trúc tests

```text
tests/
  test_core.py        — unit tests cho core logic
  test_integration.py — integration tests
  test_edge_cases.py  — edge cases và điều kiện biên
  conftest.py         — pytest fixtures
```

## Yêu cầu

Nếu công nghệ này là phần mềm, tests không được rỗng.

Ít nhất phải có:
- Test cho happy path chính
- Test cho ít nhất 3 edge cases
- Test cho error handling

Nếu không có automated tests, phải có bằng chứng trong `evidence/run_log.txt`.
