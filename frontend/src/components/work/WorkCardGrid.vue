<script setup>
import { computed } from 'vue'
import { worksApi } from '../../api/client'
import CategoryBadge from './CategoryBadge.vue'
import StatusStamp from './StatusStamp.vue'
import ProgressBar from './ProgressBar.vue'

// 原型三环框卡牌：品类色环 + 纸边 + 细描边；角标右上、印章左下、EXP 条压封面底边。
// 快捷进度按钮已移至收藏页「继续追」横轨；卡面数字用 --text-secondary 保证扫读对比度。
const props = defineProps({
  work: { type: Object, required: true },
  index: { type: Number, default: 0 },
})

const cat = computed(() => props.work.category)
const coverStyle = computed(() => {
  if (props.work.cover_url) {
    return { background: `url(${worksApi.coverUrl(props.work.id)}) center/cover no-repeat` }
  }
  return { background: `linear-gradient(135deg, var(--c-${cat.value}), var(--c-${cat.value}-light))` }
})

const iconMap = {
  anime: 'M30 24l-10-6v12l10-6z',
  novel: 'M20 12l-6 6 6 6M28 12l6 6-6 6',
  comic: 'M18 20l6-8 4 4 4-4',
  game: 'M22 18l8 5-8 5V18zM22 14V6l8 5-8 3z',
}

const stKey = computed(() => {
  const c = cat.value
  return c === 'game' ? (props.work.game_status || 'wish') : (props.work.status || 'wish')
})

// EXP 条：游戏用 GP 百分比（分母 100），其余品类按 total 折算；total 为空（连载中）不画条
const hasExp = computed(() => {
  if (cat.value === 'game') return props.work.game_progress_value != null
  return props.work.progress_value != null && !!props.work.total
})
const expCurrent = computed(() =>
  cat.value === 'game' ? (props.work.game_progress_value ?? 0) : (props.work.progress_value ?? 0)
)
const expTotal = computed(() => (cat.value === 'game' ? 100 : props.work.total || 100))

const progressLabel = computed(() => {
  const w = props.work
  if (cat.value === 'game') {
    return w.game_progress_value == null ? '' : `${Math.round(w.game_progress_value)}%`
  }
  if (w.progress_value == null) return ''
  return w.total ? `${w.progress_value} / ${w.total}` : `${w.progress_value}`
})
</script>

<template>
  <article class="card" :data-cat="cat" :style="{ '--i': Math.min(index, 14) }">
    <div class="card-art">
      <div class="cover" :style="coverStyle">
        <template v-if="!work.cover_url">
          <svg viewBox="0 0 48 48" fill="none" class="cover-icon" aria-hidden="true">
            <circle cx="24" cy="24" r="18" stroke="white" stroke-width="1.5" opacity="0.2"/>
            <path :d="iconMap[cat] || iconMap.anime" fill="white" opacity="0.45"/>
          </svg>
        </template>
      </div>
      <span class="holo" aria-hidden="true" />
      <CategoryBadge :category="cat" class="art-badge" />
      <StatusStamp :category="cat" :status="stKey" class="art-stamp" />
      <ProgressBar
        v-if="hasExp"
        overlay
        :current="expCurrent"
        :total="expTotal"
        :category="cat"
        :label="`${work.title} 进度`"
        class="art-exp"
      />
    </div>
    <div class="card-body">
      <h3 class="card-title">{{ work.title }}</h3>
      <div class="card-meta">
        <span class="mono">{{ progressLabel }}</span>
        <span v-if="work.rating != null" class="mono">★ {{ work.rating }}</span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.card {
  position: relative;
  display: block;
  border-radius: 12px;
  padding: 5px;
  background: var(--bg-surface);
  box-shadow:
    0 0 0 2.5px var(--cc),
    0 0 0 6px var(--bg-surface),
    0 0 0 7px var(--line, rgba(0, 0, 0, 0.09)),
    var(--shadow-sm);
  transition: transform 0.25s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
  animation: card-deal 0.5s cubic-bezier(0.2, 0.8, 0.2, 1) both;
  animation-delay: calc(var(--i) * 35ms);
}
.card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 0 0 2.5px var(--cc),
    0 0 0 6px var(--bg-surface),
    0 0 0 7px var(--line, rgba(0, 0, 0, 0.09)),
    0 14px 30px color-mix(in srgb, var(--cc) 28%, transparent);
}
/* 品类色环 --cc：别名既有 --c-*，非新色值 */
.card[data-cat='anime'] { --cc: var(--c-anime); }
.card[data-cat='novel'] { --cc: var(--c-novel); }
.card[data-cat='comic'] { --cc: var(--c-comic); }
.card[data-cat='game'] { --cc: var(--c-game); }

.card-art {
  position: relative;
  aspect-ratio: 3 / 4.2;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-input);
}
.cover { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; transition: transform 0.4s cubic-bezier(0.2, 0, 0, 1); }
.card:hover .cover { transform: scale(1.06); }
.cover-icon { width: 36px; height: 36px; }

/* 全息流光 */
.holo {
  position: absolute;
  inset: 0;
  background: linear-gradient(115deg, transparent 35%, rgba(255, 255, 255, 0.35) 48%, transparent 60%);
  transform: translateX(-120%);
  transition: transform 0.7s cubic-bezier(0.2, 0.8, 0.2, 1);
  pointer-events: none;
}
.card:hover .holo { transform: translateX(120%); }

.art-badge { position: absolute; top: 8px; right: 8px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25); }
.art-stamp { position: absolute; left: 8px; bottom: 16px; }
.art-exp { position: absolute; left: 0; right: 0; bottom: 0; }

.card-body { padding: 8px 4px 4px; }
.card-title {
  font-size: var(--fs-sm);
  font-weight: 600;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.7em;
}
.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
  font-size: 11px;
  color: var(--text-secondary);
  min-height: 1.2em;
}
.mono { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
@media (prefers-reduced-motion: reduce) {
  .card { animation: none; }
  .holo, .cover { transition: none; }
}
</style>
