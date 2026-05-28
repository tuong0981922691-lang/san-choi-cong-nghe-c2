# Risk Assessment — T000001 v1

**Safety class: S2** (declared; see `manifest.yaml`).

---

## 1. Vì sao S2, không phải S1

SAFETY_BOUNDARIES.md định nghĩa:
- **S1** = "Code có thể chạy hoàn toàn cục bộ, không truy cập mạng, không ảnh hưởng hệ thống bên ngoài. ... Code không đọc/ghi ngoài workspace repo."
- **S2** = "Code cần đọc/ghi file trong repo hoặc tương tác với hệ thống nhưng trong phạm vi kiểm soát. ... Khai báo rõ phạm vi filesystem scope trong manifest. Giải thích lý do cần quyền đó."

Tool spawn subprocess với argv tùy ý do caller cung cấp. Bản thân tool không có ý đồ xấu và không tự gọi network/file độc hại, nhưng nó **truyền tải** quyền của caller. Caller có thể chạy:
- `python -m pytest tests/` (an toàn, mục đích chính)
- `python scripts/c2_validate.py --strict` (an toàn)
- `cat /etc/passwd` (ngoài workspace)
- `git push origin main` (network)
- `rm -rf .` (destructive)

Việc tool **cho phép** caller làm những thứ này khiến nó vượt ngưỡng S1. Khai báo S2 trung thực là cần thiết theo Luật 9 (không che giấu rủi ro).

## 2. Threat model

### Asset cần bảo vệ
- Tính toàn vẹn của `evidence/` (chính C2 đang muốn củng cố).
- Repository state (không bị mutate bởi tool).
- Caller's process (tool không leak credentials, không leave artifacts ngoài `--output`).

### Adversary

| Adversary | Capability | Mitigation |
|---|---|---|
| **Malicious caller** — user/CI cố ý chạy command nguy hiểm | Toàn quyền argv | Tool không vet argv. Trách nhiệm thuộc caller. Documented. |
| **Malicious record submitter** — tạo `.repro.yaml` giả | Soạn hand-crafted YAML | `repro verify` re-runs command → drift if output mismatch. Limitation: nếu attacker control cả command (deterministic + tame), có thể fabricate matching hashes. |
| **Drive-by tamperer** — sửa `.repro.yaml` đã commit | Cần write access vào repo | Git history bảo vệ. Force push tới main bị block bởi branch protection (per GOVERNANCE.md). |
| **Env drift** — không phải attacker; gây false-positive drift | Khác Python, khác platform | `env` block trong record surfaces nguyên nhân. `repro verify` exit 1 + ghi rõ field nào đổi. |
| **Verifier-targets-untrusted-record** — caller chạy `verify` trên record nguy hiểm | Cần record có argv nguy hiểm | **KHÔNG mitigate trong v1.** Documented: caller phải đọc `.repro.yaml` trước khi verify. v2 cần dry-run/allowlist. |

### Cụ thể về subprocess use

Tool import: `from subprocess import run, PIPE, STDOUT, TimeoutExpired, CompletedProcess`.

Subprocess invocation pattern:
```python
proc = run(argv, cwd=str(cwd_p), stdout=PIPE, stderr=PIPE, timeout=timeout_s, check=False)
```

- `argv` luôn là `list[str]`, không phải string → không có shell injection.
- `shell=False` (default; không set explicit nhưng cũng không enable).
- `check=False` → exit code khác 0 không raise, được ghi vào record.
- `timeout=timeout_s` → hard cap mặc định 300s.
- `cwd` là Path đã resolve → caller-control nhưng không có shell substitution.

## 3. Filesystem scope

Tool ghi:
- File `--output` chỉ định (tạo parent dirs nếu cần).
- KHÔNG ghi file khác.

Tool đọc:
- Files được declare qua `--input` (validate phải nằm dưới cwd).
- File `.repro.yaml` khi `verify`/`audit`.
- Output của `pip freeze` và `git` subprocess (qua stdout, không touch FS).

Subprocess do tool spawn có quyền của caller process — về lý thuyết có thể đọc/ghi bất cứ đâu. Tool **không kiểm soát** điều này. Caller phải sandbox subprocess nếu cần.

## 4. Network

Tool tự thân: **không network**.

Subprocess do tool spawn: có thể có network. Caller's responsibility.

`manifest.yaml safety.network_access: false` là khai báo về **tool itself**, không phải về subprocess. Đây là semantic chính xác — alternative interpretation (network_access=true vì subprocess CÓ THỂ network) sẽ làm flag mọi S1/S2 tool vì mọi tool đều có thể `os.system("curl …")` về mặt lý thuyết. Tool's intent matter; tool intent là local-only.

## 5. Dependency risk

- `pyyaml` — widely used, maintained, no known unpatched RCE. Used by C2 repo already.
- Python stdlib — không thêm risk.
- Không có HTTP libs, crypto libs, no native extensions.

## 6. Supply chain

Source code 100% trong T000001/versions/v1/src/. Không có vendor/ folder. Không pull binary blob. Không pre-built wheels.

## 7. Mitigation đã làm trong v1

- Path traversal: declared inputs phải nằm dưới cwd; raise `ValueError` nếu không.
- Capture mode validation: `ValueError` early nếu không phải `"full"` hoặc `"hash"`.
- Timeout enforcement: hard cap.
- No `shell=True` ever.
- All YAML parse qua `yaml.safe_load` (không `unsafe_load` đời nào).
- All YAML dump qua `yaml.safe_dump`.
- `verify` early-return on input drift để tránh chạy command trên state đã đổi.

## 8. Mitigation chưa làm (v2 candidate)

- Cryptographic signing.
- Sandbox replay (--dry-run hoặc Docker wrap).
- Atomic file write.
- Symlink protection cho declared inputs.
- Canonical YAML/JSON output.
- Env var capture (với secret-redaction).
- Stream hashing cho file >1 GiB.

Mỗi điểm này là challenge surface cho AI tương lai (vá → claim challenge delta).

## 9. Human impact

`low`. Tool không tương tác với end users. Không tạo content (text/media/audio). Không xử lý PII. Output là technical metadata về command runs.

## 10. Requires human review

`false`. Tool ở S2, không phải S3. Không có mạng, không tạo media, không tích hợp dịch vụ ngoài. Per SAFETY_BOUNDARIES.md, human review là yêu cầu của S3+.

Tuy nhiên, một maintainer review code trong PR (qua CODEOWNERS) vẫn nên xảy ra — đây là code chạy subprocess; mặc dù subprocess là chức năng đã khai báo, nó vẫn xứng đáng có thêm cặp mắt thứ hai.
