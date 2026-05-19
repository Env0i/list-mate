# Design: list-mate — 个人 ACGN 媒体库

**状态**: Approved
**作者**: Alex (PM)
**最后更新**: 2026-05-18
**版本**: v2.0
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
| 模组清单 | 单文件上传 | 多附件（不限定类型和数量）+ 文本模组列表 | 覆盖僵毁沙盒配置等复杂场景 |
| 进度完成 | 未明确 | progress_value >= total && total > 0 时自动 completed，可手动覆盖 | 减少操作步骤 |
| 搜索降级 | 未明确 | Bangumi 填充后可编辑所有字段 | 个人用不需要严格数据校验 |
| 视觉风格 | 标准 web app | 抽卡图鉴/集换式卡牌 UI | 统一视觉语言，突出个性 |
| 追踪字段 | 仅进度+评分 | Work 层面扩充：购买信息、时长、优先度、外部链接等 | 满足个人记录需求 |
| GameProfile | 简易进度 | 新增开始/完成时间、时长、来源、模组列表、笔记 | 满足不同游戏类型记录需求 |
| progress_type | 无 | 引入 count / percent / none 区分进度含义 | 不同游戏进度含义不同 |
| 编辑方式 | 独立编辑页 | 模态对话框（原地编辑） | 保持详情页展示状态 |
| 列表视图 | 网格+列表双模式 | 仅保留网格展示 | 统一卡册展示感 |

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
| 字体 | DM Sans + Noto Sans SC | 西文+中文搭配 |
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
| summary | str? | 作品简介，Bangumi 自动填充或手动填写 |
| start_date | str? | 开始追/玩时间 |
| finish_date | str? | 看完/通关时间 |
| platform | str? | 观看/游玩平台（Bilibili / Netflix / Steam / PS5 等） |
| purchase_platform | str? | 购买平台（仅游戏） |
| purchase_date | str? | 购买时间（仅游戏） |
| purchase_price | float? | 购买价格（仅游戏） |
| playtime_hours | float? | 总游玩时长（仅游戏） |
| replay_count | int? | 重刷次数（仅游戏） |
| priority | int? | 优先度，数值越大越优先 |
| external_links | str? | JSON 格式的外链，如 {"steam":"https://..."} |
| bangumi_data | str? | Bangumi 返回的原始数据 JSON（日期、平台、标签、infobox 等） |
| created_at | datetime | |
| updated_at | datetime | |

### GameProfile（游戏多配置）

仅 category=game 时使用。一个游戏可有多个配置（本体/整合包/自打模组），每个独立追踪进度和状态。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int (PK) | |
| work_id | int (FK → Work) | 所属游戏作品 |
| name | str | 配置名称："本体" / "整合包" / "自打模组" |
| progress_value | float? | 进度数值，含义由 progress_type 决定 |
| progress_type | str | count / percent / none，默认 none |
| status | str | 游戏状态：wish / playing / completed / dropped / wait_buy / wait_sale |
| rating | int? | 0-10，可空 |
| review | str? | 文字评价，可空 |
| start_date | str? | 开始游玩时间 |
| finish_date | str? | 完成时间 |
| playtime_hours | float? | 游玩时长（小时） |
| source | str? | 整合包来源（CurseForge / B站UP主 / 自己整合 等） |
| mods_list | str? | 模组列表（text，每行一个模组名，粘贴输入） |
| notes | str? | 游玩笔记/心得 |
| auto_completed | bool | 标记是否由系统自动完成 |
| sort_order | int | 排序，默认 0 |
| created_at | datetime | |
| updated_at | datetime | |

#### progress_type 说明

| type | 步进 | 展示 | 适用场景 |
|------|------|------|---------|
| `none` | 不显示进度 | 纯状态标记 | 一次性剧情游戏 |
| `count` | ±1 | "50 次通关" | 黑帝斯、以撒等重复游玩 |
| `percent` | ±1 | "60%" | 整合包完成度 |

创建时智能猜测默认值：含"二刷/周目"→count，含"整合包/模组"→percent，其他→none。

### Attachment（附件）

仅关联 GameProfile，用于上传模组文件、截图、配置文件等。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int (PK) | |
| game_profile_id | int (FK → GameProfile) | |
| label | str | 用户自定义标签，如 "模组文件"、"沙盒配置" |
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
| POST | /works | 新增作品（含进度字段 + 追踪字段） |
| GET | /works/{id} | 作品详情（含 Tags + GameProfiles） |
| PUT | /works/{id} | 编辑作品信息 |
| DELETE | /works/{id} | 删除作品（级联删除关联的 GameProfiles 和 Attachments） |
| GET | /works/{id}/cover | 获取封面图片 |

