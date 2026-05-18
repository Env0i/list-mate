# Design: list-mate — 个人 ACGN 媒体库

**状态**: Approved
**作者**: Alex (PM)
**最后更新**: 2026-05-18
**版本**: v1.0
**基于 PRD**: docs/PRD.md

---

## 1. 设计决策摘要

### 关键改动（相对于 PRD v0.1）

| 决策 | 原方案 | 新方案 | 原因 |
|------|--------|--------|------|
| Profile 模式 | Progress + GameProfile 分开 | 统一 Profile 后改回原方案 | Work 自带进度字段，GameProfile 仅用于游戏；两套状态枚举 |
| 前端 | Uni-app + Element Plus 分开 | 单 Vue 3 响应式，一套代码 | 减少维护量，个人项目够用 |
| 移动端 | 编译为原生 App | 仅 H5，不打包 App | 省去 99$/年 Apple 开发者费用 |
| 封面处理 | 未明确 | 存 BLOB 本地缓存 + 保留 source URL | 加载速度，不依赖外部服务 |
| 模组清单 | 单文件上传 | 多附件（不限定类型和数量） | 覆盖僵毁沙盒配置等复杂场景 |
| 进度完成 | 未明确 | progress_value >= total && total > 0 时自动 completed，可手动覆盖 | 减少操作步骤 |
| 搜索降级 | 未明确 | Bangumi 填充后可编辑所有字段 | 个人用不需要严格数据校验 |

### 不做的（排期内）

内置阅读器/播放器、社交/好友、多用户、第三方平台同步导入、推荐算法、AI 功能。

---

## 2. 技术架构

```
阿里云服务器
├── FastAPI + SQLAlchemy (API 服务)
├── SQLite (数据库)
├── 封面缓存 (BLOB 存于 SQLite)
├── 附件文件 (BLOB 存于 SQLite)
├── Vue 3 SPA (静态文件，由 Nginx 提供服务)
└── Nginx (反向代理 + 静态文件)
```

### 技术栈

| 层 | 技术 | 理由 |
|----|------|------|
| 后端框架 | Python FastAPI | 与前两个项目一致，开发速度快 |
| ORM | SQLAlchemy | 成熟稳定，迁移方便 |
| 数据库 | SQLite | 单用户够用，零运维 |
| 前端 | Vue 3 + Vite | 轻量，响应式 |
| 样式 | Vue 组件内 scoped CSS | 零依赖，简单直接 |
| 部署 | deploy.py (paramiko) | 沿用 goal-mate 模式 |

---

## 3. 数据模型

### Work（作品）

动漫/小说/漫画的进度直接挂在 Work 上，游戏通过 GameProfile 管理多配置。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int (PK) | |
| title | str | 作品名称 |
| category | enum | anime / novel / comic / game |
| sub_category | str | TV/剧场版/轻小说/网络小说/漫画/条漫/单机/手游/主机... |
| progress_unit | enum | ep / chapter / volume / page / percent |
| total | int? | 可空（连载中未知总章节/集数） |
| progress_value | float? | 当前进度，动漫/小说/漫画用；游戏留空 |
| status | str? | 动漫/小说/漫画用：wish / watching / completed / paused / dropped；游戏留空 |
| rating | int? | 0-10，可空 |
| review | str? | 文字评价，可空 |
| auto_completed | bool | 标记是否由系统自动完成 |
| bangumi_id | int? | 可空，关联外部数据 |
| cover_url | str? | Bangumi 原图链接 |
| cover_data | BLOB? | 本地缓存的封面图片二进制 |
| cover_source | str | "bangumi" / "manual" / "other" |
| created_at | datetime | |
| updated_at | datetime | |

### GameProfile（游戏多配置）

仅 category=game 时使用。一个游戏可有多个配置（本体/整合包/自打模组），每个独立追踪进度和状态。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int (PK) | |
| work_id | int (FK → Work) | 所属游戏作品 |
| name | str | 配置名称："本体" / "整合包" / "自打模组" |
| progress_value | float? | 游玩进度（小时数或百分比），可空 |
| status | str | 游戏状态：wish / playing / completed / dropped / wait_buy / wait_sale |
| rating | int? | 0-10，可空 |
| review | str? | 文字评价，可空 |
| auto_completed | bool | 标记是否由系统自动完成 |
| sort_order | int | 排序，默认 0 |
| created_at | datetime | |
| updated_at | datetime | |

### Attachment（附件）

仅关联 GameProfile，用于上传模组清单、沙盒配置文件等。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int (PK) | |
| game_profile_id | int (FK → GameProfile) | |
| label | str | 用户自定义标签，如 "模组清单"、"沙盒配置" |
| file_name | str | 原始文件名 |
| file_type | str | MIME 类型 |
| file_data | BLOB | 文件二进制 |
| created_at | datetime | |

