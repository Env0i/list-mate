<script setup>
import { computed, onMounted, ref } from 'vue'
import { bangumiApi, worksApi } from '../../../api/client'
import { showToast } from '../../../utils/toast'

// 关联作品：封面轨 + 已入册印章 + 「加入想看」（Q2 决策：直接调 worksApi.create，
// 后端会触发 Bangumi 详情抓取与封面下载；按钮转 loading，失败 toast）
const props = defineProps({
  bangumiId: { type: Number, required: true },
})

const relations = ref([])
const loading = ref(true)
const busyIds = ref(new Set())

// Bangumi type → 本地品类（3=音乐无处安放，不给入册按钮）
const CAT_MAP = { 1: 'novel', 2: 'anime', 4: 'game' }
const UNIT_MAP = { anime: 'ep', novel: 'chapter', game: 'percent', comic: 'volume' }

onMounted(load)

async function load() {
  loading.value = true
  try {
    const { data } = await bangumiApi.relations(props.bangumiId)
    relations.value = data.data || []
  } catch (e) {
    console.error('Failed to load relations', e)
  } finally {
    loading.value = false
  }
}

const addable = r => CAT_MAP[r.type] && !r.in_library_work_id
const isBusy = r => busyIds.value.has(r.id)

async function add(r) {
  if (isBusy(r)) return
  busyIds.value.add(r.id)
  try {
    const { data: created } = await worksApi.create({
      bangumi_id: r.id,
      title: r.name_cn || r.name,
      category: CAT_MAP[r.type],
      progress_unit: UNIT_MAP[CAT_MAP[r.type]] || 'ep',
      status: 'wish',
      cover_url: r.image_url,
    })
    r.in_library_work_id = created.id
    showToast(`「${created.title}」已入册`)
  } catch (e) {
    console.error('relation create failed', e)
    showToast(e.response?.data?.detail || '入册失败，请重试', 'error')
  } finally {
    busyIds.value.delete(r.id)
  }
}
</script>

<template>
  <div v-if="loading" class="rail-skel" aria-hidden="true">
    <span v-for="i in 6" :key="i" class="skel-card" />
  </div>
  <div v-else-if="relations.length" class="rail" role="list">
    <div v-for="r in relations" :key="r.id" class="rel" role="listitem">
      <div class="th-wrap">
        <img
          v-if="r.image_url"
          :src="bangumiApi.imageUrl(r.image_url)"
          :alt="r.name_cn || r.name"
          loading="lazy"
        >
        <span v-if="r.in_library_work_id" class="in-lib">已入册</span>
      </div>
      <p class="rel-k">{{ r.relation }}</p>
      <p class="nm">{{ r.name_cn || r.name }}</p>
      <button v-if="addable(r)" class="add-btn" :disabled="isBusy(r)" @click="add(r)">
        {{ isBusy(r) ? '入册中…' : '＋ 加入想看' }}
      </button>
      <router-link v-else-if="r.in_library_work_id" class="go-btn" :to="`/works/${r.in_library_work_id}`">
        查看作品
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.rail-skel { display: flex; gap: 10px; overflow: hidden; }
.skel-card { flex: none; width: 120px; height: 190px; border-radius: 8px; background: linear-gradient(90deg, var(--bg-input) 25%, var(--bg-surface-hover) 50%, var(--bg-input) 75%); background-size: 200% 100%; animation: skel 1.3s ease-in-out infinite; }
@keyframes skel { to { background-position: -200% 0; } }

.rail {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding: 2px 2px 10px;
  scroll-snap-type: x proximity;
  mask-image: linear-gradient(90deg, #000 92%, transparent);
  -webkit-mask-image: linear-gradient(90deg, #000 92%, transparent);
}
.rel { flex: none; width: 120px; scroll-snap-align: start; display: flex; flex-direction: column; }
.th-wrap {
  position: relative;
  aspect-ratio: 3 / 4.2;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-input);
  box-shadow: inset 0 0 0 1px var(--color-border);
}
.th-wrap img { width: 100%; height: 100%; object-fit: cover; display: block; }
.in-lib {
  position: absolute;
  left: 6px;
  bottom: 6px;
  padding: 2px 7px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 800;
  color: var(--text-primary);
  background: color-mix(in srgb, var(--bg-surface) 90%, transparent);
  box-shadow: inset 0 0 0 1.5px var(--s-completed);
  backdrop-filter: blur(4px);
}
.rel-k { margin: 6px 0 0; font-size: 10px; color: var(--text-tertiary); }
.nm {
  margin: 1px 0 0;
  font-size: var(--fs-xs);
  font-weight: 600;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.8em;
}
.add-btn, .go-btn {
  margin-top: 4px;
  height: 30px;
  border-radius: var(--radius-sm);
  font-size: 11px;
  font-weight: 700;
  color: var(--text-primary);
  background: color-mix(in srgb, var(--primary) 12%, var(--bg-surface));
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--primary) 45%, transparent);
  transition: background 0.15s;
  text-align: center;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.add-btn:hover:not(:disabled) { background: color-mix(in srgb, var(--primary) 22%, var(--bg-surface)); }
.add-btn:disabled { opacity: 0.55; cursor: wait; }
.go-btn { background: var(--bg-surface); box-shadow: inset 0 0 0 1px var(--color-border); color: var(--text-secondary); }
.go-btn:hover { color: var(--text-primary); background: var(--bg-surface-hover); }
@media (pointer: coarse) {
  .add-btn, .go-btn { min-height: 44px; }
}
@media (prefers-reduced-motion: reduce) {
  .skel-card { animation: none; }
}
</style>