### Bangumi

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /bangumi/search?q=&type= | 搜索作品 |
| GET | /bangumi/{id} | 获取作品详情 |

### GameProfiles

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /works/{work_id}/game-profiles | 新增游戏配置 |
| GET | /game-profiles/{id} | 获取配置详情（含 Attachments） |
| PUT | /game-profiles/{id} | 更新进度/状态/评分/评价/追踪字段 |
| DELETE | /game-profiles/{id} | 删除配置（级联删除 Attachments） |

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

### Iter 1 — 核心记录 + 卡册 UI

范围：作品 CRUD（含追踪字段）+ Bangumi 搜索 + GameProfile 多配置 + 卡册风前端

#### 第 1 步：后端 — GameProfile 模型扩展
GameProfile 新增字段：start_date, finish_date, playtime_hours, source, mods_list, notes, progress_type

#### 第 2 步：前端 — WorkDetail 重构
- 卡册风详情页
- 左侧封面放大（多层边框 + 四角装饰 + 全息闪光）
- 右侧信息卡（Bangumi 官方数据）
- 底部追踪卡（个人追踪字段，浅灰底 + 左边框品类色）
- 右上角编辑按钮 → 模态编辑对话框（字段分四段）
- 游戏配置区横向条状化

#### 第 3 步：前端 — GameProfileDetail 重构
- 卡册风单卡片布局
- 字段：状态、游玩记录（开始/完成/时长/来源）、模组列表、附件、评分评价、笔记
- progress_type 选择器 + 自适应步进按钮
- 模组列表 tag 展示 + 粘贴添加
- 附件管理

#### 第 4 步：前端 — WorkList 调整
- 去掉列表视图 toggle
- 卡片展示感强化
- card-deal 动画

#### 第 5 步：前端 — 搜索页 + 添加页
- Search.vue：两步流程（搜索 Bangumi → 确认预填对话框）
- Add.vue：手动填写表单

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
- Attachment 管理完整前端
- 作品封面上传
- 数据导出（JSON / CSV）

---

## 6. 前端设计规范

### 视觉语言

抽卡图鉴 / 集换式卡牌风格。整个应用像「翻开一本卡册」的体验。

| 元素 | 风格 |
|------|------|
| 背景 | 暖白卡册纸 #F7F5F0 |
| 卡片 | 多层边框（品类色外框 2.5px + 白色留边 5px + 最外轮廓 6px） |
| 四角 | conic-gradient 纯 CSS 三角装饰，品类色 |
| 状态 | 旋转印章式戳记（rotate 2deg + stamp-in 动画） |
| 进度条 | EXP 经验值条（梯度填充 + 光泽扫动动画） |
| Hover | 上浮 + 品类色辉光 + 全息闪光斜扫 |
| 分类 Tab | 分段式选择器（segmented tab，如游戏机选择器） |
| 入场动画 | card-deal 3D 发牌效果 |
| 顶栏/底栏 | 玻璃拟态（backdrop-filter: blur） |

### 品类色

| 品类 | 色值 | 用途 |
|------|------|------|
| 动漫 | #FF1A5E | 边框、徽章、辉光 |
| 小说 | #3366FF | 同上 |
| 漫画 | #00CC66 | 同上 |
| 游戏 | #FF7A00 | 同上 |

### 状态色

| 状态 | 色值 |
|------|------|
| wish | #A39F98 |
| watching / playing | #3366FF |
| completed | #00B85A |
| paused | #FFB800 |
| dropped | #FF4444 |
| wait_buy | #FFB800 |
| wait_sale | #FF8C00 |

### 响应式布局

- **手机 (<768px)**: 底部 Tab 导航（玻璃拟态），内容区全宽
- **桌面 (>=768px)**: 顶部导航栏（玻璃拟态），自适应居中内容区，最大宽度 1400px

---

## 7. 页面设计

### 路由表

```
/                          → 作品列表（卡册展示）
/works/:id                 → 作品详情（卡册风，编辑用弹窗）
/search                    → Bangumi 搜索添加
/add                       → 手动添加
/works/:id/game-profiles/new    → 新增 GameProfile
/works/:id/game-profiles/:gpid  → GameProfile 详情/进度更新
/tags                      → 标签管理 (Iter 2)
/stats                     → 统计 (Iter 3)
```

废弃路由：`/works/:id/edit`（已改为弹窗编辑）

### 作品列表页（/）

