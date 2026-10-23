<script setup>
import { ref, computed, onMounted } from 'vue'
import { bangumiApi } from '../../api/client'
import StateBlock from '../../components/common/StateBlock.vue'
import SkeletonBlock from '../../components/common/SkeletonBlock.vue'

// 发现：今日放送（calendar，6h 缓存）+ 高分榜（ranking，24h 缓存）。
// 卡片只做入口，点击交给外层统一弹出「确认作品信息」入库模态。
const emit = defineEmits(['select'])

const loading = ref(true)
const error = ref(false)
const days = ref([])
const ranking = ref([])
const rankType = ref('2')
const rankLoading = ref(false)
const rankError = ref(false)

const rankTypes = [
  { value: '2', label: '动画' },
  { value: '1', label: '书籍' },
  { value: '4', label: '游戏' },
]

// Bangumi weekday.id 1=周一 … 7=周日；JS getDay() 0=周日
const jsDayToBgm = d => (d === 0 ? 7 : d)
const todayGroup = computed(() => {
  const id = jsDayToBgm(new Date().getDay())
  return days.value.find(d => d.weekday?.id === id) || null
})
const todayCn = computed(() => todayGroup.value?.weekday?.cn || '')

function toBangumiItem(raw) {
  return {
    bangumi_id: raw.id,
    name: raw.name,
    name_cn: raw.name_cn,
    type: raw.type,
    image_url: raw.images?.common || raw.image_url || '',
    summary: raw.summary || '',
  }
}

function coverSrc(item) {
  return item.image_url ? bangumiApi.imageUrl(item.image_url) : ''
}

async function load() {
  loading.value = true
  error.value = false
  try {
    const [cal, rank] = await Promise.all([
      bangumiApi.calendar(),
      bangumiApi.ranking(rankType.value, 10),
    ])
    days.value = cal.data.data || []
    ranking.value = rank.data.data || []
  } catch (e) {
    console.error('Failed to load discover', e)
    error.value = true
  } finally {
    loading.value = false
  }
}

async function loadRanking() {
  rankLoading.value = true
  rankError.value = false
  try {
    const { data } = await bangumiApi.ranking(rankType.value, 10)
    ranking.value = data.data || []
  } catch (e) {
    console.error('Failed to load ranking', e)
    rankError.value = true
  } finally {
    rankLoading.value = false
  }
}

function pickRankType(v) {
  rankType.value = v
  loadRanking()
}

function scoreOf(raw) {
  return raw.rating?.score || null
}

onMounted(load)
</script>

<template>
  <div>
    <StateBlock v-if="error" kind="error" title="发现内容没能加载" @retry="load" />

    <template v-else-if="loading">
      <SkeletonBlock h="26px" w="120px" style="margin-bottom: 12px" />
      <div class="disc-skel">
        <SkeletonBlock v-for="i in 6" :key="i" h="186px" style="flex: none; width: 128px" />
      </div>
      <SkeletonBlock h="26px" w="100px" style="margin: 24px 0 12px" />
      <div class="disc-skel">
        <SkeletonBlock v-for="i in 5" :key="'r' + i" h="64px" style="flex: 1" />
      </div>
    </template>

    <template v-else>
      <section class="disc-sec" aria-labelledby="disc-air-h">
        <h2 id="disc-air-h" class="disc-h">今日放送 <span v-if="todayCn" class="disc-day">{{ todayCn }}</span></h2>
        <div v-if="todayGroup && todayGroup.items.length" class="air-rail" role="list">
          <button
            v-for="raw in todayGroup.items"
            :key="raw.id"
            type="button"
            class="air-card"
            role="listitem"
            @click="emit('select', toBangumiItem(raw))"
          >
            <span class="air-th">
              <img v-if="raw.images?.common" :src="coverSrc(toBangumiItem(raw))" :alt="raw.name_cn || raw.name" loading="lazy" />
            </span>
            <span class="air-nm">{{ raw.name_cn || raw.name }}</span>
            <span v-if="scoreOf(raw)" class="air-score">{{ scoreOf(raw) }}</span>
          </button>
        </div>
        <div v-else class="disc-empty">今天没有放送，去搜索页找找想追的。</div>
      </section>

      <section class="disc-sec" aria-labelledby="disc-rank-h">
        <div class="rank-head">
          <h2 id="disc-rank-h" class="disc-h">高分榜</h2>
          <div class="rank-types" role="radiogroup" aria-label="榜单类型">
            <button
              v-for="t in rankTypes"
              :key="t.value"
              type="button"
              role="radio"
              :aria-checked="rankType === t.value"
              class="rank-type"
              :class="{ on: rankType === t.value }"
              @click="pickRankType(t.value)"
            >
              {{ t.label }}
            </button>
          </div>
        </div>
        <div v-if="rankLoading" class="disc-empty">加载中...</div>
        <div v-else-if="rankError" class="disc-empty">
          榜单没能加载
          <button type="button" class="rank-retry" @click="loadRanking">重试</button>
        </div>
        <ol v-else-if="ranking.length" class="rank-list">
          <li v-for="(raw, i) in ranking" :key="raw.id">
            <button type="button" class="rank-item" @click="emit('select', toBangumiItem(raw))">
              <span class="rank-no" :class="{ top: i < 3 }">{{ i + 1 }}</span>
              <span class="rank-th">
                <img v-if="raw.images?.common" :src="coverSrc(toBangumiItem(raw))" :alt="raw.name_cn || raw.name" loading="lazy" />
              </span>
              <span class="rank-info">
                <span class="rank-nm">{{ raw.name_cn || raw.name }}</span>
                <span class="rank-meta">
                  <span v-if="scoreOf(raw)" class="rank-score">{{ scoreOf(raw) }}</span>
                  <span v-if="raw.date" class="rank-yr">{{ raw.date.slice(0, 4) }}</span>
                </span>
              </span>
            </button>
          </li>
        </ol>
        <div v-else class="disc-empty">榜单暂时是空的。</div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.disc-skel { display: flex; gap: 10px; overflow: hidden; }

