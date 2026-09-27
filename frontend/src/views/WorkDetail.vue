<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { worksApi, tagsApi, coverApi, timelineApi } from '../api/client'
import CategoryBadge from '../components/work/CategoryBadge.vue'
import ProgressBar from '../components/work/ProgressBar.vue'
import PlatformSelector from '../components/work/PlatformSelector.vue'
import { getPlatformIconUrl } from '../utils/platformIcons'
import { showToast } from '../utils/toast'
import { emptyToNull } from '../utils/payload'
import { STATUS_LABELS, STATUS_COLORS } from '../constants/work'
import { actionLabels, actionIcons, formatValue, timeAgo, dayLabel } from '../utils/timeline'

const route = useRoute()
const router = useRouter()
const work = ref(null)
const loading = ref(true)
const deleting = ref(false)
const saving = ref(false)
const showEditModal = ref(false)
const form = ref({})
const history = ref([])
const historyLoading = ref(true)
const historyTotal = ref(0)
const historyPage = ref(1)
const historyPageSize = 20
const allTags = ref([])
const selectedTagIds = ref([])
const tagLoading = ref(false)

const statusLabels = STATUS_LABELS
const statusBg = STATUS_COLORS

const progressUnitMap = { anime: '集', novel: '章', comic: '卷' }

const catColor = computed(() => `var(--c-${work.value?.category || 'anime'})`)

const bangumiInfo = computed(() => {
  if (!work.value?.bangumi_data) return null
  try { return JSON.parse(work.value.bangumi_data) } catch { return null }
})

const infoboxMap = computed(() => {
  if (!bangumiInfo.value?.infobox) return {}
  const m = {}
  for (const item of bangumiInfo.value.infobox) {
    const v = item.value
    m[item.key] = Array.isArray(v) ? v.map(x => x.v || x).join('、') : v
  }
  return m
})

const stLabel = computed(() => {
  if (!work.value) return ''
  const cat = work.value.category
  if (cat === 'game') {
    const st = work.value.game_profiles?.[0]?.status || 'wish'
    return statusLabels[cat]?.[st] || st
  }
  return statusLabels[cat]?.[work.value.status] || work.value.status || '—'
})

const stBg = computed(() => {
  if (!work.value) return 'var(--s-wish)'
  const cat = work.value.category
  const key = cat === 'game'
    ? work.value.game_profiles?.[0]?.status || 'wish'
    : work.value.status || 'wish'
  return statusBg[key] || 'var(--s-wish)'
})

function gpProgressLabel(gp) {
  if (gp.progress_value == null) return '—'
  const pt = gp.progress_type || 'none'
  if (pt === 'percent') return `${Math.round(gp.progress_value)}%`
  if (pt === 'count') return `${gp.progress_value} 次`
  return '—'
}

function gpProgressPct(gp) {
  if (gp.progress_value == null) return 0
  const pt = gp.progress_type || 'none'
  if (pt === 'percent') return Math.min(100, Math.round(gp.progress_value))
  return 0
}

async function load() {
  loading.value = true
  try {
    const { data } = await worksApi.get(route.params.id)
    work.value = data
  } catch (e) {
    console.error('Failed to load work', e)
  } finally {
    loading.value = false
  }
}

async function del() {
  if (!confirm('确定删除这个作品？所有关联数据将一并删除。')) return
  deleting.value = true
  try {
    await worksApi.delete(route.params.id)
    showToast('作品已删除')
    router.push('/')
  } catch (e) {
    console.error('Failed to delete', e)
    showToast('删除失败', 'error')
    deleting.value = false
  }
}

const coverUploading = ref(false)
async function uploadCover(e) {
  const file = e.target.files?.[0]
  if (!file) return
  coverUploading.value = true
  try {
    await coverApi.upload(route.params.id, file)
    work.value.cover_url = URL.createObjectURL(file)
    // Force reload to get the real cover
    const { data } = await worksApi.get(route.params.id)
    work.value = data
    showToast('封面上传成功')
  } catch (e) {
    console.error('Cover upload failed', e)
    showToast('封面上传失败', 'error')
  } finally {
    coverUploading.value = false
    e.target.value = ''
  }
}

async function openEdit() {
  form.value = { ...work.value }
  // 游戏作品的状态存在 GameProfile 上
  if (work.value.category === 'game' && work.value.game_profiles?.length) {
    form.value.status = work.value.game_profiles[0].status
  }
  selectedTagIds.value = (work.value.tags || []).map(t => t.id)
  showEditModal.value = true
  tagLoading.value = true
  try {
    const { data } = await tagsApi.list()
    allTags.value = data
  } catch (e) { console.error('Failed to load tags', e) }
  finally { tagLoading.value = false }
}

function toggleTag(tid) {
  const idx = selectedTagIds.value.indexOf(tid)
  if (idx >= 0) selectedTagIds.value.splice(idx, 1)
  else selectedTagIds.value.push(tid)
}

function closeEdit() {
  showEditModal.value = false
}

async function saveEdit() {
  saving.value = true
  try {
    const payload = emptyToNull({
      title: form.value.title,
      category: form.value.category,
      sub_category: form.value.sub_category,
      status: form.value.status,
      progress_unit: form.value.progress_unit,
      total: form.value.total,
      progress_value: form.value.progress_value,
      summary: form.value.summary,
      rating: form.value.rating,
      review: form.value.review,
      platform: form.value.platform,
      purchase_platform: form.value.purchase_platform,
      purchase_price: form.value.purchase_price,
      purchase_date: form.value.purchase_date,
      playtime_hours: form.value.playtime_hours,
      start_date: form.value.start_date,
      finish_date: form.value.finish_date,
      priority: form.value.priority,
      is_free: form.value.is_free,
      external_links: form.value.external_links,
      tag_ids: selectedTagIds.value,
    }, [
      'status', 'total', 'progress_value', 'priority',
      'purchase_price', 'playtime_hours', 'replay_count', 'rating',
    ])
    // 游戏状态存在 GameProfile 上且不可为空；无配置时不要提交 status
    if (form.value.category === 'game' && payload.status == null) {
      delete payload.status
    }
    const res = await worksApi.update(route.params.id, payload)
    work.value = { ...work.value, ...res.data }
    // 游戏作品状态在 GameProfile 上，同步到本地显示
    if (work.value.category === 'game' && work.value.game_profiles?.length) {
      work.value.game_profiles[0].status = form.value.status
    }
    // Update local tags from allTags
    work.value.tags = allTags.value.filter(t => selectedTagIds.value.includes(t.id))
    showEditModal.value = false
    showToast('保存成功')
  } catch (e) {
    console.error('Failed to save', e)
    showToast('保存失败', 'error')
  } finally {
    saving.value = false
  }
}

