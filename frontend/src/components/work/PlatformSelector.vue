<script setup>
import { computed } from 'vue'
import { getPlatforms, getPlatformIconUrl } from '../../utils/platformIcons'

const props = defineProps({
  category: { type: String, required: true },
  modelValue: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const platforms = computed(() => getPlatforms(props.category))

function select(key) {
  emit('update:modelValue', props.modelValue === key ? '' : key)
}

function iconUrl(key) {
  return getPlatformIconUrl(props.category, key)
}
</script>

<template>
  <div class="platform-grid">
    <button
      v-for="p in platforms"
      :key="p.key"
      class="platform-btn"
      :class="{ active: modelValue === p.key }"
      :title="p.label"
      @click="select(p.key)"
    >
      <img
        v-if="iconUrl(p.key)"
        :src="iconUrl(p.key)"
        :alt="p.label"
        class="pi-icon"
        @error="e => e.target.style.display = 'none'"
      />
      <span v-else class="pi-label">{{ p.label }}</span>
    </button>

    <!-- 自定义手动输入的值（不在预设列表中） -->
    <span
      v-if="modelValue && !platforms.some(p => p.key === modelValue)"
      class="pi-custom"
    >
      {{ modelValue }}
    </span>
  </div>
</template>

<style scoped>
.platform-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.platform-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  border: 2px solid var(--color-border);
  background: var(--bg-primary);
  cursor: pointer;
  transition: all 0.15s;
}
.platform-btn:hover {
  border-color: var(--text-tertiary);
  background: var(--bg-surface-hover);
}
.platform-btn.active {
  border-color: var(--primary);
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  box-shadow: 0 0 0 1px var(--primary);
}
.pi-icon {
  width: 28px;
  height: 28px;
  object-fit: contain;
}
.pi-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  line-height: 1.2;
  text-align: center;
  word-break: break-all;
}
.pi-custom {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--primary);
}
</style>
