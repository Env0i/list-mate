<script setup>
import { useRoute } from 'vue-router'
import ThemeToggle from './ThemeToggle.vue'
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
  <header class="topbar">
    <div class="inner">
      <a href="/" class="brand">
        <img src="/logo.svg" alt="Zace" class="brand-logo" width="140" height="41" />
      </a>
      <nav class="nav">
        <router-link v-for="item in items" :key="item.path" :to="item.path" class="ni" :class="{ on: route.path === item.path }">
          <svg viewBox="0 0 1024 1024" fill="currentColor" class="ni-i">
            <template v-if="item.icon === 'home'">
              <path d="M362.666667 895.914667V639.850667c0-36.266667 33.109333-63.850667 72.533333-63.850667h153.6c39.253333 0 72.533333 27.648 72.533333 63.850667v256.064h59.904c61.269333 0 110.762667-47.957333 110.762667-106.730667V414.165333L557.162667 139.328a63.808 63.808 0 0 0-90.325334 0L192 414.165333v375.018667c0 58.88 49.386667 106.730667 110.762667 106.730667H362.666667z m42.666666 0h213.333334V639.850667c0-10.709333-12.586667-21.184-29.866667-21.184h-153.6c-17.408 0-29.866667 10.389333-29.866667 21.184v256.064z m469.333334-439.082667v332.352c0 82.645333-68.885333 149.397333-153.429334 149.397333H302.762667C218.133333 938.581333 149.333333 871.936 149.333333 789.184V456.832l-27.584 27.584a21.333333 21.333333 0 1 1-30.165333-30.165333L436.672 109.162667a106.474667 106.474667 0 0 1 150.656 0l345.088 345.088a21.333333 21.333333 0 0 1-30.165333 30.165333L874.666667 456.832z"/>
            </template>
            <template v-else-if="item.icon === 'search'">
              <path d="M469.333333 768c-166.4 0-298.666667-132.266667-298.666666-298.666667s132.266667-298.666667 298.666666-298.666666 298.666667 132.266667 298.666667 298.666666-132.266667 298.666667-298.666667 298.666667z m0-85.333333c119.466667 0 213.333333-93.866667 213.333334-213.333334s-93.866667-213.333333-213.333334-213.333333-213.333333 93.866667-213.333333 213.333333 93.866667 213.333333 213.333333 213.333334z m251.733334 0l119.466666 119.466666-59.733333 59.733334-119.466667-119.466667 59.733334-59.733333z"/>
            </template>
            <template v-else-if="item.icon === 'plus'">
              <path d="M801.171 483.589H544V226.418c0-17.673-14.327-32-32-32s-32 14.327-32 32v257.171H222.83c-17.673 0-32 14.327-32 32s14.327 32 32 32H480v257.17c0 17.673 14.327 32 32 32s32-14.327 32-32v-257.17h257.171c17.673 0 32-14.327 32-32s-14.327-32-32-32z"/>
            </template>
            <template v-else-if="item.icon === 'stats'">
              <path d="M1.827144 981.176313m21.354745 0l977.636222 0q21.354745 0 21.354745 21.354745l0 0.114197q0 21.354745-21.354745 21.354745l-977.636222 0q-21.354745 0-21.354745-21.354745l0-0.114197q0-21.354745 21.354745-21.354745Z"/>
              <path d="M44.650831 0m0 21.354745l0 977.636222q0 21.354745-21.354745 21.354745l-0.114197 0q-21.354745 0-21.354745-21.354745l0-977.636222q0-21.354745 21.354745-21.354745l0.114197 0q21.354745 0 21.354745 21.354745Z"/>
              <path d="M432.303425 402.092949m-15.100086 15.100085l-220.122096 220.122097q-15.100085 15.100085-30.20017 0l-0.080749-0.08075q-15.100085-15.100085 0-30.20017l220.122096-220.122096q15.100085-15.100085 30.20017 0l0.080749 0.080749q15.100085 15.100085 0 30.20017Z"/>
              <path d="M402.03781 371.717901m15.100085 15.100086l220.122097 220.122096q15.100085 15.100085 0 30.20017l-0.080749 0.08075q-15.100085 15.100085-30.200171 0l-220.122096-220.122097q-15.100085-15.100085 0-30.20017l0.080749-0.080749q15.100085-15.100085 30.20017 0Z"/>
              <path d="M872.344866 402.029735m-15.100085 15.100085l-220.122096 220.122097q-15.100085 15.100085-30.200171 0l-0.080749-0.080749q-15.100085-15.100085 0-30.200171l220.122097-220.122096q15.100085-15.100085 30.20017 0l0.080749 0.080749q15.100085 15.100085 0 30.20017Z"/>
            </template>
            <template v-else-if="item.icon === 'tag'">
              <path d="M448 853.333333L170.666667 576 576 170.666667H853.333333v277.333333L448 853.333333z m0-119.466666L768 426.666667V256h-170.666667l-307.2 320 157.866667 157.866667zM682.666667 298.666667c25.6 0 42.666667 17.066667 42.666666 42.666666s-17.066667 42.666667-42.666666 42.666667-42.666667-17.066667-42.666667-42.666667 17.066667-42.666667 42.666667-42.666666z"/>
            </template>
          </svg>
          <span class="ni-t">{{ item.name }}</span>
        </router-link>
      </nav>
      <ThemeToggle />
    </div>
  </header>
</template>

<style scoped>
.topbar {
  display: none;
  position: fixed; top: 0; left: 0; right: 0;
  height: var(--topbar-height);
  background: var(--topbar-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--topbar-border);
  z-index: 90;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.1);
}
@media (min-width: 768px) { .topbar { display: flex; } }

.inner {
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 0 28px;
  display: flex;
  align-items: center;
  height: 100%;
  gap: 40px;
}

.brand {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  text-decoration: none;
  opacity: 1;
  transition: opacity 0.15s;
}
.brand:hover { opacity: 0.8; }
.brand-logo {
  display: block;
  height: 30px;
  width: auto;
}
/* 暗色下 logo 是深色 SVG，反白保证可读 */
:root[data-theme='dark'] .brand-logo { filter: invert(0.92); }

.nav {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
}
.ni {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 7px 14px;
  border-radius: var(--radius-md);
  color: var(--text-tertiary);
  font-size: var(--fs-sm);
  font-weight: 500;
  transition: all 0.15s;
}
.ni:hover { color: var(--text-secondary); background: var(--bg-surface-hover); }
.ni:active { transform: none; }
.ni.on { color: var(--primary); background: var(--primary-light); font-weight: 600; }
.ni-i { width: 17px; height: 17px; }
</style>