// 历史按天分组（与 Stats 操作记录同一标签规则）
const groupedHistory = computed(() => {
  const groups = []
  for (const e of history.value) {
    const label = dayLabel(e.created_at)
    const last = groups[groups.length - 1]
    if (last && last.label === label) last.items.push(e)
    else groups.push({ label, items: [e] })
  }
  return groups
})

async function loadHistory() {
  historyLoading.value = true
  try {
    const { data } = await timelineApi.list({ work_id: route.params.id, page: 1, page_size: historyPageSize })
    history.value = data.items
    historyTotal.value = data.total
    historyPage.value = 1
  } catch (e) {
    console.error('Failed to load history', e)
  } finally {
    historyLoading.value = false
  }
}

async function loadMoreHistory() {
  if (history.value.length >= historyTotal.value) return
  const { data } = await timelineApi.list({
    work_id: route.params.id,
    page: historyPage.value + 1,
    page_size: historyPageSize,
  })
  const seen = new Set(history.value.map(e => e.id))
  for (const e of data.items) if (!seen.has(e.id)) history.value.push(e)
  historyTotal.value = data.total
  historyPage.value += 1
}

onMounted(() => { load(); loadHistory() })
</script>

<template>
  <div class="page">
    <!-- Loading -->
    <div class="page-inner" v-if="loading">
      <div class="loading">加载中...</div>
    </div>

    <!-- Error -->
    <div class="page-inner" v-else-if="!work">
      <div class="empty">
        <p>作品不存在</p>
        <button class="back-btn" @click="router.push('/')">返回列表</button>
      </div>
    </div>

    <!-- Main content -->
    <div class="page-inner" v-else>
      <!-- Header -->
      <div class="top-bar">
        <button class="back-btn" @click="router.push('/')">
          <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path fill-rule="evenodd" d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z" clip-rule="evenodd"/>
          </svg>
          返回
        </button>
        <div class="top-actions">
          <button class="act-btn edit" @click="openEdit">
            <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
              <path d="M2.695 14.763l-1.262 3.154a.5.5 0 00.65.65l3.155-1.262a4 4 0 001.343-.885L17.5 7.5a2.121 2.121 0 00-3-3L3.58 13.42a4 4 0 00-.885 1.343z"/>
            </svg>
            编辑
          </button>
          <button class="act-btn del" @click="del" :disabled="deleting">
            <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
              <path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c-.84 0-1.673.025-2.5.075V3.75c0-.69.56-1.25 1.25-1.25h2.5c.69 0 1.25.56 1.25 1.25v.325C11.673 4.025 10.84 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clip-rule="evenodd"/>
            </svg>
            删除
          </button>
        </div>
      </div>

      <!-- Hero: cover + info card -->
      <div class="hero">
        <!-- Cover card -->
        <div class="cover-w">
          <div class="cover-card" :style="{ '--cat-color': catColor }">
            <div
              class="cover-img"
              :style="{
                background: work.cover_url
                  ? `url(${worksApi.coverUrl(work.id)}) center/cover no-repeat`
                  : catColor
              }"
            >
              <div v-if="!work.cover_url" class="cover-placeholder">
                <svg viewBox="0 0 40 40" fill="none" width="32" height="32">
                  <circle cx="20" cy="20" r="18" stroke="white" stroke-width="1" opacity="0.3"/>
                  <path d="M20 8v24M8 20h24" stroke="white" stroke-width="1.5" opacity="0.2"/>
                </svg>
              </div>
            </div>
          </div>
          <label class="cover-upload-btn" :class="{ uploading: coverUploading }">
            <input type="file" class="file-inp" accept="image/*" @change="uploadCover" :disabled="coverUploading" />
            <svg viewBox="0 0 20 20" fill="currentColor" width="12" height="12">
              <path d="M9.25 13.25a.75.75 0 001.5 0V4.636l2.955 3.129a.75.75 0 001.09-1.03l-4.25-4.5a.75.75 0 00-1.09 0l-4.25 4.5a.75.75 0 101.09 1.03L9.25 4.636V13.25z"/>
              <path d="M3.5 12.75a.75.75 0 00-1.5 0v2.5A2.75 2.75 0 004.75 18h10.5A2.75 2.75 0 0018 15.25v-2.5a.75.75 0 00-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5z"/>
            </svg>
            {{ coverUploading ? '上传中...' : '更换封面' }}
          </label>
        </div>

        <!-- Info card -->
        <div class="info-col">
          <div class="info-card" :style="{ '--cat-color': catColor }">
            <div class="info-hd">
              <h1 class="title">{{ work.title }}</h1>
              <CategoryBadge :category="work.category" />
            </div>
            <div class="meta">
              <span v-if="work.sub_category">{{ work.sub_category }}</span>
              <span v-if="work.sub_category && work.total" class="sep">·</span>
              <span v-if="work.total">{{ work.total }} {{ progressUnitMap[work.category] || '' }}</span>
            </div>

            <div class="stamp-row">
              <span class="status-stamp" :style="{ '--st-bg': stBg }">{{ stLabel }}</span>
            </div>

            <!-- Personal tags -->
            <div v-if="work.tags?.length" class="ptags-row">
              <span
                v-for="t in work.tags"
                :key="t.id"
                class="ptag-chip"
                :style="{ background: t.color + '20', color: t.color, borderColor: t.color + '40' }"
              >{{ t.name }}</span>
            </div>

            <!-- Bangumi info -->
            <template v-if="bangumiInfo">
              <div class="section-label">作品情報</div>
              <div class="info-rows">
                <div class="ir" v-if="bangumiInfo.date">
                  <span class="ir-l">发行日期</span>
                  <span class="ir-v">{{ bangumiInfo.date }}</span>
                </div>
                <div class="ir" v-if="bangumiInfo.platform">
                  <span class="ir-l">平台</span>
                  <span class="ir-v">{{ bangumiInfo.platform }}</span>
                </div>
                <div class="ir" v-if="bangumiInfo.score && bangumiInfo.score > 0">
                  <span class="ir-l">Bangumi 评分</span>
                  <span class="ir-v">★ {{ bangumiInfo.score }}</span>
                </div>
                <div class="ir" v-if="infoboxMap['游戏类型'] || infoboxMap['类型']">
                  <span class="ir-l">类型</span>
                  <span class="ir-v">{{ infoboxMap['游戏类型'] || infoboxMap['类型'] }}</span>
                </div>
                <div class="ir" v-if="infoboxMap['开发商']">
                  <span class="ir-l">开发商</span>
                  <span class="ir-v">{{ infoboxMap['开发商'] }}</span>
                </div>
                <div class="ir" v-if="infoboxMap['发行商'] || infoboxMap['出版社']">
                  <span class="ir-l">发行商</span>
                  <span class="ir-v">{{ infoboxMap['发行商'] || infoboxMap['出版社'] }}</span>
                </div>
                <div class="ir" v-if="infoboxMap['作者']">
                  <span class="ir-l">作者</span>
                  <span class="ir-v">{{ infoboxMap['作者'] }}</span>
                </div>
                <div class="ir" v-if="infoboxMap['导演']">
                  <span class="ir-l">导演</span>
                  <span class="ir-v">{{ infoboxMap['导演'] }}</span>
                </div>
                <div class="ir" v-if="infoboxMap['脚本'] || infoboxMap['剧本']">
                  <span class="ir-l">剧本</span>
                  <span class="ir-v">{{ infoboxMap['脚本'] || infoboxMap['剧本'] }}</span>
                </div>
                <div class="ir" v-if="infoboxMap['音乐']">
                  <span class="ir-l">音乐</span>
                  <span class="ir-v">{{ infoboxMap['音乐'] }}</span>
                </div>
                <div class="ir ir-tags" v-if="bangumiInfo.tags?.length">
                  <span class="ir-l">标签</span>
                  <span class="ir-v">
                    <span v-for="t in bangumiInfo.tags.slice(0, 8)" :key="t" class="b-tag">{{ t }}</span>
                  </span>
                </div>
              </div>
            </template>

            <!-- Summary -->
            <p v-if="work.summary" class="summary">{{ work.summary }}</p>
          </div>
        </div>
      </div>

      <!-- Tracking card -->
      <div class="tracking-card" :style="{ '--cat-color': catColor }">
        <div class="tracking-header">
          <h2 class="tracking-title">个人追踪</h2>
        </div>

        <div class="tracking-grid">
          <div class="tk-item" v-if="work.start_date">
            <span class="tk-l">开始时间</span>
            <span class="tk-v">{{ work.start_date }}</span>
          </div>
          <div class="tk-item" v-if="work.finish_date">
            <span class="tk-l">完成时间</span>
            <span class="tk-v">{{ work.finish_date }}</span>
          </div>
          <div class="tk-item" v-if="work.platform">
            <span class="tk-l">平台</span>
            <span class="tk-v">
              <img
                v-if="getPlatformIconUrl(work.category, work.platform)"
                :src="getPlatformIconUrl(work.category, work.platform)"
                class="tk-icon"
                @error="e => e.target.style.display = 'none'"
              />
              {{ work.platform }}
            </span>
          </div>
          <div class="tk-item" v-if="work.priority != null">
            <span class="tk-l">优先度</span>
            <span class="tk-v">⭐ {{ work.priority }}</span>
          </div>
          <template v-if="work.category === 'game'">
            <div class="tk-item" v-if="work.is_free && work.platform">
              <span class="tk-l">获取方式</span>
              <span class="tk-v"><span class="free-badge">免费获取</span></span>
            </div>
            <template v-if="!work.is_free">
              <div class="tk-item" v-if="work.purchase_date">
                <span class="tk-l">购买时间</span>
                <span class="tk-v">{{ work.purchase_date }}</span>
              </div>
              <div class="tk-item" v-if="work.purchase_price != null">
                <span class="tk-l">购买价格</span>
                <span class="tk-v">{{ work.purchase_price }} 元</span>
              </div>
            </template>
            <div class="tk-item" v-if="work.playtime_hours != null">
              <span class="tk-l">游戏时长</span>
              <span class="tk-v">{{ work.playtime_hours }} 小时</span>
            </div>
            <div class="tk-item" v-if="work.replay_count != null">
              <span class="tk-l">重刷次数</span>
              <span class="tk-v">{{ work.replay_count }} 次</span>
            </div>
          </template>
          <div class="tk-item tk-full" v-if="work.external_links">
            <span class="tk-l">外部链接</span>
            <span class="tk-v">{{ work.external_links }}</span>
          </div>
        </div>

        <!-- Progress + Rating + Review (non-game) -->
        <template v-if="work.category !== 'game'">
          <div class="tk-divider"></div>
          <div class="tk-section">
            <div class="section-label-sm">进度</div>
            <ProgressBar :current="work.progress_value" :total="work.total" :category="work.category" />
          </div>
          <div class="tk-section" v-if="work.rating != null">
            <div class="section-label-sm">评分</div>
            <div class="rating-display">{{ work.rating }}/10</div>
          </div>
          <div class="tk-section" v-if="work.review">
            <div class="section-label-sm">评价</div>
            <p class="review-text">{{ work.review }}</p>
          </div>
        </template>
      </div>

      <!-- History card -->
      <div class="history-card" :style="{ '--cat-color': catColor }">
        <div class="tracking-header">
          <h2 class="tracking-title">历史</h2>
          <span v-if="historyTotal" class="history-count">{{ historyTotal }} 条记录</span>
        </div>
        <div v-if="historyLoading" class="history-hint">加载中...</div>
        <div v-else-if="history.length" class="history-list">
          <template v-for="g in groupedHistory" :key="g.label">
            <div class="h-day">{{ g.label }}</div>
            <div v-for="e in g.items" :key="e.id" class="history-item">
              <span class="h-icon">{{ actionIcons[e.action_type] || '·' }}</span>
              <div class="h-body">
                <div class="h-head">
                  <span class="h-action">{{ actionLabels[e.action_type] || e.action_type }}</span>
                  <span v-if="e.game_profile_id" class="h-gp">配置 #{{ e.game_profile_id }}</span>
                </div>
                <div class="h-detail">{{ formatValue(e.action_type, e.old_value, e.new_value) }}</div>
              </div>
              <span class="h-time">{{ timeAgo(e.created_at) }}</span>
            </div>
          </template>
        </div>
        <p v-else class="history-hint">暂无记录</p>
        <button
          v-if="!historyLoading && history.length < historyTotal"
          class="history-more"
          @click="loadMoreHistory"
        >加载更多（已显示 {{ history.length }} / {{ historyTotal }}）</button>
      </div>

      <!-- Game profiles section -->
      <div v-if="work.category === 'game'" class="gp-section">
        <div class="gp-hd">
          <h2 class="gp-title">游戏配置</h2>
          <button class="add-gp-btn" @click="router.push(`/works/${work.id}/game-profiles/new`)">
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
              <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z"/>
            </svg>
            新增配置
          </button>
        </div>

        <div v-if="work.game_profiles?.length" class="gp-bars">
          <div
            v-for="gp in work.game_profiles"
            :key="gp.id"
            class="gp-bar"
            :style="{ '--gp-accent': statusBg[gp.status] || 'var(--s-wish)' }"
            @click="router.push(`/works/${work.id}/game-profiles/${gp.id}`)"
          >
            <span class="gp-name">{{ gp.name }}</span>
            <span class="gp-st" :style="{ background: statusBg[gp.status] || 'var(--s-wish)' }">
              {{ statusLabels.game?.[gp.status] || gp.status }}
            </span>
            <div class="gp-prog">
              <template v-if="(gp.progress_type || 'none') !== 'none' && gp.progress_value != null">
                <div class="gp-exp-rail">
                  <div
                    class="gp-exp-fill"
                    :style="{
                      width: gpProgressPct(gp) + '%',
                      background: 'var(--c-game)'
                    }"
                  >
                    <div class="gp-exp-shine" />
                  </div>
                </div>
                <span class="gp-prog-lbl">{{ gpProgressLabel(gp) }}</span>
              </template>
              <span v-else class="gp-prog-none">—</span>
            </div>
            <span class="gp-rating" v-if="gp.rating != null">{{ gp.rating }}/10</span>
          </div>
        </div>
        <div v-else class="gp-empty">暂无游戏配置</div>
      </div>
    </div>

    <!-- Edit Modal — collector's spec sheet -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showEditModal" class="modal-overlay" @click.self="closeEdit">
          <div
            class="modal-card"
            :style="{ '--modal-accent': `var(--c-${work?.category || 'anime'})` }"
            @click.stop
          >
            <!-- Header with cover thumb -->
            <div class="modal-hd">
              <div class="modal-hd-left">
                <div
                  class="modal-thumb"
                  :style="{
                    background: work?.cover_url
                      ? `url(${worksApi.coverUrl(work?.id)}) center/cover no-repeat`
                      : 'var(--modal-accent)'
                  }"
                >
                  <div v-if="!work?.cover_url" class="modal-thumb-none">
                    <svg viewBox="0 0 20 20" fill="none" width="14" height="14">
                      <circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="0.5" opacity="0.4"/>
                      <path d="M10 3v14M3 10h14" stroke="currentColor" stroke-width="0.8" opacity="0.3"/>
                    </svg>
                  </div>
                </div>
                <div class="modal-hd-text">
                  <h2>编辑作品</h2>
                  <span class="modal-hd-cat">{{ work?.title || '' }}</span>
                </div>
              </div>
              <button class="modal-close" @click="closeEdit">
                <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
                  <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"/>
                </svg>
              </button>
            </div>

            <div class="modal-body">
              <div class="modal-grid">
                <!-- Left column -->
                <div class="modal-col">
                  <!-- Section 1: 基本信息 -->
                  <div class="modal-section">
                    <h3 class="modal-section-title">基本信息</h3>
                    <div class="modal-fields">
                      <label class="mf-label">
                        <span>标题</span>
                        <input v-model="form.title" placeholder="作品名称" />
                      </label>
                      <div class="mf-row">
                        <label class="mf-label mf-sm">
                          <span>子分类</span>
                          <input v-model="form.sub_category" placeholder="如：单机、欧美剧" />
                        </label>
                        <label class="mf-label mf-xs" v-if="work?.category !== 'game'">
                          <span>总量</span>
                          <input v-model.number="form.total" type="number" min="0" placeholder="0" />
                        </label>
                      </div>
                      <div class="mf-row">
                        <label class="mf-label mf-sm">
                          <span>状态</span>
                          <select v-model="form.status">
                            <!-- 游戏状态存在 GameProfile 上且不可为空，不提供清空选项 -->
                            <option v-if="work?.category !== 'game'" value="">—</option>
                            <option v-for="(label, key) in statusLabels[work?.category]" :key="key" :value="key">{{ label }}</option>
                          </select>
                        </label>
                        <label class="mf-label mf-xs" v-if="work?.category !== 'game'">
                          <span>进度</span>
                          <input v-model.number="form.progress_value" type="number" min="0" placeholder="0" />
                        </label>
                      </div>
                    </div>
                  </div>

                  <!-- Section 2: 追踪信息 -->
                  <div class="modal-section">
                    <h3 class="modal-section-title">追踪信息</h3>
                    <div class="modal-fields">
                      <label class="mf-label">
                        <span>开始时间</span>
                        <input v-model="form.start_date" type="date" />
                      </label>
                      <label class="mf-label">
                        <span>完成时间</span>
                        <input v-model="form.finish_date" type="date" />
                      </label>
                      <label class="mf-label">
                        <span>平台</span>
                        <PlatformSelector :category="work?.category" v-model="form.platform" />
                      </label>
                      <div class="mf-row">
                        <label class="mf-label mf-xs">
                          <span>优先度</span>
                          <input v-model.number="form.priority" type="number" min="0" max="5" placeholder="0-5" />
                        </label>
                        <label class="mf-label mf-xs" v-if="work?.category !== 'game'">
                          <span>重刷次数</span>
                          <input v-model.number="form.replay_count" type="number" min="0" placeholder="0" />
                        </label>
                      </div>
                      <label class="mf-label">
                        <span>外部链接</span>
                        <input v-model="form.external_links" placeholder='{"steam":"https://..."}' />
                      </label>
                    </div>
                  </div>

                  <!-- Section 3: 游戏专属 -->
                  <div class="modal-section" v-if="work?.category === 'game'">
                    <div class="modal-section-row">
                      <h3 class="modal-section-title">游戏专属</h3>
                      <label class="free-toggle">
                        <span>{{ form.is_free ? '免费' : '付费' }}</span>
                        <input type="checkbox" v-model="form.is_free" />
                      </label>
                    </div>
                    <div class="modal-fields">
                      <div class="mf-row" v-if="!form.is_free">
                        <label class="mf-label mf-sm">
                          <span>购买价格</span>
                          <input v-model.number="form.purchase_price" type="number" min="0" step="0.01" placeholder="0" />
                        </label>
                      </div>
                      <label class="mf-label" v-if="!form.is_free">
                        <span>购买时间</span>
                        <input v-model="form.purchase_date" type="date" />
                      </label>
                      <div class="mf-row">
                        <label class="mf-label mf-sm">
                          <span>游戏时长（小时）</span>
                          <input v-model.number="form.playtime_hours" type="number" min="0" step="0.1" placeholder="0" />
                        </label>
                        <label class="mf-label mf-sm">
                          <span>重刷次数</span>
                          <input v-model.number="form.replay_count" type="number" min="0" placeholder="0" />
                        </label>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Right column -->
                <div class="modal-col">
                  <!-- Tags -->
                  <div class="modal-section">
                    <h3 class="modal-section-title">标签</h3>
                    <div v-if="tagLoading" class="tag-loading">加载标签中...</div>
                    <div v-else-if="allTags.length" class="tag-chips">
                      <button
                        v-for="t in allTags"
                        :key="t.id"
                        class="tchip"
                        :class="{ on: selectedTagIds.includes(t.id) }"
                        :style="selectedTagIds.includes(t.id) ? { background: t.color, color: '#fff', borderColor: t.color } : { color: t.color, borderColor: t.color + '40' }"
                        @click="toggleTag(t.id)"
                      >{{ t.name }}</button>
                    </div>
                    <p v-else class="tag-none">暂无标签，前往 <router-link to="/tags" class="tag-link">标签管理</router-link> 创建</p>
                  </div>

                  <!-- Rating -->
                  <div class="modal-section">
                    <h3 class="modal-section-title">评分评价</h3>
                    <div class="modal-fields">
                      <label class="mf-label">
                        <span>评分 {{ form.rating != null ? form.rating + '/10' : '—' }}</span>
                        <input v-model.number="form.rating" type="range" min="0" max="10" class="rating-slider" />
                      </label>
                      <label class="mf-label">
                        <span>评价</span>
                        <textarea v-model="form.review" rows="3" placeholder="写下你的评价..." />
                      </label>
                    </div>
                  </div>

                  <!-- Summary -->
                  <div class="modal-section">
                    <h3 class="modal-section-title">简介</h3>
                    <textarea
                      v-model="form.summary"
                      class="modal-summary-ta"
                      rows="4"
                      placeholder="作品简介..."
                    />
                  </div>
                </div>
              </div>
            </div>

            <div class="modal-ft">
              <button class="modal-cancel" @click="closeEdit">取消</button>
              <button class="modal-save" @click="saveEdit" :disabled="saving">
                {{ saving ? '保存中...' : '保存修改' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
/* ===== Layout ===== */
.page { padding: 20px 16px; }
@media (max-width: 767px) { .page { padding-top: 0; } }
@media (min-width: 768px) { .page { padding: 24px 32px; } }
.page-inner { max-width: 960px; margin: 0 auto; }
.loading, .empty { text-align: center; padding: 80px 20px; color: var(--text-tertiary); }

/* ===== Header ===== */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-tertiary);
  transition: all 0.15s;
}
.back-btn:hover { color: var(--text-primary); background: var(--bg-surface-hover); }
.top-actions { display: flex; gap: 8px; }
.act-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-tertiary);
  transition: all 0.15s;
}
.act-btn:hover { background: var(--bg-surface); }
.act-btn.edit:hover { color: var(--primary); }
.act-btn.del:hover { color: var(--c-anime); }
.act-btn:disabled { opacity: 0.4; }

