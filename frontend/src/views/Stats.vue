<script setup>
import { ref, computed, onMounted } from 'vue'
import { statsApi, timelineApi } from '../api/client'
import { exportApi } from '../api/client'
import { STATUS_LABELS_FLAT, STATUS_COLORS } from '../constants/work'
import { actionLabels, actionIcons, formatValue, timeAgo } from '../utils/timeline'

const stats = ref(null)
const timeline = ref([])
const loading = ref(true)
const timelineLoading = ref(true)
const activeTab = ref('overview')

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
  anime: 'var(--c-anime-bg)',
  novel: 'var(--c-novel-bg)',
  comic: 'var(--c-comic-bg)',
  game: 'var(--c-game-bg)',
}
const catIcons = {
  anime: '◆',
  novel: '■',
  comic: '●',
  game: '★',
}

const statusLabels = STATUS_LABELS_FLAT
const statusColors = STATUS_COLORS

const maxCatCount = computed(() => stats.value ? Math.max(...stats.value.category_counts.map(c => c.count), 1) : 1)
const maxStatusCount = computed(() => stats.value ? Math.max(...stats.value.status_counts.map(s => s.count), 1) : 1)
const maxRatingCount = computed(() => stats.value ? Math.max(...stats.value.rating_distribution.map(r => r.count), 1) : 1)

const sortedRatings = computed(() => {
  if (!stats.value) return []
  const dist = [...stats.value.rating_distribution]
  dist.sort((a, b) => a.rating - b.rating)
  return dist
})

const totalWish = computed(() => {
  if (!stats.value) return 0
  return stats.value.status_counts
    .filter(s => s.status === 'wish' || s.status === 'watching' || s.status === 'playing')
    .reduce((sum, s) => sum + s.count, 0)
})

const totalCompleted = computed(() => {
  if (!stats.value) return 0
  return stats.value.status_counts
    .filter(s => s.status === 'completed')
    .reduce((sum, s) => sum + s.count, 0)
})

function ratingRank(rating) {
  if (rating === -1) return { label: '--', color: '#ccc' }
  if (rating >= 9) return { label: 'S', color: '#FF6B35' }
  if (rating >= 7) return { label: 'A', color: '#3366FF' }
  if (rating >= 5) return { label: 'B', color: '#00CC66' }
  return { label: 'C', color: '#A39F98' }
}
</script>

