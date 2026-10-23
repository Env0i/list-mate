<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { bangumiApi } from '../../../api/client'
import CommunityCompare from './CommunityCompare.vue'
import BangumiInfo from './BangumiInfo.vue'
import EpisodeGrid from './EpisodeGrid.vue'
import CastRail from './CastRail.vue'
import RelationRail from './RelationRail.vue'
import StaffList from './StaffList.vue'
import SkeletonBlock from '../../common/SkeletonBlock.vue'

// 作品资料区外壳（§4）：subject 拉取失败只替换本区，本地记录照常可改；
// 子区块（分集/角色/关联/Staff）各自独立请求，失败只隐藏该区；stale 时来源行提示。
const props = defineProps({
  bangumiId: { type: Number, required: true },
  category: { type: String, required: true },
  myRating: { type: Number, default: null },
})

const subject = ref(null)
const stale = ref(false)
const fetchedAt = ref(null)
const loading = ref(true)
const error = ref(false)
const reloadKey = ref(0)

async function load() {
  loading.value = true
  error.value = false
  try {
    const { data } = await bangumiApi.get(props.bangumiId)
    subject.value = data
    stale.value = !!data.stale
    fetchedAt.value = data.fetched_at
  } catch (e) {
    console.error('Bangumi zone failed', e)
    error.value = true
  } finally {
    loading.value = false
  }
}
onMounted(load)
function retry() {
  reloadKey.value++
  load()
}

const isAnime = computed(() => props.category === 'anime')

// —— 吸顶锚点导航（IntersectionObserver 高亮；锚点跳转用原生 hash，不用 scrollIntoView）——
const sections = computed(() => {
  const list = [
    { id: 'bn-info', label: '概要' },
    { id: 'bn-community', label: '社区' },
  ]
  if (isAnime.value) list.push({ id: 'bn-episodes', label: '分集' })
  list.push({ id: 'bn-cast', label: '角色' }, { id: 'bn-relations', label: '关联' }, { id: 'bn-staff', label: '制作' })
  return list
})
const activeId = ref('')
let observer = null

function setupObserver() {
  observer?.disconnect()
  observer = new IntersectionObserver(
    entries => {
      for (const en of entries) {
        if (en.isIntersecting) activeId.value = en.target.id
      }
    },
    { rootMargin: '-30% 0px -60% 0px' }
  )
  for (const s of sections.value) {
    const el = document.getElementById(s.id)
    if (el) observer.observe(el)
  }
}

function fmtTime(ts) {
  if (!ts) return '—'
  const d = new Date(ts)
  const p = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}
</script>

<template>
  <section class="bn-zone">
    <div class="zone-head">
      <h2 class="zone-title">作品资料</h2>
      <span class="zone-src-hint">来自 Bangumi，只读不回写</span>
    </div>

    <!-- 加载骨架 -->
    <div v-if="loading" class="zone-loading" aria-busy="true">
      <span class="sr-only">正在读取作品资料</span>
      <SkeletonBlock h="20px" w="180px" />
      <SkeletonBlock h="96px" w="100%" radius="var(--radius-md)" />
      <SkeletonBlock h="120px" w="100%" radius="var(--radius-md)" />
    </div>

    <!-- 错误态：只替换本区 -->
    <div v-else-if="error" class="zone-error" role="alert">
      <p class="err-title">作品资料暂时没取到</p>
      <p class="err-msg">Bangumi 服务暂时没有响应，本地记录不受影响。</p>
      <div class="err-actions">
        <button class="retry-btn" @click="retry">重新加载</button>
        <a class="bgm-link" :href="`https://bgm.tv/subject/${bangumiId}`" target="_blank" rel="noopener">去 bgm.tv 查看</a>
      </div>
    </div>

    <!-- 正常 -->
    <template v-else-if="subject">
      <nav class="zone-nav" aria-label="资料分区">
        <a
          v-for="s in sections"
          :key="s.id"
          :href="`#${s.id}`"
          :class="{ on: activeId === s.id }"
        >{{ s.label }}</a>
      </nav>

      <div :key="reloadKey">
        <section id="bn-info" class="zone-sec">
          <h3 class="sec-title">概要</h3>
          <BangumiInfo :subject="subject" />
        </section>

        <section id="bn-community" class="zone-sec">
          <h3 class="sec-title">社区对照</h3>
          <CommunityCompare :rating="subject.rating" :collection="subject.collection" :my-rating="myRating" />
        </section>

        <section v-if="isAnime" id="bn-episodes" class="zone-sec">
          <h3 class="sec-title">分集</h3>
          <EpisodeGrid :bangumi-id="bangumiId" />
        </section>

        <section id="bn-cast" class="zone-sec">
          <h3 class="sec-title">主要角色</h3>
          <CastRail :bangumi-id="bangumiId" />
        </section>

        <section id="bn-relations" class="zone-sec">
          <h3 class="sec-title">关联作品</h3>
          <RelationRail :bangumi-id="bangumiId" />
        </section>

        <section id="bn-staff" class="zone-sec">
          <h3 class="sec-title">制作人员</h3>
          <StaffList :bangumi-id="bangumiId" />
        </section>
      </div>
    </template>

    <!-- 来源行 -->
    <p class="source-line">
      数据来源 Bangumi（只读） · 取数时间 {{ fmtTime(fetchedAt) }} · 条目 #{{ bangumiId }}
      <span v-if="stale" class="stale-tag">数据可能过期</span>
    </p>
  </section>