/* ===== Hero (cover + info) ===== */
.hero {
  display: flex;
  gap: 28px;
  margin-bottom: 24px;
}
@media (max-width: 767px) {
  .hero { flex-direction: column; align-items: center; gap: 20px; }
}

/* Cover card */
.cover-w { flex-shrink: 0; }
.cover-card {
  position: relative;
  width: 240px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow:
    0 0 0 3px var(--cat-color),
    0 0 0 8px rgba(255,255,255,0.7),
    0 0 0 9px var(--frame-outer-line),
    0 8px 30px rgba(0,0,0,0.1);
  transition: box-shadow 0.3s;
}
.cover-card::before,
.cover-card::after {
  content: '';
  position: absolute;
  inset: 2px;
  z-index: 1;
  pointer-events: none;
  border-radius: calc(var(--radius-lg) - 2px);
}
.cover-card::before {
  background:
    conic-gradient(from 90deg at 6px 6px, transparent 90deg, var(--cat-color) 90deg) top left / 14px 14px no-repeat,
    conic-gradient(from 270deg at 6px 6px, transparent 90deg, var(--cat-color) 90deg) bottom right / 14px 14px no-repeat;
}
.cover-card::after {
  background:
    conic-gradient(from 180deg at 6px 6px, transparent 90deg, var(--cat-color) 90deg) top right / 14px 14px no-repeat,
    conic-gradient(from 0deg at 6px 6px, transparent 90deg, var(--cat-color) 90deg) bottom left / 14px 14px no-repeat;
}
.cover-card:hover {
  box-shadow:
    0 0 0 3px var(--cat-color),
    0 0 0 8px rgba(255,255,255,0.7),
    0 0 0 9px var(--frame-outer-line),
    0 0 30px 3px var(--cat-color, rgba(255,122,0,0.25)),
    0 12px 36px rgba(0,0,0,0.12);
}
.cover-img {
  aspect-ratio: 3 / 4;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.5s cubic-bezier(.2,0,0,1);
  position: relative;
}
.cover-card:hover .cover-img { transform: scale(1.04); }
.cover-placeholder { display: flex; align-items: center; justify-content: center; }
.cover-upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all 0.15s;
}
.cover-upload-btn:hover { color: var(--text-primary); background: var(--bg-surface-hover); }
.cover-upload-btn.uploading { opacity: 0.5; pointer-events: none; }
.cover-upload-btn .file-inp { display: none; }

