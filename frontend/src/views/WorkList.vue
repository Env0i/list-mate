<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { worksApi, tagsApi, gameProfilesApi } from '../api/client'
import { STATUS_COLORS, CATEGORIES } from '../constants/work'
import WorkCardGrid from '../components/work/WorkCardGrid.vue'
import ProgressBar from '../components/work/ProgressBar.vue'
import CategoryBadge from '../components/work/CategoryBadge.vue'
import StatusStamp from '../components/work/StatusStamp.vue'
import SegmentedControl from '../components/common/SegmentedControl.vue'
import FilterChip from '../components/common/FilterChip.vue'
import StateBlock from '../components/common/StateBlock.vue'
import SkeletonBlock from '../components/common/SkeletonBlock.vue'
import ThemeToggle from '../components/layout/ThemeToggle.vue'
import { showToast } from '../utils/toast'

const router = useRouter()
const route = useRoute()

// —— 偏好持久化：筛选/搜索/排序/视图存 localStorage，刷新与下次访问不丢 ——
const PREFS_KEY = 'zace-prefs-list'
function loadPrefs() {
  try { return JSON.parse(localStorage.getItem(PREFS_KEY)) || {} } catch { return {} }
}
const savedPrefs = loadPrefs()

const activeCat = ref(savedPrefs.cat ?? 'all')
const activeSt = ref(savedPrefs.st ?? 'all')
const activeTagId = ref(savedPrefs.tagId ?? null)
const q = ref(savedPrefs.q ?? '')
const view = ref(savedPrefs.view === 'list' ? 'list' : 'grid')
const SORTS = [
  { key: 'updated', label: '最近更新' },
  { key: 'rating', label: '评分优先' },
  { key: 'priority', label: '优先度' },
  { key: 'title', label: '标题' },
]
const sortBy = ref(SORTS.some(s => s.key === savedPrefs.sort) ? savedPrefs.sort : 'updated')

watch([activeCat, activeSt, activeTagId, q, sortBy, view], () => {
  localStorage.setItem(PREFS_KEY, JSON.stringify({
    cat: activeCat.value, st: activeSt.value, tagId: activeTagId.value, q: q.value, sort: sortBy.value, view: view.value,
  }))
})

const works = ref([])
const tags = ref([])
const loading = ref(true)
const error = ref(false)

async function load() {
  loading.value = true
  error.value = false
  try {
    const [worksRes, tagsRes] = await Promise.all([
      worksApi.list({ page_size: 500 }),
      tagsApi.list(),
    ])
    works.value = worksRes.data.items
    tags.value = tagsRes.data
    // 恢复的标签筛选若已失效则清掉
    if (activeTagId.value && !tags.value.some(t => t.id === activeTagId.value)) {
      activeTagId.value = null
    }
  } catch (e) {
    console.error('Failed to load data', e)
    error.value = true
  } finally {
    loading.value = false
  }
}
onMounted(load)

// —— 贴纸集等外部入口的 ?tag= 深链 ——
watch(() => route.query.tag, (v) => {
  if (v == null) return
  const id = Number(v)
  if (tags.value.some(t => t.id === id)) activeTagId.value = id
}, { immediate: false })

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

// 状态筛选：「全部」品类用合并语义集（原型做法），单品类用各自枚举；固定顺序、空项置灰
const ST_COLOR = {
  wish: 'var(--s-wish)', active: 'var(--s-watching)', watching: 'var(--s-watching)',
  playing: 'var(--s-watching)', completed: 'var(--s-completed)', paused: 'var(--s-paused)',
  wait_buy: 'var(--s-paused)', dropped: 'var(--s-dropped)', wait_sale: 'var(--s-wait-sale)',
}
const stSets = {
  all: [
    { key: 'all', label: '全部状态' },
    { key: 'wish', label: '想看/想玩' },
    { key: 'active', label: '进行中' },
    { key: 'completed', label: '已完成' },
    { key: 'paused', label: '暂停' },
    { key: 'dropped', label: '弃了/弃坑' },
    { key: 'wait_sale', label: '等折扣' },
  ],
  media: [
    { key: 'all', label: '全部状态' },
    { key: 'wish', label: '想看' },
    { key: 'watching', label: '在看' },
    { key: 'completed', label: '看完' },
    { key: 'paused', label: '暂停' },
    { key: 'dropped', label: '弃了' },
  ],
  game: [
    { key: 'all', label: '全部状态' },
    { key: 'wish', label: '想玩' },
    { key: 'playing', label: '在玩' },
    { key: 'completed', label: '通关' },
    { key: 'dropped', label: '弃坑' },
    { key: 'wait_buy', label: '等购买' },
    { key: 'wait_sale', label: '等折扣' },
  ],
}
const sts = computed(() =>
  activeCat.value === 'all' ? stSets.all : activeCat.value === 'game' ? stSets.game : stSets.media
)

