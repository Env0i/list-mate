# Progress Log — list-mate

## Session: 2026-05-18

### Phase 0: 需求梳理与设计
- **Status:** complete
- **Actions taken:**
  - 审阅了已有 PRD / 机会评估 / 路线图
  - 识别 PRD 盲点：多 Profile 模型、附件机制、封面缓存、自动完成逻辑、搜索降级
  - 评估技术选型：单 Vue 3 响应式前端，不做 Uni-app 原生编译
  - 确定迭代计划：Iter 1 核心记录，Iter 2 标签，Iter 3 统计时间线，Iter 4 扩展
  - 编写 design.md 设计文档
- **Files created/modified:**
  - docs/design.md (created)

### Phase 1: 后端项目初始化 + 数据模型
- **Status:** complete
- **Actions taken:**
  - 创建 backend/app/{models, schemas, routers} 目录结构
  - 编写 database.py（SQLAlchemy engine + SessionLocal + Base + init_db）
  - 编写 config.py（数据库路径 + Bangumi API 地址）
  - 编写 Work / Profile / Tag / WorkTag 四个 ORM 模型（含枚举、关系、级联删除）
  - 编写 main.py 入口（lifespan init_db + CORS + 路由注册）
  - 编写空白路由文件（works/bangumi/profiles/tags）
  - 验证：4 张表全部正确创建、uvicorn 正常启动
- **Files created/modified:**
  - backend/requirements.txt (created)
  - backend/run.py (created)
  - backend/app/__init__.py (created)
  - backend/app/config.py (created)
  - backend/app/database.py (created)
  - backend/app/main.py (created)
  - backend/app/models/__init__.py (created)
  - backend/app/models/work.py (created)
  - backend/app/models/profile.py (created)
  - backend/app/models/tag.py (created)
  - backend/app/schemas/__init__.py (created)
  - backend/app/routers/__init__.py (created)
  - backend/app/routers/works.py (created)
  - backend/app/routers/bangumi.py (created)
  - backend/app/routers/profiles.py (created)
  - backend/app/routers/tags.py (created)

### Phase 2: 后端 API — Works + Bangumi
- **Status:** complete
- **Actions taken:**
  - 添加 get_db() 依赖到 database.py
  - 创建 Pydantic schemas（WorkCreate/Update/Response, ProfileResponse, TagResponse, BangumiSearch）
  - 实现 Work CRUD（列表+筛选分页+增删改查+封面对接点）
  - 实现 Bangumi 搜索代理（search + subject detail）
  - 封面自动缓存：创建/更新作品时自动下载 cover_url 存 BLOB
  - 验证：9 个测试全部通过（CRUD + 筛选 + 404 + 级联删除）
- **Files created/modified:**
  - backend/app/database.py (modified — add get_db)
  - backend/app/schemas/__init__.py (created)
  - backend/app/schemas/work.py (created)
  - backend/app/schemas/profile.py (created)
  - backend/app/schemas/tag.py (created)
  - backend/app/schemas/bangumi.py (created)
  - backend/app/routers/works.py (rewritten — full CRUD)
  - backend/app/routers/bangumi.py (rewritten — search proxy)

## Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| List empty | GET /api/works | total=0 | total=0 | PASS |
| Create work | POST /api/works | 201 + auto profile | 201 + profile "默认" wish | PASS |
| List 1 item | GET /api/works | total=1 | total=1 | PASS |
| Get detail | GET /api/works/{id} | 200 | 200 | PASS |
| Update | PUT /api/works/{id} | title changed | title changed | PASS |
| Category filter | ?category=game | total=0 | total=0 | PASS |
| Status filter | ?status=wish | total=1 | total=1 | PASS |
| 404 | GET /api/works/999 | 404 | 404 | PASS |
| Delete | DELETE /api/works/{id} | 204 | 204 | PASS |

## Error Log
| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|