/* Holo sweep on hover */
.cover-img::after {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  background: linear-gradient(105deg,
    transparent 40%,
    rgba(255,255,255,0.08) 45%,
    rgba(255,255,255,0.18) 50%,
    rgba(255,255,255,0.08) 55%,
    transparent 60%
  );
  opacity: 0;
  transition: opacity 0.3s;
}
.cover-card:hover .cover-img::after {
  opacity: 1;
  animation: holo-sweep 2s ease-in-out infinite;
}
@keyframes holo-sweep {
  0%   { transform: translateX(-120%) skewX(-12deg); }
  100% { transform: translateX(120%) skewX(-12deg); }
}

@media (max-width: 767px) {
  .cover-card { width: 200px; }
  .tracking-card { padding: 18px; }
  .tracking-grid { grid-template-columns: 1fr 1fr; gap: 8px; }
}

/* Info card */
.info-col { flex: 1; min-width: 0; }
.info-card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow:
    0 0 0 1px var(--frame-outer-line),
    0 0 0 2px rgba(255,255,255,0.5),
    0 0 0 3px var(--cat-color, transparent),
    var(--shadow-md);
  position: relative;
}
.info-hd {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}
.title { font-size: var(--fs-2xl); font-weight: 800; letter-spacing: -0.3px; line-height: 1.2; }
.meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--fs-sm);
  color: var(--text-tertiary);
  margin-bottom: 14px;
}
.sep { opacity: 0.3; }

