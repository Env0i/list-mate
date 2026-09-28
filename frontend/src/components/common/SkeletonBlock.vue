<script setup>
// 骨架占位条：尺寸由调用方给定，装饰性元素对读屏隐藏（容器上另行 aria-busy + 文案）。
defineProps({
  h: { type: String, default: '12px' },
  w: { type: String, default: '100%' },
  radius: { type: String, default: '8px' },
})
</script>

<template>
  <div class="skel" :style="{ height: h, width: w, borderRadius: radius }" aria-hidden="true" />
</template>

<style scoped>
.skel {
  background: linear-gradient(90deg, var(--bg-input) 25%, var(--bg-surface-hover) 50%, var(--bg-input) 75%);
  background-size: 200% 100%;
  animation: skel-sweep 1.3s ease-in-out infinite;
}
@keyframes skel-sweep {
  to { background-position: -200% 0; }
}
@media (prefers-reduced-motion: reduce) {
  .skel { animation: none; }
}
</style>