## 5-Question Reboot Check
| Question | Answer |
|----------|--------|
| Where am I? | Phase 0 (complete) — ready for Phase 1 |
| Where am I going? | Phase 1-8: backend → frontend → deploy |
| What's the goal? | Iter 1 核心记录跑通 |
| What have I learned? | See findings.md |
| What have I done? | PRD review, design decisions, design.md written |

## 2026-09-27 自主接管第一轮：P0 修复

### 修复内容
1. **级联删除 FK 500（后端）**
   - 复现：DELETE /works/{id} 与带时间线的 DELETE /game-profiles/{id} 均 500，日志 `sqlite3.IntegrityError: FOREIGN KEY constraint failed`（passive_deletes=True 信任数据库级联，但 timeline FK 无 ondelete=CASCADE，且 PRAGMA foreign_keys=ON）
   - 修复：work.py 移除 passive_deletes；game_profiles.py 删除时先清时间线
2. **前端空值 422**
   - 复现：Add 页不选状态提交必 422（schema validator 拒绝 ""，validator 后于 Add 页引入）；编辑弹窗清空状态/总量同理
   - 修复：utils/payload.js emptyToNull + 三视图接入；附带修 external_url 幽灵字段、游戏状态清空防护
3. **测试**：api_full_test.py 77/77，报告已刷新；测试产生的数据已清理（库恢复为空）

### 遗留事项
- api_full_test.py 的 "Get work by valid ID" 依赖库中已有作品，空库首跑会挂 1 条（建议自建数据）
- dev server 仍在后台运行（后端 8001 / 前端 5173）
- P1 待办：状态色 4 份复制收敛到 --s-* 变量、死组件 Sidebar.vue/StatusBadge.vue 删除、Bangumi type 映射后端修正、统计页补游戏评分、rating 范围校验、page_size 100 静默截断

## 2026-09-27 自主接管第二轮：P1 常量收敛 + 数据逻辑

### 决策记录
- **Bangumi 漫画落 novel 分类：评估后决定不做自动识别**。书类型（type 1）下漫画/小说在 v0 搜索结果无可靠区分字段，用 platform 关键词猜测属于脆弱启发式；确认弹窗中分类可手动选择，已有兜底。仅修正了后端注释错误。
- **rating 范围校验只加在写入模型**：第一版误加到 WorkListItem/GameProfileResponse 响应模型，存量越界数据直接把列表接口打成 500（当场踩到），已退回——响应模型不拦存量，写入模型管增量。

### 验证
- api_full_test.py 77/77；vite build 通过；浏览器实测首页卡片与统计页渲染（截图核对渐变/状态色/游戏进度条 45%/游戏评分入分布）
- 测试数据已清理（works/tags 归零）

### 遗留事项
- 暗色主题（变量体系已就绪，加 .dark 覆盖）+ 偏好持久化（筛选状态/排序）→ 个性化两件套
- 断点 6 种并存待收敛到 768/480 两档
- GameProfile count 型自动完成仍无 total 字段支撑（产品语义待定，二刷"次数"无天然上限）

## 2026-09-27 自主接管第三轮：暗色主题 + 偏好持久化

### 实现
- 暗色主题走纯 CSS 变量覆盖（:root[data-theme='dark']），延续"暖纸→暖黑"色温，饱和色不动；color-scheme: dark 让原生控件跟随
- 主题初始化在 main.js 挂载前执行，避免暗色用户首帧闪白
- 排序为客户端排序（列表本就一次拉 500 条内存过滤），null 评分/优先度沉底；'updated' 沿用后端 updated_at desc

### 验证
- 浏览器全链路：切换主题 → localStorage 写入 → 截图核对亮/暗首页+详情页；评分排序断言；刷新恢复主题/排序/筛选
- 测试后已清理：测试作品删除、浏览器 localStorage 偏好还原

### 遗留事项
- 断点 6 种并存待收敛（768/480 两档）——涉及多文件样式，单独一轮
- 部分组件仍有零星硬编码色（卡片白边为设计母题，保留）；如发现个别暗色违和处随用随修