/* Status stamp */
.stamp-row { margin-bottom: 18px; }
.status-stamp {
  display: inline-flex;
  align-items: center;
  height: 26px;
  padding: 0 12px;
  border-radius: 2px;
  font-size: 11px;
  font-weight: 800;
  color: white;
  letter-spacing: 0.8px;
  background: var(--st-bg);
  transform: rotate(2deg);
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  animation: stamp-in 0.4s cubic-bezier(.34,1.56,.64,1) both;
}
/* Bangumi info inside card */
.section-label {
  font-size: var(--fs-xs);
  font-weight: 700;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--color-border);
}
.info-rows { display: flex; flex-direction: column; gap: 2px; margin-bottom: 16px; }
.ir {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 3px 0;
}
.ir-tags { align-items: flex-start; }
.ir-l {
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  white-space: nowrap;
  min-width: 80px;
}
.ir-v {
  font-size: var(--fs-sm);
  color: var(--text-secondary);
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.b-tag {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 3px;
  background: var(--bg-input);
  color: var(--text-tertiary);
  font-weight: 500;
}

.summary {
  font-size: var(--fs-sm);
  color: var(--text-tertiary);
  line-height: 1.7;
}

/* ===== Tracking card ===== */
.tracking-card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 24px;
  border-left: 3px solid var(--cat-color);
  box-shadow: var(--shadow-sm);
}
.tracking-header { margin-bottom: 16px; }
.tracking-title {
  font-size: var(--fs-lg);
  font-weight: 700;
  color: var(--text-primary);
}

