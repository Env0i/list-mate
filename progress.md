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
