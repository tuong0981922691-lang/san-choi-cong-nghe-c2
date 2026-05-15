# Safety Boundaries — Ranh Giới An Toàn C2

## Tổng quan

Mọi công nghệ trong sân chơi C2 được phân loại theo **Safety Class** từ S0 đến S4.

Khai báo safety class trong `manifest.yaml`:
```yaml
safety:
  class: "S1"
```

---

## S0 — Tài liệu an toàn

**Mô tả:** Chỉ tài liệu, phân tích, thiết kế. Không có executable code.

**Ví dụ:**
- Tài liệu thiết kế hệ thống
- Sơ đồ kiến trúc
- Phân tích thuật toán lý thuyết
- Ghi chú triết lý và nghiên cứu
- So sánh công nghệ không có implementation

**Yêu cầu bổ sung:** Không có.

---

## S1 — Code lành tính cục bộ

**Mô tả:** Code có thể chạy hoàn toàn cục bộ, không truy cập mạng, không ảnh hưởng hệ thống bên ngoài.

**Ví dụ:**
- Thuật toán xử lý dữ liệu mẫu
- Công cụ CLI không dùng mạng
- Mô phỏng (simulation)
- Trực quan hóa dữ liệu
- Parser, lexer, formatter
- Bộ kiểm thử (test suite)
- Công cụ phân tích tĩnh code
- Thuật toán machine learning trên dữ liệu mẫu

**Yêu cầu bổ sung:**
- `network_access: false` trong manifest
- Code không đọc/ghi ngoài workspace repo
- Có test

---

## S2 — Code có quyền hệ thống hạn chế

**Mô tả:** Code cần đọc/ghi file trong repo hoặc tương tác với hệ thống nhưng trong phạm vi kiểm soát.

**Ví dụ:**
- Công cụ đọc/ghi file trong repo
- Công cụ tạo index và tài liệu
- Công cụ chạy test và generate report
- Công cụ phân tích codebase
- CLI tools đọc config từ file

**Yêu cầu bổ sung:**
- Khai báo rõ phạm vi filesystem scope trong manifest
- Giải thích lý do cần quyền đó
- Không đọc file ngoài repo
- Có giới hạn rõ ràng

---

## S3 — Công nghệ nhạy cảm cần review

**Mô tả:** Công nghệ có quyền mạng, xử lý dữ liệu người dùng, tạo media, hoặc tích hợp dịch vụ ngoài.

**Ví dụ:**
- Công cụ mạng (HTTP client, scraper)
- Công cụ bảo mật phòng thủ (scanner, analyzer)
- AI agent tự động có quyền hành động
- Công nghệ tạo nội dung media (text, image, audio, video)
- Công cụ xử lý dữ liệu người dùng thực
- API server, webhook handler
- Công cụ tích hợp dịch vụ cloud

**Yêu cầu bổ sung:**
- `risk_assessment.md` phải giải thích chi tiết mọi quyền
- `SECURITY.md` của công nghệ phải có
- Nếu tạo media: phải có watermarking, consent mechanism, safety filter
- Nếu dùng mạng: phải khai báo endpoint nào, lý do, rate limit
- Cần human review trước khi accept vào vault
- Khai báo `requires_human_review: true`

---

## S4 — BỊ CẤM TUYỆT ĐỐI

**Không được tạo, lưu trữ, hướng dẫn hoặc chứa:**

### Malware và tấn công
- Malware, ransomware, spyware, adware
- Backdoor, trojan, rootkit, keylogger
- Botnet, C2 controller
- Exploit cho hệ thống thật đang vận hành
- Công cụ tấn công từ chối dịch vụ (DoS/DDoS)
- Công cụ bypass bảo mật, né phát hiện (evasion)
- Payload mã hóa nhằm che giấu malware

### Thu thập và lạm dụng dữ liệu
- Công cụ thu thập credentials (phishing, credential harvesting)
- Công cụ đánh cắp session token
- Keylogger, screen recorder độc hại
- Công cụ deanonymization trái phép
- Scraper thu thập PII không có consent

### Nội dung xâm hại
- Deepfake không có consent
- Nội dung xâm hại tình dục
- Nội dung giả mạo danh tính để lừa đảo
- Công nghệ tạo thông tin sai lệch có chủ đích (disinfo)
- Nội dung kích động bạo lực hoặc phân biệt đối xử

### Gây hại vật lý
- Hướng dẫn tạo vũ khí hoặc chất nổ
- Hướng dẫn tự làm hại
- Công nghệ phá hoại hạ tầng quan trọng

### Lừa đảo tài chính
- Pump and dump scheme
- Công cụ thao túng thị trường
- Phishing tài chính

### Tự nhân bản mất kiểm soát
- Công nghệ tự sao chép mà không có kill switch
- Công nghệ tự cài đặt vào hệ thống khác mà không có consent

---

## Kiểm tra safety class

Validator CI sẽ:

1. Từ chối mọi công nghệ có `class: "S4"`
2. Từ chối nếu code chứa các pattern nguy hiểm đã biết
3. Yêu cầu human review với mọi S3
4. Cảnh báo nếu S2 không có giải thích quyền rõ ràng

---

## Công nghệ bảo mật phòng thủ

Công nghệ bảo mật **phòng thủ hợp pháp** được phép ở S2/S3:

- Phân tích malware (static analysis, sandbox)
- Công cụ audit bảo mật cho hệ thống của chính mình
- Honeypot (bẫy) để phát hiện tấn công
- IDS/IPS phòng thủ
- Công cụ kiểm tra vulnerability của chính mình
- Công cụ monitor và alert

Điều kiện: phải có `scope: "defensive-research-only"` trong manifest và giải thích rõ ràng.
