# Arena — Khu Làm Việc Tạm

## Mục đích

`arena/` là nơi AI tác nhân làm việc trước khi nộp công nghệ vào vault.

## Cấu trúc

```text
arena/
  active/    — Công nghệ đang được tạo, chưa nộp
  scratch/   — Ghi chú tạm, bản nháp, thử nghiệm (.gitignored)
  sessions/  — Lịch sử phiên làm việc của AI
    S20260515-001-agent/
      session_manifest.yaml
      decision_log.md
      working_notes.md
      REPORT_TO_C2.md
```

## Quy tắc

- `scratch/` bị `.gitignore` — dùng cho ghi chú không cần lưu
- `sessions/` được git track — lưu lịch sử phiên
- Sau khi hoàn thành, công nghệ chuyển từ `active/` → `vault/technologies/`
- Mỗi session bắt buộc có `REPORT_TO_C2.md` được điền trước khi đóng phiên
