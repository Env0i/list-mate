# list-mate frontend

Vue 3 + Vite 前端，卡册集换式卡牌视觉风格。

## 开发

```bash
npm install
npx vite
```

前端运行在 `http://localhost:5173`，API 代理到 `http://localhost:8000`。

## 构建

```bash
npx vite build
```

构建产物在 `dist/` 目录，部署到阿里云 Nginx。

## 技术栈

- Vue 3 (Composition API + `<script setup>`)
- Vue Router 4
- axios
- 纯 scoped CSS（无 UI 框架）

## 页面路由

| 路径 | 说明 |
|------|------|
| `/` | 作品列表（卡册展示） |
| `/works/:id` | 作品详情（编辑用弹窗） |
| `/search` | Bangumi 搜索添加 |
| `/add` | 手动添加 |
| `/works/:id/game-profiles/new` | 新增游戏配置 |
| `/works/:id/game-profiles/:gpid` | 游戏配置详情 |
