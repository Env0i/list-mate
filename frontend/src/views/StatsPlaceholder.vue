<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <div class="page">
    <div class="page-inner">
      <div class="top-bar">
        <button class="back-btn" @click="router.push('/')">
          <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path fill-rule="evenodd" d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z" clip-rule="evenodd"/>
          </svg>
          返回
        </button>
      </div>
      <h1 class="page-title">统计仪表盘</h1>
      <p class="subtitle">Iter 3 推出 — 收藏统计、时间线、品类分布</p>
      <div class="placeholder-card">
        <svg viewBox="0 0 48 48" fill="none" width="48" height="48">
          <rect x="6" y="32" width="8" height="12" rx="2" fill="var(--c-anime)" opacity="0.3"/>
          <rect x="16" y="20" width="8" height="24" rx="2" fill="var(--c-novel)" opacity="0.3"/>
          <rect x="26" y="12" width="8" height="32" rx="2" fill="var(--c-comic)" opacity="0.3"/>
          <rect x="36" y="24" width="8" height="20" rx="2" fill="var(--c-game)" opacity="0.3"/>
        </svg>
        <p>即将推出</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 20px 16px; }
@media (min-width: 768px) { .page { padding: 24px 32px; } }
.page-inner { max-width: 600px; margin: 0 auto; }
.top-bar { margin-bottom: 16px; }
.back-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 16px; border-radius: var(--radius-md);
  font-size: var(--fs-sm); font-weight: 600; color: var(--text-tertiary);
  transition: all 0.15s;
}
.back-btn:hover { color: var(--text-primary); background: var(--bg-surface-hover); }
.page-title { font-size: var(--fs-2xl); font-weight: 800; margin-bottom: 4px; }
.subtitle { font-size: var(--fs-sm); color: var(--text-tertiary); margin-bottom: 32px; }
.placeholder-card {
  display: flex; flex-direction: column; align-items: center; gap: 16px;
  padding: 48px; background: var(--bg-surface); border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm); color: var(--text-tertiary); font-weight: 600;
}
</style>
