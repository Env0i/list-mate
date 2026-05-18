<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { worksApi, tagsApi } from '../api/client'
import WorkCardGrid from '../components/work/WorkCardGrid.vue'

const router = useRouter()
const activeCat = ref('all')
const activeSt = ref('all')
const q = ref('')
const works = ref([])
const loading = ref(true)
const tags = ref([])
const activeTagId = ref(null)

onMounted(async () => {
  try {
    const [worksRes, tagsRes] = await Promise.all([
      worksApi.list({ page_size: 100 }),
      tagsApi.list(),
    ])
    works.value = worksRes.data.items
    tags.value = tagsRes.data
  } catch (e) {
    console.error('Failed to load data', e)
  } finally {
    loading.value = false
  }
})

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
  works.value.filter(w => {
    if (activeCat.value !== 'all' && w.category !== activeCat.value) return false
    if (activeSt.value !== 'all' && workStatus(w) !== activeSt.value) return false
    if (activeTagId.value && !(w.tag_ids || []).includes(activeTagId.value)) return false
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

      <!-- Tag filter chips -->
      <div v-if="tags.length" class="tag-row">
        <button
          class="tag-filter"
          :class="{ on: activeTagId === null }"
          @click="activeTagId = null"
        >全部标签</button>
        <button
          v-for="t in tags"
          :key="t.id"
          class="tag-filter"
          :class="{ on: activeTagId === t.id }"
          :style="activeTagId === t.id ? { background: t.color, color: '#fff', borderColor: t.color } : { color: t.color, borderColor: t.color + '40' }"
          @click="activeTagId = activeTagId === t.id ? null : t.id"
        >
          <span class="tag-filter-dot" :style="{ background: t.color }" />
          {{ t.name }}
        </button>
      </div>

      <!-- Grid -->
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="filtered.length" class="grid">
        <div v-for="(w, i) in filtered" :key="w.id" :style="{ animationDelay: (i % 12) * 0.04 + 's' }" @click="router.push(`/works/${w.id}`)">
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

/* ======== Tag filter chips ======== */
.tag-row {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  padding-bottom: 2px;
}
.tag-row::-webkit-scrollbar { display: none; }
.tag-filter {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 4px;
  height: 24px;
  padding: 0 10px;
  border-radius: 12px;
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  border: 1px solid transparent;
  transition: all 0.15s;
}
.tag-filter:hover { opacity: 0.8; }
.tag-filter.on { font-weight: 700; }
.tag-filter-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ======== Loading ======== */
.loading { text-align: center; padding: 80px 20px; color: var(--text-tertiary); }

/* ======== Grid ======== */
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
@media (min-width: 640px) { .grid { grid-template-columns: repeat(3, 1fr); gap: 18px; } }
@media (min-width: 960px) { .grid { grid-template-columns: repeat(4, 1fr); } }
@media (min-width: 1200px) { .grid { grid-template-columns: repeat(5, 1fr); } }

/* ======== Empty ======== */
.empty { text-align: center; padding: 80px 20px; }
.empty-box { width: 56px; height: 56px; margin: 0 auto 10px; background: var(--bg-surface); border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; box-shadow: var(--shadow-sm); }
.empty-t { font-size: var(--fs-lg); color: var(--text-secondary); margin-bottom: 4px; }
.empty-d { font-size: var(--fs-sm); color: var(--text-tertiary); }
</style>