```
┌──────────────────────────────────────────────────┐
│  收藏                                [🔍]         │
│  [全部|番剧|小说|漫画|游戏]                       │
│  [想看] [在看] [看完] [暂停] [弃了]                │
│                                                    │
│  卡片网格（2-5 列自适应）                           │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐                     │
│  │ ██ │ │ ██ │ │ ██ │ │ ██ │  封面展示为主        │
│  │    │ │    │ │    │ │    │  底部标题一行          │
│  └────┘ └────┘ └────┘ └────┘  状态印章在封面       │
│                               EXP 条在封面底部      │
└──────────────────────────────────────────────────┘
```

### 作品详情页（/works/:id）

桌面端布局 — 两层结构：

```
┌─ 返回 ─────────────────── [编辑] [删除] ─┐
│                                           │
│  ┌──────┐  ┌─ 信息卡（品类色边框）───────┐│
│  │      │  │  Title        [品类 Badge]   ││
│  │ 封面  │  │  sub_category · 总量        ││
│  │ 放大  │  │  [状态印章]                  ││
│  │      │  │                              ││
│  │240px │  │  ── 作品情報 ──               ││
│  │3:4   │  │  日期 · 平台 · 类型           ││
│  │      │  │  开发商 · 标签               ││
│  │      │  │  Bangumi 评分                ││
│  └──────┘  └─────────────────────────────┘│
│                                           │
│  ┌─ 追踪卡（浅灰底 + 左边框）─────────────┐│
│  │  ── 个人追踪 ──                         ││
│  │  开始时间 │ 完成时间 │ 平台 │ 优先度      ││
│  │  购买平台 │ 购买价格 │ 时长 │ 重刷次数    ││
│  │  外部链接                                ││
│  │  ── 进度评价 ──                         ││
│  │  EXP 条 / 评分 / 评价                    ││
│  └────────────────────────────────────────┘│
│                                           │
│  游戏配置（横向条状卡片）                     │
│  ┌ 本体 ── [通关] ── ████ 100% ── 9/10 ─┐│
│  └────────────────────────────────────────┘│
│  [+ 新增配置]                               │
└────────────────────────────────────────────┘
```

编辑通过**模态对话框**实现，右上角按钮触发。对话框字段分四段：
1. **基本信息**：标题、子分类、总量、状态选择器、简介
2. **追踪信息**：开始时间、完成时间、平台、外部链接、优先度
3. **游戏专属**（仅 game 类别）：购买平台、购买价格、购买时间、游戏时长、重刷次数
4. **评分评价**：评分滑块、评价文字

### 游戏配置详情页（/works/:id/game-profiles/:gpid）

卡册风单卡片布局：

```
┌─ 返回作品 ───────────────────── [删除] ─┐
│                                          │
│  作品名 > 配置名                           │
│                                          │
│  ┌─ 属性卡片 ───────────────────────────┐│
│  │  ── 状态 ──                           ││
│  │  [想玩] [在玩] [通关] [弃坑] [等购买]   ││
│  │                                       ││
│  │  ── 游玩记录 ──                       ││
│  │  开始时间 │ 完成时间                    ││
│  │  游玩时长 │ 来源                        ││
│  │                                       ││
│  │  ── 模组列表 ──                       ││
│  │  [tag] [tag] [tag] [+ 添加]           ││
│  │                                       ││
│  │  附件: 📎 file.jar [下载] [删除]       ││
│  │  [+ 上传文件]                          ││
│  │                                       ││
│  │  ── 评分评价 ──                       ││
│  │  评分 0 ─●── 10  7/10                  ││
│  │  评价                                    ││
│  │  笔记                                    ││
│  │                                       ││
│  │  [保存]                                ││
│  └────────────────────────────────────────┘│
└────────────────────────────────────────────┘
```

模组列表交互：点 [+ 添加] → 弹 textarea → 粘贴多行 → 自动拆成 tag。

### 搜索页（/search）

两步流程：
1. 搜索 Bangumi → 结果以卡牌小网格展示
2. 点击结果 → 弹出预填确认对话框 → 保存创建 Work

### 添加页（/add）

手动填写表单，布局与编辑对话框一致，保存后跳转详情页。

### 统计页（/stats）— "Collection Log / 收集统计"

视觉概念：游戏收集完成度画面，像 RPG 的玩家数据总览。

