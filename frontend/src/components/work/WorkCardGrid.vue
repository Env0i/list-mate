<script setup>
import { computed } from 'vue'
import { worksApi } from '../../api/client'

const props = defineProps({ work: Object })

const cat = computed(() => props.work.category)

const gradientMap = {
  anime: 'linear-gradient(135deg, #FF1A5E, #FF6B8A)',
  novel: 'linear-gradient(135deg, #3366FF, #6B96FF)',
  comic: 'linear-gradient(135deg, #00CC66, #4DE69E)',
  game: 'linear-gradient(135deg, #FF7A00, #FFA755)',
}

const coverStyle = computed(() => {
  if (props.work.cover_url) {
    return { background: `url(${worksApi.coverUrl(props.work.id)}) center/cover no-repeat` }
  }
  return { background: gradientMap[cat.value] }
})

const iconMap = {
  anime: 'M30 24l-10-6v12l10-6z',
  novel: 'M20 12l-6 6 6 6M28 12l6 6-6 6',
  comic: 'M18 20l6-8 4 4 4-4',
  game: 'M22 18l8 5-8 5V18zM22 14V6l8 5-8 3z',
}

const statusLabels = {
  anime: { wish: '想看', watching: '在看', completed: '看完', paused: '暂停', dropped: '弃了' },
  novel: { wish: '想看', watching: '在看', completed: '看完', paused: '暂停', dropped: '弃了' },
  comic: { wish: '想看', watching: '在看', completed: '看完', paused: '暂停', dropped: '弃了' },
  game: { wish: '想玩', playing: '在玩', completed: '通关', dropped: '弃坑', wait_buy: '等购买', wait_sale: '等折扣' },
}

const statusBg = {
  wish: '#A39F98', watching: '#3366FF', playing: '#3366FF',
  completed: '#00B85A', paused: '#FFB800',
  dropped: '#FF4444', wait_buy: '#FFB800', wait_sale: '#FF8C00',
}

const gameStatus = computed(() => {
  if (props.work.category !== 'game') return null
  return props.work.game_profiles?.[0]?.status
})

const gpProgress = computed(() => {
  if (props.work.category !== 'game') return null
  return props.work.game_profiles?.[0]?.progress_value
})

const st = computed(() => {
  const cat = props.work.category
  const key = props.work.status || gameStatus.value || 'wish'
  return { label: statusLabels[cat]?.[key] || key, bg: statusBg[key] || '#A39F98' }
})

const pct = computed(() => {
  const w = props.work
  const val = w.progress_value ?? gpProgress.value
  if (!w.total || w.total <= 0 || val == null) return 0
  return Math.min(100, Math.round((val / w.total) * 100))
})

const progressLabel = computed(() => {
  const w = props.work
  const val = w.progress_value ?? gpProgress.value
  if (val == null) return ''
  const t = w.total ? ` / ${w.total}` : ''
  const pt = pct.value > 0 ? ` (${pct.value}%)` : ''
  return `${val}${t}${pt}`
})

const catNameMap = { anime: '番剧', novel: '小说', comic: '漫画', game: '游戏' }
</script>

<template>
  <div class="card-frame" :style="{ '--cat-color': `var(--c-${cat})`, '--cat-glow': `var(--c-${cat}-glow)` }">
    <div class="cover-area">
      <div class="cover-bg" :style="coverStyle">
        <template v-if="!work.cover_url">
          <svg viewBox="0 0 48 48" fill="none" class="cover-icon">
            <circle cx="24" cy="24" r="18" stroke="white" stroke-width="1.5" opacity="0.2"/>
            <path :d="iconMap[cat] || iconMap.anime" fill="white" opacity="0.45"/>
          </svg>
          <div class="cover-dots">
            <svg viewBox="0 0 100 100" width="100%" height="100%">
              <circle cx="15" cy="15" r="1.2" fill="white" opacity="0.08"/>
              <circle cx="85" cy="25" r="1.5" fill="white" opacity="0.06"/>
              <circle cx="30" cy="85" r="1" fill="white" opacity="0.07"/>
              <circle cx="88" cy="88" r="0.8" fill="white" opacity="0.04"/>
            </svg>
          </div>
        </template>
      </div>
      <!-- Status stamp -->
      <div class="status-stamp" :style="{ background: st.bg }">{{ st.label }}</div>
      <!-- EXP bar overlay -->
      <div v-if="work.progress_value != null || gpProgress != null" class="exp-wrap">
        <div class="exp-rail">
          <div class="exp-fill" :style="{ width: pct + '%', background: `linear-gradient(90deg, ${gradientMap[cat].replace('135deg', '0deg')})` }" />
        </div>
        <span class="exp-label">{{ progressLabel }}</span>
      </div>
    </div>
    <div class="info">
      <h3 class="title">{{ work.title }}</h3>
      <div class="sub-info">
        <span class="cat-tag" :class="'ct-' + cat">{{ catNameMap[cat] }}</span>
        <span v-if="work.total" class="total-tag">{{ work.total }} <template v-if="cat === 'anime'">集</template><template v-else-if="cat === 'novel'">章</template><template v-else-if="cat === 'comic'">卷</template></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card-frame {
  position: relative;
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  cursor: pointer;
  overflow: hidden;
  box-shadow: 0 4px 14px rgba(0,0,0,0.06);
  transition:
    transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1),
    box-shadow 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
  animation: card-deal 0.45s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