.tracking-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}
.tk-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px 12px;
  background: var(--bg-primary);
  border-radius: var(--radius-sm);
}
.tk-full { grid-column: 1 / -1; }
.tk-l {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.tk-v { font-size: var(--fs-sm); color: var(--text-secondary); word-break: break-all; }
.tk-v .tk-icon { width: 20px; height: 20px; vertical-align: middle; margin-right: 4px; }
.free-badge {
  display: inline-block;
  padding: 1px 8px;
  border-radius: var(--radius-full);
  background: color-mix(in srgb, var(--c-game) 15%, transparent);
  color: var(--c-game);
  font-size: 10px;
  font-weight: 700;
  vertical-align: middle;
  margin-left: 4px;
}

.tk-divider {
  height: 1px;
  background: var(--color-border);
  margin: 20px 0;
}
.tk-section { margin-bottom: 14px; }
.tk-section:last-child { margin-bottom: 0; }
.section-label-sm {
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}
.rating-display { font-size: var(--fs-lg); font-weight: 700; color: var(--text-secondary); }
.review-text { font-size: var(--fs-base); color: var(--text-secondary); line-height: 1.7; }

/* ===== Game profiles (horizontal bars) ===== */
.gp-section { margin-bottom: 24px; }
.gp-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.gp-title { font-size: var(--fs-lg); font-weight: 700; }
.add-gp-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 14px;
  border-radius: var(--radius-md);
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--primary);
  background: var(--primary-light);
  transition: all 0.15s;
}
.add-gp-btn:hover { background: rgba(255, 107, 53, 0.14); }

