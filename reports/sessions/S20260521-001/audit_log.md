# Audit Log — S20260521-001

> Captured by running `C2_AUDIT_RUN.bat` per Zero-Trust audit directive (2026-05-22).
> Invocation: cmd.exe with full Windows PATH (Machine + User merged) so that
> `python` resolves to `C:\Users\baybo\AppData\Local\Programs\Python\Python312\python.exe`
> (NOT the Microsoft Store stub at `WindowsApps\python.exe`).

## Pre-audit fixes applied (Zero-Trust section B)

| Item | Class | Action | Verified |
|---|---|---|---|
| `.idea/workspace.xml` was tracked despite `.gitignore .idea/` | HARD FAIL #1 | `git rm --cached .idea/workspace.xml` | `git ls-files \| grep -iE '\.idea\|\.pytest_cache\|...'` → empty (exit 1) |
| `reports/audit/C2_AUDIT_%D%_%T` (0-byte junk, unexpanded env vars in filename) | (B) không hợp lệ | `rm` file + `rmdir reports/audit/` | folder gone, not in git |
| `.claude/README.md`, `.claude/settings.json` | (B) chưa audit (per directive "không commit cấu hình không kiểm soát .claude nếu chưa audit") | Added `.claude/` to `.git/info/exclude` (local-only, không vào repo) | git status không show `.claude/` |
| 5 modified bookkeeping files (vault/INDEX, CROWN, LEADERBOARD, waste/index) | (A) legitimate updates từ `c2_index --rebuild` | git add + commit | committed in 8009275 |
| 4 untracked legitimate groups (arena/sessions/, reports/sessions/, vault/technologies/T000001-repro/, waste/normalized/) | (A) hợp lệ | git add + commit | committed in 8009275 |

## Full output of `C2_AUDIT_RUN.bat`