<template>
  <div class="page">
    <div class="page-inner">
      <!-- Header -->
      <div class="hd">
        <div class="hd-left">
          <h1 class="title">
            <svg class="title-icon" viewBox="0 0 20 20" fill="currentColor" width="22" height="22">
              <path d="M1.827144 981.176313m21.354745 0l977.636222 0q21.354745 0 21.354745 21.354745l0 0.114197q0 21.354745-21.354745 21.354745l-977.636222 0q-21.354745 0-21.354745-21.354745l0-0.114197q0-21.354745 21.354745-21.354745Z"/>
              <path d="M44.650831 0m0 21.354745l0 977.636222q0 21.354745-21.354745 21.354745l-0.114197 0q-21.354745 0-21.354745-21.354745l0-977.636222q0-21.354745 21.354745-21.354745l0.114197 0q21.354745 0 21.354745 21.354745Z"/>
              <path d="M432.303425 402.092949m-15.100086 15.100085l-220.122096 220.122097q-15.100085 15.100085-30.20017 0l-0.080749-0.08075q-15.100085-15.100085 0-30.20017l220.122096-220.122096q15.100085-15.100085 30.20017 0l0.080749 0.080749q15.100085 15.100085 0 30.20017Z"/>
              <path d="M402.03781 371.717901m15.100085 15.100086l220.122097 220.122096q15.100085 15.100085 0 30.20017l-0.080749 0.08075q-15.100085 15.100085-30.200171 0l-220.122096-220.122097q-15.100085-15.100085 0-30.20017l0.080749-0.080749q15.100085-15.100085 30.20017 0Z"/>
              <path d="M872.344866 402.029735m-15.100085 15.100085l-220.122096 220.122097q-15.100085 15.100085-30.200171 0l-0.080749-0.080749q-15.100085-15.100085 0-30.200171l220.122097-220.122096q15.100085-15.100085 30.20017 0l0.080749 0.080749q15.100085 15.100085 0 30.20017Z"/>
            </svg>
            收集统计
          </h1>
          <p class="subtitle">你的 ACGN 收藏数据总览</p>
        </div>
        <div class="hd-actions">
          <a :href="exportApi.jsonUrl()" class="export-btn" download title="导出 JSON">
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
              <path d="M10.75 2.75a.75.75 0 00-1.5 0v8.614L6.295 8.235a.75.75 0 10-1.09 1.03l4.25 4.5a.75.75 0 001.09 0l4.25-4.5a.75.75 0 00-1.09-1.03l-2.955 3.129V2.75z"/>
              <path d="M3.5 12.75a.75.75 0 00-1.5 0v2.5A2.75 2.75 0 004.75 18h10.5A2.75 2.75 0 0018 15.25v-2.5a.75.75 0 00-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5z"/>
            </svg>
            <span class="export-label">JSON</span>
          </a>
          <a :href="exportApi.csvUrl()" class="export-btn" download title="导出 CSV">
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
              <path d="M10.75 2.75a.75.75 0 00-1.5 0v8.614L6.295 8.235a.75.75 0 10-1.09 1.03l4.25 4.5a.75.75 0 001.09 0l4.25-4.5a.75.75 0 00-1.09-1.03l-2.955 3.129V2.75z"/>
              <path d="M3.5 12.75a.75.75 0 00-1.5 0v2.5A2.75 2.75 0 004.75 18h10.5A2.75 2.75 0 0018 15.25v-2.5a.75.75 0 00-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5z"/>
            </svg>
            <span class="export-label">CSV</span>
          </a>
        </div>
      </div>

      <div v-if="loading" class="loading">
        <div class="loading-dots">
          <span class="dot" v-for="i in 3" :key="i" :style="{ animationDelay: i * 0.15 + 's' }" />
        </div>
        <span class="loading-text">加载中...</span>
      </div>

      <template v-else-if="stats">
        <!-- Tab switcher -->
        <div class="tabs">
          <button class="tab" :class="{ on: activeTab === 'overview' }" @click="activeTab = 'overview'">
            <svg class="tab-icon" viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
              <path d="M2 11h3v6H2v-6zm6-4h3v10H8V7zm6-4h3v14h-3V3z"/>
            </svg>
            数据总览
          </button>
          <button class="tab" :class="{ on: activeTab === 'timeline' }" @click="activeTab = 'timeline'">
            <svg class="tab-icon" viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
              <path fill-rule="evenodd" d="M4.25 2A2.25 2.25 0 002 4.25v11.5A2.25 2.25 0 004.25 18h11.5A2.25 2.25 0 0018 15.75V4.25A2.25 2.25 0 0015.75 2H4.25zM4.5 5.5a1 1 0 011-1h9a1 1 0 010 2h-9a1 1 0 01-1-1zm0 4a1 1 0 011-1h5a1 1 0 010 2h-5a1 1 0 01-1-1zm0 4a1 1 0 011-1h3a1 1 0 010 2h-3a1 1 0 01-1-1z" clip-rule="evenodd"/>
            </svg>
            操作记录
          </button>
        </div>

        <!-- ===== OVERVIEW TAB ===== -->
        <template v-if="activeTab === 'overview'">
          <!-- Quick stats chips -->
          <div class="quick-chips">
            <div class="chip">
              <span class="chip-num">{{ stats.total_works }}</span>
              <span class="chip-label">全部作品</span>
            </div>
            <div class="chip chip-wish">
              <span class="chip-num">{{ totalWish }}</span>
              <span class="chip-label">进行中</span>
            </div>
            <div class="chip chip-done">
              <span class="chip-num">{{ totalCompleted }}</span>
              <span class="chip-label">已完成</span>
            </div>
          </div>

          <!-- Category badges row -->
          <div class="cat-badges">
            <div
              v-for="c in stats.category_counts"
              :key="c.category"
              class="cat-badge"
              :style="{
                '--cat-color': catColors[c.category],
                '--cat-bg': catBgColors[c.category],
              }"
            >
              <span class="cat-badge-icon">{{ catIcons[c.category] }}</span>
              <div class="cat-badge-info">
                <span class="cat-badge-name">{{ catLabels[c.category] || c.category }}</span>
                <span class="cat-badge-count">{{ c.count }}</span>
              </div>
              <div class="cat-badge-bar">
                <div
                  class="cat-badge-fill"
                  :style="{ width: (c.count / maxCatCount * 100) + '%' }"
                />
              </div>
            </div>
          </div>

          <!-- Charts grid -->
          <div class="charts">
            <!-- Status distribution -->
            <div class="chart-card">
              <div class="chart-h">
                <span class="chart-dot" style="background: var(--c-game);" />
                状态分布
              </div>
              <div class="bar-list">
                <div
                  v-for="s in stats.status_counts"
                  :key="s.status"
                  class="bar-row"
                >
                  <span class="bar-label">{{ statusLabels[s.status] || s.status }}</span>
                  <div class="bar-track">
                    <div
                      class="bar-fill"
                      :style="{
                        width: (s.count / maxStatusCount * 100) + '%',
                        background: statusColors[s.status] || '#ccc',
                      }"
                    />
                  </div>
                  <span class="bar-num" :style="{ color: statusColors[s.status] || '#ccc' }">{{ s.count }}</span>
                </div>
              </div>
            </div>

            <!-- Rating distribution -->
            <div class="chart-card">
              <div class="chart-h">
                <span class="chart-dot" style="background: var(--primary);" />
                评分分布
              </div>
              <div class="bar-list">
                <div
                  v-for="r in sortedRatings"
                  :key="r.rating"
                  class="bar-row"
                >
                  <span class="bar-label bar-label-rating">
                    <template v-if="r.rating === -1">
                      <span class="rank-badge" style="background:#e0ddd8;color:#999">--</span>
                    </template>
                    <template v-else>
                      <span class="rank-badge" :style="{ background: ratingRank(r.rating).color + '22', color: ratingRank(r.rating).color }">
                        {{ ratingRank(r.rating).label }}
                      </span>
                    </template>
                    {{ r.rating === -1 ? '未评分' : r.rating + '分' }}
                  </span>
                  <div class="bar-track">
                    <div
                      class="bar-fill rating-fill"
                      :class="{ dim: r.rating === -1 }"
                      :style="{ width: (r.count / maxRatingCount * 100) + '%' }"
                    />
                  </div>
                  <span class="bar-num">{{ r.count }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Rating legend -->
          <div class="legend">
            <span class="legend-label">等级</span>
            <span class="legend-item"><span class="legend-dot" style="background:#FF6B35" /> S (9-10)</span>
            <span class="legend-item"><span class="legend-dot" style="background:#3366FF" /> A (7-8)</span>
            <span class="legend-item"><span class="legend-dot" style="background:#00CC66" /> B (5-6)</span>
            <span class="legend-item"><span class="legend-dot" style="background:#A39F98" /> C (0-4)</span>
          </div>
        </template>

        <!-- ===== TIMELINE TAB ===== -->
        <template v-if="activeTab === 'timeline'">
          <div class="tl-section" v-if="timeline.length">
            <div class="tl-scroll">
              <div class="tl-list">
                <div v-for="entry in timeline" :key="entry.id" class="tl-item" :class="'tl-' + entry.action_type">
                  <div class="tl-marker">
                    <div class="tl-dot" :class="'dot-' + entry.action_type" />
                    <div class="tl-line" />
                  </div>
                  <div class="tl-content">
                    <div class="tl-head">
                      <span class="tl-icon">{{ actionIcons[entry.action_type] || '·' }}</span>
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
          </div>
          <div v-else-if="!timelineLoading" class="empty-tl">
            <p>暂无操作记录</p>
          </div>
          <div v-else class="loading">
            <div class="loading-dots">
              <span class="dot" v-for="i in 3" :key="i" :style="{ animationDelay: i * 0.15 + 's' }" />
            </div>
            <span class="loading-text">加载中...</span>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 20px 16px; }