const ACTIVE = ['watching', 'playing']

const workStatus = (w) => {
  if (w.category === 'game') return w.game_status || 'wish'
  return w.status || 'wish'
}
const stKey = workStatus

function matchSt(w, st) {
  if (st === 'all') return true
  if (st === 'active') return ACTIVE.includes(workStatus(w))
  return workStatus(w) === st
}

watch(activeCat, () => {
  if (!sts.value.some(s => s.key === activeSt.value)) {
    activeSt.value = 'all'
  }
})

const stCount = (key) => works.value.filter(w =>
  (activeCat.value === 'all' || w.category === activeCat.value) && matchSt(w, key)
).length

const filtered = computed(() => {
  const list = works.value.filter(w => {
    if (activeCat.value !== 'all' && w.category !== activeCat.value) return false
    if (!matchSt(w, activeSt.value)) return false
    if (activeTagId.value && !(w.tag_ids || []).includes(activeTagId.value)) return false
    if (q.value && !w.title.toLowerCase().includes(q.value.toLowerCase())) return false
    return true
  })
  if (sortBy.value === 'rating') list.sort((a, b) => (b.rating ?? -1) - (a.rating ?? -1))
  else if (sortBy.value === 'priority') list.sort((a, b) => (b.priority ?? -1) - (a.priority ?? -1))
  else if (sortBy.value === 'title') list.sort((a, b) => a.title.localeCompare(b.title, 'zh-Hans-CN'))
  // 'updated'：后端已按 updated_at desc 返回
  return list
})

const isFilterEmpty = computed(() => !!(activeTagId.value || activeCat.value !== 'all' || activeSt.value !== 'all' || q.value))

function clearFilters() {
  activeTagId.value = null
  activeCat.value = 'all'
  activeSt.value = 'all'
  q.value = ''
}

// —— 页头摘要（纯文字，非胶囊） ——
const summary = computed(() => {
  const all = works.value
  const act = all.filter(w => ACTIVE.includes(workStatus(w))).length
  const done = all.filter(w => workStatus(w) === 'completed').length
  return { total: all.length, act, done }
})

// —— 继续追横轨：在看/在玩，按最近更新（后端默认序） ——
const railWorks = computed(() => works.value.filter(w => ACTIVE.includes(workStatus(w))))
const railFull = (w) => {
  if (w.category === 'game') return (w.game_progress_value ?? 0) >= 100
  return !!(w.total && (w.progress_value ?? 0) >= w.total)
}
const unitOf = (w) => CATEGORIES.find(c => c.key === w.category)?.unitLabel || ''

// —— 行/卡共用取值 ——
const hasCover = (w) => !!w.cover_url
const coverStyle = (w) => hasCover(w)
  ? { background: `url(${worksApi.coverUrl(w.id)}) center/cover no-repeat` }
  : { background: `linear-gradient(135deg, var(--c-${w.category}), var(--c-${w.category}-light))` }
const expCurrent = (w) => (w.category === 'game' ? (w.game_progress_value ?? 0) : (w.progress_value ?? 0))
const expTotal = (w) => (w.category === 'game' ? 100 : (w.total || 0))
const hasExp = (w) => {
  if (w.category === 'game') return w.game_progress_value != null
  return w.progress_value != null && !!w.total
}
const progressText = (w) => {
  if (w.category === 'game') return w.game_progress_value == null ? '' : `${Math.round(w.game_progress_value)}%`
  if (w.progress_value == null) return ''
  return w.total ? `${w.progress_value} / ${w.total}` : `${w.progress_value}`
}

// —— +1 快捷进度（横轨）：乐观更新 + 5 秒撤销（Q1 决策；撤销 = 反向 PUT） ——
const ACTIVE_STATUS = { anime: 'watching', novel: 'watching', comic: 'watching', game: 'playing' }
const busyIds = ref(new Set())
const isBusy = (w) => busyIds.value.has(w.id)