### Tag（标签）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int (PK) | |
| name | str | 标签名称，唯一 |
| color | str | 十六进制颜色，#ff0000 |
| created_at | datetime | |

### WorkTag（作品-标签关联）

| 字段 | 类型 | 说明 |
|------|------|------|
| work_id | int (FK → Work) | |
| tag_id | int (FK → Tag) | |

### TimelineEntry（操作时间线 — Iter 3）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int (PK) | |
| work_id | int (FK → Work) | 关联的作品 |
| game_profile_id | int? (FK → GameProfile) | 可空，仅游戏操作时关联 |
| action_type | str | progress_update / status_change / rating_change / review_change |
| old_value | str? | 旧值（JSON 序列化） |
| new_value | str? | 新值（JSON 序列化） |
| created_at | datetime | |

---

## 4. API 端点

### Works

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /works | 作品列表，支持 category/status/tag 筛选 + 分页 |
| POST | /works | 新增作品（含进度字段） |
| GET | /works/{id} | 作品详情（含 Tags + GameProfiles） |
| PUT | /works/{id} | 编辑作品信息（含进度/状态/评分/评价） |
| DELETE | /works/{id} | 删除作品（级联删除关联的 GameProfiles 和 Attachments） |

### Bangumi

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /bangumi/search?q= | 搜索作品 |
| GET | /bangumi/{id} | 获取作品详情 |

### GameProfiles

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /works/{work_id}/game-profiles | 新增游戏配置 |
| GET | /game-profiles/{id} | 获取配置详情 |
| PUT | /game-profiles/{id} | 更新进度/状态/评分/评价 |
| DELETE | /game-profiles/{id} | 删除配置 |

### Tags

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /tags | 所有标签 |
| POST | /tags | 创建标签 |
| PUT | /tags/{id} | 编辑标签（名称/颜色） |
| DELETE | /tags/{id} | 删除标签 |

### Attachments

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /game-profiles/{gpid}/attachments | 上传附件 |
| GET | /attachments/{id} | 下载附件 |
| DELETE | /attachments/{id} | 删除附件 |

---

## 5. 迭代计划

### Iter 1 — 核心记录

范围：作品 CRUD（含进度字段） + Bangumi 搜索 + GameProfile 多配置

后端：
- Work / GameProfile / Tag 模型 + 迁移
- 全部 Works / GameProfiles / Tags API
- Bangumi 搜索代理 API
- 封面缓存逻辑

前端：
- 作品列表页（卡片/列表双视图，分类 Tab 筛选，显示进度）
- 作品详情页（含 GameProfile 列表 + 进度管理）
- 搜索添加页（Bangumi 搜索预览 ⇒ 填充表单）
- 手动添加页

### Iter 2 — 标记能力

- 标签 CRUD 前端页面
- 作品标记标签（多选）
- 评分 + 评价 UI
- 按标签筛选

### Iter 3 — 数据看板

- TimelineEntry 模型 + API
- 统计仪表盘页面
- 操作时间线页面
- 进度历史展示

### Iter 4 — 扩展

- Attachment 模型 + API
- 附件管理前端（关联 GameProfile）
- 作品封面上传
- 数据导出（JSON / CSV）

---

## 6. 前端页面路由

```
/                          → 作品列表（默认首页）
/search                    → 搜索添加
/add                       → 手动添加
/works/:id                 → 作品详情
/works/:id/edit            → 编辑作品
/works/:id/game-profiles/new    → 新增 GameProfile
/works/:id/game-profiles/:gpid  → GameProfile 详情/进度更新
/tags                      → 标签管理 (Iter 2)
/stats                     → 统计 (Iter 3)
/timeline                  → 时间线 (Iter 3)
```

### 响应式布局

- **手机 (<768px)**: 底部 Tab 导航（玻璃拟态），内容区全宽
- **桌面 (>=768px)**: 顶部导航栏（玻璃拟态），自适应居中内容区，最大宽度 1400px

---

## 7. 核心流程

### 添加作品（搜索 Bangumi）

```
打开搜索页 → 输入关键词 → 调用 Bangumi API → 
显示结果列表（封面+标题+类型）→ 选择一条 →
表单自动填充 → 确认/修改字段 → 保存 →
创建 Work（动漫/小说/漫画直接带进度字段，游戏则自动创建默认 GameProfile）
```

### 添加作品（手动）

```
打开手动添加页 → 填写表单 → 保存 →
创建 Work（同上）
```

### 更新进度（动漫/小说/漫画）

```
打开作品详情 → 直接在作品上更新 progress_value →
如 progress_value >= total (>0) → 自动标记 completed →
保存（前端立即反映新进度）
```

### 游戏多配置管理

```
作品详情页 → 点击"新增配置" →
填写配置名（"奇幻大修整合包"）→ 选择状态（想玩/在玩/通关等）→ 保存 →
作品详情页显示多个 GameProfile →
各自独立管理进度/状态/评分
```
