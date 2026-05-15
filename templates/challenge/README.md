# Template: Challenge

Thư mục này chứa mẫu chuẩn cho một challenge — thách thức nâng cấp công nghệ đang giữ ngôi vương.

## Cấu trúc challenge

```text
vault/challenges/{CHALLENGE_ID}/
├── challenge_manifest.yaml    — Metadata thách thức
├── target_analysis.md         — Phân tích điểm yếu của target
├── upgrade_plan.md            — Kế hoạch nâng cấp chi tiết
├── delta_report.md            — Bằng chứng version mới tốt hơn
├── self_critique.md           — Tự phản biện challenge này
├── risk_assessment.md         — Rủi ro của phương án nâng cấp
├── report.md                  — Báo cáo tổng hợp challenge
├── src/                       — Code thật của version mới
│   └── .gitkeep
├── tests/                     — Tests cho version mới
│   └── README.md
└── evidence/                  — Bằng chứng chạy được (benchmark, log)
    └── README.md
```

## Quy trình

1. Phân tích `self_critique.md` của target trong `vault/technologies/{TARGET}/versions/{VER}/`
2. Tạo `challenge_manifest.yaml` với `proposed_delta` trong [0.1, 2.0]
3. Viết `target_analysis.md` — điểm yếu nào bạn sẽ giải quyết
4. Viết `upgrade_plan.md` — kế hoạch cụ thể
5. Thi công code trong `src/`, tests trong `tests/`
6. Chạy tests và lưu output vào `evidence/`
7. Viết `delta_report.md` — bằng chứng so sánh trực tiếp với target
8. Tự phản biện trong `self_critique.md`
9. Báo cáo rủi ro trong `risk_assessment.md`
10. Tóm tắt trong `report.md`

## Luật challenge

- `proposed_delta` phải trong [0.1, 2.0]
- Phải có `delta_report.md` khi có `proposed_delta > 0`
- Code phải chạy và tests phải pass
- Không được claim thắng mà không có bằng chứng thực tế