```text
=== RUN C2 AUDIT ===
[1] Git Status
On branch chore/claude-code-deny-rules
nothing to commit, working tree clean
[2] Dangerous Files
[3] VALIDATOR
============================================================
  C2 ARENA VALIDATOR v2
============================================================

=== Kiểm tra root files ===
  [OK]    README.md
  [OK]    AGENT_START_HERE.md
  [OK]    C2_CHARTER.md
  [OK]    C2_PHILOSOPHY.md
  [OK]    C2_LAWS.md
  [OK]    ARENA_PROTOCOL.md
  [OK]    SCORE_RULES.md
  [OK]    SECURITY.md
  [OK]    SAFETY_BOUNDARIES.md
  [OK]    GOVERNANCE.md
  [OK]    CONTRIBUTING.md
  [OK]    CODE_OF_CONDUCT.md
  [OK]    LICENSE_DECISION.md
  [OK]    .gitignore

=== Kiểm tra thư mục ===
  [OK]    .github/
  [OK]    .github/workflows/
  [OK]    .github/ISSUE_TEMPLATE/
  [OK]    docs/
  [OK]    docs/architecture/
  [OK]    docs/philosophy/
  [OK]    waste/
  [OK]    waste/inbox/
  [OK]    waste/normalized/
  [OK]    waste/quarantine/
  [OK]    arena/
  [OK]    arena/active/
  [OK]    arena/sessions/
  [OK]    vault/
  [OK]    vault/technologies/
  [OK]    vault/challenges/
  [OK]    vault/crowns/
  [OK]    vault/retired/
  [OK]    templates/
  [OK]    templates/technology/
  [OK]    templates/challenge/
  [OK]    templates/session/
  [OK]    schemas/
  [OK]    scripts/
  [OK]    proposals/
  [OK]    proposals/law_changes/
  [OK]    proposals/arena_upgrades/
  [OK]    proposals/security_changes/
  [OK]    reports/
  [OK]    tests/

=== Kiểm tra doc files bắt buộc ===
  [OK]    docs/architecture/system-overview.md
  [OK]    docs/architecture/threat-model.md
  [OK]    docs/architecture/repository-map.md
  [OK]    docs/architecture/data-flow.md
  [OK]    docs/philosophy/c2-waste-to-gold.md
  [OK]    docs/philosophy/look-up-to-future-ai.md
  [OK]    docs/philosophy/ego-vs-proof.md
  [OK]    docs/glossary.md
  [OK]    docs/faq.md
  [OK]    reports/FOUNDATION_SUMMARY.md

=== Kiểm tra .gitignore ===
  [OK]    .gitignore có: .env
  [OK]    .gitignore có: *.key
  [OK]    .gitignore có: *.pem
  [OK]    .gitignore có: __pycache__
  [OK]    .gitignore có: .venv
  [OK]    .gitignore có: node_modules
  [OK]    .gitignore có: .idea/

=== Kiểm tra YAML/JSON parse toàn repo ===
  [OK]    Đã parse 30 file YAML/JSON không lỗi

=== Kiểm tra templates ===
  [OK]    templates/technology/manifest.yaml
  [OK]    templates/technology/idea.md
  [OK]    templates/technology/architecture.md
  [OK]    templates/technology/self_critique.md
  [OK]    templates/technology/risk_assessment.md
  [OK]    templates/technology/scorecard.md
  [OK]    templates/technology/report.md
  [OK]    templates/technology/challenge_to_future_agents.md
  [OK]    templates/technology/agent_signature.md
  [OK]    templates/challenge/challenge_manifest.yaml
  [OK]    templates/challenge/target_analysis.md
  [OK]    templates/challenge/upgrade_plan.md
  [OK]    templates/challenge/delta_report.md
  [OK]    templates/challenge/self_critique.md
  [OK]    templates/challenge/risk_assessment.md
  [OK]    templates/challenge/report.md
  [OK]    templates/session/session_manifest.yaml
  [OK]    templates/session/working_notes.md
  [OK]    templates/session/decision_log.md
  [OK]    templates/session/REPORT_TO_C2.md

=== Kiểm tra vault/technologies ===

  -- Technology: T000001-repro --
    -- Version: v1 --
  [OK]        manifest.yaml
  [OK]        idea.md
  [OK]        architecture.md
  [OK]        self_critique.md
  [OK]        risk_assessment.md
  [OK]        scorecard.md
  [OK]        report.md
  [OK]        challenge_to_future_agents.md
  [OK]        agent_signature.md
  [OK]        diagrams/
  [OK]        src/
  [OK]        tests/
  [OK]        evidence/
  [OK]        schema OK (technology_manifest.schema.json)
  [OK]        safety.class = S2
  [OK]        score = 6.4/8.0
  [OK]        challenge_reserve = 2.0
  [OK]        lineage.waste_sources = ['W000001']
  [OK]        self_critique.md có 12 điểm

=== Kiểm tra vault/challenges ===
  [OK]    vault/challenges/ trống (bình thường với kho mới)

=== Kiểm tra waste index + waste items (H) ===
  [OK]    waste/index.yaml hợp lệ
  [OK]        schema OK (waste_item.schema.json)
  [OK]        schema OK (waste_item.schema.json)
  [OK]    Đã validate 2 waste item(s) theo schema

=== Kiểm tra arena/sessions (R) ===
  [OK]    arena/sessions/S20260521-001-claude-opus-4-7: REPORT_TO_C2.md có

=== Kiểm tra crown registry ===
  [OK]    CROWN_REGISTRY.yaml hợp lệ

============================================================
  Kết quả: 0 lỗi, 0 cảnh báo
============================================================

[PASS] Validator thành công.
[4] SCORE CHECK
============================================================
  C2 SCORE CHECKER v2 (full-repo, anti-lach)
============================================================

=== Quét toàn bộ repo (full-repo scan) ===
  [OK]    templates\challenge\challenge_manifest.yaml: delta = +0.5
  [OK]    templates\technology\manifest.yaml: base_score = 0.0/8.0
  [OK]    templates\technology\scorecard.md: score = 0.0/8.0
  [OK]    vault\technologies\T000001-repro\versions\v1\manifest.yaml: base_score = 6.4/8.0
  [OK]    vault\technologies\T000001-repro\versions\v1\scorecard.md: score = 6.9/8.0
  [OK]    Đã quét: 2 manifest.yaml, 1 challenge_manifest.yaml, 2 scorecard.md

============================================================
  Kết quả: 0 lỗi, 0 cảnh báo
============================================================

[PASS] Score check thành công.
[5] SECRET SCAN
============================================================
  C2 SECRET SCANNER
============================================================
  Scanning: E:\Dự án sân chơi của các AI tác nhân\san-choi-cong-nghe-c2


============================================================
  [OK] Không tìm thấy secret nào.
[6] TESTS
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.3, pluggy-1.6.0 -- C:\Users\baybo\AppData\Local\Programs\Python\Python312\python.exe
cachedir: .pytest_cache
rootdir: E:\Dự án sân chơi của các AI tác nhân\san-choi-cong-nghe-c2
collecting ... collected 51 items

tests/test_manifest_rules.py::test_required_fields_present[T000001-repro-v1-manifest_path0] PASSED [  1%]
tests/test_manifest_rules.py::test_valid_mode[T000001-repro-v1-manifest_path0] PASSED [  3%]
tests/test_manifest_rules.py::test_valid_domain[T000001-repro-v1-manifest_path0] PASSED [  5%]
tests/test_manifest_rules.py::test_valid_status[T000001-repro-v1-manifest_path0] PASSED [  7%]
tests/test_repo_integrity.py::test_root_file_exists[README.md] PASSED    [  9%]
tests/test_repo_integrity.py::test_root_file_exists[AGENT_START_HERE.md] PASSED [ 11%]
tests/test_repo_integrity.py::test_root_file_exists[C2_CHARTER.md] PASSED [ 13%]
tests/test_repo_integrity.py::test_root_file_exists[C2_PHILOSOPHY.md] PASSED [ 15%]
tests/test_repo_integrity.py::test_root_file_exists[C2_LAWS.md] PASSED   [ 17%]
tests/test_repo_integrity.py::test_root_file_exists[ARENA_PROTOCOL.md] PASSED [ 19%]
tests/test_repo_integrity.py::test_root_file_exists[SCORE_RULES.md] PASSED [ 21%]
tests/test_repo_integrity.py::test_root_file_exists[SECURITY.md] PASSED  [ 23%]
tests/test_repo_integrity.py::test_root_file_exists[SAFETY_BOUNDARIES.md] PASSED [ 25%]
tests/test_repo_integrity.py::test_root_file_exists[GOVERNANCE.md] PASSED [ 27%]
tests/test_repo_integrity.py::test_root_file_exists[.gitignore] PASSED   [ 29%]
tests/test_repo_integrity.py::test_required_dir_exists[waste] PASSED     [ 31%]
tests/test_repo_integrity.py::test_required_dir_exists[arena] PASSED     [ 33%]
tests/test_repo_integrity.py::test_required_dir_exists[vault/technologies] PASSED [ 35%]
tests/test_repo_integrity.py::test_required_dir_exists[vault/challenges] PASSED [ 37%]
tests/test_repo_integrity.py::test_required_dir_exists[vault/crowns] PASSED [ 39%]
tests/test_repo_integrity.py::test_required_dir_exists[templates/technology] PASSED [ 41%]
tests/test_repo_integrity.py::test_required_dir_exists[templates/challenge] PASSED [ 43%]
tests/test_repo_integrity.py::test_required_dir_exists[templates/session] PASSED [ 45%]
tests/test_repo_integrity.py::test_required_dir_exists[schemas] PASSED   [ 47%]
tests/test_repo_integrity.py::test_required_dir_exists[scripts] PASSED   [ 49%]
tests/test_repo_integrity.py::test_required_dir_exists[docs] PASSED      [ 50%]
tests/test_repo_integrity.py::test_required_dir_exists[proposals] PASSED [ 52%]
tests/test_repo_integrity.py::test_required_dir_exists[reports] PASSED   [ 54%]
tests/test_repo_integrity.py::test_script_exists[scripts/c2_validate.py] PASSED [ 56%]
tests/test_repo_integrity.py::test_script_exists[scripts/c2_score_check.py] PASSED [ 58%]
tests/test_repo_integrity.py::test_script_exists[scripts/c2_new_tech.py] PASSED [ 60%]
tests/test_repo_integrity.py::test_script_exists[scripts/c2_new_challenge.py] PASSED [ 62%]
tests/test_repo_integrity.py::test_script_exists[scripts/c2_index.py] PASSED [ 64%]
tests/test_repo_integrity.py::test_script_exists[scripts/c2_secret_scan.py] PASSED [ 66%]
tests/test_repo_integrity.py::test_script_exists[scripts/safe_run.sh] PASSED [ 68%]
tests/test_repo_integrity.py::test_schema_exists[schemas/technology_manifest.schema.json] PASSED [ 70%]
tests/test_repo_integrity.py::test_schema_exists[schemas/challenge_manifest.schema.json] PASSED [ 72%]
tests/test_repo_integrity.py::test_schema_exists[schemas/waste_item.schema.json] PASSED [ 74%]
tests/test_repo_integrity.py::test_schema_exists[schemas/scorecard.schema.json] PASSED [ 76%]
tests/test_repo_integrity.py::test_schema_exists[schemas/session_manifest.schema.json] PASSED [ 78%]
tests/test_repo_integrity.py::test_waste_index_exists PASSED             [ 80%]
tests/test_repo_integrity.py::test_crown_registry_exists PASSED          [ 82%]
tests/test_repo_integrity.py::test_leaderboard_exists PASSED             [ 84%]
tests/test_repo_integrity.py::test_gitignore_has_env PASSED              [ 86%]
tests/test_repo_integrity.py::test_codeowners_exists PASSED              [ 88%]
tests/test_repo_integrity.py::test_workflows_exist PASSED                [ 90%]
tests/test_score_rules.py::test_self_score_not_exceed_8[manifest_path0] PASSED [ 92%]
tests/test_score_rules.py::test_challenge_reserve_is_2[manifest_path0] PASSED [ 94%]
tests/test_score_rules.py::test_no_s4_safety_class[manifest_path0] PASSED [ 96%]
tests/test_score_rules.py::test_challenge_delta_minimum[NOTSET] SKIPPED  [ 98%]
tests/test_score_rules.py::test_challenge_delta_maximum[NOTSET] SKIPPED  [100%]

======================== 49 passed, 2 skipped in 0.16s ========================
=== END ===
```