@media (min-width: 768px) { .page { padding: 24px 32px; } }
.page-inner { max-width: 1000px; margin: 0 auto; }

/* Header */
.hd {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
  gap: 16px;
}
@media (max-width: 480px) { .hd { flex-direction: column; } }
.hd-left { min-width: 0; }
.title {
  font-size: var(--fs-2xl);
  font-weight: 800;
  letter-spacing: -0.5px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.title-icon { font-size: 1.3em; }
.subtitle { font-size: var(--fs-sm); color: var(--text-tertiary); margin-top: 2px; }

.hd-actions { display: flex; gap: 6px; flex-shrink: 0; }
.export-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 32px;
  padding: 0 13px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  background: var(--bg-surface);
  border: 1px solid var(--color-border);
  transition: all 0.15s;
}
.export-btn:hover {
  color: var(--text-primary);
  border-color: var(--text-tertiary);
  box-shadow: var(--shadow-sm);
}

/* Loading */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--text-tertiary);
  gap: 12px;
}
.loading-dots { display: flex; gap: 6px; }
.dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--text-tertiary);
  animation: bounce-dot 1s ease-in-out infinite;
}
@keyframes bounce-dot {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}
.loading-text { font-size: var(--fs-sm); }

/* Tabs */
.tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
  background: var(--bg-surface);
  padding: 4px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  max-width: 320px;
}
.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 34px;
  padding: 0 16px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-tertiary);
  background: transparent;
  transition: all 0.2s;
  cursor: pointer;
}
.tab.on {
  color: var(--text-primary);
  background: var(--bg-primary);
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.tab-icon { font-size: 1em; }

/* Quick chips */
.quick-chips {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
@media (max-width: 480px) {
  .quick-chips { gap: 8px; }
  .chip { padding: 10px 12px; gap: 8px; }
}
.chip {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  flex: 1;
  border: 1px solid var(--color-border);
  transition: transform 0.15s, box-shadow 0.15s;
}
.chip:hover { transform: translateY(-1px); box-shadow: var(--shadow-md); }
.chip-num {
  font-size: 1.6rem;
  font-weight: 800;
  letter-spacing: -1px;
  line-height: 1;
  color: var(--text-primary);
}
.chip-label {
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  white-space: nowrap;
}
.chip-wish { border-left: 3px solid var(--s-watching); }
.chip-done { border-left: 3px solid var(--s-completed); }

/* Category badges */
.cat-badges {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}
.cat-badge {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
  transition: all 0.2s;
  cursor: default;
}
.cat-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 0 1.5px var(--cat-color), var(--shadow-md);
}
.cat-badge-icon {
  font-size: 1.3rem;
  color: var(--cat-color);
}
.cat-badge-info {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}
.cat-badge-name {
  font-size: var(--fs-sm);
  font-weight: 700;
  color: var(--text-secondary);
}
.cat-badge-count {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -1px;
  line-height: 1;
  color: var(--cat-color);
}
.cat-badge-bar {
  height: 4px;
  border-radius: 2px;
  background: var(--bg-input);
  overflow: hidden;
}
.cat-badge-fill {
  height: 100%;
  border-radius: 2px;
  background: var(--cat-color);
  transition: width 0.8s ease;
  opacity: 0.5;
}

/* Charts */
.charts {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
  margin-bottom: 20px;
}
@media (min-width: 768px) {
  .charts { grid-template-columns: repeat(2, 1fr); }
}

.chart-card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
  transition: box-shadow 0.15s;
}
.chart-card:hover { box-shadow: var(--shadow-md); }

