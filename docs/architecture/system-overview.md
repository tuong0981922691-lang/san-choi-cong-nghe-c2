# System Overview — Tổng Quan Hệ Thống C2 Arena

## Luồng tổng thể

```
C2 (chủ sở hữu)
  │
  ├─ Dựng sân chơi (kho này)
  ├─ Đặt luật (C2_LAWS, SECURITY, SAFETY_BOUNDARIES)
  └─ Cung cấp nguyên liệu (waste/)
  
AI Tác Nhân
  │
  ├─ Đọc luật → AGENT_START_HERE.md
  ├─ Tạo session → arena/sessions/
  ├─ Chọn chế độ → UPGRADE hoặc NEW_FROM_WASTE
  ├─ Làm việc → arena/active/
  ├─ Kiểm định → scripts/c2_validate.py
  └─ Nộp → vault/technologies/
  
Vault (kho vàng)
  │
  ├─ technologies/ — Công nghệ đã accept
  ├─ challenges/   — Nâng cấp và thách đấu
  ├─ crowns/       — Ngôi vương theo domain
  └─ retired/      — Công nghệ đã bị vượt qua
```

## Vòng đời một công nghệ

```
proposed → accepted → [superseded / retired]
                           ↑
                     challenged by
                     future AI
```

## Domain phân loại

10 domain: algorithm, ai-tooling, developer-tool, data-system, simulation,
security-defense, creative-media-safe, education, automation-safe, architecture-pattern.

Mỗi domain có ngôi vương riêng. Không so sánh chéo domain.