## 2026-09-27 自主接管第四轮：断点收敛

- 非标准断点 3 处归档到 767 主移动断点；全仓 @media 现在只有 767/768/480 三档 + 网格列数阶梯（640/900/960/1200，合法保留）
- 740px 宽度浏览器实测编辑弹窗单列布局正常；测试数据已清理

## 2026-09-27 自主接管第五轮：搜索回填 + 类型过滤存量 bug

### 重要发现
- **Bangumi 类型过滤从未生效**：v0 POST /v0/search/subjects 的过滤参数是 filter.type 数组，
  裸 type 字段被静默忽略。测试套件 "Bangumi search with type filter" 只断言 200+有结果、
  没断言过滤正确性，所以一直绿——教训：过滤类功能的测试必须断言"过滤后的特征"，不能只断言"有响应"。

### 实现
- 动画搜索结果自动回填总集数（total_episodes 与 ep 单位一致）；漫画/小说因单位是卷/章不回填，
  避免话数错当卷数；回填失败静默降级
- 测试脚本 "Get work by valid ID" 空库自建数据，消除对库内已有数据的环境依赖（此前两轮反复被它绊）

### 验证
- 裸 API 对照实验确认修复；浏览器全链路（番剧过滤 → 选中 → 总量 26 回填）；
  api_full_test.py 全部通过；测试数据已清理

## 2026-09-27 自主接管第六轮：移动端体验打磨

### 修复
- 首页 375px 下标题"收藏"被挤压竖排（hd-right 固定宽度挤占）→ 移动端标题与工具行分两行
- 统计页三张摘要卡在 375px 下 label 换行（"全部作/品"）→ label nowrap + 小屏 padding 收紧
- 触控目标：st-filter 24px→36px、cat-tab 32px→38px（移动端）、底栏 item 垂直内边距 4→6px、主题按钮 44px；全部加 touch-action: manipulation 消除 300ms 延迟
- 一次样式补丁把 @media 插进了 .st-filter 规则中间导致括号不配对 build 失败，当场发现修正

### 验证
- build 通过；375px 修复前后截图对比（首页标题一行、统计卡一行）

## 2026-09-27 自主接管第六轮补充：count 型产品决策

- 用户三选一确认：count 型（二周目等）保持手动标记，percent 型自动完成规则不变
- 决策记录到 findings.md「产品决策」节；task_plan.md 遗留事项正式关闭此条
- 代码零改动（现状即所需行为），仅文档与决策记录提交

## 2026-09-27 自主接管第七轮：详情页作品历史

### 实现
- WorkDetail 新增"历史"区块（timelineApi work_id 过滤，后端现成支持），数据一直有记录但此前只能去统计页看聚合
- 时间线展示逻辑抽到 utils/timeline.js 共享，Stats 与详情页单一来源

### 顺带修复的两个存量显示 bug（都在 Stats 页存在已久）
- timeAgo 时区：后端 UTC 无时区串被 new Date 按本地解析，东八区全部偏差 8 小时 → 检测无时区标记时补 Z
- formatValue 反序列化：状态变更显示原始 "watching" → 带引号枚举而非"在看 → 暂停" → unjson 后映射中文标签

### 验证
- build 通过；浏览器实测：历史渲染（"状态变更 在看 → 暂停 1分钟前"、"添加 葬送的芙莉莲 16分钟前"）、API 变更即时入历史
- 测试数据已清理

## 2026-09-27 自主接管第八轮：导出完整性 + 历史回归

### 方法
- 造全字段+边界值数据（progress=0、rating=0、priority=0、is_free、多配置游戏、标签关联），
  脚本逐项断言"导出内容 == detail 接口返回"（JSON 20 字段 + GP 8 字段 + 标签名单；CSV 表头列与边界值落列）
