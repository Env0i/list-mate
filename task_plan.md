# Task Plan: list-mate

## Current Phase
Iter 2 已完成，待用户验证

## Iter 1: 卡册风全面重构 ✅
全部完成，已提交 `4f6ccc0`。

## Iter 2: 自定义标签 + 评分评价 + 标签筛选 ✅

### Phase 1: 后端 — tag_ids 支持
- [x] WorkCreate 新增 tag_ids 字段
- [x] WorkUpdate 新增 tag_ids 字段
- [x] WorkListItem 新增 tag_ids 字段（用于客户端筛选）
- [x] create_work 处理 tag 关联
- [x] update_work 同步 tag 关联
- **Status:** complete

### Phase 2: 标签管理页
- [x] 替换 TagsPlaceholder.vue 为真实 CRUD
- [x] 标签列表展示（颜色圆点 + 名称 + 编辑/删除按钮）
- [x] 新建标签（名称 + 预设色板 + 自定义颜色）
- [x] 编辑标签（行内编辑：名称 + 颜色）
- [x] 删除标签（确认对话框）
- **Status:** complete

### Phase 3: 标签展示
- [x] WorkDetail 信息卡在状态印章下方显示作品标签
- [x] 标签 chip 使用标签颜色 + 透明背景 + 有色边框
- **Status:** complete

### Phase 4: 标签分配
- [x] WorkDetail 编辑对话框新增标签多选区域
- [x] 打开编辑时加载全部标签，已分配标签高亮
- [x] 点击 chip 切换标签选择
- [x] 保存时提交 tag_ids
- **Status:** complete

### Phase 5: 标签筛选
- [x] WorkList 加载全部标签
- [x] 标签筛选 Chips 行（在状态筛选行下方）
- [x] 点击标签筛选，再次点击取消
- [x] 与分类/状态筛选同时生效（客户端过滤）
- **Status:** complete

### Phase 6: 评分评价验证
- [x] 非游戏作品评分/评价在追踪卡中正确展示（Iter 1 已实现）
- [x] 编辑对话框评分滑块和评价文本框正常（Iter 1 已实现）
- [x] 游戏作品评分在 GameProfileDetail 正常（Iter 1 已实现）
- **Status:** complete

## Iter 3: 统计仪表盘 + 操作时间线 (待开始)
- 收藏统计图表（品类分布、状态分布、评分分布）
- 操作时间线（添加、完成、评分变更等历史记录）
- 进度追踪总览

## Iter 4: 附件管理 + 数据导出 + 扩展 (待开始)
- 文件上传/下载
- JSON/CSV 数据导出
- 扩展功能