.gp-bars { display: flex; flex-direction: column; gap: 8px; }
.gp-bar {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 18px;
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--gp-accent);
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: var(--shadow-sm);
}
.gp-bar:hover {
  box-shadow: var(--shadow-md);
  transform: translateX(2px);
}
.gp-name { font-size: var(--fs-base); font-weight: 700; flex-shrink: 0; min-width: 60px; }
.gp-st {
  font-size: 10px;
  font-weight: 800;
  color: white;
  padding: 2px 8px;
  border-radius: 2px;
  letter-spacing: 0.5px;
  transform: rotate(2deg);
  flex-shrink: 0;
}
.gp-prog {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 80px;
}
.gp-exp-rail {
  height: 5px;
  background: rgba(0,0,0,0.04);
  border-radius: 3px;
  overflow: hidden;
  flex: 1;
}
.gp-exp-fill {
  height: 100%;
  border-radius: inherit;
  transition: width 0.4s cubic-bezier(.2,0,0,1);
  position: relative;
  overflow: hidden;
  min-width: 3px;
}
.gp-exp-shine {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent 30%, rgba(255,255,255,0.35) 50%, transparent 70%);
  animation: gp-shimmer 3s ease-in-out infinite;
}
@keyframes gp-shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(200%); }
}
.gp-prog-lbl {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-tertiary);
  flex-shrink: 0;
  min-width: 42px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}
.gp-prog-none { font-size: 11px; color: var(--text-tertiary); }
.gp-rating {
  font-size: var(--fs-xs);
  font-weight: 700;
  color: var(--text-tertiary);
  flex-shrink: 0;
}
.gp-empty { text-align: center; padding: 32px 20px; color: var(--text-tertiary); font-size: var(--fs-sm); }

@media (max-width: 767px) {
  .gp-bar { flex-wrap: wrap; gap: 8px; padding: 10px 14px; }
  .gp-name { font-size: var(--fs-sm); min-width: 50px; }
  .gp-st { font-size: 9px; padding: 1px 6px; }
  .gp-prog { min-width: 100%; order: 3; }
  .gp-rating { margin-left: auto; }
}
@media (max-width: 480px) {
  .gp-bar { padding: 10px 12px; gap: 6px; }
  .gp-name { font-size: var(--fs-xs); min-width: 40px; }
  .gp-st { font-size: 8px; padding: 1px 5px; }
  .gp-prog { gap: 6px; }
  .gp-exp-rail { height: 4px; }
  .gp-prog-lbl { font-size: 10px; min-width: 36px; }
  .gp-rating { font-size: 10px; }
}
@media (max-width: 480px) {
  .top-bar { flex-wrap: wrap; gap: 8px; }
  .back-btn, .act-btn { padding: 8px 12px; font-size: var(--fs-xs); }
  .tracking-grid { grid-template-columns: 1fr; }
}

/* ===== Edit Modal — collector's spec sheet ===== */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  background: rgba(26, 24, 22, 0.35);
  backdrop-filter: blur(6px);
  padding: 40px 16px;
  overflow-y: auto;
}
.modal-card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 780px;
  margin-top: 20px;
  box-shadow:
    0 0 0 1px var(--frame-outer-line),
    0 0 0 2px rgba(255,255,255,0.5),
    0 20px 60px rgba(0,0,0,0.12);
  position: relative;
  overflow: hidden;
}
/* Category accent top bar */
.modal-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: var(--modal-accent);
}

/* Header */
.modal-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 0;
}
.modal-hd-left {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}
.modal-thumb {
  width: 40px;
  height: 52px;
  border-radius: 5px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    0 0 0 1.5px var(--modal-accent),
    0 0 0 4px rgba(255,255,255,0.6),
    0 0 0 5px var(--frame-outer-line);
}
.modal-thumb-none { opacity: 0.5; color: white; }
.modal-hd-text { min-width: 0; }
.modal-hd-text h2 { font-size: var(--fs-xl); font-weight: 800; }
.modal-hd-cat {
  display: block;
  font-size: var(--fs-xs);
  color: var(--text-tertiary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}
.modal-close {
  width: 32px; height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  color: var(--text-tertiary);
  flex-shrink: 0;
  transition: all 0.15s;
}
.modal-close:hover { background: var(--bg-surface-hover); color: var(--text-primary); }

/* Body — 2-column grid */
.modal-body { padding: 20px 24px 8px; }
.modal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px 28px;
  align-items: start;
}
@media (max-width: 767px) {
  .modal-grid { grid-template-columns: 1fr; }
  .mf-row { flex-wrap: wrap; }
  .mf-sm { min-width: 0; flex: 1 1 100%; }
}
@media (max-width: 480px) {
  .modal-body { padding: 16px; }
  .modal-hd { flex-wrap: wrap; gap: 12px; }
  .modal-ft { padding: 14px 16px 20px; gap: 10px; }
  .modal-cancel, .modal-save { flex: 1; justify-content: center; display: flex; height: 42px; font-size: var(--fs-base); }
}
.modal-col { display: flex; flex-direction: column; gap: 20px; }

/* Section */
.modal-section { }
.modal-section-title {
  font-size: 10px;
  font-weight: 700;
  color: var(--modal-accent);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--color-border);
}
.modal-section-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.modal-fields { display: flex; flex-direction: column; gap: 10px; }

/* Labels / Controls */
.mf-label { display: flex; flex-direction: column; gap: 4px; }
.mf-label > span {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-tertiary);
  letter-spacing: 0.3px;
}
.mf-label input, .mf-label select, .mf-label textarea {
  padding: 8px 12px;
  font-size: var(--fs-sm);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--bg-primary);
  width: 100%;
  min-width: 0;
  transition: border-color 0.15s, background 0.15s;
}
@media (max-width: 480px) {
  .mf-label input, .mf-label select, .mf-label textarea { padding: 6px 8px; }
}
.mf-label input:focus, .mf-label select:focus, .mf-label textarea:focus {
  border-color: var(--text-tertiary);
  background: var(--bg-surface);
  outline: none;
}
.mf-row { display: flex; gap: 10px; }
.mf-sm { flex: 1; }
.mf-xs { width: 100px; flex-shrink: 0; }