- 甄别比对脚本自身误报 2 条（列表接口本就不含 review/external_links；GP 按 name 匹配修正）

### 修复
- JSON 导出缺 is_free/purchase_date/bangumi_id/auto_completed（备份还原会丢数据）；GP 缺 auto_completed/sort_order
- CSV 缺购买时间/免费列；`or ""` 把合法 0 吞成空（进度 0、评分 0、优先度 0）；整数值浮点格式化
- CSV 无 BOM 导致 Excel 中文乱码

### 教训
- 导出功能的"正确性"以前只被断言 200+有内容；完整性必须用"逐字段对比数据源"的脚本验证

## 2026-09-27 自主接管第九轮：部署脚本 dry-run 体检

### 实锤问题（全部修复）
1. WAL/SHM 入上传清单——ignore 精确匹配漏了 -shm/-wal 后缀文件；服务器 DB 有被本地事务数据污染的风险
2. 健康检查永远失败——本地脚本打 127.0.0.1:8002（那是服务器的回环地址）；改走公网 Nginx 链路
3. paramiko 本机未安装——部署脚本第一步就 ImportError
4. dist 旧产物无限累积——上传前清空远端 dist
5. fix_game_status.py 混入上传清单——一次性清洗脚本不应部署

### 方法
- 未连接服务器：_upload_dir 的 walk+ignore 逻辑本地模拟出真实上传清单逐项核对 + py_compile + 静态审查
- 注意：下次实际部署时健康检查将首次真正生效，若服务器未起会有 60s 重试后告警（预期行为）

## 2026-09-27 自主接管第十轮：数据库一键备份

### 实现
- /api/backup 用 SQLite 在线 backup API（tempfile 快照 + BackgroundTask 清理），
  解决 WAL 模式下"拷 db 文件丢数据"和"JSON 导出不完整"两层问题
- 前端入口复用导出按钮样式

### 过程记录
- 给测试脚本写入 b"...\x00" 字面量时踩了三层转义坑（heredoc → patch 脚本 → 源文件），
  最终以 bytes([92]) 构造反斜杠绕开；该环境怪癖已记入长期记忆（heredoc 会折叠 \ 为 \）

## 2026-09-27 自主接管第十一轮：样式漂移清零

- 审计点名的小漂移全部处理完毕；至此 style.css 设计令牌是唯一的颜色来源（色板可选色除外）
- FAB 渐变抽象为 --primary-gradient 令牌，暗色主题未来可直接覆盖
- Tags 页色板数组中的 #ef4444 是用户可选色不属漂移，保留

## 2026-09-27 自主接管第十二轮：从备份还原

### 实现
- 还原采用"先快照后覆盖"策略：还原前当前库经在线 backup API 快照到服务器
  backups/ 目录（pre-restore-时间戳.db），覆盖式还原永远有回退路径
- engine.dispose() 释放连接池，替换文件后新请求即读新库；清理 WAL/SHM 残留
- 用户确认暂不部署：十轮成果留本地，python deploy.py 由用户自行执行

### 验证
- 测试闭环：备份→还原→数据不丢、非 SQLite 文件 400；build 通过；还原按钮挂载与禁用态截图确认
- IAB 不支持 file chooser 交互，UI 层验证到入口挂载为止（API 层由测试覆盖）

## 2026-09-27 第十三轮：v1.0.0 阶段性收口

- 导出/备份文件名带日期（zace-export-20260927.json / zace-backup-20260927.db），多次导出不互相覆盖；顺带修掉文件名中的旧品牌残留（list-mate→zace）
- 全量回归：api_full_test 78/78、vite build 通过、测试数据清零
- 打 annotated tag v1.0.0：十二轮迭代的干净还原点（核心功能完整 + 备份/还原闭环 + 24 处审计问题修复）
- 部署状态：成果在本地 master，用户确认自行执行 python deploy.py

## 2026-09-27 自主接管第十四轮：卡片快捷进度 +1

