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
      <h1 class="page-title">自定义标签</h1>
      <p class="subtitle">Iter 2 推出 — 创建、管理标签，按标签筛选作品</p>
      <div class="placeholder-card">
        <svg viewBox="0 0 48 48" fill="none" width="48" height="48">
          <path d="M6 10a2 2 0 012-2h16l6 6v28a2 2 0 01-2 2H8a2 2 0 01-2-2V10z" stroke="var(--primary)" stroke-width="1.5" opacity="0.3"/>
          <circle cx="16" cy="22" r="4" stroke="var(--primary)" stroke-width="1.5" opacity="0.2"/>
          <path d="M24 30l-4 4-2-2" stroke="var(--primary)" stroke-width="1.5" opacity="0.2"/>
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
