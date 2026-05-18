# Task Plan: list-mate Iter 1 — 核心记录

## Goal
实现 list-mate 的 Iter 1（核心记录）：后端全部 API + 前端作品管理、进度记录核心流程跑通。

## Current Phase
Phase 4

## Phases

### Phase 1: 后端项目初始化 + 数据模型
- [x] 创建 FastAPI 项目结构
- [x] 编写数据库模型（Work / Profile / Tag / WorkTag）
- [x] 实现 database.py 和 config.py
- [x] 验证数据库初始化可运行
- **Status:** complete

### Phase 2: 后端 API — Works + Bangumi
- [x] Work CRUD API（增删改查 + 筛选分页）
- [x] Bangumi 搜索代理 API
- [x] 封面缓存逻辑（搜索时自动下载存 BLOB）
- **Status:** complete

### Phase 3: 后端 API — Profiles + Tags
- [x] Profiles CRUD API（含自动完成逻辑）
- [x] Tags CRUD API
- **Status:** complete

### Phase 4: 前端项目初始化
- [ ] Vue 3 + Vite + Vue Router 项目搭建
- [ ] 响应式布局框架（底部导航 / 侧边栏）
- [ ] API 调用封装（axios）
- **Status:** pending

### Phase 5: 前端 — 作品列表页
- [ ] 分类 Tab 筛选（全部/动漫/小说/漫画/游戏）
- [ ] 卡片视图 + 列表视图
- [ ] 状态筛选 + 搜索
- **Status:** pending

### Phase 6: 前端 — 作品详情 + Profile 管理
- [ ] 作品详情页（封面+信息+Profile列表）
- [ ] Profile 进度更新（一键递增/手动输入）
- [ ] Profile 创建/编辑/删除
- **Status:** pending

### Phase 7: 前端 — 搜索添加 + 手动添加
- [ ] Bangumi 搜索页（结果预览→填充表单）
- [ ] 手动添加作品页
- **Status:** pending

### Phase 8: 部署
- [ ] deploy.py 脚本
- [ ] 本地全流程测试
- **Status:** pending

## Key Questions
1. Bangumi API Token 是否需要配置？（需要用户提供）
2. 封面的 BLOB 存储如何处理大文件？（SQLite BLOB 对封面的尺寸足够）

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Profile 统一模型替代 Progress+GameProfile | 支持二刷/多配置，数据一致 |
| 单 Vue 3 响应式前端替代 Uni-app + Element Plus | 个人项目，减少维护量 |
| SQLite BLOB 存封面 | 不依赖外部图片服务，加载快 |
| 附件文件也存 BLOB（Iter 4） | 一致的数据存储方式，无需文件系统管理 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |

## Notes
- 先本地开发，再部署到阿里云
- 部署模式沿用 goal-mate 的 deploy.py + nginx
- Iter 1 仅实现 P0 功能，Iter 2 之后的标签/统计/时间线不做