### 动机
追番更新一集是本应用最高频操作，原流程"进详情→编辑→改数字→保存"六步；
现在列表卡片 EXP 条上一个 +1 按钮直接完成，且到达 total 时自动完成规则联动、
状态戳即时变化——高频摩擦点消除。

### 实现
- WorkCardGrid exp-wrap 内加 28px 圆钮；步长按品类（ep/chapter/volume +1、game +5%）
- 就地更新 props.work 的 progress_value/status/auto_completed，父列表无需刷新
- progress 上限钳制在 total（有 total 时），防误触溢出

### 过程记录
- IAB 合成点击（locator.click/cua.click）对该按钮不触发 Vue 事件（elementFromPoint
  证明无遮挡、原生 el.click() 正常）——判定为环境合成事件怪癖，功能本身无问题；
  已补入环境怪癖记忆

## 2026-09-27 自主接管第十五轮：±1 回退与游戏分流

### 发现并修复 R14 遗留 bug
游戏卡的 +1 调的是 worksApi.update（改 Work.progress_value），但游戏进度挂在
GameProfile 上且列表响应不含 GP id——表现为"游戏卡点了没反应"。修复：列表响应
补 game_profile_id，卡片 ±1 按品类分流（game→gameProfilesApi.update(GP id)）。

### 设计决策
- 对称 −1 按钮代替撤销 toast（无需改造 toast 组件，可发现性更好）
- auto_completed 状态随进度回退自动恢复"进行中"（Work→watching、GP→playing），
  避免"11/12 但状态已完成"的不协调；非自动完成的状态不由 ±1 触碰

### 验证
四条链路浏览器实测全通（动画 +1 自动完成、−1 回退、游戏 GP +1/−1 分流）；
过程中游戏分支基数取错（GP 被写成 5）当场发现修正并恢复数据。

## 2026-09-27 自主接管第十六轮：本周活跃维度

- 指派先行的全量回归通过（R15 后端改动无回归）
- week_activity 口径：operations=最近 7 天时间线条数（含系统触发的自动完成），
  works_updated=最近 7 天有更新的作品数；时间字段均为 UTC，与 utcnow 可比
- 摘要卡从三张扩到四张，小屏（480px）自动两行布局

## 2026-09-27 自主接管第十七轮：主题三态 + 移动端入口重做（用户指派）

### 用户明确任务
移动端主题切换不放底栏 → 先误判要做"我的"页（用户纠正：没有我的页，放页面右上角）；
三态选项含"跟随系统"，默认白天。

### 实现
- theme.js 三态模型：stored ∈ system/light/dark，null 默认 light；
  resolveTheme 将 system 展开为 matchMedia 结果，并监听系统偏好变化实时应用
- ThemeToggle 改为弹出层组件（floating 变体固定移动端右上角；桌面仍由 TopBar 承载）；
  图标按解析主题切换（太阳/月亮/半填充圆）
- 移动端 main 顶部留白 48px 防遮挡；底栏移除主题按钮

### 过程记录
- 桌面按钮初版误做成两态快捷切换（跟随系统无入口），自查后统一为三选弹出层
- heredoc 反斜杠折叠 + patch 断言失败连环坑再次出现，改用行号删除/逐条 replace 规避

## 2026-09-27 补充（用户纠错）：主题按钮与"收藏"同行

- 用户指出悬浮在屏幕右上角与内容脱节——改为页内布局：主题按钮移入
  WorkList 页头行（与"收藏"标题同行右侧，移动端显示/桌面隐藏用 TopBar）
- App 级悬浮按钮与 main 顶部留白移除
- 375px 截图验证：按钮与标题同行、弹出层正常

## 2026-09-27 自主接管第十八轮：时间线分组 + 空状态引导

- dayLabel/timeAgo 共用 dateOf 时区修正，消除重复
- 造数据用 SQL UPDATE 把测试记录的 created_at 挪到昨天（仅测试数据，未触碰用户数据），
  验证跨天归组正确（时区修复后无错组）

