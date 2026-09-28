<script setup>
import { computed } from 'vue'
import { actionLabels, actionIcons, formatValue, timeAgo, dayLabel } from '../../utils/timeline'

// 时间线统一皮肤（原 Stats 与 WorkDetail 各写一套）：竖线 + 动作色圆点 + 按天分组。
// showWork 用于跨作品的统计页时间线（作品 #id 可点进详情）。
const props = defineProps({
  entries: { type: Array, default: () => [] },
  showWork: { type: Boolean, default: false },
})

const groups = computed(() => {
  const out = []
  for (const e of props.entries) {
    const label = dayLabel(e.created_at)
    const last = out[out.length - 1]
    if (last && last.label === label) last.items.push(e)
    else out.push({ label, items: [e] })
  }
  return out
})

// 动作色一律取设计令牌（旧实现里 review_change 的紫色 #8b5cf6 不是令牌，改用中性次级文字色）
const ACTION_COLORS = {
  created: 'var(--s-completed)',
  status_change: 'var(--s-watching)',
  rating_change: 'var(--s-paused)',
  review_change: 'var(--text-secondary)',
  progress_update: 'var(--primary)',
}
</script>

<template>
  <ol class="tl">
    <template v-for="g in groups" :key="g.label">
      <li class="tl-day" aria-hidden="true">{{ g.label }}</li>
      <li v-for="entry in g.items" :key="entry.id" class="tl-item" :style="{ '--tc': ACTION_COLORS[entry.action_type] || 'var(--text-tertiary)' }">
        <span class="tl-marker" aria-hidden="true" />
        <div class="tl-main">
          <div class="tl-head">
            <span class="tl-icon" aria-hidden="true">{{ actionIcons[entry.action_type] || '·' }}</span>
            <span class="tl-action">{{ actionLabels[entry.action_type] || entry.action_type }}</span>
            <router-link v-if="showWork" class="tl-work" :to="`/works/${entry.work_id}`">作品 #{{ entry.work_id }}</router-link>
            <span v-if="entry.game_profile_id" class="tl-gp">配置 #{{ entry.game_profile_id }}</span>
          </div>
          <div class="tl-detail">{{ formatValue(entry.action_type, entry.old_value, entry.new_value) }}</div>
        </div>
        <time class="tl-time">{{ timeAgo(entry.created_at) }}</time>
      </li>
    </template>
  </ol>
</template>

<style scoped>
.tl {
  list-style: none;
  position: relative;
  margin: 0;
  padding: 0 0 0 22px;
}
.tl::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 8px;
  bottom: 8px;
  width: 2px;
  background: var(--color-border);
}
.tl-day {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.06em;
  color: var(--text-tertiary);
  padding: 14px 0 4px;
}
.tl-day:first-child { padding-top: 2px; }
.tl-item {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  padding: 7px 0;
  font-size: var(--fs-sm);
}
.tl-item:last-child { padding-bottom: 2px; }
.tl-marker {
  position: absolute;
  left: -21px;
  top: 14px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--bg-primary);
  box-shadow: inset 0 0 0 3px var(--tc);
}
.tl-main { min-width: 0; flex: 1; }
.tl-head {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}
.tl-icon {
  font-size: 12px;
  width: 16px;
  text-align: center;
  color: var(--text-tertiary);
  flex: none;
}
.tl-action { font-size: var(--fs-xs); font-weight: 700; }
.tl-work {
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-secondary);
}
.tl-work:hover { color: var(--text-primary); text-decoration: underline; }
.tl-gp {
  font-size: 11px;
  color: var(--text-tertiary);
}
.tl-detail {
  color: var(--text-secondary);
  font-size: var(--fs-xs);
  margin-top: 1px;
  word-break: break-word;
}
.tl-time {
  font-size: 11px;
  color: var(--text-tertiary);
  white-space: nowrap;
  flex: none;
}
@media (max-width: 767px) {
  .tl-item { flex-wrap: wrap; }
  .tl-time { margin-left: 24px; }
}
</style>
