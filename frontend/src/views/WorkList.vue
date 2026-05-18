<script setup>
import { ref, computed, watch } from 'vue'
import WorkCardGrid from '../components/work/WorkCardGrid.vue'

const viewMode = ref('grid')
const activeCat = ref('all')
const activeSt = ref('all')
const q = ref('')

const mockWorks = [
  { id: 1, title: '葬送的芙莉莲', category: 'anime', total: 28, progress_value: 22, status: 'watching', game_profiles: [] },
  { id: 2, title: '我独自升级 S2', category: 'anime', total: 13, progress_value: 13, status: 'completed', game_profiles: [] },
  { id: 3, title: '怪兽8号', category: 'anime', total: 12, progress_value: 8, status: 'watching', game_profiles: [] },
  { id: 4, title: '鬼灭之刃 无限城篇', category: 'anime', total: null, progress_value: 0, status: 'wish', game_profiles: [] },
  { id: 5, title: '神秘复苏', category: 'novel', total: null, progress_value: 734, status: 'watching', game_profiles: [] },
  { id: 6, title: '牧神记', category: 'novel', total: 1523, progress_value: 1523, status: 'completed', game_profiles: [] },
  { id: 7, title: '诡秘之主', category: 'novel', total: 1431, progress_value: 892, status: 'watching', game_profiles: [] },
  { id: 8, title: '一人之下', category: 'comic', total: 680, progress_value: 340, status: 'watching', game_profiles: [] },
  { id: 9, title: '进击的巨人 漫画', category: 'comic', total: 139, progress_value: 139, status: 'completed', game_profiles: [] },
  { id: 10, title: '艾尔登法环', category: 'game', total: null, progress_value: null, status: null, game_profiles: [{ status: 'playing' }] },
  { id: 11, title: '赛博朋克 2077', category: 'game', total: null, progress_value: null, status: null, game_profiles: [{ status: 'wish' }] },
  { id: 12, title: '博德之门 3', category: 'game', total: null, progress_value: null, status: null, game_profiles: [{ status: 'dropped' }] },
]

const catColorMap = {
  anime: 'var(--c-anime)',
  novel: 'var(--c-novel)',
  comic: 'var(--c-comic)',
  game: 'var(--c-game)',
}

const cats = [
  { key: 'all', label: '全部' },
  { key: 'anime', label: '番剧' },
  { key: 'novel', label: '小说' },
  { key: 'comic', label: '漫画' },
  { key: 'game', label: '游戏' },
]

const allSts = {
  default: [
    { key: 'all', label: '全部' },
    { key: 'wish', label: '想看' },
    { key: 'watching', label: '在看' },
    { key: 'completed', label: '看完' },
    { key: 'paused', label: '暂停' },
    { key: 'dropped', label: '弃了' },
  ],
  game: [
    { key: 'all', label: '全部' },
    { key: 'wish', label: '想玩' },
    { key: 'playing', label: '在玩' },
    { key: 'completed', label: '通关' },
    { key: 'dropped', label: '弃坑' },
    { key: 'wait_buy', label: '等购买' },
    { key: 'wait_sale', label: '等折扣' },
  ],
}

const sts = computed(() => activeCat.value === 'game' ? allSts.game : allSts.default)

const validKeys = computed(() => sts.value.map(s => s.key))

watch(activeCat, () => {
  if (!validKeys.value.includes(activeSt.value)) {
    activeSt.value = 'all'
  }
})

const workStatus = (w) => {
  if (w.category === 'game') return w.game_profiles?.[0]?.status || 'wish'
  return w.status || 'wish'
}

const filtered = computed(() =>
  mockWorks.filter(w => {
    if (activeCat.value !== 'all' && w.category !== activeCat.value) return false
    if (activeSt.value !== 'all' && workStatus(w) !== activeSt.value) return false
    if (q.value && !w.title.includes(q.value)) return false
    return true
  })
)

function catStyle(c) {
  if (c.key === 'all' || activeCat.value !== c.key) return {}
  return { '--tab-color': catColorMap[c.key] || 'var(--primary)' }
}
</script>

