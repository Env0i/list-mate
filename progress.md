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
