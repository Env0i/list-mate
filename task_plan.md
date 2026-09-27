# Task Plan: list-mate

## Current Phase
P0 修复完成（2026-09-27）；下一步 P1：前端常量收敛 + 死组件清理 + Bangumi type 映射修正

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

## P0 修复: 级联删除 500 + 前端空值 422 ✅ (2026-09-27)

### Phase 1: 后端级联删除
- [x] models/work.py 移除 timeline_entries 的 passive_deletes（FK 无数据库级 CASCADE，须 ORM 删除）
- [x] game_profiles.py delete 路由先清理 TimelineEntry.game_profile_id
- **Status:** complete

### Phase 2: 前端空值归一化
- [x] 新增 utils/payload.js emptyToNull（空串→null）
- [x] Add.vue / Search.vue / WorkDetail.vue 提交前归一化数字/状态字段
- [x] WorkDetail 幽灵字段 external_url → external_links（编辑外部链接原本静默丢失）
- [x] 游戏作品隐藏"—"清空选项；无配置时不提交 status
- **Status:** complete

### Phase 3: 验证
- [x] 修复前后对照复现：DELETE 500 → 204
- [x] api_full_test.py 77/77（报告已刷新）
- [x] 浏览器实测：只填标题提交成功；编辑设置/清空状态与总量保存成功（抓包核对 payload）
- **Status:** complete

## P1 修复: 常量收敛 + 数据逻辑补漏 ✅ (2026-09-27 第二轮)

### Phase 1: 前端一致性
- [x] 新增 src/constants/work.js（STATUS_LABELS/STATUS_COLORS/categoryGradient），6 个视图/组件删除本地副本
- [x] style.css 补 --c-*-light 与 --s-wait-sale 令牌
- [x] 删除死组件 Sidebar.vue、StatusBadge.vue（全仓无引用）
- **Status:** complete

### Phase 2: 后端数据逻辑
- [x] rating 0-10 范围校验（仅 Create/Update，响应模型不拦存量数据）
- [x] 统计页评分分布合并 GameProfile 评分
- [x] WorkListItem/works.py 补 game_progress_value（修复游戏卡 EXP 条幽灵字段）
- [x] record_timeline 变更类新旧值相同跳过（杜绝 completed→completed 垃圾记录）
- [x] page_size 上限 100→500（前后端），列表不再静默截断
- [x] bangumi.py type 映射注释纠错
- **Status:** complete

### Phase 3: 验证
- [x] api_full_test.py 77/77；vite build 通过
- [x] 浏览器抽查：首页卡片（渐变/状态戳/EXP 条 45%）、统计页（游戏评分 6 分入分布）
- [x] GameProfileDetail 仅 status 变化时提交 → percent>=100 自动完成规则 UI 可达
- **Status:** complete

## 第三轮: 个性化两件套 — 暗色主题 + 偏好持久化 ✅ (2026-09-27)

### Phase 1: 暗色主题
- [x] src/utils/theme.js：localStorage('zace-theme') 持久化，未设置时跟随系统 prefers-color-scheme，main.js 挂载前应用防首帧闪白
- [x] style.css 新增 :root[data-theme='dark'] 暖黑变量覆盖（color-scheme: dark，品类/状态饱和色不变）
- [x] TopBar/MobileNav 背景令牌化（--topbar-bg/--nav-bg 等），ThemeToggle 组件双端接入（桌面右上角 + 移动底栏）
- [x] 暗色下 logo 反白（invert）保证可读
- **Status:** complete

### Phase 2: 偏好持久化 + 排序
- [x] WorkList 筛选/搜索/排序状态存 localStorage('zace-prefs-list')，恢复时校验有效性（失效标签筛选自动清空）
- [x] 新增排序 UI：最近更新/评分优先/优先度/标题（客户端排序，评分与优先度 null 值沉底）
- **Status:** complete

### Phase 3: 验证
- [x] vite build 通过（后端零改动，API 测试状态沿用 77/77）
- [x] 浏览器实测：亮/暗首页与详情页截图；切主题 localStorage 写入 dark；评分排序断言 9→8→6；刷新后主题/排序/分类筛选全部恢复
- [x] 测试数据与浏览器偏好已还原
- **Status:** complete

## 第四轮: 断点收敛 ✅ (2026-09-27)

- [x] WorkDetail 编辑弹窗 700px → 767px（单列切换与全局移动档对齐）
- [x] Add.vue / GameProfileDetail.vue 639px → 767px（卡片内边距压缩跟上移动档）
- [x] 网格列数阶梯（640/900/960/1200）确认为合法响应式步进，保留
- [x] 断点规范写入 AGENTS.md：主断点 767/768 + 小屏档 480，网格阶梯例外
- [x] 验证：build 通过；740px 宽度实测编辑弹窗单列
- **Status:** complete

## 第五轮: Bangumi 回填总集数 + 类型过滤修复 ✅ (2026-09-27)

### Phase 1: 搜索添加自动回填
- [x] Search.vue 选中动画条目时拉取详情，total_episodes 自动填入总量（单位语义一致）；
      漫画(卷)/小说(章)单位不匹配不做回填；失败静默
- **Status:** complete

### Phase 2: 类型过滤真修复（浏览器实测发现的存量 bug）
- [x] bangumi.py 裸 type 字段被 v0 API 静默忽略 → filter.type 数组格式
- [x] api_full_test.py "Get work by valid ID" 空库自建数据（消除环境依赖）
- **Status:** complete

### Phase 3: 验证
- [x] 裸 API 对照：裸 type 返回混合类型，filter.type 返回全 2
- [x] 浏览器：番剧过滤 → 选中动画 → 总量自动填 26
- [x] api_full_test.py 全部通过（含空库自洽用例）
- **Status:** complete

## 第六轮: 移动端体验打磨 ✅ (2026-09-27)

- [x] 375px 逐页审查（首页/详情/添加/统计/标签/搜索）
- [x] 首页标题"收藏"竖排换行 → 移动端 hd-row 两行布局（标题行 + 工具行）
- [x] 统计卡"全部作品"label 换行 → nowrap + 小屏内边距收紧
- [x] 触控目标：状态筛选 24px→36px、分类 tab 32px→38px、底栏 item 4→6px 垂直内边距、主题按钮 44px
- [x] 验证：build 通过 + 375px 前后对比截图
- **Status:** complete

## 第六轮补充: count 型产品决策已关闭 ✅ (2026-09-27)
- 用户确认 count 型保持手动标记，不加字段不加规则；决策已记录到 findings.md
- 此条从遗留事项中移除——后续轮次不再重复处理