## 2026-09-27 自主接管第十九轮：README 与使用流程盘点

### 修复
- README 七处更新（端口/新功能/API 概览/数据管理章节/项目状态）
- 还原成功 message 补重启引导——此前只说"还原成功"不提重启，用户会以为没生效

### 评估结论：卡片长按微调菜单不做
理由：±1/−1 已覆盖高频微调；长按在移动端无可供性暗示（用户不知道能长按）；
桌面无对应交互；自定义进度的完整入口已在详情页编辑对话框。
结论与理由记录在案，后续不再作为候选。

## 2026-09-27 自主接管第二十轮：部署前验收走查

### 走查矩阵
桌面 1280 亮/暗 + 移动 375 暗，遍历收藏/详情/统计/添加/搜索；
暗色统计页首帧全黑为路由过渡帧误报（DOM 探针确认渲染完整）。

### 修复（3 处，含 1 个深层 bug）
1. 游戏卡 EXP 百分比：GP percent 进度被按 Work.total 折算 → fill 0%、label 无 %。
   percent 型自带分母 100，直接取值。R14 引入 ±1 时未波及（那时 GP 显示走旧逻辑），
   实为更早的显示缺陷
2. 游戏无进度时 EXP 条整体隐藏（±1 不可达）→ game 卡恒显示，null 按 0%
3. 搜索框聚焦 white 底 → 令牌化

### 保留项（非问题）
Add/WorkDetail 的 background: white 是 toggle 开关圆点；详情页封面白边是卡牌母题。

## 2026-09-27 自主接管第二十一轮：GP 详情 ±1 即时化

- 与 R15 的列表卡 ±1 行为对齐：GP 详情页步进按钮从"改本地等保存"改为即时 API 提交
- 步长按 progress_type（percent +5 / count +1 / none 禁用）；originalStatus 随响应同步，
  避免自动完成改状态后用户保存时误提交旧状态
- 过程插曲：造数据时 GP progress_type 默认为 none（_guess_progress_type 对"本体"返回 NONE）
  导致按钮按设计隐藏——修正测试数据为 percent 后重测
## 2026-09-27 自主接管第二十二轮：搜索信息密度 + 实时筛选

- 搜索结果卡补类型徽章（rt-2 番剧橙 / rt-4 游戏橙等品类色）与年份徽章——
  同名多版本条目（如命运石之门 TV/OVA/游戏/广播剧）可一眼区分
- 类型切换 watch 触发自动重搜（有关键词时），消除"切类型还要再点搜索"的摩擦
- 外部 Bangumi API 偶发瞬时失败（首次搜索 0 条，重搜即成功）——既有行为，未处理
## 2026-09-27 自主接管第二十三轮：搜索竞态守卫（用户指派）

用户问：切类型自动重搜后快速连点会不会重复/网络异常怎么办。设计答复与实现：
- 请求序号（seq）守卫——并发请求安全，只有最新一次的结果会渲染（实测连切
  书籍→音乐→动画→游戏，稳定收敛为游戏类型结果）
- 类型按钮不禁用（自由切换），加载中已有"搜索中..."指示与按钮禁用
- 错误分支：横幅"搜索失败，请重试"且不再误示"没有结果"（empty 条件排除 error）
- 验证：连切实测 + XHR 劫持模拟网络异常（fetch 劫持无效——前端 axios 走 XHR）+ 恢复复测
## 2026-09-27 自主接管第二十四轮：月度活跃接口 + 历史分页

- monthly_activity 为方向三（统计页月度趋势模块）铺路——前端渲染等设计稿到位后接
- 过程教训：heredoc 补丁两次静默未落盘（打印 ok 但 git 无 diff）——改用 Edit 工具
  分步编辑并 grep 验证落盘，绕开该环境 heredoc 不可靠的问题
## 2026-09-27 自主接管第二十五轮：月度活跃趋势前端