async function railPlus1(w) {
  if (isBusy(w)) return
  busyIds.value.add(w.id)
  const cat = w.category
  const isGame = cat === 'game'
  const step = isGame ? 5 : 1
  const cur = isGame ? (w.game_progress_value ?? 0) : (w.progress_value ?? 0)
  const max = isGame ? 100 : (w.total || Infinity)
  const next = Math.min(max, cur + step)
  if (next === cur) {
    busyIds.value.delete(w.id)
    return
  }
  // 快照：撤销时恢复（含自动完成回退）
  const snap = { progress_value: w.progress_value, status: w.status, game_status: w.game_status, auto_completed: w.auto_completed }
  const apply = (d) => {
    if (isGame) {
      w.game_progress_value = d.progress_value
      w.game_status = d.status
      w.auto_completed = d.auto_completed
    } else {
      w.progress_value = d.progress_value
      w.status = d.status
      w.auto_completed = d.auto_completed
    }
  }
  try {
    const { data } = isGame
      ? await gameProfilesApi.update(w.game_profile_id, { progress_value: next })
      : await worksApi.update(w.id, { progress_value: next })
    apply(data)
    const justDone = data.status === 'completed' && !snap.auto_completed
    showToast(justDone ? `「${w.title}」已完成，盖章入档` : `「${w.title}」进度已更新`, 'success', {
      action: {
        label: '撤销',
        handler: async () => {
          try {
            const payload = { progress_value: snap.progress_value ?? 0 }
            if (!snap.auto_completed && data.auto_completed) payload.status = ACTIVE_STATUS[cat]
            const { data: d2 } = isGame
              ? await gameProfilesApi.update(w.game_profile_id, payload)
              : await worksApi.update(w.id, payload)
            apply(d2)
          } catch {
            showToast('没保存成功', 'error')
          }
        },
      },
    })
  } catch (e) {
    console.error('progress +1 failed', e)
    showToast('没保存成功', 'error')
  } finally {
    busyIds.value.delete(w.id)
  }
}
</script>

