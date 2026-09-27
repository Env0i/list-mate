# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 技术栈

- **后端**: Python FastAPI + SQLAlchemy + SQLite
- **前端**: Vue 3 + Vite + Vue Router（单 SPA，响应式布局适配手机+桌面）
- **部署**: 阿里云服务器 (47.108.188.175), Nginx 反向代理
- **数据源**: Bangumi API 自动填充作品信息

## 项目结构

```
backend/            # FastAPI 后端
  app/
    main.py         # 入口 + 动态迁移
    database.py     # SQLite 连接
    config.py       # 配置
    models/         # ORM 模型 (Work, GameProfile, Tag, WorkTag, Attachment, TimelineEntry)
    schemas/        # Pydantic 请求/响应模型
    routers/        # API 路由 (works, game_profiles, tags, bangumi, stats, timeline, attachments, export)
  bangumi_cache/    # 封面图片缓存目录（或存 BLOB，见设计文档）
  list_mate.db      # SQLite 数据库
  requirements.txt
  run.py            # 启动入口

frontend/           # Vue 3 前端
  src/
    api/            # API 调用封装 (worksApi, gameProfilesApi, bangumiApi, tagsApi)
    components/     # 通用组件
      layout/       # TopBar（桌面导航）、MobileNav（手机底部导航）
      work/         # WorkCardGrid、ProgressBar、CategoryBadge
    views/          # 页面组件 (WorkList, WorkDetail, GameProfileDetail, GameProfileNew, Search, Add, Stats, Tags)
    constants/      # 展示常量 (品类/状态标签与颜色，设计令牌引用)
    utils/          # toast/payload/theme/timeline 等共享工具
    router/         # 路由配置
    style.css       # 全局 CSS 变量、品类色、动画关键帧
    App.vue         # 根组件（TopBar + router-view + MobileNav）
```

## 核心设计决策

- **数据模型分离**: 动漫/小说/漫画的进度字段直接挂在 Work 上；GameProfile 仅用于游戏多配置（支持二刷/整合包/自打模组）
- **两套状态枚举**: 动漫/小说/漫画用 wish/watching/completed/paused/dropped；游戏用 wish/playing/completed/dropped/wait_buy/wait_sale
- **单前端 + 响应式**: 不做 Uni-app 原生编译，一套 Vue 3 代码适配手机和桌面
- **封面缓存**: Bangumi 图片存为 BLOB，不依赖外部服务展示
- **进度自动完成**: 动漫/小说/漫画在 progress_value >= total(>0) 且本次请求未显式改状态时自动标记 completed（auto_completed 旗标防止反复触发，手动改回非 completed 会重置）；游戏 GameProfile 仅 percent 型 ≥100 自动完成；count（二刷次数）/none 型**保持手动标记**（2026-09-27 用户确认，决策见 findings.md）
- **GameProfile 进度类型**: progress_type 决定进度含义 — count（通关次数）、percent（完成百分比）、none（纯状态）
- **多附件**: 每个 GameProfile 可挂多个附件（不限定格式）
- **编辑方式**: 模态对话框编辑，无独立编辑页
- **开发本地 → 部署服务器**: 本地开发完成后用 deploy.py 上传到阿里云

## 迭代记录

| Iter | 范围 | 状态 |
|------|------|------|
| Iter 1 | 作品 CRUD + Bangumi 搜索 + GameProfile 多配置 + 卡册风前端 | ✅ |
| Iter 2 | 自定义标签 + 评分评价 + 标签筛选 | ✅ |
| Iter 3 | 统计仪表盘 + 操作时间线 | ✅ |
| Iter 4 | 附件管理 + 数据导出 + 封面上传 | ✅ |
| v1.0.0 | 二十一轮自主打磨：审计修复、暗色主题、备份还原、快捷进度、验收走查等 | ✅ 已打 tag |

## 关键约定

- **API 基础路径**: `/api` → Vite dev proxy: `http://localhost:8001`
- **响应式断点**: `<768px` 手机（底部 Tab），`>=768px` 桌面（顶部导航栏 TopBar）
- **视觉风格**: 抽卡图鉴/集换式卡牌 UI — 暖白卡册纸背景 (#F7F5F0)，品类色辉光，全息闪光 hover，EXP 经验值条，印章式状态戳记，发牌入场动画
- **字体**: DM Sans + Noto Sans SC
- **进度单位**: anime→ep, novel→chapter, comic→volume, game→percent
- **状态枚举（动漫/小说/漫画）**: wish / watching / completed / paused / dropped
- **状态枚举（游戏）**: wish / playing / completed / dropped / wait_buy / wait_sale
- **评分**: 0-10 整数，null 表示未评分
- **total 为空**: 表示连载中/未知总进度

## 启动

```bash
# 后端 (端口 8001，run.py 实际监听)
cd backend
pip install -r requirements.txt
python run.py

# 前端 (端口 5173, 代理 /api → 8001)
cd frontend
npm install
npx vite
```

## 部署

```bash
# 构建前端
cd frontend
npx vite build

# 上传到服务器
python deploy.py
```

## Karpathy 开发准则

### 1. Think Before Coding

- 遇到歧义先问，不做假设
- 有更简单方案先提出来
- 不确定就停下来，说明困惑点，问清楚

### 2. Simplicity First

- 不多写一行代码
- 不做未来可能需要的抽象
- 不处理不可能发生的错误
- 不写不需要的灵活性和可配置性
- 200 行能改成 50 行就改

### 3. Surgical Changes

- 只改需求涉及的文件
- 不改无关代码格式
- 不改没坏的东西
- 不清理他人的遗留问题（除非需求涉及）
- 自己改动导致的未使用代码必须清理

### 4. Goal-Driven Execution

- 每一步有可验证的检查点
- "加验证" → "先写测试用例，再让它通过"
- "修 bug" → "先写能复现的用例，再修"
- 多步骤任务先列计划再执行

## 设计文档

- [docs/PRD.md](docs/PRD.md) — 原始产品需求
- [docs/design.md](docs/design.md) — 最新设计文档（以此为准）
- [task_plan.md](task_plan.md) — 当前实施计划
- [findings.md](findings.md) — 技术决策记录
- [progress.md](progress.md) — 进度日志