<template>
  <div class="page">
    <div class="page-inner">
      <!-- Header row -->
      <div class="hd-row">
        <div class="hd-left">
          <h1 class="title">收藏</h1>
          <span class="count">{{ filtered.length }}</span>
        </div>
        <div class="hd-right">
          <div class="search-w">
            <svg class="s-icon" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
              <path fill-rule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clip-rule="evenodd"/>
            </svg>
            <input v-model="q" type="text" class="s-inp" placeholder="搜索..."/>
          </div>
          <button class="toggle-btn" @click="viewMode = viewMode === 'grid' ? 'list' : 'grid'" :title="viewMode === 'grid' ? '列表' : '网格'">
            <svg v-if="viewMode === 'grid'" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
              <path fill-rule="evenodd" d="M4.25 2A2.25 2.25 0 002 4.25v2.5A2.25 2.25 0 004.25 9h2.5A2.25 2.25 0 009 6.75v-2.5A2.25 2.25 0 006.75 2h-2.5zm0 9A2.25 2.25 0 002 13.25v2.5A2.25 2.25 0 004.25 18h2.5A2.25 2.25 0 009 15.75v-2.5A2.25 2.25 0 006.75 11h-2.5zm9-9A2.25 2.25 0 0011 4.25v2.5A2.25 2.25 0 0013.25 9h2.5A2.25 2.25 0 0018 6.75v-2.5A2.25 2.25 0 0015.75 2h-2.5zm0 9A2.25 2.25 0 0011 13.25v2.5A2.25 2.25 0 0013.25 18h2.5A2.25 2.25 0 0018 15.75v-2.5A2.25 2.25 0 0015.75 11h-2.5z" clip-rule="evenodd"/>
            </svg>
            <svg v-else viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
              <path fill-rule="evenodd" d="M2 3.75A.75.75 0 012.75 3h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 3.75zm0 4.167a.75.75 0 01.75-.75h14.5a.75.75 0 010 1.5H2.75a.75.75 0 01-.75-.75zm0 4.166a.75.75 0 01.75-.75h14.5a.75.75 0 010 1.5H2.75a.75.75 0 01-.75-.75zm0 4.167a.75.75 0 01.75-.75h14.5a.75.75 0 010 1.5H2.75a.75.75 0 01-.75-.75z" clip-rule="evenodd"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Category tabs — segmented game selector -->
      <div class="cat-tabs">
        <button
          v-for="c in cats"
          :key="c.key"
          class="cat-tab"
          :class="{ on: activeCat === c.key }"
          :style="catStyle(c)"
          @click="activeCat = c.key"
        >
          <span v-if="activeCat === c.key && c.key !== 'all'" class="cat-dot" :style="{ background: catColorMap[c.key] }" />
          {{ c.label }}
        </button>
      </div>

      <!-- Status filters — compact inline row -->
      <div class="st-row">
        <button v-for="s in sts" :key="s.key" class="st-filter" :class="{ on: activeSt === s.key }" @click="activeSt = s.key">
          {{ s.label }}
        </button>
      </div>

      <!-- Grid -->
      <div v-if="filtered.length" class="grid" :class="{ list: viewMode === 'list' }">
        <div v-for="(w, i) in filtered" :key="w.id" :style="{ animationDelay: (i % 12) * 0.04 + 's' }">
          <WorkCardGrid :work="w" />
        </div>
      </div>

      <!-- Empty -->
      <div v-else class="empty">
        <div class="empty-box">
          <svg viewBox="0 0 40 40" fill="none" width="30" height="30">
            <rect x="8" y="10" width="24" height="22" rx="4" stroke="currentColor" stroke-width="1.5" opacity="0.15"/>
            <path d="M16 18l4-3v12l-4-3v-6z" fill="currentColor" opacity="0.08"/>
          </svg>
        </div>
        <p class="empty-t">还没有作品</p>
        <p class="empty-d">搜索或手动添加第一部作品</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 20px 16px;
}
@media (min-width: 768px) {
  .page { padding: 24px 32px; }
}
.page-inner {
  max-width: 1400px;
  margin: 0 auto;
}

/* ======== Header Row ======== */
.hd-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}
.hd-left { display: flex; align-items: baseline; gap: 10px; }
.title { font-size: var(--fs-2xl); font-weight: 800; letter-spacing: -0.5px; }
.count {
  font-size: var(--fs-sm);
  font-weight: 700;
  color: var(--primary);
}
.hd-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Search — compact inline */
.search-w {
  position: relative;
  width: 180px;
}
@media (min-width: 768px) { .search-w { width: 200px; } }
.s-icon {
  position: absolute; left: 11px; top: 50%; transform: translateY(-50%);
  color: var(--text-tertiary); pointer-events: none;
}
.s-inp {
  height: 34px;
  padding-left: 32px;
  border-radius: var(--radius-full);
  font-size: var(--fs-xs);
}
.s-inp::placeholder { color: var(--text-tertiary); }

.toggle-btn {
  display: flex; align-items: center; justify-content: center;
  width: 34px; height: 34px;
  border-radius: var(--radius-md);
  color: var(--text-tertiary);
  background: var(--bg-surface);
  border: 1px solid var(--color-border);
  transition: all 0.15s;
  flex-shrink: 0;
}
.toggle-btn:hover { color: var(--text-primary); border-color: var(--text-tertiary); }

/* ======== Category Tabs — segmented game selector ======== */
.cat-tabs {
  display: flex;
  gap: 2px;
  background: rgba(0,0,0,0.02);
  padding: 3px;
  border-radius: var(--radius-md);
  margin-bottom: 8px;
}
.cat-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 32px;
  padding: 0 12px;
  border-radius: 8px;
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-tertiary);
  transition: all 0.2s;
  white-space: nowrap;
}
.cat-tab:hover { color: var(--text-secondary); }
.cat-tab.on {
  background: var(--bg-surface);
  color: var(--text-primary);
  font-weight: 700;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  color: var(--tab-color, var(--text-primary));
}
.cat-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
  display: inline-block;
}

/* ======== Status Filters ======== */
.st-row {
  display: flex;
  gap: 4px;
  margin-bottom: 20px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.st-row::-webkit-scrollbar { display: none; }
.st-filter {
  flex-shrink: 0;
  height: 24px;
  padding: 0 10px;
  border-radius: 12px;
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  transition: all 0.15s;
}
.st-filter:hover { color: var(--text-secondary); }
.st-filter.on {
  background: var(--bg-surface);
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  color: var(--text-primary);
}

/* ======== Grid ======== */
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
.grid.list { grid-template-columns: 1fr; }
@media (min-width: 640px) { .grid { grid-template-columns: repeat(3, 1fr); gap: 18px; } }
@media (min-width: 960px) { .grid { grid-template-columns: repeat(4, 1fr); } }
@media (min-width: 1200px) { .grid { grid-template-columns: repeat(5, 1fr); } }

/* ======== Empty ======== */
.empty { text-align: center; padding: 80px 20px; }
.empty-box { width: 56px; height: 56px; margin: 0 auto 10px; background: var(--bg-surface); border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; box-shadow: var(--shadow-sm); }
.empty-t { font-size: var(--fs-lg); color: var(--text-secondary); margin-bottom: 4px; }
.empty-d { font-size: var(--fs-sm); color: var(--text-tertiary); }
</style>
