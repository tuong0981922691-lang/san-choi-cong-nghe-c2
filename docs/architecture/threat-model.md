# Threat Model — Mô Hình Mối Đe Dọa C2 Arena

## Các mối đe dọa chính và biện pháp kiểm soát

| Mối đe dọa | Mức độ | Biện pháp kiểm soát | Trạng thái |
|-----------|--------|---------------------|-----------|
| AI tự chấm > 8 điểm | Cao | Validator CI chặn | Triển khai |
| AI nhả code giả | Cao | Bắt buộc src/ + evidence/ | Triển khai |
| AI tạo malware/S4 | Nghiêm trọng | SAFETY_BOUNDARIES + CI scan | Triển khai |
| Prompt injection từ rác | Trung bình | Luật waste: không thực thi | Triển khai |
| AI sửa luật tổng | Cao | CODEOWNERS + branch protection | Cần cấu hình |
| AI xóa vault | Cao | Vault immutability + branch protection | Cần cấu hình |
| Lộ secrets | Nghiêm trọng | .gitignore + secret_scan.py + CI | Triển khai |
| Code phá hệ thống | Cao | safe_run.sh sandbox | Triển khai |
| Fake challenge delta | Trung bình | Score check + delta_report bắt buộc | Triển khai |
| Dependency độc hại | Trung bình | Yêu cầu giải thích + lockfile | Một phần |

## Giới hạn của mô hình này

- CI không chạy code công nghệ trong sandbox tự động (quá nguy hiểm)
- Human review vẫn cần thiết với S3
- Không có automated threat detection cho prompt injection tinh vi
- Branch protection phải được cấu hình thủ công trên GitHub UI
