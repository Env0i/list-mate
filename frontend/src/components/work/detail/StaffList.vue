<script setup>
import { computed, onMounted, ref } from 'vue'
import { bangumiApi } from '../../../api/client'

// 制作人员：关键岗位（staffHi 语义）排前并高亮，其余按接口顺序
const props = defineProps({
  bangumiId: { type: Number, required: true },
})

const persons = ref([])
const loading = ref(true)

const KEY_ROLES = ['原作', '导演', '系列构成', '脚本', '人物设定', '音乐', '动画制作', '插画']

onMounted(async () => {
  try {
    const { data } = await bangumiApi.persons(props.bangumiId)
    persons.value = data.data || []
  } catch (e) {
    console.error('Failed to load persons', e)
  } finally {
    loading.value = false
  }
})

const isKey = p => KEY_ROLES.some(k => (p.relation || '').includes(k))
const sorted = computed(() => [
  ...persons.value.filter(isKey),
  ...persons.value.filter(p => !isKey(p)),
])
</script>

<template>
  <div v-if="loading" class="staff-skel" aria-hidden="true">
    <span v-for="i in 4" :key="i" class="skel-row" />
  </div>
  <ul v-else-if="sorted.length" class="staff">
    <li v-for="p in sorted" :key="p.id" :class="{ key: isKey(p) }">
      <span class="rel">{{ p.relation }}</span>
      <span class="nm">{{ p.name }}</span>
    </li>
  </ul>
</template>

<style scoped>
.staff-skel { display: flex; flex-direction: column; gap: 6px; }
.skel-row { display: block; height: 28px; border-radius: 6px; background: linear-gradient(90deg, var(--bg-input) 25%, var(--bg-surface-hover) 50%, var(--bg-input) 75%); background-size: 200% 100%; animation: skel 1.3s ease-in-out infinite; }
@keyframes skel { to { background-position: -200% 0; } }

.staff { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; }
.staff li {
  display: grid;
  grid-template-columns: minmax(72px, auto) 1fr;
  gap: 12px;
  align-items: baseline;
  padding: 7px 2px;
  border-bottom: 1px solid var(--line, rgba(0, 0, 0, 0.09));
  font-size: var(--fs-sm);
}
.staff li:last-child { border-bottom: 0; }
.staff .rel { color: var(--text-tertiary); font-size: var(--fs-xs); }
.staff .nm { color: var(--text-secondary); font-weight: 500; }
.staff li.key .rel { color: var(--s-paused); font-weight: 700; }
.staff li.key .nm { color: var(--text-primary); font-weight: 700; }
@media (prefers-reduced-motion: reduce) {
  .skel-row { animation: none; }
}
</style>