</template>

<style scoped>
.bn-zone {
  margin-top: 24px;
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm), inset 0 0 0 1px var(--color-border);
  padding: 20px 22px 16px;
}
.zone-head { display: flex; align-items: baseline; gap: 12px; margin-bottom: 14px; flex-wrap: wrap; }
.zone-title { font-size: var(--fs-lg); font-weight: 800; margin: 0; }
.zone-src-hint { font-size: var(--fs-xs); color: var(--text-tertiary); }

.zone-loading { display: flex; flex-direction: column; gap: 12px; padding: 8px 0 16px; }

.zone-error { padding: 32px 0 36px; text-align: center; }
.err-title { margin: 0 0 4px; font-size: var(--fs-lg); font-weight: 700; color: var(--text-primary); }
.err-msg { margin: 0 0 14px; font-size: var(--fs-sm); color: var(--text-secondary); }
.err-actions { display: flex; justify-content: center; gap: 10px; }
.retry-btn {
  height: 40px;
  padding: 0 16px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-primary);
  background: var(--bg-surface);
  box-shadow: inset 0 0 0 1px var(--color-border);
}
.retry-btn:hover { background: var(--bg-surface-hover); }
.bgm-link {
  display: inline-flex;
  align-items: center;
  height: 40px;
  padding: 0 16px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-secondary);
  text-decoration: underline;
  text-underline-offset: 3px;
  text-decoration-color: var(--line, rgba(0,0,0,0.09));
}
.bgm-link:hover { color: var(--text-primary); }

/* 吸顶分区导航 */
.zone-nav {
  position: sticky;
  top: var(--topbar-height);
  z-index: 15;
  display: flex;
  gap: 2px;
  padding: 6px 0;
  margin: 0 -2px 4px;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--color-border);
  overflow-x: auto;
  scrollbar-width: none;
}
.zone-nav::-webkit-scrollbar { display: none; }
.zone-nav a {
  flex: none;
  padding: 5px 12px;
  border-radius: var(--radius-full);
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-secondary);
}
.zone-nav a:hover { color: var(--text-primary); background: var(--bg-surface-hover); }
.zone-nav a.on { color: var(--primary); background: var(--primary-light); font-weight: 700; }

.zone-sec {
  padding-top: 14px;
  scroll-margin-top: calc(var(--topbar-height) + 56px);
}
.sec-title {
  margin: 0 0 10px;
  font-size: var(--fs-xs);
  font-weight: 700;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--color-border);
}

.source-line {
  margin: 18px 0 0;
  padding-top: 10px;
  border-top: 1px solid var(--color-border);
  font-size: 11px;
  color: var(--text-tertiary);
}
.stale-tag {
  margin-left: 8px;
  padding: 1px 7px;
  border-radius: 4px;
  font-weight: 700;
  color: var(--s-paused);
  box-shadow: inset 0 0 0 1.5px var(--s-paused);
}
@media (pointer: coarse) {
  .retry-btn, .bgm-link { min-height: 44px; }
  .zone-nav a { min-height: 36px; }
}
@media (max-width: 767px) {
  .bn-zone { padding: 16px 14px 12px; }
}
</style>