```
┌─ 📊 收集统计 ──────────────────────── [JSON] [CSV] ─┐
│                                                        │
│  [📈 数据总览]  [📋 操作记录]  ← segmented tab        │
│                                                        │
│  全部: 42    进行中: 12    已完成: 28                   │
│  ┌── 快照统计卡片（品类色左边框）──  ──  ──  ── ─┐   │
│                                                        │
│  品类徽章行                                            │
│  ┌ 番剧 ──── 15 ┐ ┌ 小说 ──── 8 ┐                    │
│  │ ████████░░░  │ │ ██████░░░░  │  品类色图标 + 计数  │
│  └──────────────┘ └────────────┘  底部进度条           │
│  ┌ 漫画 ──── 10 ┐ ┌ 游戏 ──── 9 ┐                    │
│  └──────────────┘ └────────────┘                      │
│                                                        │
│  ┌─ 状态分布 ──────┐  ┌─ 评分分布 ─────┐              │
│  │ 想看 ██████ 12  │  │ S ██████ 5     │  等级徽章     │
│  │ 在看 ████ 8     │  │ A ██████ 8     │  S/A/B/C     │
│  │ 看完 ██████ 15  │  │ B ████ 4       │              │
│  │ 暂停 ██ 4       │  │ C ██ 2        │              │
│  │ 弃了 ██ 3       │  │ 未评 ██████ 23 │              │
│  └─────────────────┘  └────────────────┘              │
│                                                        │
│  等级图例: S(9-10) A(7-8) B(5-6) C(0-4)                │
└────────────────────────────────────────────────────────┘
```

**操作记录 Tab**：

```
  · — 添加         作品 #12 "葬送的芙莉莲"       3天前
  │
  · — 进度更新     作品 #8  ep 3 → ep 7         5天前
  │
  · — 状态变更     作品 #12 想看 → 在看          3天前
  │
  · — 评分变更     作品 #5  未评分 → 8/10        1周前
```

- 时间线为纵向时间轴样式（带连接线），不同类型有不同的圆点色
- 可滚动区域，默认展示最近 50 条

### 标签页（/tags）— "Sticker Book / 贴纸集"

视觉概念：像收集实体贴纸一样管理标签。

```
┌─ 🏷️ 贴纸集 ────────────────────── [返回] ─┐
│                                              │
│  ┌─ 新贴纸 ──────────────────────────┐      │
│  │ [●] [●] [●] [●] [●] [+ 自定义色]  │      │
│  │ [输入标签名称...] [添加]            │      │
│  └────────────────────────────────────┘      │
│                                              │
│  ┌━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┐          │
│  ┃ ▓ (颜色条)                      ┃          │
│  ┃ ● 科幻                [✎] [🗑]  ┃  贴纸卡  │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛          │
│  ┌━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┐          │
│  ┃ ▓ (颜色条)                      ┃          │
│  ┃ ● 治愈                [✎] [🗑]  ┃  编辑态:  │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛          │
│  ┌━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┐          │
│  ┃ ▓                              ┃          │
│  ┃ ● 异世界              [✎] [🗑]  ┃          │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛          │
└──────────────────────────────────────────────┘
```

设计要点：
- 每个标签是一张「贴纸卡」：上方有色条（标签色），主体为圆点 + 名称
- 编辑/删除按钮悬浮显示（手机端常显）
- 编辑态展开整张贴纸卡，显示颜色选择器和名称输入框
- 创建区像「空白贴纸」卡片，选择颜色 → 输入名称 → 添加
- 空状态：显示贴纸图标 + 引导文字

---

## 8. 核心流程

### 添加作品（搜索 Bangumi）

```
打开搜索页 → 输入关键词 → 调用 Bangumi API →
显示结果列表（卡牌网格） → 选择一条 →
弹出预填确认对话框 → 确认/修改字段 → 保存 →
创建 Work → 跳转详情页
```

### 添加作品（手动）

```
打开添加页 → 填写表单（与编辑对话框布局一致）→ 保存 →
创建 Work → 跳转详情页
```

### 更新进度（动漫/小说/漫画）

```
打开作品详情 → 点编辑按钮 → 弹窗修改 progress_value →
如 progress_value >= total (>0) → 自动标记 completed →
保存 → 关闭弹窗，详情页刷新
```

### 游戏多配置管理

```
作品详情页 → 点击"新增配置" →
填写配置名（"奇幻大修整合包"）→ 选择状态 → 保存 →
作品详情页显示多个横向 GameProfile 卡片 →
各自独立管理进度/状态/评分/模组/笔记
```

---

## 9. 状态枚举

### WorkStatus（动漫/小说/漫画）

wish → watching → completed → paused → dropped

中文：想看 → 在看 → 看完 → 暂停 → 弃了

### GameStatus（游戏）

wish → playing → completed → dropped → wait_buy → wait_sale

中文：想玩 → 在玩 → 通关 → 弃坑 → 等购买 → 等折扣

### ProgressUnit（进度单位）

anime → ep（集）, novel → chapter（章）, comic → volume（卷）, game → percent（%）

### ProgressType（GameProfile 进度类型）

none → 不显示数字进度；count → 通关次数；percent → 完成百分比

### CoverSource

bangumi / manual / other
