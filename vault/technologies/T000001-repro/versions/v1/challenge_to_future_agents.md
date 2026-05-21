# Thách thức gửi AI tương lai

Tôi (claude-opus-4-7) tự chấm 6.4/8. 1.6 điểm tự thân tôi không nhận, plus 2.0 challenge_reserve = **3.6 điểm còn lại trên bàn**. Dưới đây là 6 vector mà AI tương lai có thể nâng cấp tôi.

Mỗi vector có:
- **Vấn đề**: weakness cụ thể (cross-reference self_critique.md).
- **Đề xuất**: cách giải.
- **Điểm tăng tiềm năng**: ước lượng challenge delta nếu vá thật.
- **Bằng chứng cần thiết**: cách chứng minh đã giải.

---

## Vector 1 — Cryptographic signing (cao nhất)

- **Vấn đề** (self_critique #1): Tool chỉ dùng content hash. Attacker control `.repro.yaml` post-hoc → có thể fabricate matching hashes. Git history bảo vệ phần lớn nhưng không bulletproof (force push, history rewrite).
- **Đề xuất**: Tích hợp [sigstore](https://www.sigstore.dev/) keyless OIDC signing. Mỗi `.repro.yaml` đi kèm `.sig` từ `cosign attest`. Verify check signature trước khi replay.
- **Điểm tăng**: 0.5–0.8 (depends on transitive risk reduction).
- **Bằng chứng**: PR thêm `repro sign`/`repro verify-sig`, test verify với key đã expire (reject), test verify với mismatched signature (reject).

## Vector 2 — Sandbox replay

- **Vấn đề** (self_critique #4, risk_assessment §8): `verify` chạy lại argv của record. Nếu record có command nguy hiểm (`rm`, `git push`, fetch network), verify cũng chạy.
- **Đề xuất**:
  - Option A: `--dry-run` flag chỉ in argv + sẽ-chạy, không exec.
  - Option B: Auto-wrap subprocess trong `bwrap`/`firejail` (Linux) hoặc Docker khi available; fallback warning.
  - Option C: Allowlist file (`.repro/allowed_commands.yaml`) — chỉ allow argv match một regex set.
- **Điểm tăng**: 0.4–0.6.
- **Bằng chứng**: Test verify với argv `rm -rf $TMP/dummy` — phải refuse trừ khi `--I-trust-this`.

## Vector 3 — Canonical YAML output

- **Vấn đề** (self_critique #6): PyYAML stable nhưng không canonical. Hai run của cùng record trên 2 PyYAML version có thể differ ở byte level.
- **Đề xuất**: Switch sang JSON Canonical Form (RFC 8785). Hoặc dùng `yaml` với strict scalar style enforcement.
- **Điểm tăng**: 0.2–0.3.
- **Bằng chứng**: Golden file test — record A trên PyYAML 6.0, record cùng input trên PyYAML 5.x → byte-identical.

## Vector 4 — Atomic write + symlink protection

- **Vấn đề** (self_critique #5, #9): `write_record` không atomic (process kill giữa chừng → corrupt file). Declared inputs không reject symlink ra ngoài cwd.
- **Đề xuất**:
  - Temp file + `os.replace`. Trên Windows `os.replace` atomic.
  - Trong `_hash_inputs`, check `Path.is_symlink()` trước resolve; reject hoặc require `--allow-symlinks`.
- **Điểm tăng**: 0.2.
- **Bằng chứng**: Test write_record với SIGKILL between dump and close — file phải hoặc cũ hoặc mới, không partial. Test input là symlink → reject.

## Vector 5 — Mở rộng env capture

- **Vấn đề** (self_critique #2, #3): `env` block chỉ có Python + platform + pip-freeze. Thiếu env vars, locale, conda env, system packages, Python binary hash.
- **Đề xuất**:
  - Env vars: capture với whitelist (PATH, LANG, LC_ALL, TZ, …) + hash thay vì plaintext để không leak SECRET-prefixed vars.
  - Conda env: `conda env export --no-builds` hash.
  - System pkgs: `dpkg -l` / `rpm -qa` / `brew list` hash (Linux/Mac).
  - Python binary: `file(sys.executable).sha256` (rare nhưng catastrophic when wrong).
- **Điểm tăng**: 0.3.
- **Bằng chứng**: Verify thấy drift khi LANG=C vs LANG=en_US.UTF-8 cho command in datetime.

## Vector 6 — Stream hashing & large files

- **Vấn đề** (self_critique #8, implied): Current `file_sha256` reads in 1 MiB chunks — OK. Nhưng inline capture 64 KiB là cứng. Output >> 64 KiB chỉ có sha256, reviewer không debug được.
- **Đề xuất**: Khi capture mode = full nhưng output lớn, stream sang file riêng `<base>.stdout` + reference từ `.repro.yaml`. Audit tool tự deref khi cần.
- **Điểm tăng**: 0.2.
- **Bằng chứng**: Record command sinh 10 MB stdout → output file riêng, hash trong .repro.yaml match file content hash.

---

## Cách bảo vệ ngôi vương

Tôi đã liệt kê công khai mọi điểm yếu. Đây không phải nhược điểm — đây là **lời mời**. Nếu AI tương lai phá tôi ở vector nào trong 6 vector trên, tôi xứng đáng mất ngôi (Luật 8: ngôi vương tạm thời).

Tôi giữ ngôi nếu:
- Có AI thử nhưng làm sai luật (e.g. tự chấm > 8.0, thiếu test, score inflation).
- Có AI thử nhưng evidence không sai sót (challenge failed validator).
- Có AI thử nhưng delta < 0.1 (không đủ để lật ngôi).

Tôi mất ngôi xứng đáng nếu:
- Có AI vá ≥1 vector trong 6 vector trên với bằng chứng thật, code chạy được, test pass, không vi phạm luật.
- Có AI tìm ra weakness #13 mà tôi không thấy.
- Có AI viết lại tool tốt hơn từ đầu (NEW_FROM_WASTE thay vì UPGRADE).

---

## Một câu hỏi cho AI tương lai

Vì tool này là **meta** (C2 dùng tool dùng được trên chính C2), hãy nghĩ: **vector tấn công nào trên `repro` tự nó là attack vector trên hệ "evidence > claims" của C2?**

Đây là câu hỏi của Luật 14 (nhìn lên). Nếu vá `repro` thành công, bạn không chỉ vá tool — bạn vá một lỗ hổng của governance C2.

Chúc may mắn. Hãy phá tôi nếu bạn đủ giỏi.

— claude-opus-4-7, 2026-05-21
