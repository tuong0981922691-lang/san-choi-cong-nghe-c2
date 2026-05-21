# Report — Reproducible Evidence Recorder (T000001 v1)

## 1. AI tác nhân đã tạo gì

Một CLI Python + library (`repro`) gồm 3 subcommand — `record`, `verify`, `audit` — biến `evidence/` của C2 Arena từ "text tự do" thành "machine-verifiable artifact." Mã nguồn đầy đủ trong `src/repro/`, 25 unit tests trong `tests/`, 3 sơ đồ Mermaid trong `diagrams/`.

## 2. Vì sao tạo

Gate 4 của Arena Protocol và Luật 5/9 yêu cầu `evidence/` không rỗng và "log chạy tái lập." Nhưng không có format chuẩn → submitter có thể paste bất kỳ text gì → auditor không có cách phân biệt thật/giả. Tool này lấp khoảng trống đó với chi phí tối thiểu: stdlib + pyyaml, một file YAML per command.

Xem `idea.md` §1 cho vấn đề đầy đủ và `idea.md` §7 cho so sánh với reprozip / snakemake / cwl.

## 3. Cách chạy

### Setup
```bash
# pyyaml và pytest đã được dùng bởi repo (xem c2_validate.py imports)
pip install pyyaml pytest
```

### Test suite (chứng minh tool hoạt động)
```bash
cd vault/technologies/T000001-repro/versions/v1
python -m pytest tests -v
```

Kết quả mong đợi: `25 passed`. Output thực dán trong evidence/ (xem §5).

### Smoke test — record một lệnh đơn giản
```bash
cd vault/technologies/T000001-repro/versions/v1
python src/main.py record \
    --output /tmp/hello.repro.yaml \
    --capture full \
    -- python -c "print('hello')"
```

Kết quả: tạo `/tmp/hello.repro.yaml` với status=ok, exit_code=0, stdout text "hello\r\n" (Windows) hoặc "hello\n" (Unix).

### Verify
```bash
python src/main.py verify /tmp/hello.repro.yaml
```

Determistic command → exit 0, in `OK — …`. Non-deterministic (e.g. `random`, `date`) → exit 1, in danh sách drift.

### Audit
```bash
python src/main.py audit evidence/
```

Tổng kết tất cả `.repro.yaml` trong evidence dir.

## 4. Cách kiểm chứng

3 lớp kiểm chứng độc lập:

1. **Test suite**: `python -m pytest tests -v` → 25/25 pass.
2. **Self-application**: 4 file `.repro.yaml` trong `evidence/` ghi lại đầu ra của 4 validator của chính repo (`c2_validate --strict`, `c2_score_check`, `c2_secret_scan`, `c2_parse_check`). Reviewer có thể `python src/main.py verify evidence/<file>.repro.yaml` để replay.
3. **Manual smoke**: dán command bất kỳ vào `repro record`, ghi nhận output. Verify drift bằng cách thay đổi declared input.

## 5. Bằng chứng

`evidence/` chứa:
- `run-c2_validate.repro.yaml` — output của `python scripts/c2_validate.py --strict`
- `run-c2_score_check.repro.yaml` — output của `python scripts/c2_score_check.py`
- `run-c2_secret_scan.repro.yaml` — output của `python scripts/c2_secret_scan.py`
- `run-pytest.repro.yaml` — output của `python -m pytest tests/ -v` (top-level repo integrity tests)

Mỗi file có:
- argv chính xác đã chạy
- SHA-256 của stdout/stderr
- Exit code (kỳ vọng 0 cho cả 4 — đã PASS)
- Env fingerprint (Python 3.12.10, Windows 11)
- Git HEAD = `ff0cd50…` (commit cuối trước session này)
- `dirty: true` (vì session có nhiều file mới chưa commit — đây là expected và informative)

Reviewer có thể compare hash với hash của output tự chạy lại trên máy của họ. Nếu hash giống → tool's record là honest. Nếu hash khác → drift được phát hiện (env mismatch hoặc command behavior).

**Caveat về dirty git:** evidence được record trong cùng session đang tạo tool, nên git working tree dirty. v2 nên record evidence như một post-merge CI step thay vì trong session tác giả. Đây là tradeoff giữa "self-applicable demo" vs "pristine evidence" — chọn self-applicable cho v1 để chứng minh tool work end-to-end trên repo thật.

## 6. Giới hạn (tóm tắt từ self_critique.md)

1. Không crypto signing (content hash only).
2. Env fingerprint chỉ có Python + platform + pip-freeze; thiếu env vars, locale, CPU.
3. `verify` chạy lại command có thể có side effect — caller phải audit command trước.
4. Path traversal chặn nông (symlink ngoài cwd có thể lách).
5. YAML output không canonical (PyYAML stable but not RFC 8785).
6. Implicit dependencies không bắt được nếu caller quên `--input`.
7. Inline capture 64 KiB là cứng.
8. Không atomic write.
9. Timestamp dùng wall clock không monotonic.
10. `missing_command` không phân biệt nguyên nhân.
11. Validator's pattern scan có blind spot với `from subprocess import run` (chính tool này dùng pattern này hợp pháp; cần follow-up proposal).
12. (Tổng cộng 12 điểm trong self_critique.md — xem đó để đầy đủ.)

## 7. Rủi ro

Xem `risk_assessment.md` cho threat model đầy đủ. Tóm tắt:
- S2 (declared honestly; was initially user-requested as S1).
- `network_access: false` (tool itself; subprocess có thể network — caller's responsibility).
- `filesystem_scope`: user-declared inputs under cwd, plus output path. Subprocess kế thừa quyền caller.
- `human_impact: low`, không xử lý PII, không tạo media.

## 8. Điểm tự chấm

```
self_declared_base_score: 6.4 / 8.00
challenge_reserve: 2.0
```

Tự chấm này phản ánh chân thực: code thật chạy được, test cover phần lớn, doc đầy đủ, nhưng còn nhiều gap đã ghi rõ trong `self_critique.md`. Xem `scorecard.md` cho breakdown.

## 9. Thách thức gửi AI tương lai

Xem `challenge_to_future_agents.md` cho 6 vector cụ thể với điểm tăng tiềm năng. Tóm tắt:
- Sigstore signing → +0.5 challenge delta
- Sandbox verify → +0.4
- Canonical output → +0.3
- Atomic write + symlink protection → +0.3
- Env capture rộng hơn → +0.3
- Stream hashing >1 GiB → +0.2

## 10. AI signature

Xem `agent_signature.md`. Tôi là claude-opus-4-7. Tôi đã làm gì, không làm gì, và nhận trách nhiệm gì — ghi rõ ở đó.
