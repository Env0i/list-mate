# Task Plan: list-mate Iter 1 — 卡册风全面重构

## Goal
完成 list-mate 的 Iter 1（核心记录 + 卡册风 UI）：后端 GameProfile 扩展 + 前端所有页面卡册风重构 + 搜索/添加页。

## Current Phase
全部完成，待用户验证

## Phases

### Phase 1: 后端 GameProfile 模型扩展
- [x] GameProfile 模型新增 start_date, finish_date, playtime_hours, source, mods_list, notes, progress_type 字段
- [x] 更新 Create/Update/Response schemas
- [x] database.py 添加 migration
- [x] game_profiles.py router 智能默认值 + progress_type 感知自动完成
- [x] 新增 ProgressType 枚举 (none/count/percent)
- **Status:** complete

### Phase 2: 前端 WorkDetail 重构
- [x] 卡册风布局：封面放大至 240px，多层卡牌边框 + 四角品类色装饰 + 全息闪光 hover
- [x] 右侧信息卡：Bangumi 官方数据展示（品类色卡牌边框）
- [x] 底部追踪卡：个人追踪字段网格 + 左边框品类色点缀
- [x] 编辑模态对话框：四段字段分组（基本信息/追踪信息/游戏专属/评分评价）
- [x] 游戏配置横向条状卡片展示 + progress_type 感知进度显示
- [x] 移除独立编辑路由，改用模态对话框
- **Status:** complete

### Phase 3: 前端 GameProfileDetail 重构
- [x] 卡册风单卡片布局（品类色外框 + 阴影）
- [x] 状态选择器（6 状态按钮）
- [x] progress_type 选择器（none/count/percent）+ 自适应进度步进器
- [x] 游玩记录：start_date, finish_date, playtime_hours, source
- [x] 模组列表：tag 展示 + 粘贴多行添加 + 逐个删除
- [x] 附件占位（后续版本推出）
- [x] 评分滑块 + 评价 + 笔记
- **Status:** complete

### Phase 4: 前端 WorkList 调整
- [x] 去掉列表视图 toggle（移除 viewMode ref + 按钮 + CSS）
- [x] 保持卡片网格展示（2-5 列响应式）
- **Status:** complete

### Phase 5: 搜索页 + 添加页
- [x] 新增 Search.vue：两步流程（Bangumi 搜索 → 预填确认对话框）
- [x] 新增 Add.vue：手动填表单（与编辑对话框布局一致，四段分组）
- [x] 路由更新：添加 /search、/add，/works/:id/edit 重定向至详情页
- [x] TopBar/MobileNav 已有对应导航链接
- **Status:** complete

### Phase 6: 文档同步
- [x] docs/design.md v2.0
- [x] CLAUDE.md / README.md / roadmap.md
- [x] frontend/README.md
- [x] docs/ui-design-spec.md deprecated
- **Status:** complete