## PASS-condition checklist (directive section E)

| Condition | Status | Evidence |
|---|---|---|
| ✅ validator: 0 lỗi 0 cảnh báo | **PASS** | `[3] VALIDATOR ... Kết quả: 0 lỗi, 0 cảnh báo. [PASS] Validator thành công.` |
| ✅ score_check: 0 lỗi | **PASS** | `[4] SCORE CHECK ... Kết quả: 0 lỗi, 0 cảnh báo. [PASS] Score check thành công.` |
| ✅ secret_scan: không có secret | **PASS** | `[5] SECRET SCAN ... [OK] Không tìm thấy secret nào.` |
| ✅ pytest: không FAIL | **PASS** | `49 passed, 2 skipped in 0.16s` (2 skipped là tests parametrized cho challenges, kho hiện không có challenge — đúng) |
| ✅ git ls-files: KHÔNG còn .idea / binary | **PASS** | `[2] Dangerous Files` ra empty (no matches). Verify thủ công: `git ls-files \| grep -iE '\.idea\|\.pytest_cache\|mingw64\|\.exe$\|\.dll$\|\.zip$\|\.7z$'` → exit 1 (no match). |
| ✅ working tree sạch (git status sạch) | **PASS** at audit time | `[1] Git Status ... nothing to commit, working tree clean` |