.disc-sec { margin-bottom: 28px; }
.disc-h {
  font-size: var(--fs-base);
  font-weight: 800;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.disc-day { font-size: var(--fs-xs); font-weight: 600; color: var(--text-tertiary); }

/* 今日放送横轨 */
.air-rail {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding: 2px 2px 10px;
  scroll-snap-type: x proximity;
}
.air-card {
  flex: none;
  width: 128px;
  scroll-snap-align: start;
  display: flex;
  flex-direction: column;
  text-align: left;
  position: relative;
}
.air-th {
  aspect-ratio: 3 / 4.2;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--bg-input);
  box-shadow: inset 0 0 0 1px var(--color-border);
  display: block;
}
.air-th img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.25s ease; }
.air-card:hover .air-th img { transform: scale(1.04); }
.air-nm {
  margin-top: 6px;
  font-size: var(--fs-xs);
  font-weight: 600;
  line-height: 1.4;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.air-score {
  position: absolute;
  top: 6px;
  right: 6px;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  color: var(--text-primary);
  background: color-mix(in srgb, var(--bg-surface) 88%, transparent);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--s-completed) 55%, transparent);
  backdrop-filter: blur(4px);
}

/* 高分榜 */
.rank-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; flex-wrap: wrap; }
.rank-types { display: flex; gap: 4px; }
.rank-type {
  height: 26px;
  padding: 0 12px;
  border-radius: var(--radius-full);
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  transition: all 0.15s;
}
.rank-type:hover { color: var(--text-secondary); }
.rank-type.on {
  background: var(--bg-surface);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}
.rank-list { list-style: none; display: flex; flex-direction: column; gap: 8px; }
.rank-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 10px;
  border-radius: var(--radius-md);
  text-align: left;
  transition: background 0.15s;
}
.rank-item:hover { background: var(--bg-surface-hover); }
.rank-no {
  flex: none;
  width: 22px;
  font-size: var(--fs-sm);
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  color: var(--text-tertiary);
  text-align: center;
}
.rank-no.top { color: var(--primary); }
.rank-th {
  flex: none;
  width: 44px;
  height: 58px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--bg-input);
  box-shadow: inset 0 0 0 1px var(--color-border);
}
.rank-th img { width: 100%; height: 100%; object-fit: cover; display: block; }
.rank-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.rank-nm {
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rank-meta { display: flex; align-items: center; gap: 8px; }
.rank-score { font-size: var(--fs-xs); font-weight: 800; color: var(--s-completed); font-variant-numeric: tabular-nums; }
.rank-yr { font-size: var(--fs-xs); color: var(--text-tertiary); font-variant-numeric: tabular-nums; }

.disc-empty {
  padding: 24px 12px;
  text-align: center;
  font-size: var(--fs-sm);
  color: var(--text-tertiary);
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  box-shadow: inset 0 0 0 1px var(--color-border);
}
.rank-retry {
  margin-left: 8px;
  font-weight: 700;
  color: var(--primary);
  text-decoration: underline;
  text-underline-offset: 3px;
}

/* 触控目标 44px（Q3 决策） */
@media (pointer: coarse) {
  .air-card { width: 148px; }
  .rank-type, .rank-retry { min-height: 44px; }
  .rank-item { min-height: 44px; }
}
@media (prefers-reduced-motion: reduce) {
  .air-th img { transition: none; }
}
</style>
