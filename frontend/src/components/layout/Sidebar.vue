<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
const items = [
  { name: '收藏', path: '/', icon: 'home' },
  { name: '搜索', path: '/search', icon: 'search' },
  { name: '添加', path: '/add', icon: 'plus' },
  { name: '统计', path: '/stats', icon: 'stats' },
  { name: '标签', path: '/tags', icon: 'tag' },
]
</script>

<template>
  <aside class="sidebar">
    <div class="hd">
      <div class="logo-w">
        <svg viewBox="0 0 28 28" fill="none" width="22" height="22">
          <rect width="28" height="28" rx="7" fill="white" fill-opacity="0.2"/>
          <path d="M14 7v14M7 14h14" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
      </div>
      <span class="logo-t">list-mate</span>
    </div>
    <nav class="nav">
      <router-link v-for="item in items" :key="item.path" :to="item.path" class="ni" :class="{ on: route.path === item.path }">
        <svg viewBox="0 0 22 22" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="ni-i">
          <template v-if="item.icon === 'home'">
            <path d="M3 11l2-2m0 0l6-6 6 6M5 9v9a1 1 0 001 1h3m-3-7h10m0 0l2 2m-2-2v7a1 1 0 01-1 1h-3m-4 0a1 1 0 001-1v-3a1 1 0 011-1h2a1 1 0 011 1v3a1 1 0 001 1"/>
          </template>
          <template v-else-if="item.icon === 'search'">
            <circle cx="10" cy="10" r="7"/><path d="M15 15l5 5"/>
          </template>
          <template v-else-if="item.icon === 'plus'">
            <path d="M11 5v12M5 11h12"/>
          </template>
          <template v-else-if="item.icon === 'stats'">
            <path d="M4 18h16M6 14l3-5 4 4 5-7"/>
          </template>
          <template v-else-if="item.icon === 'tag'">
            <path d="M19.59 12.41l-6.17 6.17a2 2 0 01-2.83 0L2 11V2h9l8.59 8.59a2 2 0 010 2.82z"/><path d="M6.5 6.5h.01"/>
          </template>
        </svg>
        <span>{{ item.name }}</span>
      </router-link>
    </nav>
    <div class="ft">
      <div class="div"/>
      <div class="cats">
        <span class="cat-l">分类</span>
        <router-link to="/?category=all" class="ci"><span>全部</span></router-link>
        <router-link to="/?category=anime" class="ci"><span class="d da"/><span>动漫</span></router-link>
        <router-link to="/?category=novel" class="ci"><span class="d dn"/><span>小说</span></router-link>
        <router-link to="/?category=comic" class="ci"><span class="d dc"/><span>漫画</span></router-link>
        <router-link to="/?category=game" class="ci"><span class="d dg"/><span>游戏</span></router-link>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  display: none;
  position: fixed; left: 0; top: 0;
  width: var(--sidebar-width); height: 100vh;
  background: var(--bg-surface);
  border-right: 1px solid var(--color-border);
  z-index: 90;
  flex-direction: column;
}
@media (min-width: 768px) { .sidebar { display: flex; } }

.hd {
  background: linear-gradient(135deg, #FB7299, #FC9BB5);
  padding: 28px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.logo-w {
  width: 32px; height: 32px;
  background: rgba(255,255,255,0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}
.logo-t {
  font-size: var(--fs-lg);
  font-weight: 700;
  color: white;
  letter-spacing: -0.3px;
}

.nav { display: flex; flex-direction: column; gap: 2px; padding: 12px 10px; }
.ni {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 12px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: var(--fs-sm);
  font-weight: 500;
  transition: all 0.15s;
  position: relative;
}
.ni:hover { background: var(--bg-surface-hover); color: var(--text-primary); }
.ni.on {
  background: var(--primary-light);
  color: var(--primary);
  font-weight: 600;
}
.ni.on::before {
  content: '';
  position: absolute; left: -10px; top: 50%; transform: translateY(-50%);
  width: 3px; height: 20px;
  background: var(--primary);
  border-radius: 0 3px 3px 0;
}
.ni-i { width: 18px; height: 18px; flex-shrink: 0; }

.ft { flex: 1; display: flex; flex-direction: column; padding: 0 10px 20px; }
.div { margin: 8px 10px; height: 1px; background: var(--color-border); }
.cats { display: flex; flex-direction: column; gap: 2px; }
.cat-l { font-size: var(--fs-xs); color: var(--text-tertiary); font-weight: 500; padding: 8px 12px 6px; letter-spacing: 0.5px; }
.ci { display: flex; align-items: center; gap: 8px; padding: 7px 12px; border-radius: var(--radius-md); font-size: var(--fs-sm); color: var(--text-secondary); transition: all 0.15s; }
.ci:hover { background: var(--bg-surface-hover); color: var(--text-primary); }
.d { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.da { background: var(--c-anime); }
.dn { background: var(--c-novel); }
.dc { background: var(--c-comic); }
.dg { background: var(--c-game); }
</style>
