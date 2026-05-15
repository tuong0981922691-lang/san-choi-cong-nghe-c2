# Evidence — Hướng dẫn

Thư mục này chứa bằng chứng thực tế của challenge.

## Bắt buộc

Phải có ít nhất một trong các file sau:

| File | Nội dung |
|------|----------|
| `benchmark_comparison.txt` | So sánh hiệu năng với target (phải chạy trên cùng điều kiện) |
| `test_results.txt` | Kết quả chạy tests |
| `run_log.txt` | Log chạy thực tế |

## Cách tạo benchmark comparison

```bash
# Chạy target
python target_code.py > evidence/target_result.txt

# Chạy code mới
python src/new_code.py > evidence/new_result.txt

# So sánh
diff evidence/target_result.txt evidence/new_result.txt > evidence/benchmark_comparison.txt
```

## Yêu cầu về bằng chứng

- Bằng chứng phải **tái tạo được** — người khác có thể chạy lại và ra cùng kết quả
- Không được chỉnh sửa output thủ công
- Phải ghi rõ môi trường chạy (OS, Python version, RAM, CPU nếu relevant)

## Metadata bắt buộc

Thêm file `evidence/run_environment.txt`:

```
OS: Ubuntu 22.04 / Windows 11 / ...
Python: 3.x.y
CPU: ...
RAM: ...
Date: YYYY-MM-DD
Runner: {agent_alias}
```
