<script setup>
import { computed } from 'vue'
import { worksApi, gameProfilesApi } from '../../api/client'
import { STATUS_LABELS, STATUS_COLORS, categoryGradient } from '../../constants/work'
import { showToast } from '../../utils/toast'

const props = defineProps({ work: Object })

const cat = computed(() => props.work.category)

const coverStyle = computed(() => {
  if (props.work.cover_url) {
    return { background: `url(${worksApi.coverUrl(props.work.id)}) center/cover no-repeat` }
  }
  return { background: categoryGradient(cat.value, 135) }
})

const iconMap = {
  anime: 'M30 24l-10-6v12l10-6z',
  novel: 'M20 12l-6 6 6 6M28 12l6 6-6 6',
  comic: 'M18 20l6-8 4 4 4-4',
  game: 'M22 18l8 5-8 5V18zM22 14V6l8 5-8 3z',
}

const gameStatus = computed(() => {
  if (props.work.category !== 'game') return null
  return props.work.game_status
})

const st = computed(() => {
  const cat = props.work.category
  const key = cat === 'game' ? (gameStatus.value || 'wish') : (props.work.status || 'wish')
  return { label: STATUS_LABELS[cat]?.[key] || key, bg: STATUS_COLORS[key] || 'var(--s-wish)' }
})

// 游戏 GP 的 percent 型进度自带分母 100；其余品类按 total 折算
const pct = computed(() => {
  const w = props.work
  if (cat.value === 'game') {
    const v = w.game_progress_value
    return v == null ? 0 : Math.min(100, Math.round(v))
  }
  const val = w.progress_value
  if (!w.total || w.total <= 0 || val == null) return 0
  return Math.min(100, Math.round((val / w.total) * 100))
})

const progressLabel = computed(() => {
  const w = props.work
  if (cat.value === 'game') {
    const v = w.game_progress_value
    return v == null ? '' : `${Math.round(v)}%`
  }
  const val = w.progress_value
  if (val == null) return ''
  const t = w.total ? ` / ${w.total}` : ''
  const pt = pct.value > 0 ? ` (${pct.value}%)` : ''
  return `${val}${t}${pt}`
})

// 卡片快捷进度：动漫 +1 集 / 小说 +1 章 / 漫画 +1 卷 / 游戏 +5%
const step = computed(() => cat.value === 'game' ? 5 : 1)
const busy = computed(() => props.work.__busy)
// auto_completed 状态回退时恢复到的"进行中"状态
const ACTIVE_STATUS = { anime: 'watching', novel: 'watching', comic: 'watching', game: 'playing' }

async function stepProgress(ev, dir) {
  ev.stopPropagation()
  if (props.work.__busy) return
  props.work.__busy = true
  try {
    const w = props.work
    // 游戏的进度基数取 GP（game_progress_value），其余品类取 Work 的 progress_value
    const cur = (cat.value === 'game' ? (w.game_progress_value ?? 0) : (w.progress_value ?? 0))
    let next = cur + dir * step.value
    if (dir > 0 && w.total) next = Math.min(next, w.total)
    next = Math.max(next, 0)
    if (next === cur) return

    // 游戏进度挂在 GameProfile 上；其余品类在 Work 上
    if (cat.value === 'game') {
      const gpid = w.game_profile_id
      if (!gpid) return
      const payload = { progress_value: next }
      // 自动完成后的回退：状态一并恢复"进行中"
      if (dir < 0 && w.auto_completed) payload.status = ACTIVE_STATUS.game
      const { data } = await gameProfilesApi.update(gpid, payload)
      w.game_progress_value = data.progress_value
      w.game_status = data.status
      w.auto_completed = data.auto_completed
    } else {
      const payload = { progress_value: next }
      if (dir < 0 && w.auto_completed) payload.status = ACTIVE_STATUS[cat.value]
      const { data } = await worksApi.update(w.id, payload)
      w.progress_value = data.progress_value
      w.status = data.status
      w.auto_completed = data.auto_completed
    }
  } catch (e) {
    console.error('progress step failed', e)
    showToast('进度更新失败', 'error')
  } finally {
    props.work.__busy = false
  }
}

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
      <div v-if="cat === 'game' || work.progress_value != null" class="exp-wrap">
        <div class="exp-rail">
          <div class="exp-fill" :style="{ width: pct + '%', background: categoryGradient(cat, 0) }" />
        </div>
        <span class="exp-label">{{ progressLabel }}</span>
        <button v-if="(work.progress_value ?? gpProgress ?? 0) > 0" class="exp-plus" :disabled="busy" title="进度 −1" @click="stepProgress($event, -1)">−1</button>
        <button class="exp-plus" :disabled="busy" title="进度 +1" @click="stepProgress($event, 1)">+1</button>
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
.exp-plus {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-full);
  background: rgba(255,255,255,0.18);
  backdrop-filter: blur(4px);
  color: #fff;
  font-size: 11px;
  font-weight: 800;
  line-height: 1;
  transition: all 0.15s;
}
.exp-plus:hover { background: rgba(255,255,255,0.32); transform: scale(1.08); }
.exp-plus:active { transform: scale(0.94); }
.exp-plus:disabled { opacity: 0.5; }

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