<template>
  <div class="page">
    <div class="page-inner">
      <!-- 页头：eyebrow + 标题 + 纯文字摘要（只读摘要不用胶囊形） -->
      <header class="page-head">
        <div class="ph-left">
          <p class="eyebrow">My Collection</p>
          <h1 class="title">我的卡册</h1>
        </div>
        <div class="ph-right">
          <p class="summary" aria-label="收藏概况">
            收藏 <b class="mono">{{ summary.total }}</b>
            <span class="sep" aria-hidden="true">·</span> 进行中 <b class="mono">{{ summary.act }}</b>
            <span class="sep" aria-hidden="true">·</span> 已完成 <b class="mono">{{ summary.done }}</b>
          </p>
          <ThemeToggle class="hd-theme" />
        </div>
      </header>

      <!-- 继续追横轨 -->
      <section v-if="!loading && !error && works.length" class="rail-sec" aria-labelledby="contH">
        <div class="sec-head">
          <h2 id="contH" class="sec-title">继续追</h2>
          <span class="sec-sub">在看 / 在玩，按最近更新排序 · 点「+1」即记一次进度</span>
        </div>
        <p v-if="!railWorks.length" class="rail-empty">没有进行中的作品。把一张卡的状态改成「在看 / 在玩」，它就会出现在这里。</p>
        <div v-else class="rail">
          <article v-for="w in railWorks" :key="w.id" class="cont" :data-cat="w.category">
            <div class="th" :style="coverStyle(w)" aria-hidden="true" />
            <div class="cont-main">
              <h3 class="cont-title">
                <router-link :to="`/works/${w.id}`">{{ w.title }}</router-link>
              </h3>
              <ProgressBar
                :current="expCurrent(w)"
                :total="expTotal(w)"
                :category="w.category"
                :label="`${w.title} 进度`"
              />
              <div class="cont-row">
                <span class="p mono">{{ progressText(w) }}</span>
                <button class="plus1" :disabled="railFull(w) || isBusy(w)" @click="railPlus1(w)">
                  {{ railFull(w) ? '已满' : (w.category === 'game' ? '+5%' : `+1 ${unitOf(w)}`) }}
                </button>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- 吸顶工具栏 -->
      <div class="toolbar">
        <div class="tb-row">
          <SegmentedControl
            v-model="activeCat"
            :options="cats.map(c => ({ value: c.key, label: c.label, count: c.key === 'all' ? works.length : works.filter(w => w.category === c.key).length, dot: c.key === 'all' ? null : catColorMap[c.key] }))"
            aria-label="品类"
          />
          <div class="grow">
            <svg class="s-icon" viewBox="0 0 20 20" fill="currentColor" width="14" height="14" aria-hidden="true">
              <path fill-rule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clip-rule="evenodd"/>
            </svg>
            <input v-model="q" type="search" class="s-inp" placeholder="在卡册里找…" aria-label="在收藏中搜索">
          </div>
          <div class="right">
            <label class="sr-only" for="sortSel">排序</label>
            <select id="sortSel" v-model="sortBy" class="sort-sel">
              <option v-for="s in SORTS" :key="s.key" :value="s.key">{{ s.label }}</option>
            </select>
            <SegmentedControl
              v-model="view"
              :options="[{ value: 'grid', label: '卡牌' }, { value: 'list', label: '列表' }]"
              aria-label="视图"
            />
          </div>
        </div>
        <div class="tb-row chips-row" role="group" aria-label="状态筛选">
          <FilterChip
            v-for="s in sts"
            :key="s.key"
            :active="activeSt === s.key"
            :dot="s.key === 'all' ? null : ST_COLOR[s.key]"
            :count="s.key === 'all' ? undefined : stCount(s.key)"
            :disabled="s.key !== 'all' && stCount(s.key) === 0 && activeSt !== s.key"
            @click="activeSt = s.key"
          >
            {{ s.label }}
          </FilterChip>
          <FilterChip
            v-if="activeTagId != null"
            :active="true"
            :dot="tags.find(t => t.id === activeTagId)?.color"
            @click="activeTagId = null"
          >
            标签：{{ tags.find(t => t.id === activeTagId)?.name }} ×
          </FilterChip>
        </div>
      </div>

      <!-- 标签筛选 -->
      <div v-if="!loading && !error && tags.length" class="chips-row tag-row" role="group" aria-label="按标签筛选">
        <FilterChip
          v-for="t in tags"
          :key="t.id"
          :active="activeTagId === t.id"
          :dot="t.color"
          @click="activeTagId = activeTagId === t.id ? null : t.id"
        >
          {{ t.name }}
        </FilterChip>
      </div>

      <p class="count" aria-live="polite">
        <template v-if="!loading && !error">共 {{ filtered.length }} 张卡</template>
        <template v-else-if="loading">正在读取卡册…</template>
      </p>

      <!-- 错误态 -->
      <StateBlock
        v-if="error"
        kind="error"
        title="卡册没能打开"
        message="本地服务暂时没有响应，已保存的记录不会丢失。"
        @retry="load"
      />

      <!-- 加载骨架 -->
      <div v-else-if="loading" class="grid" aria-busy="true">
        <span class="sr-only">正在读取卡册</span>
        <div v-for="i in 10" :key="i" class="skel-card" aria-hidden="true">
          <div class="skel-cover"><SkeletonBlock h="100%" w="100%" radius="6px" /></div>
          <SkeletonBlock h="14px" w="86%" radius="6px" class="skel-t" />
          <SkeletonBlock h="11px" w="50%" radius="6px" />
        </div>
      </div>

      <!-- 卡牌视图 -->
      <div v-else-if="filtered.length && view === 'grid'" class="grid">
        <div
          v-for="(w, i) in filtered"
          :key="w.id"
          role="button"
          tabindex="0"
          @click="router.push(`/works/${w.id}`)"
          @keydown.enter="router.push(`/works/${w.id}`)"
          @keydown.space.prevent="router.push(`/works/${w.id}`)"
        >
          <WorkCardGrid :work="w" :index="i" />
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-else-if="filtered.length && view === 'list'" class="rows" role="list">
        <div
          v-for="w in filtered"
          :key="w.id"
          class="lrow"
          :data-cat="w.category"
          role="listitem"
          tabindex="0"
          @click="router.push(`/works/${w.id}`)"
          @keydown.enter="router.push(`/works/${w.id}`)"
        >
          <span class="th" :style="coverStyle(w)" aria-hidden="true" />
          <span class="t">
            {{ w.title }}
            <small v-if="w.total">{{ w.total }} {{ unitOf(w) }}</small>
          </span>
          <CategoryBadge :category="w.category" class="hide-m" />
          <StatusStamp :category="w.category" :status="stKey(w)" class="row-stamp" />
          <span class="pg hide-m">
            <span class="mono muted">{{ progressText(w) || '—' }}</span>
            <ProgressBar
              v-if="hasExp(w)"
              :current="expCurrent(w)"
              :total="expTotal(w)"
              :category="w.category"
              :label="`${w.title} 进度`"
            />
          </span>
          <span class="mono hide-m">{{ w.rating != null ? '★ ' + w.rating : '—' }}</span>
        </div>
      </div>

      <!-- 空：筛选无结果 -->
      <StateBlock
        v-else-if="isFilterEmpty"
        title="这一格还是空的"
        message="当前筛选下没有作品。换个条件，或者清空筛选看看全部收藏。"
      >
        <button class="empty-btn" @click="clearFilters">清空筛选</button>
      </StateBlock>

      <!-- 空：还没有作品 -->
      <StateBlock
        v-else
        title="卡册还没有第一张卡"
        message="从 Bangumi 搜一部正在看的作品，一键入册；找不到的也可以手动添加。"
      >
        <button class="empty-btn primary" @click="router.push('/search')">去搜索添加</button>
        <button class="empty-btn" @click="router.push('/add')">手动添加</button>
      </StateBlock>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 20px 16px 64px; }