- 简版视觉（复用条形卡语言），设计方向三到位后可整体替换为设计稿版本
- 补零月份条宽 0%（空 rail）——"哪些月没在记录"本身就是信息
## 2026-09-27 自主接管第二十六轮：历史卡回到顶部

- 加载更多把用户带到列表深处，回顶是自然配套；按钮放历史卡头部（比浮动按钮克制）
- 显示阈值 = 已加载数 ≥ 一页（20 条），单页用户看不到多余按钮
## 2026-09-28 UI 进化 S1：令牌补充 / 字体 / 印章对比度 / 触控目标 / 五个共享组件

按 zace-implementation-handoff.md §6 落地第一阶段（S1），四项前置决策已拍板：
Q1 +1集带5秒撤销、Q2 加入想看直接调 worksApi.create、Q3 触控目标 44px、Q4 统计口径后端加 monthly_added（均在后续阶段落地）。

- 令牌：style.css 新增 --cc-on（anime/comic/game 深墨、novel 白，双主题固定以过 4.5:1）、
  --font-mono、全局 :focus-visible 兜底、.sr-only；CategoryBadge 改品类实底+--cc-on 文字
- 字体：DM Sans 400/500/700 + JetBrains Mono 400/700 拉丁子集自托管至 public/fonts/（含 OFL 许可证），
  @font-face 挂入 style.css（unicode-range 限定拉丁，中文走系统字体）
- 印章：新建 StatusStamp.vue（纸底+状态色描边+圆点+正文色文字，替换暂停黄白字 1.8:1 的旧样式），
  WorkCardGrid 与 WorkDetail 接入；卡面数字 total-tag 提级 --text-secondary（2.6→7.1:1）
- 五个共享组件：StatusStamp / StateBlock / SkeletonBlock / BaseModal / TimelineList（components/common/）
  TimelineList 统一 Stats 与 WorkDetail 两套时间线皮肤；BaseModal 换 WorkDetail 编辑模态壳
  （Esc/焦点圈定/焦点还原/移动端抽屉）；StateBlock+SkeletonBlock 接入 WorkList loading/empty
- 触控目标：TopBar/ThemeToggle/WorkCardGrid 及全部视图交互控件补 @media (pointer: coarse) ≥44px
- 其他：暗色 logo 补 hue-rotate(180deg)（四角品类色还原）
- 验证：npm run build 通过；浏览器实测亮/暗 × 1440/375（收藏/详情/统计/底栏/主题菜单）；
  四态：空（StateBlock）/加载（30 骨架块+aria-busy+读屏文案）/满载逐个打开，错误态 UI 留 S2；
  编辑模态焦点进出与 Esc 闭环实测通过；对比度实测徽章 4.68:1、印章正文色文字；
  字体确认加载（document.fonts）。环境怪癖：IAB 渲染器路由过渡不触发 transitionend，
  SPA 换页视图冻结（真实浏览器不受影响）——验收改用整页加载
## 2026-09-28 UI 进化 S2：收藏页/标签页/游戏配置页按原型改造 + 四态 + 撤销

用户确认按清单开工（卡上快捷按钮移除、标签删除撤销走重建+回贴）。

- 新组件：SegmentedControl（分段+方向键+计数）、FilterChip（筛选胶囊，只读摘要不再用胶囊形）、
  GameProfileForm（游戏配置共用表单，新建/详情两页复用）、ProgressBar 按原型 .exp 重做
  （role=progressbar + aria-valuenow，overlay 形态压封面底边）
- 收藏页：页头改「我的卡册」+纯文字摘要；新增「继续追」横轨（在看/在玩+EXP+进度文本+「+1」按钮，
  游戏 +5%）；+1 带 5 秒撤销（乐观更新+反向 PUT 回退，Q1 决策）；吸顶工具栏（品类/视图分段+搜索+排序）；
  状态 chips 固定顺序带计数、空项置灰不再消失；「全部」品类用合并语义集（进行中=在看/在玩）；
  新增列表视图（行式布局）；?tag= 深链支持；两种空态区分（无作品 vs 筛选无结果+清空筛选）；
  /works 失败补 StateBlock error+重试（原先只有 toast）