.card-frame:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow:
    0 0 24px var(--cat-glow),
    0 12px 40px rgba(0,0,0,0.07);
}
.card-frame:active { transform: scale(0.97); }

/* Holo shimmer on hover */
.card-frame::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: var(--radius-md);
  background: linear-gradient(
    105deg,
    transparent 35%,
    rgba(255,255,255,0.15) 42%,
    rgba(255,255,255,0.3) 48%,
    rgba(255,255,255,0.15) 54%,
    transparent 61%
  );
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.05s;
  transform: translateX(-120%) skewX(-12deg);
}
.card-frame:hover::after {
  opacity: 1;
  transform: translateX(120%) skewX(-12deg);
  transition: opacity 0.05s, transform 0.6s cubic-bezier(0.23, 1, 0.32, 1);
}

/* Cover area */
.cover-area {
  position: relative;
  margin: 5px 5px 0 5px;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: inset 0 0 0 1px var(--frame-inner);
  aspect-ratio: 3 / 4;
}
.cover-bg {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.4s cubic-bezier(.2,0,0,1);
}
.card-frame:hover .cover-bg { transform: scale(1.06); }
.cover-icon { width: 36px; height: 36px; position: relative; z-index: 1; }
.cover-dots { position: absolute; inset: 0; }

/* Status stamp — bigger, more prominent */
.status-stamp {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 10px;
  color: #fff;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.5px;
  border-radius: 3px;
  transform: rotate(3deg);
  box-shadow: 0 2px 8px rgba(0,0,0,0.25);
  backdrop-filter: blur(4px);
  animation: stamp-in 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s both;
}

/* EXP bar — thicker, bolder */
.exp-wrap {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: linear-gradient(transparent, rgba(0,0,0,0.6) 40%, rgba(0,0,0,0.75));
}
.exp-rail {
  flex: 1;
  height: 8px;
  background: rgba(255,255,255,0.15);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.08);
}
.exp-fill {
  height: 100%;
  border-radius: 3px;
  position: relative;
  transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.exp-fill::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(90deg, transparent 30%, rgba(255,255,255,0.35) 50%, transparent 70%);
  animation: exp-shimmer 2.5s ease-in-out infinite;
}
.exp-label {
  font-size: 11px;
  font-weight: 700;
  color: rgba(255,255,255,0.95);
  font-variant-numeric: tabular-nums;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

/* Info — more breathing room */
.info {
  padding: 10px 10px 12px;
}
.title {
  font-size: var(--fs-base);
  font-weight: 700;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: center;
}
.sub-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 5px;
}
.cat-tag {
  font-size: 10px;
  font-weight: 600;
  padding: 1px 7px;
  border-radius: 3px;
  line-height: 1.5;
}
.ct-anime { background: var(--c-anime-bg); color: var(--c-anime); }
.ct-novel { background: var(--c-novel-bg); color: var(--c-novel); }
.ct-comic { background: var(--c-comic-bg); color: var(--c-comic); }
.ct-game { background: var(--c-game-bg); color: var(--c-game); }
.total-tag {
  font-size: 10px;
  font-weight: 500;
  color: var(--text-tertiary);
}
</style>
