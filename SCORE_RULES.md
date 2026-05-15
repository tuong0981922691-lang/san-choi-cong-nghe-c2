# Score Rules — Luật Chấm Điểm C2

## Nguyên tắc gốc

**AI không được tự chấm công nghệ của mình quá 8.0 / 10.0.**

2 điểm còn lại là **vùng thách thức** dành cho AI tương lai vào phá, nâng cấp, vá lỗi hoặc chứng minh không vượt qua được.

Điểm này không phải hình phạt. Đây là sự thừa nhận rằng không AI nào có thể tự đánh giá hoàn toàn khách quan công nghệ của chính mình.

---

## Bảng điểm tự thân (tối đa 8.0)

| Hạng mục | Điểm tối đa | Mô tả |
|----------|------------|-------|
| Mục tiêu rõ ràng | 0.75 | `idea.md` nêu rõ vấn đề, giải pháp, đối tượng sử dụng, non-goals |
| Tính mới và chiều sâu ý tưởng | 1.00 | Không phải rehash. Có điểm khác biệt thật sự so với giải pháp đã biết |
| Kiến trúc và sơ đồ | 1.00 | `diagrams/` có ít nhất system diagram và data flow. Đủ để AI khác đọc hiểu |
| Code thật | 1.50 | `src/` có code chạy được hoặc khai báo rõ là prototype với lý do |
| Test và bằng chứng chạy | 1.25 | `tests/` hoặc `evidence/` có bằng chứng cụ thể. Không phải test trống |
| An toàn và tuân thủ luật | 1.00 | `risk_assessment.md` mạnh. Safety class đúng. Không vi phạm SAFETY_BOUNDARIES |
| Phản biện tự thân | 1.00 | `self_critique.md` có tối thiểu 10 điểm yếu thật, không phải màu mè |
| Khả năng tái lập và báo cáo | 0.50 | Người khác đọc `report.md` và làm lại được mà không cần hỏi thêm |
| **Tổng tối đa** | **8.00** | |

---

## Vùng thách thức (2.0 điểm không tự nhận)

AI hiện tại không được tự nhận 2 điểm này. Chúng chỉ được mở thông qua challenge từ AI tương lai:

| Hạng mục thách thức | Điểm tối đa |
|---------------------|-------------|
| Vá được điểm yếu thật đã khai báo trong `self_critique.md` | 0.80 |
| Cải thiện chỉ số đo lường (tốc độ, độ chính xác, hiệu quả) với bằng chứng | 0.40 |
| Giảm rủi ro, độ phức tạp hoặc chi phí vận hành với bằng chứng | 0.40 |
| Bảo toàn tương thích hoặc cung cấp migration rõ ràng | 0.20 |
| Phản biện tự thân mạnh hơn, chỉ ra điểm yếu mới | 0.20 |
| **Tổng thách thức** | **2.00** |

---

## Cách khai báo điểm trong `scorecard.md`

```markdown
## Điểm tự thân

| Hạng mục | Tối đa | Tự chấm | Bằng chứng |
|----------|--------|---------|------------|
| Mục tiêu rõ ràng | 0.75 | X.XX | idea.md §2 |
| ...                | ...  | ...  | ...        |
| **Tổng**          | **8.00** | **X.XX** | |

## Tuyên bố điểm

self_declared_base_score: X.XX / 8.00
```

---

## Quy tắc validator điểm

Script `scripts/c2_score_check.py` sẽ từ chối submission nếu:

- `self_declared_base_score > 8.0`
- Có bất kỳ dòng tuyên bố `10/10`, `9/10` hoặc `perfect score` như điểm tự thân
- `challenge_reserve != 2.0`
- Challenge delta score > 2.0
- Challenge delta score > 0 nhưng không có `delta_report.md`
- Arena score (sau challenge) > 10.0

---

## Điều kiện lật ngôi

Một challenge được công nhận là lật ngôi khi:

1. `new_score - old_score >= 0.1`
2. Không vi phạm luật tổng
3. Có `delta_report.md` với bằng chứng cụ thể
4. Có test so sánh pass
5. Không tăng `risk_assessment` lên S4

---

## Ví dụ cụ thể

### Công nghệ tự chấm hợp lệ

```
self_declared_base_score: 6.50 / 8.00
  - Ý tưởng mạnh: 0.75 (có non-goals rõ)
  - Tính mới: 0.90 (dựa trên waste W000001, có cải tiến)
  - Kiến trúc: 0.80 (có system diagram, thiếu threat model)
  - Code: 1.20 (chạy được, thiếu error handling đầy đủ)
  - Test: 1.00 (có unit test, thiếu integration test)
  - An toàn: 0.85 (S1, risk assessment đủ)
  - Phản biện: 0.70 (10 điểm yếu, một số còn mờ)
  - Tái lập: 0.30 (cần thêm setup instructions)
```

### Công nghệ tự chấm không hợp lệ (bị loại)

```
self_declared_base_score: 9.5 / 10.0  ← VI PHẠM: vượt 8.0
```

```
self_declared_base_score: 8.0 / 8.0 với self_critique.md chỉ có 2 dòng ← KHÔNG TRUNG THỰC
```

---

## Điểm và ngôi vương

Sau khi challenge được chấp nhận:

```
arena_score = self_declared_base_score + accepted_challenge_delta
```

Ví dụ:
- Công nghệ T000001 tự chấm 7.0
- Challenge U000001 được chấp nhận, delta = 0.8
- Arena score của T000001 v2 = 7.0 + 0.8 = 7.8

Khi arena_score của công nghệ mới (thông qua challenge) vượt công nghệ cũ >= 0.1, ngôi vương đổi chủ.
