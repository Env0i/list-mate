<script setup>
import { ref, onMounted } from 'vue'
import { currentTheme, toggleTheme } from '../../utils/theme'

const theme = ref('light')
onMounted(() => { theme.value = currentTheme() })

function onClick() {
  theme.value = toggleTheme()
}
</script>

<template>
  <button class="theme-toggle" :title="theme === 'dark' ? '切换到亮色' : '切换到暗色'" @click="onClick">
    <!-- 太阳（暗色时显示，点击切回亮色） -->
    <svg v-if="theme === 'dark'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" width="16" height="16">
      <circle cx="12" cy="12" r="4.2"/>
      <path d="M12 2.5v2.4M12 19.1v2.4M2.5 12h2.4M19.1 12h2.4M4.9 4.9l1.7 1.7M17.4 17.4l1.7 1.7M19.1 4.9l-1.7 1.7M6.6 17.4l-1.7 1.7"/>
    </svg>
    <!-- 月亮（亮色时显示，点击切到暗色） -->
    <svg v-else viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
      <path d="M20.6 14.6A8.6 8.6 0 0 1 9.4 3.4a.7.7 0 0 0-.9-.9 9.9 9.9 0 1 0 13 13 .7.7 0 0 0-.9-.9z"/>
    </svg>
  </button>
</template>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-md);
  color: var(--text-tertiary);
  transition: all 0.15s;
  flex-shrink: 0;
}
.theme-toggle:hover { color: var(--text-secondary); background: var(--bg-surface-hover); }
</style>
