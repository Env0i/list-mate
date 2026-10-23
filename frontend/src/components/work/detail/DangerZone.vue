<script setup>
// 危险操作折叠区：删除作品收进页底（评审 R1：游戏配置页/详情页统一收底部折叠）
defineProps({
  deleting: { type: Boolean, default: false },
})
defineEmits(['request-delete'])
</script>

<template>
  <details class="danger">
    <summary>危险操作</summary>
    <div class="danger-body">
      <p class="hint">删除作品会一并清除进度、评分、历史记录和游戏配置，不可恢复。</p>
      <button class="del-btn" :disabled="deleting" @click="$emit('request-delete')">
        {{ deleting ? '删除中...' : '删除这部作品' }}
      </button>
    </div>
  </details>
</template>

<style scoped>
.danger {
  margin-top: 24px;
  border: 1px dashed color-mix(in srgb, var(--s-dropped) 45%, transparent);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--s-dropped) 4%, transparent);
}
summary {
  padding: 10px 14px;
  font-size: var(--fs-sm);
  font-weight: 700;
  color: var(--text-tertiary);
  cursor: pointer;
  list-style: none;
}
summary::-webkit-details-marker { display: none; }
summary::before { content: '▸ '; }
.danger[open] summary::before { content: '▾ '; }
.summary:hover { color: var(--text-secondary); }
.danger-body { padding: 0 14px 14px; }
.hint { margin: 0 0 10px; font-size: var(--fs-xs); color: var(--text-tertiary); }
.del-btn {
  height: 36px;
  padding: 0 16px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--s-dropped);
  background: var(--bg-surface);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--s-dropped) 40%, transparent);
}
.del-btn:hover:not(:disabled) { background: color-mix(in srgb, var(--s-dropped) 10%, var(--bg-surface)); }
.del-btn:disabled { opacity: 0.5; }
@media (pointer: coarse) {
  .del-btn, summary { min-height: 44px; }
}
</style>
