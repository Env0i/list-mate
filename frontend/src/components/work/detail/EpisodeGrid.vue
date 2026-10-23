<script setup>
import { computed, onMounted, ref } from 'vue'
import { bangumiApi } from '../../../api/client'

// 分集格子：正片/SP/OP/ED + 热度条 + 下一集 + 未播出虚线（§5：TODAY 用真实日期，按东八区比较）
const props = defineProps({
  bangumiId: { type: Number, required: true },
})

const episodes = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await bangumiApi.episodes(props.bangumiId)
    episodes.value = data.data || []
  } catch (e) {
    console.error('Failed to load episodes', e)
    // 局部失败只隐藏本区（§4）
  } finally {
    loading.value = false
  }
})

const TYPE_LABEL = { 0: '', 1: 'SP', 2: 'OP', 3: 'ED' }

// 东八区今天（YYYY-MM-DD）
function todayCN() {
  const now = new Date()
  const cn = new Date(now.getTime() + (8 * 60 + now.getTimezoneOffset()) * 60000)
  const p = n => String(n).padStart(2, '0')
  return `${cn.getFullYear()}-${p(cn.getMonth() + 1)}-${p(cn.getDate())}`
}

const maxComment = computed(() => Math.max(...episodes.value.map(e => e.comment || 0), 1))
const aired = e => !e.airdate || e.airdate <= todayCN()
const nextEp = computed(() => episodes.value.find(e => !aired(e)))

const shown = computed(() => episodes.value)
</script>

<template>
  <div v-if="loading" class="ep-skel" aria-hidden="true">
    <span v-for="i in 12" :key="i" class="skel-box" />
  </div>
  <div v-else-if="shown.length" class="ep-grid">
    <div
      v-for="e in shown"
      :key="`${e.type}-${e.sort}`"
      class="ep"
      :class="{ future: !aired(e), next: nextEp && e === nextEp }"
    >
      <div class="ep-top">
        <span class="sort mono">{{ e.sort }}</span>
        <span v-if="TYPE_LABEL[e.type]" class="type">{{ TYPE_LABEL[e.type] }}</span>
        <span v-if="nextEp && e === nextEp" class="next-tag">下一集</span>
        <span v-else-if="!aired(e)" class="future-tag">未播出</span>
      </div>
      <p class="name">{{ e.name_cn || e.name }}</p>
      <p class="meta mono">{{ e.airdate || '—' }}<template v-if="e.duration"> · {{ e.duration }}</template></p>
      <div class="heat" aria-hidden="true"><i :style="{ width: Math.round(((e.comment || 0) / maxComment) * 100) + '%' }" /></div>
      <span class="cmt mono">{{ e.comment || 0 }} 讨论</span>
    </div>
  </div>
</template>

<style scoped>
.mono { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
.ep-skel { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }
.skel-box { display: block; height: 96px; border-radius: 8px; background: linear-gradient(90deg, var(--bg-input) 25%, var(--bg-surface-hover) 50%, var(--bg-input) 75%); background-size: 200% 100%; animation: skel 1.3s ease-in-out infinite; }
@keyframes skel { to { background-position: -200% 0; } }

.ep-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }
.ep {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px 12px;
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  box-shadow: inset 0 0 0 1px var(--color-border);
  overflow: hidden;
}
.ep.future { border: 1.5px dashed var(--line, rgba(0,0,0,0.09)); box-shadow: none; background: transparent; }
.ep.next { box-shadow: inset 0 0 0 2px var(--s-watching); }
.ep-top { display: flex; align-items: center; gap: 6px; }
.sort { font-size: 15px; font-weight: 700; }
.type, .next-tag, .future-tag {
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 700;
  background: var(--bg-input);
  color: var(--text-secondary);
}
.next-tag { background: var(--s-watching); color: #fff; }
.future-tag { background: transparent; box-shadow: inset 0 0 0 1px var(--line, rgba(0,0,0,0.09)); color: var(--text-tertiary); }
.name {
  margin: 0;
  font-size: var(--fs-xs);
  font-weight: 600;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.8em;
}
.meta { margin: 0; font-size: 10px; color: var(--text-tertiary); }
.heat { height: 4px; border-radius: 2px; background: var(--bg-input); overflow: hidden; margin-top: 2px; }
.heat i { display: block; height: 100%; background: var(--primary); opacity: 0.55; border-radius: inherit; }
.cmt { font-size: 10px; color: var(--text-tertiary); }
@media (prefers-reduced-motion: reduce) {
  .skel-box { animation: none; }
}
</style>
