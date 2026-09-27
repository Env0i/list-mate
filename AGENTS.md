# AGENTS.md

ZCode 每次会话自动加载本文件。**完整项目文档见 [CLAUDE.md](CLAUDE.md)（权威来源）**——接手新模块或执行长任务前先通读它。最新设计与进度以 [docs/design.md](docs/design.md)、[progress.md](progress.md)、[task_plan.md](task_plan.md) 为准。

## 项目速览

Zace（list-mate）：个人作品进度管理（动漫/小说/漫画/游戏）。后端 FastAPI + SQLAlchemy + SQLite（`backend/`），前端 Vue 3 + Vite 单 SPA（`frontend/`），响应式适配手机+桌面，数据源 Bangumi API。本地个人使用，完成后用 `deploy.py` 部署阿里云。

## 红线

- 不得删除或重置 `backend/list_mate.db`（含 -wal/-shm）
- 不得 force push；`git push` 前必须经用户确认
- 本地个人项目：无需备案/合规/安全加固类改造

## 启动与验证

```bash
# 后端（端口 8001，run.py 实际监听）
cd backend && python run.py

# 前端（端口 5173，/api 代理到 8001）
cd frontend && npx vite

# 后端接口全量测试（从仓库根目录，脚本要求后端跑在 localhost:8001）
python api_full_test.py
```

改动验收：

- 后端改动：跑通 `api_full_test.py`；行为变更补测试
- UI 改动：启动前后端，浏览器实际操作 + 截图验证，不允许只看代码就宣布完成
- 每个独立里程碑 `git commit`，风格：`类型: 中文描述`（Fix: / Refactor: / Docs: / Chore:）

## 关键约定（细节见 CLAUDE.md）

- API 前缀 `/api`；`<768px` 手机（底部 Tab），`>=768px` 桌面（TopBar）
- 断点规范：主断点 `767/768`，小屏档 `480`；`640/900/960/1200` 仅用于网格列数阶梯，不再新增其他断点
- 视觉风格：抽卡图鉴/集换式卡牌——暖白纸背景 #F7F5F0、品类色辉光、全息闪光 hover、EXP 条、印章状态戳、发牌入场动画
- 状态枚举：动漫/小说/漫画 `wish/watching/completed/paused/dropped`；游戏 `wish/playing/completed/dropped/wait_buy/wait_sale`
- 进度单位：anime→ep、novel→chapter、comic→volume、game→percent；`progress >= total(>0)` 自动 completed（可手动覆盖）
- 评分 0-10 整数，null 表示未评分；total 为空表示连载中/未知

## 开发准则

遵循 CLAUDE.md 的 Karpathy 准则：先想后写、简单优先、外科手术式改动（只改需求涉及的文件）、目标驱动（每步有可验证检查点）。产品级二选一先问用户，技术细节自行决定并说明理由。