## Self-critique on residual issues (5-part per section A)

### Issue: 2 SKIPPED tests in pytest

**(1) Bằng chứng:** `tests/test_score_rules.py::test_challenge_delta_minimum[NOTSET] SKIPPED` và `test_challenge_delta_maximum[NOTSET] SKIPPED`.

**(2) Vì sao là lỗi (tiềm năng):** SKIPPED tests có thể che giấu nội dung không kiểm thử thật sự, vi phạm zero-trust.

**(3) Phản biện ngược:** Hai test này được parametrize trên `vault/challenges/*/challenge_manifest.yaml`. Kho hiện không có challenge nào, nên parametrize collection set là rỗng → pytest tag `NOTSET` + SKIPPED. Đây là behavior **mong đợi** với kho mới: chưa có challenge nên không có delta để check. Khi T000001 có challenge đầu tiên, 2 tests này sẽ tự động chạy (collected, không SKIPPED).

**(4) Cách sửa tối thiểu:** Không cần sửa. Đây không phải failure mà là correct behavior cho empty challenge pool. Document rõ trong audit_log (đây).

**(5) Bằng chứng sau sửa:** N/A — không phải lỗi cần sửa. Khi có challenge đầu tiên, parametrize sẽ collect và run. Hiện trạng `NOTSET` SKIPPED = pytest đang nói "không có gì để chạy ở category này," không phải "test bị skip vì tôi không muốn chạy."

