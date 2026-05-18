<script setup>
import { ref, computed, onMounted } from 'vue'
import { statsApi, timelineApi } from '../api/client'

const stats = ref(null)
const timeline = ref([])
const loading = ref(true)
const timelineLoading = ref(true)

onMounted(async () => {
  try {
    const [statsRes, tlRes] = await Promise.all([
      statsApi.get(),
      timelineApi.list({ page_size: 50 }),
    ])
    stats.value = statsRes.data
    timeline.value = tlRes.data.items
  } catch (e) {
    console.error('Failed to load stats', e)
  } finally {
    loading.value = false
    timelineLoading.value = false
  }
})

const catLabels = { anime: '番剧', novel: '小说', comic: '漫画', game: '游戏' }
const catColors = { anime: 'var(--c-anime)', novel: 'var(--c-novel)', comic: 'var(--c-comic)', game: 'var(--c-game)' }
const catBgColors = {
  anime: 'rgba(255,26,94,.08)',
  novel: 'rgba(51,102,255,.08)',
  comic: 'rgba(0,204,102,.08)',
  game: 'rgba(255,122,0,.08)',
}

const statusLabels = {
  wish: '想看', watching: '在看', completed: '看完', paused: '暂停', dropped: '弃了',
  playing: '在玩', wait_buy: '等购买', wait_sale: '等折扣',
}
const statusColors = {
  wish: 'var(--s-wish)', watching: 'var(--s-watching)', completed: 'var(--s-completed)',
  paused: 'var(--s-paused)', dropped: 'var(--s-dropped)',
  playing: 'var(--s-watching)', wait_buy: 'var(--s-paused)', wait_sale: '#FF8C00',
}

const actionLabels = {
  created: '添加', status_change: '状态变更', rating_change: '评分变更',
  review_change: '评价变更', progress_update: '进度更新',
}

const maxCatCount = computed(() => stats.value ? Math.max(...stats.value.category_counts.map(c => c.count), 1) : 1)
const maxStatusCount = computed(() => stats.value ? Math.max(...stats.value.status_counts.map(s => s.count), 1) : 1)
const maxRatingCount = computed(() => stats.value ? Math.max(...stats.value.rating_distribution.map(r => r.count), 1) : 1)

const sortedRatings = computed(() => {
  if (!stats.value) return []
  const dist = [...stats.value.rating_distribution]
  dist.sort((a, b) => a.rating - b.rating)
  return dist
})

function workTitle(wid) {
  return `#${wid}`
}

function formatValue(actionType, oldVal, newVal) {
  if (actionType === 'status_change') {
    const o = oldVal ? (statusLabels[oldVal] || oldVal) : '无'
    const n = newVal ? (statusLabels[newVal] || newVal) : '无'
    return `${o} → ${n}`
  }
  if (actionType === 'rating_change') {
    const o = oldVal != null ? `${oldVal}/10` : '未评分'
    const n = newVal != null ? `${newVal}/10` : '未评分'
    return `${o} → ${n}`
  }
  if (actionType === 'progress_update') {
    return `${oldVal ?? '—'} → ${newVal ?? '—'}`
  }
  if (actionType === 'created') {
    try { return JSON.parse(newVal).title }
    catch { return newVal }
  }
  return newVal ? String(newVal).slice(0, 60) : ''
}

