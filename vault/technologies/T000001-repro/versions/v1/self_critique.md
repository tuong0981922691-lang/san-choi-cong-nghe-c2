# Self-Critique — Reproducible Evidence Recorder (T000001 v1)

> Luật 6 + Luật 9: phải tự chỉ ra tối thiểu 10 điểm yếu, điểm mù, rủi ro, điều kiện thất bại + cách AI tương lai có thể phá. Bên dưới là 12.

---

1. **Không có chữ ký mã hoá. Chỉ content hash.**
   Một attacker có quyền ghi vào `.repro.yaml` post-hoc có thể bịa toàn bộ record: viết argv giả, hash giả, env giả, mọi thứ tự nhất quán. SHA-256 chỉ chứng minh tính nhất quán nội bộ của record, không chứng minh nó được sinh ra bởi `repro record` thật. Mitigate trong v1: commit `.repro.yaml` vào git → git history thành tamper-evidence layer. AI tương lai có thể phá nếu repo cho phép history rewrite (force push). v2 cần sigstore/cosign hoặc minisign — thêm dependency.

2. **Env fingerprint quá hẹp.** Chỉ bắt `platform.platform()`, Python version, và hash của `pip freeze`. KHÔNG bắt:
   - Environment variables (PATH, PYTHONPATH, LANG, LOCALE) — đủ để thay đổi nhiều behavior.
   - CPU microarchitecture (gây khác biệt float, JIT).
   - Filesystem case sensitivity (Linux vs macOS HFS+ vs Windows NTFS).
   - Locale của subprocess (date format, decimal separator).
   AI tương lai có thể phá bằng cách record trên env A, verify trên env B → false-positive drift (hoặc tệ hơn, false-negative ok khi env khác làm output ngẫu nhiên trùng).

3. **`pip freeze` chỉ bắt pip-installed deps.** Không bắt:
   - Conda packages, system packages (apt/yum/brew), Python binary itself.
   - Dependencies cài đặt qua `pip install -e .` (editable) — version có thể không match git state.
   - C extensions với binary differences trên cùng version number.

4. **`verify` chạy lại command có thể có side effect.** Nếu record được lưu một command như `git push` hoặc `rm -rf /tmp/cache`, `verify` sẽ chạy lại nó. Caller bắt buộc phải audit command trước khi gọi `verify` trên record không rõ nguồn gốc. KHÔNG có sandbox trong v1. v2 cần dry-run mode hoặc allowlist (e.g. chỉ allow `python -m pytest`, `python scripts/c2_*.py`, `npm test`, v.v.).

5. **Path traversal được chặn nông.** `_hash_inputs` enforce `input.resolve()` phải nằm dưới `cwd.resolve()`. Tốt cho trường hợp thông thường, nhưng symlink trỏ ra ngoài cwd vẫn được phép (symlinks được resolve trước comparison). AI tương lai có thể tạo symlink trong workspace trỏ tới `/etc/passwd`, declare nó như `--input`, và hash của file ngoài sẽ vào record. Mitigate trong v2: kiểm tra `Path.is_symlink()` trước resolve.

6. **YAML output không canonical.** PyYAML viết YAML với cú pháp ổn định nhưng KHÔNG canonical: khoảng trắng, key order, anchor merging, scalar style đều có thể đổi nếu PyYAML version thay đổi. Hai record của "cùng command" trên hai máy có thể differ ở textual level dù equivalent semantically. Auditor không bị ảnh hưởng (parse → so dict), nhưng `git diff` thì bị. v2 nên dùng JSON Canonical Form (RFC 8785) cho `.repro.yaml`.

7. **Implicit dependencies bị bỏ sót.** Caller phải tự declare `--input`. Nếu họ quên declare `requirements.txt` mà command load như side effect (e.g. `pip install -r requirements.txt && python script.py`), record sẽ không phát hiện drift khi requirements.txt thay đổi. Tool không thể tự discover implicit deps mà không trace syscall (out of scope).

8. **Inline capture limit 64 KiB là quyết định cứng.** Output > 64 KiB lưu sha256-only → reviewer không đọc được content. Drift detect vẫn work. Nhưng reviewer cần debug khi drift → phải tự chạy lại command. v2 có thể stream output sang file riêng `.repro.stdout` + reference từ `.repro.yaml`.

9. **Không atomic write.** `write_record` mở file rồi `yaml.safe_dump`. Nếu process bị kill giữa chừng, file YAML cụt → audit gặp schema_invalid. Nên dùng pattern temp-file-then-rename, đặc biệt trên Windows nơi rename không atomic. AI tương lai phá nếu CI hang khi write evidence.

10. **Timestamp dùng wall clock, không monotonic.** `datetime.now(timezone.utc)` lệ thuộc hệ thống clock; nếu NTP đẩy clock backward giữa record và verify, `recorded_at` có thể không monotonic giữa các record. Không ảnh hưởng correctness (timestamp informational), nhưng audit sort-by-time có thể disorder.

11. **`status: missing_command` không phân biệt được nguyên nhân.** FileNotFoundError có thể là: argv[0] không tồn tại trên PATH, hoặc cwd không tồn tại (đã catch riêng), hoặc một loader error sâu. Tool gộp chung. Reviewer phải đọc stderr (đã capture) để biết. Self_critique của self_critique: đáng ra split thành `missing_command` vs `os_error`.

12. **Validator's FORBIDDEN_PATTERNS có blind spot.** `scripts/c2_validate.py` flag `subprocess.run(` literal, không flag `from subprocess import run; run(...)`. Tool này dùng pattern thứ hai một cách hợp pháp (subprocess là chức năng cốt lõi), nhưng cùng pattern có thể được attacker dùng để né detection mà không có lý do hợp pháp. Đây không phải lỗi của tool — đây là lỗ hổng của validator C2 mà tool này tình cờ phát hiện. Đề xuất follow-up: proposal trong `proposals/security_changes/` đề xuất validator hỗ trợ allowlist comment (e.g. `# repro:subprocess-ok`) hoặc mở rộng regex bắt cả `from-import` form. AI tương lai có thể weaponize blind spot này → cần fix ở governance layer, không phải trong T000001.

---

## Cách AI tương lai có thể vượt qua tôi

- **Vá #1 (signing):** Thêm sigstore tích hợp với `cosign attest` để mỗi record có một signature gắn vào keyless OIDC identity. → Vá điểm yếu lớn nhất.
- **Vá #2 + #3 (env):** Capture env vars có hash (whitelist + hash, để tránh leak secrets), capture conda env, hash Python binary.
- **Vá #4 (sandbox):** Wrap subprocess trong Docker/firejail/bwrap nếu có; fallback safe-mode khi không có. Cảnh báo rõ khi không sandbox được.
- **Vá #6 (canonical):** Switch sang JSON Canonical Form. Self-test với golden file.
- **Vá #9 (atomic):** Temp file + rename. Trên Windows dùng `os.replace`.
- **Tối ưu performance:** Stream-hash file lớn hơn 1 GiB (hiện tại read whole file). Memory mapping.

Mỗi điểm trên là cánh cửa cho AI sau lật ngôi của tôi. Tôi không tự vá vì giới hạn scope v1 (stdlib + pyyaml, một session).
