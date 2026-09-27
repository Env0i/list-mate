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

## 第七轮: 详情页作品历史（时间线 UI）✅ (2026-09-27)

- [x] 新增 utils/timeline.js：actionLabels/actionIcons/formatValue/timeAgo 共享，Stats 操作记录换用（消除两份漂移）
- [x] WorkDetail 新增"历史"卡：品类色边框，展示该作品全部操作（添加/状态/评分/进度/评价），最多 20 条 + 总数
- [x] 修复 timeAgo 时区 bug：后端 UTC 无时区串按本地解析导致偏差 8 小时（Stats 页同病），补 Z 修正
- [x] 修复 formatValue 反序列化：时间线 old/new 是 json.dumps 串，原样显示成 "watching" → 带引号枚举；
      先 unjson 再映射中文标签（Stats 页同病）
- [x] 验证：build 通过；浏览器实测历史渲染（"状态变更 在看 → 暂停 1分钟前"），变更即时入历史
- **Status:** complete

## 第八轮: 导出完整性核对 + 历史功能回归 ✅ (2026-09-27)

### 导出完整性（库内 vs 导出逐项比对）
- [x] JSON 补缺失字段：is_free、purchase_date、bangumi_id、auto_completed；GP 补 auto_completed、sort_order
- [x] CSV 补"购买时间""免费"列；0 值不再被 `or ""` 吞掉（None 才写空）；整数值浮点格式化为整数（17.0→17）
- [x] CSV 加 UTF-8 BOM（无 BOM 时 Excel 打开中文乱码）
- [x] 比对结果：PASS——JSON 全字段=detail 接口、GP 全字段一致、CSV 边界值（0 进度/0 评分/0 优先度）正确落列
- **Status:** complete

### 历史功能回归
- [x] 详情页历史卡渲染正常（"＋添加 回归检查-动画 0分钟前"）
- [x] Stats 操作记录正常（共享工具改动后无回归，时区修复在聚合页同样生效）
- [x] api_full_test.py 77/77
- **Status:** complete

## 第九轮: deploy.py 部署流程 dry-run 体检 ✅ (2026-09-27，未实际部署)

- [x] 上传清单模拟核对：**发现 list_mate.db-shm/-wal 会被上传**（ignore 只有精确名 list_mate.db）——本地未 checkpoint 的事务数据可能污染服务器 DB，已补忽略
- [x] fix_game_status.py（一次性清洗脚本）移出上传清单，防止服务器误运行
- [x] 健康检查 bug 修复：原在本地执行却打服务器回环地址 127.0.0.1:8002（永远不通，白等 60s），改走 Nginx 公网链路 HOST:8081（nginx→uvicorn 全验证）
- [x] dist 上传前清空远端旧产物（vite hash 文件名无限累积）
- [x] 本机安装 paramiko（部署依赖，此前缺失会直接 ImportError）
- [x] 验证：py_compile 通过、上传清单 31 个文件无敏感/冗余残留、vite build 通过（未实际连接服务器）
- **Status:** complete

## 第十轮: 数据库一键备份 ✅ (2026-09-27)

- [x] 新增 GET /api/backup：SQLite 在线 backup API 生成一致性快照（WAL 模式下直接拷 .db 会丢未 checkpoint 数据），响应后自动清理临时文件
- [x] 覆盖 JSON/CSV 导出不包含的数据：时间线、附件、封面 BLOB——这才是可完整还原的备份
- [x] Stats 页导出区新增"备份"按钮（JSON/CSV/备份三个入口并排）
- [x] api_full_test.py 新增用例：备份为合法 SQLite 文件 + 含 timeline_entries 表
- [x] 验证：78 条用例全通过；浏览器实测下载事件真实触发
- **Status:** complete

## 第十一轮: 样式漂移清零 ✅ (2026-09-27)

- [x] MobileNav FAB 渐变 → style.css 新增 --primary-soft/--primary-gradient 令牌
- [x] Tags.vue .err/.act-del:hover 危险色 #ef4444 → var(--s-dropped)（第 18 行色板数组里的是用户可选色，保留）
- [x] WorkDetail stamp-in 关键帧分叉归一（删除本地 2deg 版本，统一全局 3deg；元素静止角 2deg 不变）
- [x] 验证：build 通过；375px 标签页/FAB 截图无回归
- **Status:** complete

## 第十二轮: 从备份还原（备份闭环）✅ (2026-09-27)

- [x] POST /api/restore：上传 .db → 校验 SQLite 文件头 + 必需表结构 → 当前库自动快照到
      backups/pre-restore-<时间戳>.db → 替换库文件 + 清理 WAL/SHM + engine.dispose
