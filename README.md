# Zace

> 个人 ACGN 媒体库 — 记录动漫、小说、漫画、游戏的进度与评价，以抽卡图鉴/集换式卡牌风格呈现。

## 功能特性

- **作品管理** — 动漫、小说、漫画、游戏四类作品统一管理，支持子分类
- **Bangumi 集成** — 搜索 Bangumi 数据库自动填充作品信息与封面
- **进度追踪** — 按品类区分进度单位（集/章/卷/%），自动标记完成
- **游戏多配置** — 同一游戏可创建多个独立配置（本体、整合包、自打模组），各自追踪进度与状态
- **模组管理** — tag 式模组列表粘贴添加，支持附件上传（任意格式）
- **自定义标签** — 创建标签并关联作品，支持颜色选择与按标签筛选
- **评分评价** — 0–10 整数评分、文字评价、游玩笔记
- **统计仪表盘** — 分类计数、状态分布、评分等级分布（S/A/B/C）、操作时间线
- **数据导出** — JSON / CSV 格式导出作品数据（文件名自带日期）
- **备份与还原** — 一键下载 SQLite 整库备份（含时间线/附件/封面），支持从备份文件还原（还原前自动快照兜底）
- **主题三态** — 跟随系统 / 白天 / 黑夜（默认白天），右上角切换即时生效
- **快捷进度** — 列表卡片 ±1 直接更新进度，到达总量自动标记完成
- **作品历史** — 详情页按天分组展示该作品的全部操作记录
- **本周活跃** — 统计页展示最近 7 天操作数与更新作品数
- **卡册风 UI** — 多层边框 + 四角装饰 + 全息闪光 Hover + EXP 经验值条 + 印章式状态戳记 + 发牌入场动画

## 技术栈

| 层级   | 技术                               |
|--------|------------------------------------|
| 前端   | Vue 3, Vite, Vue Router            |
| 后端   | Python FastAPI, SQLAlchemy, SQLite |
| 字体   | DM Sans, Noto Sans SC              |
| 部署   | Nginx, uvicorn, systemd            |

## 项目结构

```
zace/
├── backend/
│   ├── app/
│   │   ├── main.py              # 应用入口、动态数据库迁移
│   │   ├── database.py           # 数据库连接与会话管理
│   │   ├── config.py             # 应用配置
│   │   ├── models/               # ORM 数据模型
│   │   ├── schemas/              # Pydantic 请求/响应模型
│   │   └── routers/              # API 路由
│   ├── bangumi_cache/            # Bangumi 封面图片缓存
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                  # API 调用封装
│   │   ├── components/           # 通用组件
│   │   │   ├── layout/           # 桌面导航栏、手机底部导航
│   │   │   └── work/             # 卡片、进度条、品类徽章
│   │   ├── views/                # 页面组件
│   │   ├── router/               # 路由配置
│   │   ├── style.css             # 全局样式、CSS 变量、动画关键帧
│   │   └── App.vue               # 根组件
│   └── package.json
├── docs/
│   ├── PRD.md                    # 产品需求文档
│   ├── design.md                 # 设计文档
│   └── ui-design-spec.md         # UI 设计规范
├── deploy.py                     # 自动化部署脚本
├── AGENTS.md                     # AI 辅助开发配置（ZCode）
└── CLAUDE.md                     # AI 辅助开发配置（Claude Code）
```

## 快速开始

### 前置要求

- Python 3.8+
- Node.js 18+
- npm

### 安装与运行

```bash
# 1. 克隆仓库
git clone <repo-url>
cd zace

# 2. 启动后端（端口 8001，run.py 实际监听）
cd backend
pip install -r requirements.txt
python run.py

# 3. 启动前端（端口 5173，开发模式代理 /api → 8001）
cd ../frontend
npm install
npx vite
```

打开浏览器访问 `http://localhost:5173`。

## 部署

支持一键部署到阿里云服务器：

```bash
python deploy.py
```

部署流程：

1. 构建前端（`npx vite build`）
2. 通过 SFTP 上传 `dist/` + `backend/` 到服务器
3. 服务器自动创建虚拟环境并安装依赖
4. 创建 Nginx 配置与 systemd 服务并重启

当前部署地址：`http://47.108.188.175:8081`

## 数据管理

所有入口在 **统计页右上角**：

| 操作 | 说明 |
|------|------|
| **JSON / CSV** | 导出作品数据（不含时间线/附件/封面），文件名自带日期 |
| **备份** | 下载 SQLite 整库快照（`.db`），是可直接还原的完整备份 |
| **还原** | 上传 `.db` 备份覆盖当前数据；**还原前当前数据会自动快照**到服务器 `backups/` 目录，还原后需重启后端服务生效 |

## API 概览

### 作品

- `GET/POST /api/works` — 作品列表 / 创建
- `GET/PUT/DELETE /api/works/{id}` — 作品详情 / 更新 / 删除

### 游戏配置

- `GET /api/works/{id}/game-profiles` — 游戏配置列表
- `POST /api/works/{id}/game-profiles` — 新增游戏配置
- `PUT/DELETE /api/game-profiles/{id}` — 更新 / 删除游戏配置

### 附件

- `GET /api/works/{id}/attachments` — 附件列表
- `POST /api/works/{id}/attachments` — 上传附件
- `GET/DELETE /api/attachments/{id}` — 下载 / 删除附件

### 数据管理

- `GET /api/export/json` / `GET /api/export/csv` — 导出作品数据
- `GET /api/backup` — 下载 SQLite 整库备份（含时间线/附件/封面）
- `POST /api/restore` — 从备份文件还原（覆盖式，还原前自动快照到服务器 backups/）

### 其他

- `GET/POST/PUT/DELETE /api/tags` — 标签 CRUD
- `POST /api/bangumi/search` — Bangumi 搜索（type 过滤）
- `GET /api/stats` — 统计数据（含 week_activity 本周活跃）
- `GET /api/timeline` — 操作时间线（支持 work_id 过滤）

## 品类色系统

- **动漫** — `#FF1A5E` — 卡片边框、徽章、辉光
- **小说** — `#3366FF`
- **漫画** — `#00CC66`
- **游戏** — `#FF7A00`

## 项目状态

当前已完成全部四个迭代并经十三轮自主打磨优化（v1.0.0）。

- **Iter 1** — 作品 CRUD + Bangumi + GameProfile + 卡册 UI
- **Iter 2** — 自定义标签 + 评分评价 + 标签筛选
- **Iter 3** — 统计仪表盘 + 操作时间线
- **Iter 4** — 附件管理 + 数据导出 + 封面上传

## 许可

本项目采用 MIT 许可证。