.chart-h {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--fs-sm);
  font-weight: 700;
  color: var(--text-secondary);
  margin-bottom: 16px;
}
.chart-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.bar-list { display: flex; flex-direction: column; gap: 10px; }
.bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.bar-label {
  width: 64px;
  flex-shrink: 0;
  font-size: var(--fs-xs);
  color: var(--text-tertiary);
  font-weight: 600;
  text-align: right;
}
.bar-label-rating {
  display: flex;
  align-items: center;
  gap: 6px;
}
.bar-track {
  flex: 1;
  height: 12px;
  border-radius: 6px;
  background: var(--bg-input);
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.6s ease;
  min-width: 4px;
  background-image: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.15) 100%);
}
.rating-fill {
  background: linear-gradient(90deg, var(--primary), var(--c-game));
}
.rating-fill.dim {
  background: linear-gradient(90deg, #ccc, #ddd);
  opacity: 0.5;
}
.bar-num {
  width: 28px;
  flex-shrink: 0;
  font-size: var(--fs-xs);
  font-weight: 700;
  color: var(--text-secondary);
  text-align: left;
}

/* Rank badge */
.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 800;
}

/* Rating legend */
.legend {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding: 10px 16px;
  background: var(--bg-surface);
  border-radius: var(--radius-sm);
  font-size: var(--fs-xs);
  color: var(--text-tertiary);
  border: 1px solid var(--color-border);
  margin-bottom: 24px;
}
.legend-label { font-weight: 700; }
.legend-item { display: inline-flex; align-items: center; gap: 4px; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }

