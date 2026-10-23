<script setup>
import { computed } from 'vue'
import { STATUS_LABELS_FLAT } from '../../../constants/work'

// 社区对照：评分分布 S/A/B/C（9-10/7-8/5-6/1-4）+ 我的位置 + 收藏人数
const props = defineProps({
  rating: { type: Object, default: null },     // {score, rank, total, count{1..10}}
  collection: { type: Object, default: null }, // {wish, doing, collect, on_hold, dropped}
  myRating: { type: Number, default: null },
})

const GRADES = [
  { key: 'S', label: 'S', range: '9-10', min: 9, max: 10 },
  { key: 'A', label: 'A', range: '7-8', min: 7, max: 8 },
  { key: 'B', label: 'B', range: '5-6', min: 5, max: 6 },
  { key: 'C', label: 'C', range: '0-4', min: 1, max: 4 },
]

const buckets = computed(() => {
  const count = props.rating?.count || {}
  const total = GRADES.reduce((s, g) => {
    let n = 0
    for (let i = g.min; i <= g.max; i++) n += count[String(i)] || count[i] || 0
    return s + n
  }, 0)
  const max = Math.max(...GRADES.map(g => {
    let n = 0
    for (let i = g.min; i <= g.max; i++) n += count[String(i)] || count[i] || 0
    return n
  }), 1)
  return { total, rows: GRADES.map(g => {
    let n = 0
    for (let i = g.min; i <= g.max; i++) n += count[String(i)] || count[i] || 0
    return { ...g, n, pct: Math.round((n / max) * 100) }
  }) }
})

const myGrade = computed(() => {
  if (props.myRating == null) return null
  return GRADES.find(g => props.myRating >= g.min && props.myRating <= g.max)?.key || null
})

// 高于 N% 的评分者：严格低于我评分的人数占比
const betterThan = computed(() => {
  if (props.myRating == null || !props.rating?.count) return null
  const count = props.rating.count
  let below = 0
  for (let i = 1; i < props.myRating; i++) below += count[String(i)] || count[i] || 0
  const total = props.rating.total || GRADES.reduce((s, g) => {
    let n = 0
    for (let i = g.min; i <= g.max; i++) n += count[String(i)] || count[i] || 0
    return s + n
  }, 0)
  if (!total) return null
  return Math.round((below / total) * 100)
})

// 收藏人数：键映射到 constants 的状态标签（§5：标签不从原型写死）
const COLLECT_MAP = [
  { key: 'wish', label: STATUS_LABELS_FLAT.wish },
  { key: 'doing', label: STATUS_LABELS_FLAT.watching },
  { key: 'collect', label: STATUS_LABELS_FLAT.completed },
  { key: 'on_hold', label: STATUS_LABELS_FLAT.paused },
  { key: 'dropped', label: STATUS_LABELS_FLAT.dropped },
]
const collectRows = computed(() => {
  if (!props.collection) return []
  return COLLECT_MAP.map(c => ({ ...c, n: props.collection[c.key] || 0 })).filter(r => r.n > 0)
})
const collectTotal = computed(() => collectRows.value.reduce((s, r) => s + r.n, 0))
</script>

<template>
  <div class="cc">
    <div v-if="rating?.score" class="cc-score">
      <div class="score-big mono">{{ rating.score }}</div>
      <div class="score-side">
        <p class="muted">Bangumi {{ collectTotal }} 人收藏 · {{ rating.total }} 人评分</p>
        <p v-if="myRating != null" class="mine">
          我的 {{ myRating }} 分
          <span v-if="betterThan != null" class="mine-pct">高于 {{ betterThan }}% 的评分者</span>
        </p>
      </div>
    </div>

    <div class="cc-bars">
      <div v-for="g in buckets.rows" :key="g.key" class="cc-row">
        <span class="g mono" :class="{ on: myGrade === g.key }">{{ g.label }}</span>
        <span class="range">{{ g.range }}</span>
        <div class="bar"><i :style="{ width: g.pct + '%' }" /></div>
        <span class="n mono">{{ g.n }}</span>
      </div>
    </div>

    <div v-if="collectTotal" class="cc-collect">
      <span v-for="r in collectRows" :key="r.key" class="c-item">
        <b class="mono">{{ r.n }}</b> {{ r.label }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.cc { display: flex; flex-direction: column; gap: 16px; }
.mono { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
.muted { color: var(--text-secondary); font-size: var(--fs-sm); }
.cc-score { display: flex; align-items: center; gap: 16px; }
.score-big { font-size: var(--fs-3xl, 2rem); font-weight: 700; line-height: 1; }
.score-side { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.mine { font-size: var(--fs-sm); color: var(--text-primary); font-weight: 700; }
.mine-pct { color: var(--s-paused); font-weight: 600; margin-left: 8px; }

.cc-bars { display: flex; flex-direction: column; gap: 6px; }
.cc-row { display: grid; grid-template-columns: 20px 44px 1fr 52px; align-items: center; gap: 10px; font-size: 11px; }
.cc-row .g { font-weight: 800; color: var(--text-tertiary); }
.cc-row .g.on { color: var(--s-paused); }
.cc-row .range { color: var(--text-tertiary); }
.cc-row .bar { height: 8px; border-radius: 4px; background: var(--bg-input); overflow: hidden; }
.cc-row .bar i { display: block; height: 100%; border-radius: inherit; background: var(--s-watching); transition: width 0.5s cubic-bezier(0.2, 0.8, 0.2, 1); }
.cc-row .n { color: var(--text-secondary); text-align: right; }

.cc-collect { display: flex; flex-wrap: wrap; gap: 6px 16px; font-size: var(--fs-xs); color: var(--text-secondary); }
.cc-collect b { color: var(--text-primary); margin-right: 3px; }
@media (prefers-reduced-motion: reduce) {
  .cc-row .bar i { transition: none; }
}
</style>
