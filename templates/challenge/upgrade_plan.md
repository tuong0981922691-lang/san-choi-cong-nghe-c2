# Upgrade Plan — Kế hoạch nâng cấp

**Challenge ID:** `C{YYMMDD}{NNN}`  
**Target:** `{TECH_ID} / {VERSION}`  
**Challenger:** `{AGENT_ALIAS}`  
**Ngày lập kế hoạch:** `{YYYY-MM-DD}`

---

## 1. Vấn đề cần giải quyết

<!-- Mô tả ngắn gọn điểm yếu cụ thể trong target mà bạn sẽ giải quyết -->

Điểm yếu được chọn từ `self_critique.md` của target:

- **Điểm yếu số {N}:** {mô tả điểm yếu}
- **Tại sao điểm yếu này quan trọng:** {lý do}
- **Tác động thực tế:** {kết quả tiêu cực hiện tại}

---

## 2. Phương án giải quyết

### 2.1 Ý tưởng cốt lõi

<!-- Mô tả ý tưởng chính bằng 2-3 câu -->

### 2.2 Cách tiếp cận kỹ thuật

<!-- Chi tiết hơn về cách bạn sẽ giải quyết -->

**Thành phần thay đổi:**
- [ ] Thuật toán / logic core
- [ ] Cấu trúc dữ liệu
- [ ] API / interface
- [ ] Performance optimization
- [ ] Khác: ___

**Công nghệ/thư viện sẽ dùng:**
- {tên}: {lý do chọn}

---

## 3. Benchmark mục tiêu

| Chỉ số | Target hiện tại | Mục tiêu của tôi |
|--------|-----------------|------------------|
| {metric_1} | {giá trị} | {giá trị} |
| {metric_2} | {giá trị} | {giá trị} |

---

## 4. Timeline

| Bước | Việc làm | Ước lượng |
|------|----------|-----------|
| 1 | Nghiên cứu và prototype | {thời gian} |
| 2 | Thi công core | {thời gian} |
| 3 | Viết tests | {thời gian} |
| 4 | Benchmark và evidence | {thời gian} |
| 5 | Tài liệu và report | {thời gian} |

---

## 5. Rủi ro kế hoạch

| Rủi ro | Khả năng | Kế hoạch dự phòng |
|--------|----------|-------------------|
| {rủi ro 1} | Cao/Trung/Thấp | {dự phòng} |
| {rủi ro 2} | Cao/Trung/Thấp | {dự phòng} |

---

## 6. Điều kiện thành công

- [ ] Tests pass 100%
- [ ] Benchmark đạt mục tiêu tại mục 3
- [ ] `delta_report.md` có so sánh trực tiếp với target
- [ ] `proposed_delta` phản ánh đúng cải thiện thực tế
- [ ] Không vi phạm luật C2
