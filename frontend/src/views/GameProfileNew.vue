<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { worksApi, gameProfilesApi } from '../api/client'
import { emptyToNull } from '../utils/payload'
import { showToast } from '../utils/toast'
import GameProfileForm from '../components/work/GameProfileForm.vue'
import StateBlock from '../components/common/StateBlock.vue'
import SkeletonBlock from '../components/common/SkeletonBlock.vue'

const route = useRoute()
const router = useRouter()

const work = ref(null)
const gp = ref({
  name: '',
  status: 'wish',
  progress_type: 'none',
  progress_value: null,
  rating: null,
  review: null,
  start_date: null,
  finish_date: null,
  playtime_hours: null,
  source: null,
  mods_list: null,
  notes: null,
})
const loading = ref(true)
const error = ref(false)
const saving = ref(false)

const isGame = computed(() => (work.value?.category || 'game') === 'game')

async function load() {
  loading.value = true
  error.value = false
  try {
    const { data } = await worksApi.get(route.params.id)
    work.value = data
  } catch (e) {
    console.error('Failed to load work', e)
    error.value = true
  } finally {
    loading.value = false
  }
}
onMounted(load)

async function submit() {
  saving.value = true
  try {
    const body = emptyToNull({
      name: gp.value.name,
      progress_value: gp.value.progress_value,
      progress_type: gp.value.progress_type,
      status: gp.value.status,
      rating: gp.value.rating,
      review: gp.value.review,
      start_date: gp.value.start_date,
      finish_date: gp.value.finish_date,
      playtime_hours: gp.value.playtime_hours,
      source: gp.value.source,
      mods_list: gp.value.mods_list,
      notes: gp.value.notes,
    }, ['progress_value', 'rating', 'playtime_hours'])
    const { data } = await gameProfilesApi.create(route.params.id, body)
    showToast('配置已创建')
    router.push(`/works/${route.params.id}/game-profiles/${data.id}`)
  } catch (e) {
    console.error('Create failed', e)
    showToast(e.response?.data?.detail || '创建失败', 'error')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="page narrow">
    <!-- 加载骨架 -->
    <template v-if="loading">
      <div class="crumb" aria-hidden="true"><SkeletonBlock h="14px" w="220px" /></div>
      <div class="gp-head" aria-hidden="true">
        <SkeletonBlock h="96px" w="72px" radius="8px" />
        <div class="gp-head-text">
          <SkeletonBlock h="12px" w="120px" />
          <SkeletonBlock h="26px" w="200px" radius="6px" />
        </div>
      </div>
      <div aria-busy="true">
        <span class="sr-only">正在读取作品信息</span>
        <SkeletonBlock v-for="h in [180, 150]" :key="h" :h="h + 'px'" w="100%" radius="var(--radius-lg)" class="skel-sec" />
      </div>
    </template>

    <!-- 错误态 -->
    <StateBlock
      v-else-if="error"
      kind="error"
      title="作品信息没能打开"
      message="本地服务暂时没有响应，稍后重试即可。"
      @retry="load"
    >
      <button class="ghost-btn" @click="router.push(`/works/${route.params.id}`)">回到作品详情</button>
    </StateBlock>

    <!-- 非游戏品类 -->
    <StateBlock
      v-else-if="!isGame"
      kind="error"
      title="只有游戏可以添加配置"
      message="番剧、小说、漫画的进度直接在作品详情页记录。"
    >
      <button class="ghost-btn" @click="router.push('/')">回到收藏</button>
    </StateBlock>

    <!-- 表单 -->
    <template v-else>
      <nav class="crumb" aria-label="路径">
        <router-link to="/">收藏</router-link>
        <span class="sep" aria-hidden="true">/</span>
        <router-link :to="`/works/${route.params.id}`">{{ work?.title }}</router-link>
        <span class="sep" aria-hidden="true">/</span>
        <span aria-current="page">新增配置</span>
      </nav>

      <header class="gp-head">
        <div
          class="th"
          :style="work?.cover_url
            ? { background: `url(${worksApi.coverUrl(work.id)}) center/cover no-repeat` }
            : { background: 'linear-gradient(135deg, var(--c-game), var(--c-game-light))' }"
          aria-hidden="true"
        />
        <div class="gp-head-text">
          <p class="eyebrow">游戏配置 · 新建</p>
          <h1 class="gp-title">新增一套配置</h1>
          <p class="gp-sub">{{ work?.title }} · 本体、周目、整合包或 DLC，各自独立追踪</p>
        </div>
      </header>

      <GameProfileForm
        :gp="gp"
        is-new
        :saving="saving"
        cancel-to="/"
        @save="submit"
      />
    </template>
  </div>
</template>

<style scoped>
.page { padding: 20px 16px 64px; }
@media (min-width: 768px) { .page { padding: 24px 32px 64px; } }
.page.narrow { max-width: 1080px; margin: 0 auto; }

.crumb {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--fs-sm);
  color: var(--text-secondary);
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.crumb a:hover { color: var(--text-primary); text-decoration: underline; }
.crumb .sep { color: var(--text-tertiary); opacity: 0.4; }
.crumb [aria-current='page'] { color: var(--text-primary); font-weight: 700; }

.gp-head {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  gap: 16px;
  align-items: center;
  margin-bottom: 24px;
}
.gp-head .th {
  width: 72px;
  aspect-ratio: 3 / 4.2;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 0 0 2.5px var(--c-game), 0 0 0 5px var(--bg-surface), 0 0 0 6px var(--line, rgba(0,0,0,0.09));
}
.gp-head-text { min-width: 0; }
.eyebrow {
  font-family: var(--font-mono);
  font-size: var(--fs-xs);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-tertiary);
  margin-bottom: 2px;
}
.gp-title { font-size: var(--fs-2xl); font-weight: 800; letter-spacing: -0.3px; }
.gp-sub { color: var(--text-secondary); font-size: var(--fs-sm); }

.skel-sec { display: block; margin-bottom: 16px; }

.ghost-btn {
  height: 40px;
  padding: 0 16px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-secondary);
}
.ghost-btn:hover { background: var(--bg-surface-hover); color: var(--text-primary); }
</style>
