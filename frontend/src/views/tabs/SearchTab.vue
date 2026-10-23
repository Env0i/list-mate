<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { bangumiApi } from '../../api/client'

// 搜索 Tab：原独立搜索页的能力（竞态守卫 + 类型实时重筛），
// 封面走本地图床代理；选中项交给外层统一弹出「确认作品信息」入库模态
const emit = defineEmits(['select'])

const route = useRoute()

const q = ref('')
const activeType = ref('all')
const results = ref([])
const searching = ref(false)
const error = ref('')

const typeLabels = [
  { key: 'all', label: '全部' },
  { key: '1', label: '书籍' },
  { key: '2', label: '番剧' },
  { key: '3', label: '音乐' },
  { key: '4', label: '游戏' },
]

function coverUrl(item) {
  return item.image_url ? bangumiApi.imageUrl(item.image_url) : ''
}

function itemTitle(item) {
  return item.name_cn || item.name || '未知'
}

function itemId(item) {
  return item.bangumi_id
}

// 深链 ?q=：进入搜索 Tab 时自动搜索
onMounted(() => {
  const pre = typeof route.query.q === 'string' ? route.query.q.trim() : ''
  if (pre) {
    q.value = pre
    search()
  }
})

// 切换类型时实时重新筛选（已有关键词时），无需手动再点搜索
watch(activeType, () => {
  if (q.value.trim()) search()
})

// 竞态守卫：每次搜索自增序号，响应返回时若已有更新的搜索则丢弃——
// 快速切换类型/重搜时，慢的旧响应不会覆盖新结果
let searchSeq = 0

async function search() {
  if (!q.value.trim()) return
  const seq = ++searchSeq
  searching.value = true
  error.value = ''
  try {
    const type = activeType.value === 'all' ? undefined : activeType.value
    const { data } = await bangumiApi.search(q.value.trim(), type)
    if (seq !== searchSeq) return
    results.value = data.results || data.items || []
  } catch (e) {
    if (seq !== searchSeq) return
    error.value = '搜索失败，请重试'
    results.value = []
  } finally {
    if (seq === searchSeq) searching.value = false
  }
}
</script>

<template>
  <div>
    <!-- Search bar -->
    <div class="search-bar">
      <div class="search-w">
        <svg class="s-icon" viewBox="0 0 20 20" fill="currentColor" width="16" height="16" aria-hidden="true">
          <path fill-rule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clip-rule="evenodd"/>
        </svg>
        <input
          v-model="q"
          class="s-inp"
          placeholder="搜索作品名..."
          aria-label="搜索作品名"
          @keyup.enter="search"
        />
      </div>
      <button class="search-btn" @click="search" :disabled="searching">
        {{ searching ? '搜索中...' : '搜索' }}
      </button>
    </div>

    <!-- Type filter -->
    <div class="type-row" role="radiogroup" aria-label="搜索类型">
      <button
        v-for="t in typeLabels"
        :key="t.key"
        type="button"
        role="radio"
        :aria-checked="activeType === t.key"
        class="type-opt"
        :class="{ on: activeType === t.key }"
        @click="activeType = t.key"
      >
        {{ t.label }}
      </button>
    </div>

    <!-- Error -->
    <p v-if="error" class="err" role="alert">{{ error }}</p>

    <!-- Results -->
    <div v-if="searching" class="loading">搜索中...</div>

    <div v-else-if="results.length" class="results">
      <button
        v-for="item in results"
        :key="itemId(item)"
        type="button"
        class="result-card"
        @click="emit('select', item)"
      >
        <span
          class="rc-cover"
          :style="{ backgroundImage: coverUrl(item) ? `url(${coverUrl(item)})` : 'none' }"
        >
          <span v-if="!coverUrl(item)" class="rc-placeholder">
            <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16" aria-hidden="true">
              <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V4z"/>
            </svg>
          </span>
        </span>
        <span class="rc-title">{{ itemTitle(item) }}</span>
        <span class="rc-meta">
          <span class="rc-type" :class="'rt-' + item.type">{{ typeLabels.find(t => t.key === String(item.type))?.label || '其他' }}</span>
          <span v-if="item.date" class="rc-date">{{ item.date.slice(0, 4) }}</span>
        </span>
      </button>
    </div>

    <div v-else-if="q && !searching && !error" class="empty">
      没有结果，试试别的关键词
    </div>
  </div>
</template>

<style scoped>
/* Search */
.search-bar { display: flex; gap: 8px; margin-bottom: 14px; }
.search-w { flex: 1; position: relative; }
.s-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-tertiary); pointer-events: none; }
.s-inp {
  height: 40px;
  width: 100%;
  padding-left: 36px;
  padding-right: 12px;
  border-radius: var(--radius-md);
  font-size: var(--fs-base);
  background: var(--bg-surface);
  border: 1px solid var(--color-border);
}
.s-inp:focus { border-color: var(--text-tertiary); background: var(--bg-surface); outline: none; }
.search-btn {
  height: 40px;
  padding: 0 24px;
  border-radius: var(--radius-md);
  background: var(--primary);
  color: white;
  font-size: var(--fs-sm);
  font-weight: 700;
  transition: all 0.15s;
  flex-shrink: 0;
}
.search-btn:hover { background: var(--primary-hover); }
.search-btn:disabled { opacity: 0.6; }

/* Type filter */
.type-row { display: flex; gap: 4px; margin-bottom: 20px; }
.type-opt {
  height: 28px;
  padding: 0 12px;
  border-radius: var(--radius-full);
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  transition: all 0.15s;
}
.type-opt:hover { color: var(--text-secondary); }
.type-opt.on {
  background: var(--bg-surface);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}

.err { color: var(--c-anime); font-size: var(--fs-sm); margin-bottom: 12px; }
.loading { text-align: center; padding: 60px 20px; color: var(--text-tertiary); }

/* Results grid */
.results {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
@media (min-width: 640px) { .results { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 900px) { .results { grid-template-columns: repeat(4, 1fr); } }

.result-card {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: var(--shadow-sm);
  display: block;
  text-align: left;
}
.result-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.rc-cover {
  display: flex;
  align-items: center;
  justify-content: center;
  aspect-ratio: 3 / 4;
  background-color: var(--bg-input);
  background-size: cover;
  background-position: center;
}
.rc-placeholder { color: var(--text-tertiary); opacity: 0.2; }
.rc-title {
  display: block;
  padding: 10px 12px 4px;
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rc-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 12px 10px;
}
.rc-type {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-tertiary);
  background: var(--bg-input);
  padding: 1px 6px;
  border-radius: 3px;
}
.rt-2 { color: var(--c-anime); }
.rt-4 { color: var(--c-game); }
.rc-date { font-size: 10px; color: var(--text-tertiary); font-variant-numeric: tabular-nums; }

.empty { text-align: center; padding: 60px 20px; color: var(--text-tertiary); }

/* 触屏：操作控件达到 44px 触控目标（Q3 决策） */
@media (pointer: coarse) {
  .type-opt, .search-btn { min-height: 44px; }
}
</style>
