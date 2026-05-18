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
    models/         # ORM 模型 (Work, Profile, Tag, WorkTag, Attachment, TimelineEntry)
    schemas/        # Pydantic 请求/响应模型
    routers/        # API 路由 (works, profiles, tags, bangumi, stats)
  bangumi_cache/    # 封面图片缓存目录（或存 BLOB，见设计文档）
  list_mate.db      # SQLite 数据库
  requirements.txt
  run.py            # 启动入口

frontend/           # Vue 3 前端（原来称 mobile/）
  src/
    api/            # API 调用封装
    components/     # 通用组件
    views/          # 页面组件
    router/         # 路由配置
    App.vue         # 根组件 + 全局样式
```

## 核心设计决策

- **Profile 统一模型**: 所有品类共用 Profile（取代独立的 Progress + GameProfile），支持二刷/多配置
- **单前端 + 响应式**: 不做 Uni-app 原生编译，一套 Vue 3 代码适配手机和桌面
- **封面缓存**: Bangumi 图片存为 BLOB，不依赖外部服务展示
- **进度自动完成**: progress_value >= total (>0) 时自动标记 completed，可手动覆盖
- **多附件**: 每个 Profile 可挂多个附件（不限定格式），取代单文件上传
- **开发本地 → 部署服务器**: 本地开发完成后用 deploy.py 上传到阿里云

## 迭代计划

| Iter | 范围 |
|------|------|
| Iter 1 | 作品 CRUD + Bangumi 搜索 + 多 Profile 进度管理 |
| Iter 2 | 自定义标签 + 评分评价 + 标签筛选 |
| Iter 3 | 统计仪表盘 + 操作时间线 |
| Iter 4 | 附件上传 + 数据导出 + 扩展功能 |

## 关键约定

- **API 基础路径**: `/api` → Vite dev proxy: `http://localhost:8000`
- **响应式断点**: `<768px` 手机（底部 Tab），`>=768px` 桌面（侧边栏）
- **进度单位**: anime→ep, novel→chapter, comic→volume, game→percent
- **状态枚举**: wish / watching / completed / paused / dropped
- **评分**: 0-10 整数，null 表示未评分
- **total 为空**: 表示连载中/未知总进度

## 启动

```bash
# 后端 (端口 8000)
cd backend
pip install -r requirements.txt
python run.py

# 前端 (端口 5173, 代理 /api → 8000)
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
