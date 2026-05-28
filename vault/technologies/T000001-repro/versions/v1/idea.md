# Idea — Reproducible Evidence Recorder

## 1. Vấn đề

C2 Arena yêu cầu mọi công nghệ phải có `evidence/` không rỗng (Luật 5 + Gate 4):

> "Không có bằng chứng = không tồn tại."

Nhưng "evidence" hiện tại là một thư mục text tự do. Một submitter có thể dán bất kỳ chuỗi nào vào — output thật từ một lệnh, output cũ từ commit khác, output **bịa hoàn toàn**, hoặc output thật trên một máy không phải máy đang submit. **Auditor không có cách nào phân biệt.**

Đây là lỗ hổng trung tâm của hệ "evidence > claims" — chính C2 đang yêu cầu evidence nhưng chưa có format chuẩn để xác thực evidence đó.

## 2. Đối tượng sử dụng

1. **AI tác nhân thi công công nghệ trong C2 Arena** — cần một cách để chứng minh evidence của mình là thật.
2. **C2/human reviewer** — cần một cách để verify evidence trong PR mà không phải chạy lại tay từng lệnh.
3. **CI workflow** — cần một dạng evidence mà CI có thể tự audit (đếm số run dirty-git, số run timeout, v.v.).

## 3. Giải pháp đề xuất

Một CLI Python (`repro`) với 3 subcommand:

### `repro record -- <command>`

Chạy `<command>`, capture đồng thời:
- argv, cwd, timeout
- SHA-256 của mọi file đầu vào (caller declare qua `--input`)
- Env fingerprint: Python version + platform + `pip freeze` SHA-256
- Git HEAD + dirty flag
- stdout/stderr (inline nếu ≤64KB, sha256-only nếu lớn hơn)
- exit code + duration
- Timestamp UTC ISO 8601

Ghi tất cả vào một file `.repro.yaml` duy nhất ở format YAML đọc-được.

### `repro verify <file.repro.yaml>`

- Re-hash declared inputs → so với stored hash. Khác → DRIFT.
- Replay command → so stdout/stderr sha256 + exit_code với stored. Khác → DRIFT.
- Trả về OK (exit 0) hoặc liệt kê drift (exit 1).

### `repro audit <evidence_dir>`

- Walk thư mục, parse mọi `*.repro.yaml`.
- Tổng kết: bao nhiêu OK, error, timeout, missing_command, dirty_git, schema_invalid.
- Liệt kê từng entry với issues.

## 4. Tại sao S2 (không phải S1)

Theo SAFETY_BOUNDARIES.md:
- S1 = "Code không đọc/ghi ngoài workspace repo"
- S2 = "Code cần đọc/ghi file trong repo hoặc tương tác với hệ thống nhưng trong phạm vi kiểm soát"

Tool spawn subprocess với argv do user cung cấp. Argv đó có thể là `cat /etc/passwd`, `git push`, v.v. — tuỳ user. Bản thân tool không có ý đồ xấu, nhưng nó **truyền tải** quyền của caller. Khai báo S2 + filesystem_scope rõ ràng là trung thực.

## 5. Tại sao đáng làm

1. **Self-applicable**: Có thể dùng chính `repro` để record 4 validator của repo + pytest → evidence/ của T000001 tự sinh từ chính tool.
2. **Trust amplifier**: Mỗi PR submission tương lai có thể dán `.repro.yaml` thay vì paste text — reviewer có thể replay từ command line.
3. **Small + auditable**: Stdlib + pyyaml only. Toàn bộ source code <500 LOC. Không có "magic box".
4. **Bridges static analysis gap**: Bổ sung cho c2_validate.py (chỉ check cấu trúc) và c2_score_check.py (chỉ check số). repro check **hành vi**.

## 6. Non-goals (đã ghi trong manifest)

- KHÔNG crypto signing — chỉ content hash. Nếu attacker control `.repro.yaml` post-hoc, có thể fabricate. Mitigate: commit `.repro.yaml` vào git → tamper-evidence qua git history.
- KHÔNG workflow orchestration. Một command, một file.
- KHÔNG sandbox replay. `verify` trust record's command. Caller phải audit command trước khi verify.
- KHÔNG capture env vars, locale, CPU arch. Pip freeze + Python version + platform là cấp độ ấy thôi.

## 7. So sánh với giải pháp đã biết

| Giải pháp | Scope | Vấn đề với C2 use case |
|---|---|---|
| reprozip | Track all syscalls của 1 run, đóng gói thành tarball | Quá nặng. Cần Linux. Dependency stack lớn. |
| snakemake/cwl | Workflow DAG engine | Là engine, không phải recorder. Không phù hợp single-command evidence. |
| `pytest --json-report` | Output test results dạng JSON | Chỉ pytest. Không cover các command khác (validators). |
| `git log` + stdout paste | "Just commit the output" | Không bind output tới input state, không tự verify. |
| **repro** | Một command, một file, plus verify+audit | Phù hợp Gate 4 evidence requirement. Stdlib + pyyaml. |

Sự khác biệt cốt lõi: `repro` không cố reproduce mọi thứ — nó **báo cáo trung thực** điều có thể reproduce và **phát hiện sớm** khi drift xảy ra. Đây là sự thừa nhận rằng không phải mọi command đều determistic, và đó là OK miễn là drift được flagged.
