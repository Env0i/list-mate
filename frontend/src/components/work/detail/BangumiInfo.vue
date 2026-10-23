<script setup>
import { computed } from 'vue'

// 作品情报：infobox 全量键值 + 发行日期/平台/评分 + Bangumi 标签（带人数）+ 简介
const props = defineProps({
  subject: { type: Object, required: true }, // /bangumi/{id} 扩展响应
})

const infoboxRows = computed(() => {
  const rows = []
  if (props.subject.date) rows.push({ k: '发行日期', v: props.subject.date })
  const info = props.subject.infobox || []
  for (const item of info) {
    const v = item.value
    const text = Array.isArray(v) ? v.map(x => (typeof x === 'object' ? x.v : x)).join('、') : v
    if (text) rows.push({ k: item.key, v: text })
  }
  return rows
})

const tags = computed(() => (props.subject.tags || []).slice(0, 10))
</script>

<template>
  <div class="bn-info">
    <dl class="kv">
      <div v-for="r in infoboxRows" :key="r.k" class="kv-item">
        <dt>{{ r.k }}</dt>
        <dd>{{ r.v }}</dd>
      </div>
    </dl>

    <div v-if="tags.length" class="b-tags">
      <span v-for="t in tags" :key="t.name" class="b-tag">
        {{ t.name }} <small class="mono">{{ t.count }}</small>
      </span>
    </div>

    <p v-if="subject.summary" class="summary">{{ subject.summary }}</p>
  </div>
</template>

<style scoped>
.bn-info { display: flex; flex-direction: column; gap: 14px; }
.mono { font-family: var(--font-mono); }
.kv { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px 20px; margin: 0; }
.kv-item dt { font-size: 11px; color: var(--text-tertiary); letter-spacing: 0.04em; }
.kv-item dd { font-size: var(--fs-sm); font-weight: 600; margin: 2px 0 0; word-break: break-word; }
.b-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.b-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 9px;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-primary);
  background: color-mix(in srgb, var(--text-tertiary) 12%, transparent);
}
.b-tag small { color: var(--text-tertiary); }
.summary { font-size: var(--fs-sm); color: var(--text-secondary); line-height: 1.7; margin: 0; display: -webkit-box; -webkit-line-clamp: 6; -webkit-box-orient: vertical; overflow: hidden; }
</style>
