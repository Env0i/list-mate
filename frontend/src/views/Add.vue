<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SegmentedControl from '../components/common/SegmentedControl.vue'
import BangumiCreateModal from '../components/work/BangumiCreateModal.vue'
import DiscoverTab from './tabs/DiscoverTab.vue'
import SearchTab from './tabs/SearchTab.vue'
import ManualTab from './tabs/ManualTab.vue'

// S5 添加页合并：发现 / 搜索 / 手动 三个 Tab 共用一页；?tab= 深链可直达
const route = useRoute()
const router = useRouter()

const TAB_KEYS = ['discover', 'search', 'manual']
const tabs = [
  { value: 'discover', label: '发现' },
  { value: 'search', label: '搜索' },
  { value: 'manual', label: '手动' },
]

const tab = ref(TAB_KEYS.includes(route.query.tab) ? route.query.tab : 'discover')

watch(() => route.query.tab, (t) => {
  if (TAB_KEYS.includes(t) && t !== tab.value) tab.value = t
})
watch(tab, (t) => {
  if (route.query.tab !== t) router.replace({ path: '/add', query: { tab: t } })
})

const tabComps = { discover: DiscoverTab, search: SearchTab, manual: ManualTab }

// 发现/搜索卡片选中 → 统一弹出「确认作品信息」入库模态
const modalOpen = ref(false)
const modalItem = ref(null)

function openCreate(item) {
  modalItem.value = item
  modalOpen.value = true
}

function onCreated(work) {
  modalOpen.value = false
  router.push(`/works/${work.id}`)
}
</script>

<template>
  <div class="page">
    <div class="page-inner">
      <h1 class="page-title">添加作品</h1>
      <p class="subtitle">从 Bangumi 发现、搜索，或手动录入你的藏品</p>

      <SegmentedControl v-model="tab" :options="tabs" aria-label="添加方式" class="add-tabs" />

      <div class="tab-body">
        <KeepAlive>
          <component :is="tabComps[tab]" @select="openCreate" />
        </KeepAlive>
      </div>
    </div>

    <BangumiCreateModal :open="modalOpen" :item="modalItem" @close="modalOpen = false" @created="onCreated" />
  </div>
</template>

<style scoped>
.page { padding: 20px 16px; }
@media (max-width: 767px) { .page { padding-top: 0; } }
@media (min-width: 768px) { .page { padding: 24px 32px; } }
.page-inner { max-width: 800px; margin: 0 auto; }

.page-title { font-size: var(--fs-2xl); font-weight: 800; margin-bottom: 4px; }
.subtitle { font-size: var(--fs-sm); color: var(--text-tertiary); margin-bottom: 20px; }

.add-tabs { margin-bottom: 20px; max-width: 360px; }
.tab-body { min-height: 320px; }
</style>
