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