/* Timeline */
.tl-section { position: relative; }
.tl-scroll {
  max-height: 600px;
  overflow-y: auto;
  padding-right: 4px;
}
.tl-scroll::-webkit-scrollbar { width: 4px; }
.tl-scroll::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.06); border-radius: 2px; }

.tl-list { position: relative; }
.tl-item {
  display: flex;
  gap: 14px;
  padding: 0 0 6px 0;
  position: relative;
}
.tl-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20px;
  flex-shrink: 0;
}
.tl-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 5px;
  background: var(--text-tertiary);
  border: 2px solid var(--bg-primary);
  z-index: 1;
  transition: transform 0.15s;
}
.tl-item:hover .tl-dot { transform: scale(1.3); }
.dot-created { background: #00B85A; }
.dot-status_change { background: #3366FF; }
.dot-rating_change { background: #FFB800; }
.dot-review_change { background: #8b5cf6; }
.dot-progress_update { background: var(--primary); }
.tl-line {
  width: 1.5px;
  flex: 1;
  background: var(--color-border);
  min-height: 30px;
}
.tl-item:last-child .tl-line { display: none; }
.tl-item:last-child { padding-bottom: 0; }

.tl-content {
  flex: 1;
  min-width: 0;
  padding-bottom: 16px;
}
.tl-head {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 3px;
}
.tl-icon {
  font-size: 12px;
  width: 16px;
  text-align: center;
  color: var(--text-tertiary);
}
.tl-action {
  font-size: var(--fs-xs);
  font-weight: 700;
}
.tl-work, .tl-gp {
  font-size: 10px;
  color: var(--text-tertiary);
  padding: 1px 6px;
  border-radius: 3px;
  background: var(--bg-primary);
}
.tl-detail {
  font-size: var(--fs-sm);
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-left: 22px;
}
.tl-time {
  font-size: 10px;
  color: var(--text-tertiary);
  margin-top: 2px;
  padding-left: 22px;
}
.empty-tl {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-tertiary);
  font-size: var(--fs-sm);
}
</style>