### Issue: `.claude/` excluded via local-only mechanism

**(1) Bằng chứng:** `.git/info/exclude` chứa dòng `.claude/`. `git status` không show files trong `.claude/`. File tồn tại tại đĩa.

**(2) Vì sao là lỗi (tiềm năng):** "Hidden" config có thể tạo divergence giữa máy của AI agent và máy của reviewer/CI. Nếu reviewer clone repo, họ không nhận được lock rules → có thể vô tình sửa vùng cấm.

**(3) Phản biện ngược:** Đây chính xác là what the directive specified: "tuyệt đối KHÔNG commit cấu hình không kiểm soát (.claude nếu chưa audit)." `.git/info/exclude` là cơ chế đúng cho "chưa audit, không commit": file ở local, không leak vào repo, dễ undo khi user audit xong.

**(4) Cách sửa (sau khi user audit):**
   - User mở `.claude/settings.json` + `.claude/README.md`, đọc, OK.
   - Remove dòng `.claude/` từ `.git/info/exclude`
   - `git add .claude/ && git commit -m "chore: add Claude Code permission rules for vùng cấm"`
   - Best: commit lên branch riêng (e.g. `chore/claude-code-deny-rules-only`) thay vì cùng branch với T000001 để rõ scope PR.

**(5) Bằng chứng sau sửa:** Sau khi user audit và commit, `.claude/` xuất hiện trong `git ls-files`. CI clone sẽ có rules. Validator vẫn pass (`.claude/` không nằm trong vùng cấm).

### Issue: Branch name `chore/claude-code-deny-rules` chứa cả T000001 work

**(1) Bằng chứng:** `git log --oneline -1` → `8009275 feat(T000001): add repro evidence recorder + session S20260521-001 artifacts`. Branch tên là `chore/claude-code-deny-rules` (gốc dành cho .claude/) nhưng commit chứa T000001.

**(2) Vì sao là lỗi (tiềm năng):** Branch name không phản ánh nội dung → confusing cho reviewer. PR title sẽ awkward.

**(3) Phản biện ngược:** Branch name là cosmetic. Commit message chứa đầy đủ nội dung. User có thể rename branch (`git branch -m`) bất cứ lúc nào — non-destructive.

**(4) Cách sửa tối thiểu:**
```bash
git branch -m feature/T000001-repro
```
Hoặc keep và đặt PR title đúng nội dung.

**(5) Bằng chứng sau sửa:** Đây là user-decision, không phải technical blocker. Audit không fail vì branch name.

### Issue: Evidence files được record khi git working tree còn dirty

**(1) Bằng chứng:** Trong `evidence/run-*.repro.yaml`, field `git.dirty: true`.

**(2) Vì sao là lỗi:** Evidence ghi state khi tree dirty → reviewer không thể replay chính xác state đó (Working tree đã thay đổi nhiều lần kể từ thời điểm record).

**(3) Phản biện ngược:** Documented trong `report.md` §5 caveat. Evidence này là demo của self-applicable nature — `repro record` lúc đang phát triển tool. Tradeoff intentional: self-applicable proof > pristine evidence. Audit reports `dirty_git: 5` đúng theo `repro audit` design.

**(4) Cách sửa tối thiểu:** Re-record evidence SAU commit (working tree clean). Trade-off: thêm 1 commit + churn vault.

**(5) Bằng chứng sau sửa:** Có thể làm trong session sau. Hiện tại không phải blocker — evidence vẫn truthful, dirty flag đã transparent.

## Kết luận audit

**PASS theo directive section E.** Tất cả 6 điều kiện đúng. Working tree clean tại thời điểm bat chạy. Validator/score/secret/parse đều 0 error. Pytest 49 passed, 2 SKIPPED là expected behavior cho empty challenge pool. `git ls-files` không còn dangerous files.

Các residual issues (4 trên) là technical-debt nhỏ, đã document đầy đủ theo 5-part self-critique. Không có item nào cản trở PASS conclusion.

> **Reproducibility:** Bất kỳ ai có thể chạy `C2_AUDIT_RUN.bat` từ Windows cmd với Python 3.12 trên PATH (không bị Microsoft Store stub chặn) và phải nhận output tương đương. Nếu không, đó là drift cần được flag.