- [x] Stats 页"还原"按钮：file input + confirm 二次确认（提示自动备份兜底）+ 还原中禁用态
- [x] 测试：还原闭环（备份→还原→数据不丢）+ 非法文件 400；78 条用例全绿
- [x] 用户确认暂不真实部署，部署留给用户自行执行
- **Status:** complete

## 第十四轮: 列表卡片快捷进度 +1 ✅ (2026-09-27)

- [x] WorkCardGrid EXP 条右端新增 +1 圆钮（步长：动漫 +1 集/小说 +1 章/漫画 +1 卷/游戏 +5%）
- [x] 到达 total 时后端自动完成规则联动，卡片状态戳/进度条即时同步（就地更新不刷新页面）
- [x] stopPropagation 防止误触跳转详情页；busy 状态防连点
- [x] 验证：build 通过；浏览器实测 10/12 → 11 → 12/12(100%) 状态戳自动变"看完"
- **Status:** complete

## 第十五轮: ±1 配套（对称回退 + 游戏分流修复）✅ (2026-09-27)

- [x] 修 R14 遗留 bug：游戏卡 +1 错改 Work.progress_value（游戏进度实际在 GP 上）——
      WorkListItem/works.py 补 game_profile_id，卡片 ±1 按品类分流到正确对象
- [x] 对称 −1 按钮（进度 >0 时显示）：误触/回退；auto_completed 状态随进度回退
      自动恢复"进行中"（Work→watching、GP→playing）
- [x] 过程修正：游戏分支进度基数曾误用 Work 的空值（GP 被写成 5），当场改为
      game_progress_value 并恢复数据
- [x] 验证：四链路全通——动画 +1→12/12 自动"看完"、−1→回退"在看"、
      游戏 +1→GP 95、−1→GP 90
- **Status:** complete

## 第十六轮: 统计页"本周活跃"维度 ✅ (2026-09-27)

- [x] 全量回归先行：R15 后端改动（列表响应补 game_profile_id）确认无回归（79/79）
- [x] /api/stats 新增 week_activity：最近 7 天时间线操作数 + 有更新的作品数（UTC 口径与库一致）
- [x] Stats 概览新增第四张摘要卡"本周活跃"（主色左边框）；480px 下四卡自动两行
- [x] 测试断言补 week_activity 结构校验；79/79 全绿
- [x] 验证：build 通过；截图确认卡片渲染（清理数据后归零语义正确）
- **Status:** complete

## 第十七轮: 主题三态设置 + 移动端入口重做 ✅ (2026-09-27，用户明确指派)

- [x] theme.js 重构为三态模式（跟随系统/白天/黑夜），**默认白天**（用户要求，原为跟随系统）；
      跟随系统下监听 matchMedia 变化实时生效；兼容旧存储值
- [x] ThemeToggle 重构为弹出层组件：三选项 + 当前态高亮；桌面 TopBar 与移动端共用
- [x] 移动端入口移出底栏（用户明确要求）：改为右上角固定悬浮按钮（App 级，全页面可用），
      main 顶部留白防遮挡；底栏回归 5 项
- [x] 验证：桌面/移动端弹出层截图、跟随系统存储与解析、清存储后默认白天、79 测试与 build 通过
- **Status:** complete

## 第十八轮: 时间线按天分组 + 空状态引导 ✅ (2026-09-27)

- [x] utils/timeline.js 加 dayLabel（今天/昨天/M月D日，跨年补年份）与 dateOf 共用解析
- [x] Stats 操作记录、WorkDetail 历史两处按天分组渲染（同一天条目归组，日期分隔头）
- [x] WorkList 空状态加"去搜索添加/手动添加"引导按钮
- [x] 验证：build 通过；截图确认详情页历史"今天/昨天"分组（时区修复后归组正确）、
      Stats 操作记录分组、空状态按钮渲染
- **Status:** complete

## 第十九轮: README 与使用流程盘点 ✅ (2026-09-27)

- [x] README 更新：端口 8000→8001、功能特性补六项新功能（备份还原/主题三态/±1/历史/分组/本周活跃）、
      API 概览补 export/backup/restore、新增"数据管理"使用说明章节（含还原自动快照与重启说明）、
      项目状态标注 v1.0.0
- [x] 还原成功 message 补"重启后端服务后完全生效"引导（toast 直达用户）
- [x] 评估卡片长按微调菜单：**结论不做**——与详情页编辑功能重复，移动端长按无可供性暗示，
      ±1/−1 已覆盖高频微调；结论记录于 progress.md
- [x] 验证：api_full_test 79/79 全绿
- **Status:** complete
