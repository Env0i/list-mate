<script setup>
// 空 / 错误态统一组件：错误态自带「重新加载」（emit retry），其余动作放默认插槽。
defineProps({
  kind: { type: String, default: 'empty' }, // 'empty' | 'error'
  title: { type: String, required: true },
  message: { type: String, default: '' },
})
defineEmits(['retry'])
</script>

<template>
  <div class="state" :class="{ error: kind === 'error' }" :role="kind === 'error' ? 'alert' : undefined">
    <div class="glyph" aria-hidden="true">
      <svg v-if="kind === 'error'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="26" height="26">
        <path d="M21 12a9 9 0 1 1-2.64-6.36" />
        <path d="M21 3v6h-6" />
      </svg>
      <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" width="26" height="26">
        <path d="M21 8l-9-5-9 5v8l9 5 9-5z" />
        <path d="M3 8l9 5 9-5" />
        <path d="M12 13v9" />
      </svg>
    </div>
    <h3>{{ title }}</h3>
    <p v-if="message">{{ message }}</p>
    <div v-if="kind === 'error' || $slots.default" class="actions">
      <slot />
      <button v-if="kind === 'error'" class="state-btn" @click="$emit('retry')">重新加载</button>
    </div>
  </div>
</template>

<style scoped>
.state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 12px;
  padding: 48px 16px;
  color: var(--text-secondary);
}
.glyph {
  width: 72px;
  height: 96px;
  border-radius: 10px;
  border: 2px dashed var(--color-border);
  display: grid;
  place-items: center;
  color: var(--text-tertiary);
  transform: rotate(-4deg);
  background: var(--bg-surface);
}
.state.error .glyph {
  border-color: color-mix(in srgb, var(--s-dropped) 50%, transparent);
  color: var(--s-dropped);
}
h3 {
  font-size: var(--fs-lg);
  color: var(--text-primary);
}
p {
  max-width: 36ch;
  font-size: var(--fs-sm);
}
.actions {
  display: flex;
  gap: 10px;
  margin-top: 4px;
}
.state-btn {
  height: 40px;
  padding: 0 16px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-primary);
  background: var(--bg-surface);
  box-shadow: inset 0 0 0 1px var(--color-border);
  transition: background 0.15s;
}
.state-btn:hover { background: var(--bg-surface-hover); }
</style>
