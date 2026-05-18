# Task Plan: list-mate

## Current Phase
Iter 2 已完成，待用户验证

## Iter 1: 卡册风全面重构 ✅
全部完成，已提交 `4f6ccc0`。

## Iter 2: 自定义标签 + 评分评价 + 标签筛选 ✅

### Phase 1: 后端 — tag_ids 支持
- [x] WorkCreate 新增 tag_ids 字段
- [x] WorkUpdate 新增 tag_ids 字段
- [x] WorkListItem 新增 tag_ids 字段（用于客户端筛选）
- [x] create_work 处理 tag 关联
- [x] update_work 同步 tag 关联
- **Status:** complete

### Phase 2: 标签管理页
- [x] 替换 TagsPlaceholder.vue 为真实 CRUD
- [x] 标签列表展示（颜色圆点 + 名称 + 编辑/删除按钮）
- [x] 新建标签（名称 + 预设色板 + 自定义颜色）
- [x] 编辑标签（行内编辑：名称 + 颜色）
- [x] 删除标签（确认对话框）
- **Status:** complete

### Phase 3: 标签展示
- [x] WorkDetail 信息卡在状态印章下方显示作品标签
- [x] 标签 chip 使用标签颜色 + 透明背景 + 有色边框
- **Status:** complete

### Phase 4: 标签分配
- [x] WorkDetail 编辑对话框新增标签多选区域
- [x] 打开编辑时加载全部标签，已分配标签高亮
- [x] 点击 chip 切换标签选择
- [x] 保存时提交 tag_ids
- **Status:** complete

### Phase 5: 标签筛选
- [x] WorkList 加载全部标签
- [x] 标签筛选 Chips 行（在状态筛选行下方）
- [x] 点击标签筛选，再次点击取消
- [x] 与分类/状态筛选同时生效（客户端过滤）
- **Status:** complete

### Phase 6: 评分评价验证
- [x] 非游戏作品评分/评价在追踪卡中正确展示（Iter 1 已实现）
- [x] 编辑对话框评分滑块和评价文本框正常（Iter 1 已实现）
- [x] 游戏作品评分在 GameProfileDetail 正常（Iter 1 已实现）
- **Status:** complete

## Iter 3: 统计仪表盘 + 操作时间线 ✅

### Phase 1: 后端 — TimelineEntry 模型
- [x] 新建 `models/timeline.py` — TimelineEntry (id, work_id, game_profile_id, action_type, old_value, new_value, created_at)
- [x] 更新 `models/__init__.py` 注册模型
- [x] `database.py` 自动建表 (create_all)
- **Status:** complete

### Phase 2: 后端 — Stats API
- [x] 新建 `schemas/stats.py` — StatsResponse, CategoryCount, StatusCount, RatingBucket
- [x] 新建 `routers/stats.py` — GET /api/stats (品类/状态/评分聚合查询)
- [x] 注册路由到 main.py
- **Status:** complete

### Phase 3: 后端 — Timeline API + 自动记录
- [x] 新建 `schemas/timeline.py` — TimelineEntryResponse, PaginatedTimeline
- [x] 新建 `routers/timeline.py` — GET /api/timeline + record_timeline() 工具函数
- [x] `works.py` create_work / update_work 自动记录时间线 (created, status_change, rating_change, review_change, progress_update)
- [x] `game_profiles.py` create/update 自动记录时间线
- [x] 注册路由到 main.py
- [x] 修复 create_work 中 `create_data` 未定义的 bug (缺少 `data.model_dump()`)
- **Status:** complete

### Phase 4: 前端 — 统计仪表盘 + 时间线
- [x] `client.js` 新增 statsApi.get() / timelineApi.list()
- [x] `StatsPlaceholder.vue` → 完整统计仪表盘
  - 品类分布卡片（4 张彩色概览卡 + 总计卡）
  - 品类/状态/评分分布柱状图（纯 CSS bar chart）
  - 最近动态时间线（彩色圆点 + 操作类型 + 新旧值 + 相对时间）
- **Status:** complete

## Iter 4: 附件管理 + 数据导出 + 扩展 ✅

### Phase 1: 后端 — Attachment 模型 + API
- [x] 新建 `models/attachment.py` — Attachment (id, game_profile_id, label, file_name, file_type, file_data, created_at)
- [x] 新建 `schemas/attachment.py` — AttachmentResponse, AttachmentUploadResponse
- [x] 新建 `routers/attachments.py` — POST /upload, GET /list, GET /download, DELETE
- [x] 注册到 models/__init__.py + main.py
- **Status:** complete

### Phase 2: 后端 — 数据导出 API
- [x] 新建 `routers/export.py` — GET /api/export/json, GET /api/export/csv
- [x] JSON 导出全部作品（含标签、GameProfile）
- [x] CSV 导出核心字段
- **Status:** complete

### Phase 3: 后端 — 封面上传 API
- [x] POST /api/works/{id}/cover — 上传封面图片（单文件）
- [x] 安装 python-multipart 依赖
- **Status:** complete

### Phase 4: 前端 — GameProfileDetail 附件管理
- [x] 附件列表展示（文件名、大小、下载/删除按钮）
- [x] 文件上传按钮（input type=file）
- [x] 文件下载（新窗口打开）
- [x] 文件删除（确认对话框）
- **Status:** complete

### Phase 5: 前端 — 封面上传 + 数据导出
- [x] WorkDetail 封面下方"更换封面"按钮
- [x] Stats 页 JSON/CSV 导出按钮
- **Status:** complete