@media (min-width: 768px) { .page { padding: 24px 32px 64px; } }
.page-inner { max-width: 1400px; margin: 0 auto; }
.mono { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
.muted { color: var(--text-secondary); }

/* ======== 页头 ======== */
.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.ph-left .eyebrow {
  font-family: var(--font-mono);
  font-size: var(--fs-xs);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-tertiary);
  margin-bottom: 2px;
}
.title { font-size: var(--fs-2xl); font-weight: 800; letter-spacing: -0.5px; }
.ph-right { display: flex; align-items: center; gap: 12px; }
.summary { font-size: var(--fs-sm); color: var(--text-secondary); }
.summary b { color: var(--text-primary); font-weight: 700; }
.summary .sep { color: var(--text-tertiary); margin: 0 4px; }
@media (min-width: 768px) { .hd-theme { display: none; } }

/* ======== 继续追横轨 ======== */
.rail-sec { margin-bottom: 24px; }
.sec-head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; margin-bottom: 10px; flex-wrap: wrap; }
.sec-title { font-size: var(--fs-xl); font-weight: 700; }
.sec-sub { font-size: var(--fs-sm); color: var(--text-tertiary); }
.rail-empty { font-size: var(--fs-sm); color: var(--text-secondary); }
.rail {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: minmax(300px, 1fr);
  gap: 12px;
  overflow-x: auto;
  padding: 4px 2px 10px;
  scroll-snap-type: x mandatory;
  scrollbar-width: thin;
}
.cont {
  scroll-snap-align: start;
  display: grid;
  grid-template-columns: 64px minmax(0, 1fr);
  gap: 12px;
  align-items: center;
  padding: 12px;
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  box-shadow: inset 0 0 0 1px var(--color-border);
}
.cont[data-cat='anime'] { --cc: var(--c-anime); }
.cont[data-cat='novel'] { --cc: var(--c-novel); }
.cont[data-cat='comic'] { --cc: var(--c-comic); }
.cont[data-cat='game'] { --cc: var(--c-game); }
.cont .th {
  width: 64px;
  aspect-ratio: 3 / 4.2;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 0 0 2px var(--cc);
}
.cont-main { min-width: 0; }
.cont-title { font-size: var(--fs-sm); font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cont-title a:hover { text-decoration: underline; }
.cont-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: 6px; }
.cont-row .p { font-size: var(--fs-xs); color: var(--text-secondary); }
.cont-main > .exp { margin-top: 6px; }
.plus1 {
  height: 32px;
  min-width: 56px;
  padding: 0 10px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-xs);
  font-weight: 700;
  background: color-mix(in srgb, var(--cc) 12%, var(--bg-surface));
  color: var(--text-primary);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--cc) 45%, transparent);
  transition: background 0.15s;
}
.plus1:hover:not(:disabled) { background: color-mix(in srgb, var(--cc) 22%, var(--bg-surface)); }
.plus1:disabled { opacity: 0.45; cursor: not-allowed; }

