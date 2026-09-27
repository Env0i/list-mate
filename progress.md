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
