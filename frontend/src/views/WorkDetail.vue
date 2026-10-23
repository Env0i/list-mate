<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { worksApi, tagsApi, coverApi, timelineApi } from '../api/client'
import CategoryBadge from '../components/work/CategoryBadge.vue'
import ProgressBar from '../components/work/ProgressBar.vue'
import { getPlatformIconUrl } from '../utils/platformIcons'
import { showToast } from '../utils/toast'
import { emptyToNull } from '../utils/payload'
import { STATUS_COLORS, STATUS_LABELS } from '../constants/work'
import StatusStamp from '../components/work/StatusStamp.vue'
import TimelineList from '../components/common/TimelineList.vue'
import BaseModal from '../components/common/BaseModal.vue'
import BangumiZone from '../components/work/detail/BangumiZone.vue'
import DangerZone from '../components/work/detail/DangerZone.vue'
import WorkEditModal from '../components/work/WorkEditModal.vue'

const route = useRoute()
const router = useRouter()
const work = ref(null)
const loading = ref(true)
const deleting = ref(false)
const showDelConfirm = ref(false)
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

// 印章只认状态键：游戏作品取首个配置的状态
const stKey = computed(() => {
  if (!work.value) return 'wish'
  const cat = work.value.category
  return cat === 'game'
    ? (work.value.game_profiles?.[0]?.status || 'wish')
    : (work.value.status || 'wish')
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
  deleting.value = true
  try {
    await worksApi.delete(route.params.id)
    showToast('作品已删除')
    router.push('/')
  } catch (e) {
    console.error('Failed to delete', e)
    showToast('删除失败', 'error')
    deleting.value = false
  } finally {
    showDelConfirm.value = false
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

// 历史按天分组逻辑已收进 TimelineList 组件（与 Stats 操作记录同一标签规则）

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

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
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
              <StatusStamp :category="work.category" :status="stKey" />
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

            <!-- 作品情報已收进 BangumiZone（实时数据 + 社区对照/分集/角色/关联/Staff） -->

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
          <div class="history-head-actions">
            <span v-if="historyTotal" class="history-count">{{ history.length }}/{{ historyTotal }} 条</span>
            <button
              v-if="history.length >= historyPageSize"
              class="history-top"
              title="回到顶部"
              @click="scrollToTop"
            >↑ 顶部</button>
          </div>
        </div>
        <div v-if="historyLoading" class="history-hint">加载中...</div>
        <div v-else-if="history.length" class="history-list">
          <TimelineList :entries="history" />
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

      <!-- Bangumi 资料区：无 bangumi_id（手动添加）不渲染 -->
      <BangumiZone
        v-if="work.bangumi_id"
        :bangumi-id="work.bangumi_id"
        :category="work.category"
        :my-rating="work.rating"
      />

      <!-- 危险操作 -->
      <DangerZone :deleting="deleting" @request-delete="showDelConfirm = true" />
    </div>

    <!-- 删除确认 -->
    <BaseModal :open="showDelConfirm" size="sm" @close="showDelConfirm = false">
      <template #head><h2>删除这部作品？</h2></template>
      <p class="del-confirm-text">「{{ work?.title }}」的进度、评分、历史记录和游戏配置会一并删除，不可恢复。</p>
      <template #foot>
        <button class="modal-cancel" @click="showDelConfirm = false">保留</button>
        <button class="modal-save del-solid" @click="del" :disabled="deleting">
          {{ deleting ? '删除中...' : '删除作品' }}
        </button>
      </template>
    </BaseModal>

    <WorkEditModal
      :open="showEditModal"
      :work="work"
      :form="form"
      :saving="saving"
      :all-tags="allTags"
      :selected-tag-ids="selectedTagIds"
      :tag-loading="tagLoading"
      @close="closeEdit"
      @save="saveEdit"
      @toggle-tag="toggleTag"
    />
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

/* Status stamp 已收进 StatusStamp 组件 */
.stamp-row { margin-bottom: 18px; }
/* 作品情報样式已随 BangumiInfo 组件迁出 */


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

/* 编辑模态样式已随 WorkEditModal 组件迁出 */


/* 删除确认模态 */
.del-confirm-text { font-size: var(--fs-sm); color: var(--text-secondary); }
.modal-save.del-solid { background: var(--s-dropped); box-shadow: none; }
.modal-save.del-solid:hover:not(:disabled) { background: color-mix(in srgb, var(--s-dropped) 85%, black); box-shadow: none; }

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
.history-head-actions { display: flex; align-items: center; gap: 8px; }
.history-top {
  height: 26px;
  padding: 0 10px;
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
  font-size: var(--fs-xs);
  color: var(--text-tertiary);
  transition: all 0.15s;
}
.history-top:hover { color: var(--text-secondary); border-color: var(--text-tertiary); }
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


/* 触屏：操作控件达到 44px 触控目标（Q3 决策） */
@media (pointer: coarse) {
  .add-gp-btn, .free-toggle, .modal-close, .modal-cancel, .modal-save, .history-top, .history-more { min-height: 44px; }
  .modal-close { min-width: 44px; }
}
</style>
