# list-mate

个人 ACGN 媒体库 — 记录动漫、小说、漫画、游戏的进度和评价。

## 功能

- 记录四类 ACGN 作品的观看/阅读/游玩进度
- 多 Profile 支持（二刷、多配置、游戏整合包分别追踪）
- Bangumi API 搜索自动填充作品信息
- 自定义标签 + 评分评价
- 统计仪表盘

## 技术栈

- **后端**: Python FastAPI + SQLAlchemy + SQLite
- **前端**: Vue 3 + Vite + Vue Router（响应式，手机+桌面）
- **部署**: 阿里云服务器，Nginx

## 迭代计划

| Iter | 范围 |
|------|------|
| Iter 1 | 作品 CRUD + Bangumi 搜索 + 多 Profile 进度管理 |
| Iter 2 | 自定义标签 + 评分评价 |
| Iter 3 | 统计仪表盘 + 操作时间线 |
| Iter 4 | 附件上传 + 数据导出 |

## 快速开始

```bash
# 后端
cd backend
pip install -r requirements.txt
python run.py

# 前端
cd frontend
npm install
npx vite
```

## 文档

- [设计文档](docs/design.md)
- [产品需求](docs/PRD.md)
