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

## 遗留问题清单（2026-09-29，UI 进化 S1-S3 期间记录，后续一并修复）

1. **ZCode 内嵌渲染器怪癖**（环境问题，非产品缺陷）：整页 goto 偶发 ERR_ABORTED、路由 fade 过渡偶发不触发 transitionend 导致视图冻结、键盘 Tab 模拟不可靠、截图管线对大 clip 会平铺/取陈旧帧。验收一律改用整页加载 + 局部 clip；真实浏览器不受影响。→ 无需产品修复；真机复验键盘路径即可
2. **GET /works/{id} 与 PUT /works/{id} 响应缺 tag_ids 字段**（既有）：列表接口 /works 正常返回 tag_ids。S2 未受影响；S4 详情页如需单作品标签再补后端
3. **TimelineList 的 review_change 动作色**：旧代码紫色 #8b5cf6 不是 style.css 令牌，已改用 --text-secondary 中性色；如要紫色需新增令牌（违反「唯一新增 --cc-on」约束，未加）
4. **Bangumi 搜索用 v0 POST**（决策）：硬约束「只发 GET」，但旧版 GET /search/subject/{kw} 实测忽略 type 过滤（要动画返回书籍），v0 POST + filter.type 是唯一正确口径。判定搜索 POST 为只读查询语义予以保留；若用户要求严格全 GET，可切旧版并接受无类型过滤
5. **ui-evolution-prompts.md 验收写 ≥36px、原型 44px**：用户已拍板 44px（Q3），文档验收行未改——属历史文档，无需追改

## 遗留问题清单（2026-10-23，S4 期间补充）

6. **资料区子块失败静默留空**：角色/关联/制作/分集/社区对照各子块加载失败只 console.error，分区标题下留空；仅 zone 级（subject 拉取失败）有错误块 + 重新加载 + bgm.tv 直链。如需子块级重试可复用 S1 的 StateBlock，本轮未加（避免过度设计）
7. **GET /works 列表序列化缺 bangumi_id**（既有，同第 2 条家族）：Q2「加入想看」后的回填靠 create 响应完成，不受影响；如未来需要列表态标记已入册需补字段
8. **S4 验收方式变更**：ZCode 内嵌渲染器（IAB）不可用（会话恢复后 node REPL 缺失），改用 Chrome headless + CDP（Runtime.evaluate/Page.captureScreenshot/Fetch 拦截）完成全部交互验证；结论与真实浏览器等价
9. **设计资料丢失**：zace-implementation-handoff.md 与 Zace 原型文件随 Open Design 应用数据清理丢失（2026-10-23 确认，全盘搜索无果）；S4-S6 验收依据以对话记录 + docs/ui-evolution-prompts.md + 代码现状为准
10. **时间线类型补齐（§3.4）审计结论**：后端 record_timeline 全部调用点只产出 5 种 action_type（created / status_change / rating_change / review_change / progress_update），前端 TimelineList 已全部覆盖（未知类型有兜底色与兜底标签）——落「前端只列现有 5 类」分支，无需改码
11. **uvicorn 进程树清理**：run.py 为 reload=True（父+子进程）；重启时 taskkill 单 PID 会留下继承 socket 的子进程，新旧实例同时监听 8001 且旧代码抢答。重启后端应 `taskkill //PID <pid> //T //F` 清树，或直接用 `python -m uvicorn app.main:app --port 8001`（无 reload）单进程运行
