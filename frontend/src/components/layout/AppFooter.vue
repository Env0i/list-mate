<script setup>
import { ref, onMounted } from 'vue'
import { statsApi } from '../../api/client'

// 页脚：数据来源说明 + 本地卡册统计 + 版本号（vite define 注入 package.json version）
const version = typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : ''
const totalWorks = ref(null)

onMounted(async () => {
  try {
    const { data } = await statsApi.get()
    totalWorks.value = data.total_works
  } catch {
    totalWorks.value = null
  }
})
</script>

<template>
  <footer class="app-footer">
    <span>数据来源 Bangumi API（只读）</span>
    <span class="dot" aria-hidden="true">·</span>
    <span>本地卡册 {{ totalWorks == null ? '—' : totalWorks + ' 部作品' }}</span>
    <span class="dot" aria-hidden="true">·</span>
    <span class="mono">v{{ version || '—' }}</span>
  </footer>
</template>

<style scoped>
.app-footer {
  max-width: 800px;
  margin: 40px auto 0;
  padding: 16px 16px 24px;
  text-align: center;
  font-size: 11px;
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
  border-top: 1px solid var(--color-border);
}
.dot { opacity: 0.6; }
.mono { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
</style>
