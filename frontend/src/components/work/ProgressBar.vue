<script setup>
import { computed } from 'vue'

// 原型 .exp 经验条：游戏品类由调用方传百分比（current=pct, total=100）
// overlay=true 时压在封面底边（深色衬底、直角），否则为面板内常规条
const props = defineProps({
  current: { type: Number, default: 0 },
  total: { type: Number, default: 100 },
  category: { type: String, default: '' },
  label: { type: String, default: '进度' },
  overlay: { type: Boolean, default: false },
  size: { type: String, default: '' }, // '' | 'lg'
})

const pct = computed(() => {
  if (!props.total || props.total <= 0) return 0
  return Math.min(100, Math.max(0, Math.round((props.current / props.total) * 100)))
})
const cc = computed(() => (props.category ? `var(--c-${props.category})` : 'var(--primary)'))
</script>

<template>
  <div
    class="exp"
    :class="{ overlay, lg: size === 'lg' }"
    :style="{ '--cc': cc, '--p': pct + '%' }"
    role="progressbar"
    :aria-valuenow="pct"
    aria-valuemin="0"
    aria-valuemax="100"
    :aria-label="label"
  >
    <i />
  </div>
</template>

<style scoped>
.exp {
  position: relative;
  height: 6px;
  border-radius: 3px;
  background: color-mix(in srgb, var(--cc) 16%, var(--bg-input));
  overflow: hidden;
}
.exp > i {
  position: absolute;
  inset: 0 auto 0 0;
  width: var(--p);
  border-radius: inherit;
  background: linear-gradient(90deg, var(--cc), color-mix(in srgb, var(--cc) 60%, white));
  transition: width 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
  overflow: hidden;
}
.exp > i::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.55), transparent);
  animation: exp-shimmer 2.4s ease-in-out infinite;
}
/* 封面底边形态 */
.exp.overlay {
  height: 5px;
  border-radius: 0;
  background: rgba(0, 0, 0, 0.35);
}
.exp.lg { height: 10px; border-radius: 5px; }
@media (prefers-reduced-motion: reduce) {
  .exp > i { transition: none; }
  .exp > i::after { animation: none; display: none; }
}
</style>
