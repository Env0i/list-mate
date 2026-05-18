# list-mate

个人 ACGN 媒体库 — 记录动漫、小说、漫画、游戏的进度和评价。抽卡图鉴/集换式卡牌视觉风格。

## 功能

- 记录四类 ACGN 作品的观看/阅读/游玩进度
- 游戏多配置独立追踪（本体/整合包/自打模组），支持 progress_type（次数/百分比/纯状态）
- 模组列表粘贴管理 + 附件文件上传
- Bangumi API 搜索自动填充作品信息
- 追踪字段完整：购买信息、游玩时长、开始/完成时间、优先度、外部链接
- 自定义标签 + 评分评价 + 笔记
- 卡册风 UI：品类色系统、玻璃拟态导航、全息卡片动画、EXP 经验值条

## 技术栈

- **后端**: Python FastAPI + SQLAlchemy + SQLite
- **前端**: Vue 3 + Vite + Vue Router（响应式，手机+桌面）
- **视觉**: 抽卡图鉴风格 UI，品类色系统，玻璃拟态导航，全息卡片动画
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

- [设计文档](docs/design.md) — 架构与数据模型
- [UI 设计规范](docs/ui-design-spec.md) — 视觉风格与组件规范
- [产品需求](docs/PRD.md)
