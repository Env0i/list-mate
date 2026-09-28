<script setup>
import { computed } from 'vue'

// 原型 .seg 分段控件：v-model + options[{ value, label, count?, dot? }]，
// radiogroup 语义 + 左右方向键切换；count 显示为右侧等宽小数字
const props = defineProps({
  modelValue: { type: [String, Number], required: true },
  options: { type: Array, required: true }, // [{ value, label, count, dot }] dot 为 CSS 颜色值
  ariaLabel: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

function pick(v) {
  emit('update:modelValue', v)
}
function onKeydown(e) {
  if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return
  e.preventDefault()
  const idx = props.options.findIndex(o => o.value === props.modelValue)
  const dir = e.key === 'ArrowRight' ? 1 : -1
  const next = props.options[(idx + dir + props.options.length) % props.options.length]
  if (next) {
    emit('update:modelValue', next.value)
    // 焦点随值移动（roving tabindex 由选中项承担）
    requestAnimationFrame(() => e.currentTarget?.querySelector('[aria-checked="true"]')?.focus())
  }
}
const hasCounts = computed(() => props.options.some(o => o.count !== undefined))
</script>

<template>
  <div class="seg" role="radiogroup" :aria-label="ariaLabel || undefined" @keydown="onKeydown">
    <button
      v-for="o in options"
      :key="o.value"
      type="button"
      role="radio"
      :aria-checked="o.value === modelValue"
      :tabindex="o.value === modelValue ? 0 : -1"
      @click="pick(o.value)"
    >
      <span v-if="o.dot" class="dot" :style="{ '--dc': o.dot }" aria-hidden="true" />
      <span>{{ o.label }}</span>
      <span v-if="hasCounts" class="n">{{ o.count ?? 0 }}</span>
    </button>
  </div>
</template>

<style scoped>
.seg {
  display: inline-flex;
  padding: 3px;
  gap: 2px;
  background: var(--bg-input);
  border-radius: var(--radius-md);
  max-width: 100%;
  overflow-x: auto;
  scrollbar-width: none;
}
.seg::-webkit-scrollbar { display: none; }
.seg button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 34px;
  padding: 0 14px;
  border-radius: 8px;
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-secondary);
  white-space: nowrap;
}
.seg button:hover { color: var(--text-primary); }
.seg button[aria-checked='true'] {
  background: var(--bg-surface);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}
.seg .n {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-tertiary);
  font-weight: 500;
}
.dot { width: 8px; height: 8px; border-radius: 50%; flex: none; background: var(--dc, var(--text-tertiary)); }
/* 触屏触控目标 */
@media (pointer: coarse) {
  .seg button { min-height: 44px; }
}
</style>
