# Findings — list-mate Iter 1

## Requirements
- 作品 CRUD（动漫/小说/漫画/游戏四类）
- Bangumi 搜索自动填充（可编辑降级）
- 多 Profile 进度管理（所有品类共用）
- 封面缓存（Bangumi 图片存本地 BLOB）
- 进度自动完成（progress_value >= total 时自动标记 completed）
- 响应式前端（手机+桌面自适应）
- 部署到阿里云服务器

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| FastAPI + SQLAlchemy + SQLite | 与前两个项目一致 |
| Vue 3 + Vite + Vue Router | 轻量，响应式 |
| Scoped CSS | 零额外依赖 |
| 封面存 BLOB | 不依赖外部服务 |
| Profile 统一模型 | 支持二刷/多配置 |

## Resources
- Bangumi API 文档: https://bangumi.github.io/api/
- 阿里云服务器: 47.108.188.175
- 部署密钥: C:/Users/29522/.ssh/money-mate.pem
- 之前项目结构参考: goal-mate/ (FastAPI + 前端分离)

## Visual/Browser Findings
-

## 产品决策 (2026-09-27 自主接管第六轮)

### GameProfile count 型进度不自动完成 — 用户确认
- percent 型 ≥100% 自动标 completed；count 型（二周目等通关次数）**保持手动标记**
- 理由：次数是开放积累（一刷/二刷/三刷…），没有天然的"完成"锚点；引入"目标次数"字段属于过度设计
- 影响范围：GameProfile 自动完成规则仅覆盖 percent；count/none 型状态由用户手动管理
- 用户拍板方式：AskUserQuestion 三选一（保持手动/目标次数字段/≥2次自动），用户选"保持手动标记（推荐）"