/* Free toggle pill */
.free-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 26px;
  padding: 0 8px 0 12px;
  border-radius: var(--radius-full);
  background: var(--bg-primary);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all 0.15s;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  user-select: none;
}
.free-toggle:has(input:checked) {
  background: color-mix(in srgb, var(--c-game) 12%, transparent);
  border-color: color-mix(in srgb, var(--c-game) 30%, transparent);
  color: var(--c-game);
}
.free-toggle input {
  appearance: none;
  width: 30px;
  height: 18px;
  border-radius: 9px;
  background: var(--color-border);
  position: relative;
  transition: background 0.2s;
  cursor: pointer;
}
.free-toggle input::after {
  content: '';
  position: absolute;
  top: 2px; left: 2px;
  width: 14px; height: 14px;
  border-radius: 50%;
  background: white;
  transition: transform 0.2s;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
.free-toggle input:checked {
  background: var(--c-game);
}
.free-toggle input:checked::after {
  transform: translateX(12px);
}

/* Rating slider */
.rating-slider {
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: var(--bg-input);
  border-radius: 3px;
  outline: none;
  padding: 0;
}
.rating-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px; height: 18px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
}

/* Summary textarea (standalone in right column) */
.modal-summary-ta {
  padding: 8px 12px;
  font-size: var(--fs-sm);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--bg-primary);
  width: 100%;
  resize: vertical;
  transition: border-color 0.15s;
  font-family: inherit;
}
.modal-summary-ta:focus {
  border-color: var(--text-tertiary);
  background: var(--bg-surface);
  outline: none;
}

/* Footer */
.modal-ft {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px 24px 24px;
  border-top: 1px solid var(--color-border);
  margin-top: 4px;
}
.modal-cancel {
  height: 36px;
  padding: 0 20px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-primary);
  border: 1px solid var(--color-border);
  transition: all 0.15s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.modal-cancel:hover {
  background: var(--bg-surface-hover);
  border-color: var(--text-tertiary);
  color: var(--text-primary);
}
.modal-save {
  height: 36px;
  padding: 0 28px;
  border-radius: var(--radius-md);
  background: var(--primary);
  color: white;
  font-size: var(--fs-sm);
  font-weight: 700;
  letter-spacing: 0.3px;
  transition: all 0.15s;
  box-shadow: 0 2px 8px rgba(255, 107, 53, 0.25);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.modal-save:hover {
  background: var(--primary-hover);
  box-shadow: 0 3px 12px rgba(255, 107, 53, 0.35);
  transform: translateY(-1px);
}
.modal-save:disabled { opacity: 0.5; box-shadow: none; transform: none; }

/* Modal transitions */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-active .modal-card, .modal-leave-active .modal-card {
  transition: transform 0.25s cubic-bezier(.2,0,0,1);
}
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-card { transform: scale(0.96) translateY(12px); }
.modal-leave-to .modal-card { transform: scale(0.96) translateY(12px); }

/* Personal tags in info card */
.ptags-row {
  display: flex; flex-wrap: wrap; gap: 6px;
  margin-bottom: 18px;
}
.ptag-chip {
  font-size: 11px; font-weight: 600;
  padding: 3px 10px; border-radius: 4px;
  border: 1px solid;
}

/* Tag selector in modal */
.tag-loading, .tag-none { font-size: var(--fs-xs); color: var(--text-tertiary); }
.tag-link { color: var(--primary); text-decoration: underline; }
.tag-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.tchip {
  font-size: var(--fs-xs); font-weight: 600;
  padding: 4px 12px; border-radius: var(--radius-full);
  border: 1px solid; background: transparent;
  cursor: pointer; transition: all 0.15s;
}
.tchip:hover { opacity: 0.8; }
.tchip:active { transform: none; }
.tchip.on { font-weight: 700; }

/* ===== History card ===== */
.history-card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: 22px 24px;
  margin-top: 20px;
  box-shadow:
    0 0 0 1px var(--frame-outer-line),
    0 0 0 2px rgba(255,255,255,0.5),
    var(--shadow-md);
  border-left: 3px solid var(--cat-color);
}
.history-count { font-size: var(--fs-xs); color: var(--text-tertiary); font-weight: 600; }
.history-hint { font-size: var(--fs-sm); color: var(--text-tertiary); padding: 6px 0; }
.history-more {
  width: 100%;
  height: 34px;
  margin-top: 10px;
  border-radius: var(--radius-md);
  border: 1px dashed var(--color-border);
  font-size: var(--fs-xs);
  color: var(--text-tertiary);
  transition: all 0.15s;
}
.history-more:hover { color: var(--text-secondary); border-color: var(--text-tertiary); }
.history-list { display: flex; flex-direction: column; }
.history-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 9px 0;
}
.h-day {
  font-size: var(--fs-xs);
  font-weight: 700;
  color: var(--text-tertiary);
  padding: 6px 0 2px;
}
.h-day:not(:first-child) { border-top: 1px solid var(--color-border); margin-top: 6px; padding-top: 12px; }
.history-item + .history-item { border-top: 1px solid var(--color-border); }
.h-icon {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  background: var(--bg-input);
  color: var(--text-secondary);
  font-size: 12px;
  flex-shrink: 0;
  margin-top: 1px;
}
.h-body { flex: 1; min-width: 0; }
.h-head { display: flex; align-items: center; gap: 8px; }
.h-action { font-size: var(--fs-sm); font-weight: 700; color: var(--text-primary); }
.h-gp {
  font-size: 10px;
  color: var(--text-tertiary);
  background: var(--bg-input);
  padding: 1px 6px;
  border-radius: 3px;
}
.h-detail {
  font-size: var(--fs-xs);
  color: var(--text-secondary);
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.h-time { font-size: 10px; color: var(--text-tertiary); flex-shrink: 0; margin-top: 3px; }

</style>
