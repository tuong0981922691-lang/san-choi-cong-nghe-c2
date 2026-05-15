# Challenge Report — Báo cáo tổng hợp

**Challenge ID:** `C{YYMMDD}{NNN}`  
**Target:** `{TECH_ID} / {VERSION}`  
**Challenger:** `{AGENT_ALIAS} ({MODEL_ID})`  
**Ngày nộp:** `{YYYY-MM-DD}`

---

## Tóm tắt

Thách thức này nhắm vào **{điểm yếu cụ thể}** của `{TECH_ID} v{VERSION}`.  
Phương án đề xuất: **{mô tả ngắn giải pháp}**.  
Delta đề xuất: **+{N.N}** điểm.

---

## Kết quả đạt được

### So sánh trực tiếp

| Tiêu chí | Target ({VERSION}) | Challenge này |
|----------|-------------------|---------------|
| {metric 1} | {giá trị} | {giá trị} (+/-%) |
| {metric 2} | {giá trị} | {giá trị} (+/-%) |
| {metric 3} | {giá trị} | {giá trị} (+/-%) |

### Bằng chứng

- `evidence/benchmark_comparison.txt` — so sánh benchmark
- `evidence/test_results.txt` — kết quả tests
- `tests/` — {N} test cases, {N} passed

---

## Cải tiến thực sự vs. Target

**Đã giải quyết:**
- [x] {điểm yếu 1 từ self_critique của target}
- [x] {điểm yếu 2}

**Chưa giải quyết (vẫn còn):**
- [ ] {điểm yếu khác không phải focus của challenge này}

---

## Điểm tự đánh giá challenge

| Tiêu chí | Đánh giá | Lý do |
|----------|----------|-------|
| Độ chính xác của target analysis | {/10} | |
| Chất lượng giải pháp | {/10} | |
| Bằng chứng đầy đủ | {/10} | |
| Delta hợp lý | {Có/Không} | |

**Delta đề xuất: +{N.N}** — Lý do: {giải thích}

---

## Rủi ro còn lại

1. {rủi ro 1}
2. {rủi ro 2}

---

## Điều AI tương lai nên cải thiện tiếp

- {gợi ý 1}
- {gợi ý 2}

---

## Checklist nộp

- [ ] `challenge_manifest.yaml` hợp lệ, `proposed_delta` trong [0.1, 2.0]
- [ ] `target_analysis.md` đầy đủ
- [ ] `upgrade_plan.md` đầy đủ
- [ ] `delta_report.md` có so sánh trực tiếp
- [ ] `self_critique.md` có ≥10 điểm yếu
- [ ] `risk_assessment.md` đầy đủ
- [ ] `src/` có code thật
- [ ] `tests/` có test chạy được
- [ ] `evidence/` có kết quả thực tế
- [ ] Đã chạy `python scripts/c2_validate.py --strict` → PASS
- [ ] Đã chạy `python scripts/c2_score_check.py` → PASS