function timeAgo(ts) {
  const d = new Date(ts)
  const now = new Date()
  const diff = now - d
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins}分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}天前`
  const months = Math.floor(days / 30)
  if (months < 12) return `${months}个月前`
  return `${Math.floor(months / 12)}年前`
}
</script>

<template>
  <div class="page">
    <div class="page-inner">
      <!-- Header -->
      <div class="hd">
        <h1 class="title">统计</h1>
      </div>

      <div v-if="loading" class="loading">加载中...</div>

      <template v-else-if="stats">
        <!-- Overview cards -->
        <div class="overview">
          <div v-for="c in stats.category_counts" :key="c.category" class="ov-card" :style="{ background: catBgColors[c.category], borderColor: catColors[c.category] + '20' }">
            <span class="ov-num" :style="{ color: catColors[c.category] }">{{ c.count }}</span>
            <span class="ov-label">{{ catLabels[c.category] || c.category }}</span>
          </div>
          <div class="ov-card total-card">
            <span class="ov-num">{{ stats.total_works }}</span>
            <span class="ov-label">总计</span>
          </div>
        </div>

        <!-- Charts row -->
        <div class="charts">
          <!-- Category -->
          <div class="chart-card">
            <h3 class="chart-h">品类分布</h3>
            <div class="bar-list">
              <div v-for="c in stats.category_counts" :key="c.category" class="bar-row">
                <span class="bar-label">{{ catLabels[c.category] || c.category }}</span>
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: (c.count / maxCatCount * 100) + '%', background: catColors[c.category] }" />
                </div>
                <span class="bar-num" :style="{ color: catColors[c.category] }">{{ c.count }}</span>
              </div>
            </div>
          </div>

          <!-- Status -->
          <div class="chart-card">
            <h3 class="chart-h">状态分布</h3>
            <div class="bar-list">
              <div v-for="s in stats.status_counts" :key="s.status" class="bar-row">
                <span class="bar-label">{{ statusLabels[s.status] || s.status }}</span>
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: (s.count / maxStatusCount * 100) + '%', background: statusColors[s.status] || '#ccc' }" />
                </div>
                <span class="bar-num" :style="{ color: statusColors[s.status] || '#ccc' }">{{ s.count }}</span>
              </div>
            </div>
          </div>

          <!-- Rating -->
          <div class="chart-card">
            <h3 class="chart-h">评分分布</h3>
            <div class="bar-list">
              <div v-for="r in sortedRatings" :key="r.rating" class="bar-row">
                <span class="bar-label">{{ r.rating === -1 ? '未评分' : r.rating + '分' }}</span>
                <div class="bar-track">
                  <div class="bar-fill rating-fill" :style="{ width: (r.count / maxRatingCount * 100) + '%' }" :class="{ dim: r.rating === -1 }" />
                </div>
                <span class="bar-num">{{ r.count }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Timeline -->
        <div class="tl-section" v-if="timeline.length">
          <h2 class="tl-title">最近动态</h2>
          <div class="tl-list">
            <div v-for="entry in timeline" :key="entry.id" class="tl-item">
              <div class="tl-dot" :class="'dot-' + entry.action_type" />
              <div class="tl-content">
                <div class="tl-head">
                  <span class="tl-action">{{ actionLabels[entry.action_type] || entry.action_type }}</span>
                  <span class="tl-work">作品 #{{ entry.work_id }}</span>
                  <span v-if="entry.game_profile_id" class="tl-gp">配置 #{{ entry.game_profile_id }}</span>
                </div>
                <div class="tl-detail">{{ formatValue(entry.action_type, entry.old_value, entry.new_value) }}</div>
                <div class="tl-time">{{ timeAgo(entry.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 20px 16px; }
@media (min-width: 768px) { .page { padding: 24px 32px; } }
.page-inner { max-width: 1000px; margin: 0 auto; }

/* Header */
.hd { margin-bottom: 20px; }
.title { font-size: var(--fs-2xl); font-weight: 800; letter-spacing: -0.5px; }

.loading { text-align: center; padding: 80px 20px; color: var(--text-tertiary); }

/* Overview cards */
.overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}
.ov-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 20px 16px;
  border-radius: var(--radius-lg);
  border: 1px solid;
  background: var(--bg-surface);
}
.ov-num {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -1px;
  line-height: 1;
}
.ov-label {
  font-size: var(--fs-xs);
  color: var(--text-tertiary);
  font-weight: 600;
}
.total-card {
  background: var(--bg-surface);
  border-color: var(--color-border) !important;
}
.total-card .ov-num { color: var(--text-primary); }

/* Charts */
.charts {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  margin-bottom: 32px;
}
@media (min-width: 768px) {
  .charts { grid-template-columns: repeat(2, 1fr); }
}

.chart-card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-sm);
}
.chart-h {
  font-size: var(--fs-sm);
  font-weight: 700;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.bar-list { display: flex; flex-direction: column; gap: 8px; }
.bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.bar-label {
  width: 50px;
  flex-shrink: 0;
  font-size: var(--fs-xs);
  color: var(--text-tertiary);
  font-weight: 600;
  text-align: right;
}
.bar-track {
  flex: 1;
  height: 10px;
  border-radius: 5px;
  background: var(--bg-input);
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.6s ease;
  min-width: 4px;
}
.rating-fill { background: var(--primary); }
.rating-fill.dim { background: var(--text-tertiary); opacity: 0.4; }
.bar-num {
  width: 28px;
  flex-shrink: 0;
  font-size: var(--fs-xs);
  font-weight: 700;
  color: var(--text-secondary);
  text-align: left;
}

/* Timeline */
.tl-section { margin-top: 8px; }
.tl-title {
  font-size: var(--fs-lg);
  font-weight: 700;
  margin-bottom: 16px;
}
.tl-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.tl-item {
  display: flex;
  gap: 14px;
  padding: 12px 0;
  border-bottom: 1px solid var(--color-border);
}
.tl-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 5px;
  background: var(--text-tertiary);
}
.dot-created { background: #00B85A; }
.dot-status_change { background: #3366FF; }
.dot-rating_change { background: #FFB800; }
.dot-review_change { background: #8b5cf6; }
.dot-progress_update { background: var(--primary); }

.tl-content { flex: 1; min-width: 0; }
.tl-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}
.tl-action {
  font-size: var(--fs-xs);
  font-weight: 700;
}
.tl-work, .tl-gp {
  font-size: 11px;
  color: var(--text-tertiary);
}
.tl-detail {
  font-size: var(--fs-sm);
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tl-time {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-top: 2px;
}
</style>
