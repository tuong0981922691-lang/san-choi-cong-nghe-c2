# Risk Assessment — Đánh giá rủi ro Challenge

**Challenge ID:** `C{YYMMDD}{NNN}`  
**Target:** `{TECH_ID} / {VERSION}`  
**Safety class đề xuất:** `S{0-3}`

---

## 1. Safety Classification

| Class | Mô tả | Áp dụng? |
|-------|-------|----------|
| S0 | Chỉ tài liệu/thiết kế, không code chạy | ☐ |
| S1 | Code chạy, không side effects nguy hiểm | ☐ |
| S2 | Truy cập mạng/file giới hạn, cần review | ☐ |
| S3 | Xử lý dữ liệu nhạy cảm, cần C2 approve | ☐ |
| S4 | **TUYỆT ĐỐI CẤM — không được chọn** | ✗ |

**Phân loại của challenge này:** `S{N}`

**Lý do:** {giải thích ngắn}

---

## 2. Rủi ro kỹ thuật

| Rủi ro | Khả năng | Mức độ nghiêm trọng | Kiểm soát |
|--------|----------|---------------------|-----------|
| {rủi ro 1} | Cao/Trung/Thấp | Cao/Trung/Thấp | {biện pháp} |
| {rủi ro 2} | Cao/Trung/Thấp | Cao/Trung/Thấp | {biện pháp} |

---

## 3. Rủi ro regression

Các tính năng của target có thể bị ảnh hưởng khi áp dụng phương án nâng cấp:

- **{tính năng 1}:** Rủi ro {mức độ} — {lý do}
- **{tính năng 2}:** Rủi ro {mức độ} — {lý do}

---

## 4. Rủi ro về tính khả thi

- [ ] Phương án này có thể triển khai trong điều kiện thực tế không?
- [ ] Dependencies có stable không?
- [ ] Có vấn đề licensing không?

---

## 5. Rủi ro về an toàn và đạo đức

- Công nghệ này có thể bị lạm dụng không? **{Có/Không}**
- Nếu có, kiểm soát là: {mô tả}
- Tuân thủ pháp luật Việt Nam và quốc tế: **{Có/Không}**

---

## 6. Kết luận rủi ro

**Đánh giá tổng thể:** Rủi ro {Thấp / Trung bình / Cao}

**Khuyến nghị:** {Challenge này {nên/không nên} được chấp nhận vì...}
