<script setup>
import { computed } from 'vue'
import { categoryGradient } from '../../constants/work'

const props = defineProps({
  current: [Number, null], total: [Number, null], category: String,
})

const pct = computed(() => {
  if (!props.total || props.total <= 0 || props.current == null) return 0
  return Math.min(100, Math.round((props.current / props.total) * 100))
})
const label = computed(() => {
  if (props.current == null) return '--'
  if (props.category === 'game') return `${pct.value}%`
  const t = props.total ? ` / ${props.total}` : ''
  return `${props.current}${t}`
})
const fillBg = computed(() => categoryGradient(props.category || 'anime', 90))
</script>

<template>
  <div class="exp-wrap">
    <div class="exp-rail">
      <div class="exp-fill" :style="{ width: pct + '%', background: fillBg }">
        <div class="exp-shine" />
      </div>
    </div>
    <span class="exp-lbl">{{ label }}</span>
  </div>
</template>

<style scoped>
.exp-wrap { display: flex; align-items: center; gap: 8px; }
.exp-rail { flex: 1; height: 6px; background: rgba(0,0,0,0.04); border-radius: 3px; overflow: hidden; border: 1px solid rgba(0,0,0,0.03); }
.exp-fill { height: 100%; border-radius: inherit; transition: width 0.4s cubic-bezier(.2,0,0,1); position: relative; overflow: hidden; min-width: 4px; }
.exp-shine { position: absolute; inset: 0; background: linear-gradient(90deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%); animation: exp-shimmer 2.5s ease-in-out infinite; }
@keyframes exp-shimmer { 0% { transform: translateX(-100%); } 100% { transform: translateX(200%); } }
.exp-lbl { font-size: 11px; font-weight: 700; color: var(--text-tertiary); flex-shrink: 0; min-width: 36px; text-align: right; font-variant-numeric: tabular-nums; }
</style>
