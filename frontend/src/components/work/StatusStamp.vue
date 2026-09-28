<script setup>
import { computed } from 'vue'
import { STATUS_LABELS, STATUS_COLORS } from '../../constants/work'

// 状态印章：文字一律正文色保证对比度（暂停黄底白字只有 1.8:1），
// 状态色只上描边与圆点。定位由父级控制（组件本身不绝对定位）。
const props = defineProps({
  category: { type: String, required: true },
  status: { type: String, required: true },
  size: { type: String, default: '' }, // '' | 'big'
})

const label = computed(() => STATUS_LABELS[props.category]?.[props.status] || props.status)
const color = computed(() => STATUS_COLORS[props.status] || 'var(--s-wish)')
</script>

<template>
  <span class="stamp" :class="{ big: size === 'big' }" :style="{ '--sc': color }">
    {{ label }}
  </span>
</template>

<style scoped>
.stamp {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.06em;
  line-height: 1.4;
  color: var(--text-primary);
  background: color-mix(in srgb, var(--bg-surface) 90%, transparent);
  box-shadow: inset 0 0 0 1.5px var(--sc);
  backdrop-filter: blur(4px);
  animation: stamp-in 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
.stamp::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--sc);
  flex: none;
}
.stamp.big {
  font-size: var(--fs-sm);
  padding: 5px 12px;
  box-shadow: inset 0 0 0 2px var(--sc);
}
@media (prefers-reduced-motion: reduce) {
  .stamp { animation: none; }
}
</style>