- WorkCardGrid 重做为原型三环框卡牌：品类色环+角标右上（CategoryBadge）+印章左下（StatusStamp）+
  EXP 条压封面底边+全息流光+卡面数字（进度/评分，--text-secondary）；卡上 ±1 按钮移除（快捷进度归横轨）
- 标签页：新建面板改 7 色令牌色板（旧 hex 数据仍兼容）；贴纸卡（色带+圆点+使用数+封面缩略条≤6）；
  删除改 BaseModal 确认（提示 N 部作品会摘掉）+ 5 秒撤销（重建标签新 id+按快照批量回贴 tag_ids）；
  四态：骨架/失败（禁用新建）/**空集**/满载
- 游戏配置：GameProfileDetail/New 共用 GameProfileForm；面包屑+配置页头+双栏（表单+吸顶侧栏其他配置）；
  进度方式三卡单选补右上勾（评审 R1）；状态选择带状态色点；模组 chips+粘贴批量添加 BaseModal+
  移除撤销；附件改拖放区；删除配置改 BaseModal 确认；保存条常驻（未保存/已保存）+beforeunload 保护；
  四态：骨架/读取失败（重试）/非游戏品类（只有游戏可以添加配置）/满载
- toast 扩展 action 按钮（撤销），App.vue 渲染；默认 5s（带动作时）
- 验证：build 通过；浏览器实测亮/暗 × 1440/375（收藏页/列表视图/标签页/GP 详情/新建）；
  +1 撤销闭环（12→13→撤销→12）；删标签撤销闭环（删除→toast→撤销→恢复且回贴 1 部作品）；
  模组粘贴弹窗（2 个 chips+脏状态）；非游戏错误态；beforeunload 脏保护实际触发（导航被拦）；
  修 GP 详情 dirty-on-load bug（load 赋值误触发深度 watch）
- 无后端改动；既有怪癖记录：GET /works/{id} 与 PUT 响应缺 tag_ids 字段（列表接口正常）——S2 未受影响，
  S4 详情页改造时如需单作品标签再补

## UI 进化 S4-S6（2026-10-23，commit 28277ff / 3ac3be2 / d1f5073）

- S4 详情页：BangumiZone 六分区（CommunityCompare S/A/B/C 分桶+百分位、BangumiInfo 全量
  infobox+tags、EpisodeGrid 东八区今日/SP/OP/ED、CastRail、RelationRail Q2 加入想看、
  StaffList 关键职位高亮）、DangerZone、WorkEditModal 迁出；修 3 缺陷（STATUS_LABELS
  崩溃、create 缺 progress_unit 422、入册缺 status=wish）；bangumi_cache 图片移出仓库并
  gitignore
- S5 添加页壳：DiscoverTab（今日放送 22 卡/高分榜三类型）/SearchTab/ManualTab +
  BangumiCreateModal 共用；Settings 页（主题/数据管理/关于）；AppFooter；导航 D3；
  Search.vue 删除；/search 重定向
- S6 统计：monthly_added 稀疏聚合 + 每月新增 12 月柱图（年份切换）；时间线类型审计收口
- 验收方式：ZCode IAB 不可用（node REPL 缺失），全程 Chrome headless CDP（Runtime.evaluate/
  captureScreenshot/Fetch 拦截做局部错误态）；回归 79/79；§5 替换点 grep 清零
- 环境事故记录：项目被移至 D:/Projects/01-active/list-mate（旧路径空壳遗留 .zcode 脚本
  可删）；交接文档与原型随 Open Design 数据丢失（findings #9）；git push 需绕过失效本地
  代理（-c http.proxy=）