/* ======== 吸顶工具栏 ======== */
.toolbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px 0;
  margin-bottom: 4px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--line, rgba(0, 0, 0, 0.09));
}
@media (min-width: 768px) { .toolbar { top: var(--topbar-height); } }
.tb-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.tb-row .grow { flex: 1; min-width: 180px; max-width: 320px; position: relative; }
.tb-row .right { margin-left: auto; display: flex; gap: 8px; align-items: center; }
.s-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-tertiary); pointer-events: none; }
.s-inp { height: 40px; padding-left: 34px; border-radius: var(--radius-full); font-size: var(--fs-sm); }
.s-inp::placeholder { color: var(--text-tertiary); }
.sort-sel {
  height: 40px;
  padding: 0 10px;
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: border-color 0.15s;
}
.sort-sel:hover { border-color: var(--text-tertiary); }
.sort-sel:focus { outline: none; border-color: var(--text-tertiary); }
@media (max-width: 767px) {
  .tb-row .right { margin-left: 0; width: 100%; justify-content: flex-end; }
  .tb-row .grow { max-width: none; }
}
.chips-row { display: flex; gap: 8px; flex-wrap: wrap; }
.tag-row { margin-top: 10px; }

/* ======== 计数 ======== */
.count { font-size: var(--fs-xs); color: var(--text-tertiary); margin: 14px 0 10px; }

/* ======== 加载骨架 ======== */
.skel-card {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  padding: 5px 5px 12px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.06);
}
.skel-cover { aspect-ratio: 3 / 4.2; border-radius: 6px; overflow: hidden; margin-bottom: 10px; }
.skel-t { margin-bottom: 6px; }

/* ======== 卡牌网格 ======== */
.grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px 14px; }
@media (min-width: 640px) { .grid { grid-template-columns: repeat(3, 1fr); gap: 24px 16px; } }
@media (min-width: 960px) { .grid { grid-template-columns: repeat(4, 1fr); } }
@media (min-width: 1200px) { .grid { grid-template-columns: repeat(5, 1fr); } }

/* ======== 列表视图 ======== */
.rows {
  display: flex;
  flex-direction: column;
  gap: 2px;
  background: var(--line, rgba(0,0,0,0.09));
  border-radius: var(--radius-md);
  overflow: hidden;
}
.lrow {
  display: grid;
  grid-template-columns: 44px minmax(0, 2.4fr) 80px 90px minmax(120px, 1.4fr) 60px;
  gap: 12px;
  align-items: center;
  padding: 8px 12px;
  background: var(--bg-surface);
  cursor: pointer;
}
.lrow:hover { background: var(--bg-surface-hover); }
.lrow[data-cat='anime'] { --cc: var(--c-anime); }
.lrow[data-cat='novel'] { --cc: var(--c-novel); }
.lrow[data-cat='comic'] { --cc: var(--c-comic); }
.lrow[data-cat='game'] { --cc: var(--c-game); }
.lrow .th { width: 44px; aspect-ratio: 3 / 4.2; border-radius: 4px; overflow: hidden; box-shadow: 0 0 0 1.5px var(--cc); }
.lrow .t { font-weight: 600; font-size: var(--fs-sm); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lrow .t small { display: block; font-weight: 400; color: var(--text-tertiary); font-size: 11px; }
.row-stamp { justify-self: start; }
.row-stamp :deep(.stamp) { animation: none; }
.lrow .pg { display: flex; flex-direction: column; gap: 4px; font-size: 11px; }
.lrow .pg .mono { color: var(--text-secondary); }
@media (max-width: 767px) {
  .lrow { grid-template-columns: 44px minmax(0, 1fr) auto; }
  .hide-m { display: none; }
}

/* ======== 空态按钮 ======== */
.empty-btn {
  height: 36px;
  padding: 0 18px;
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-secondary);
  transition: all 0.15s;
}
.empty-btn:hover { border-color: var(--text-tertiary); color: var(--text-primary); }
.empty-btn.primary { background: var(--primary); color: #fff; border-color: transparent; }
.empty-btn.primary:hover { background: var(--primary-hover); }

/* 触屏：操作控件达到 44px 触控目标（Q3 决策；分段/胶囊在组件内处理） */
@media (pointer: coarse) {
  .sort-sel, .s-inp, .plus1, .empty-btn { min-height: 44px; }
}
@media (prefers-reduced-motion: reduce) {
  .rail { scroll-behavior: auto; }
}
</style>
