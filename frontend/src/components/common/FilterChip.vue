<script setup>
// 原型 .chip 筛选胶囊：可交互筛选项专用（只读摘要不用胶囊，用纯文字）
// props: active(aria-pressed), dot(CSS 颜色), count；激活时描边/底色用 --dc 色冒
const props = defineProps({
  active: { type: Boolean, default: false },
  dot: { type: String, default: '' },
  count: { type: [Number, String], default: undefined },
})
defineEmits(['click'])
</script>

<template>
  <button type="button" class="chip" :class="{ on: active }" :style="dot ? { '--dc': dot } : null" :aria-pressed="active" @click="$emit('click')">
    <span v-if="dot" class="dot" aria-hidden="true" />
    <slot />
    <span v-if="count !== undefined" class="n">{{ count }}</span>
  </button>
</template>

<style scoped>
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 12px;
  border-radius: var(--radius-full);
  font-size: var(--fs-xs);
  font-weight: 600;
  background: var(--bg-surface);
  color: var(--text-secondary);
  box-shadow: inset 0 0 0 1px var(--line);
  white-space: nowrap;
}
.chip:hover { color: var(--text-primary); background: var(--bg-surface-hover); }
.chip:disabled { opacity: 0.4; cursor: not-allowed; }
.chip:disabled:hover { color: var(--text-secondary); background: var(--bg-surface); }
.chip.on {
  color: var(--text-primary);
  box-shadow: inset 0 0 0 1.5px var(--dc, var(--text-primary));
  background: color-mix(in srgb, var(--dc, var(--text-primary)) 10%, var(--bg-surface));
}
.chip .n {
  font-family: var(--font-mono);
  color: var(--text-tertiary);
  font-weight: 500;
}
.dot { width: 8px; height: 8px; border-radius: 50%; flex: none; background: var(--dc, var(--text-tertiary)); }
/* 触屏触控目标 */
@media (pointer: coarse) {
  .chip { height: 44px; }
}
</style>
