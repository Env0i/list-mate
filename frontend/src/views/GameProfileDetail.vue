<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { worksApi, gameProfilesApi, attachmentsApi } from '../api/client'
import { showToast } from '../utils/toast'
import { emptyToNull } from '../utils/payload'
import { STATUS_LABELS, STATUS_COLORS } from '../constants/work'

const route = useRoute()
const router = useRouter()

const gp = ref(null)
const workTitle = ref('')
const originalStatus = ref(null)
const loading = ref(true)
const saving = ref(false)
const deleting = ref(false)
const showModInput = ref(false)
const modInputText = ref('')
const attachments = ref([])
const uploading = ref(false)

const statusOptions = Object.entries(STATUS_LABELS.game).map(([key, label]) => ({ key, label }))

const progressTypes = [
  { key: 'none', label: '纯状态', desc: '不追踪数字进度' },
  { key: 'count', label: '次数', desc: '记录通关次数' },
  { key: 'percent', label: '百分比', desc: '记录完成百分比' },
]

const statusBgMap = STATUS_COLORS

const progressLabel = computed(() => {
  if (!gp.value) return ''
  const pt = gp.value.progress_type || 'none'
  if (pt === 'count') return `${gp.value.progress_value || 0} 次`
  if (pt === 'percent') return `${gp.value.progress_value || 0}%`
  return ''
})

const modsList = computed(() => {
  if (!gp.value?.mods_list) return []
  return gp.value.mods_list.split('\n').filter(m => m.trim())
})

const activeStatusBg = computed(() => statusBgMap[gp.value?.status] || '#A39F98')

async function load() {
  loading.value = true
  try {
    const { data } = await gameProfilesApi.get(route.params.gpid)
    gp.value = data
    originalStatus.value = data.status
    const workRes = await worksApi.get(data.work_id)
    workTitle.value = workRes.data.title
    await loadAttachments()
  } catch (e) {
    console.error('Failed to load game profile', e)
  } finally {
    loading.value = false
  }
}

async function loadAttachments() {
  try {
    const { data } = await attachmentsApi.list(route.params.gpid)
    attachments.value = data
  } catch (e) {
    console.error('Failed to load attachments', e)
  }
}

async function uploadAttachment(e) {
  const file = e.target.files?.[0]
  if (!file) return
  uploading.value = true
  try {
    await attachmentsApi.upload(route.params.gpid, file)
    await loadAttachments()
    showToast('附件上传成功')
  } catch (e) {
    console.error('Upload failed', e)
    showToast('上传失败', 'error')
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}

function downloadAttachment(id) {
  window.open(attachmentsApi.downloadUrl(id), '_blank')
}

async function deleteAttachment(id) {
  if (!confirm('确定删除这个附件？')) return
  try {
    await attachmentsApi.delete(id)
    attachments.value = attachments.value.filter(a => a.id !== id)
    showToast('附件已删除')
  } catch (e) {
    console.error('Delete failed', e)
    showToast('删除失败', 'error')
  }
}

function setProgressType(pt) {
  gp.value.progress_type = pt
  if (pt === 'none') gp.value.progress_value = null
  else if (gp.value.progress_value == null) gp.value.progress_value = 0
}

// 快捷进度即时提交（与列表卡 ±1 对齐）：percent +5 / count +1，
// 到 100% 触发后端自动完成；自动完成后的 −1 随回退恢复"进行中"
const stepping = ref(false)

async function stepProgress(dir) {
  if (!gp.value || stepping.value) return
  const pt = gp.value.progress_type || 'none'
  if (pt === 'none') return
  const step = pt === 'percent' ? 5 : 1
  const cur = gp.value.progress_value ?? 0
  let next = Math.max(0, cur + dir * step)
  if (pt === 'percent') next = Math.min(100, next)
  if (next === cur) return
  stepping.value = true
  try {
    const payload = { progress_value: next }
    if (dir < 0 && gp.value.auto_completed) payload.status = 'playing'
    const { data } = await gameProfilesApi.update(route.params.gpid, payload)
    gp.value = data
    originalStatus.value = data.status
  } catch (e) {
    console.error('GP step failed', e)
    showToast('进度更新失败', 'error')
  } finally {
    stepping.value = false
  }
}

function addMods() {
  if (!modInputText.value.trim()) { showModInput.value = false; return }
  const newMods = modInputText.value.split('\n').map(m => m.trim()).filter(m => m)
  const current = modsList.value
  const combined = [...new Set([...current, ...newMods])]
  gp.value.mods_list = combined.join('\n')
  modInputText.value = ''
  showModInput.value = false
}

function removeMod(mod) {
  gp.value.mods_list = modsList.value.filter(m => m !== mod).join('\n')
}

async function save() {
  saving.value = true
  try {
    const body = emptyToNull({
      name: gp.value.name,
      progress_value: gp.value.progress_value,
      progress_type: gp.value.progress_type,
      // 仅在状态被用户改动时提交，否则后端视为"用户显式设状态"而跳过自动完成规则
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
    if (gp.value.status === originalStatus.value) {
      delete body.status
    }
    const { data } = await gameProfilesApi.update(route.params.gpid, body)
    gp.value = data
    showToast('保存成功')
  } catch (e) {
    console.error('Failed to save', e)
    showToast('保存失败', 'error')
  } finally {
    saving.value = false
  }
}

async function del() {
  if (!confirm('确定删除这个游戏配置？')) return
  deleting.value = true
  try {
    await gameProfilesApi.delete(route.params.gpid)
    showToast('配置已删除')
    router.push(`/works/${route.params.id}`)
  } catch (e) {
    console.error('Failed to delete', e)
    showToast('删除失败', 'error')
    deleting.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="page-inner" v-if="loading">
      <div class="loading">加载中...</div>
    </div>

    <div class="page-inner" v-else-if="gp">
      <!-- Header -->
      <div class="top-bar">
        <button class="back-btn" @click="router.push(`/works/${route.params.id}`)">
          <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path fill-rule="evenodd" d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z" clip-rule="evenodd"/>
          </svg>
          返回作品
        </button>
        <button class="act-btn del" @click="del" :disabled="deleting">
          <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c-.84 0-1.673.025-2.5.075V3.75c0-.69.56-1.25 1.25-1.25h2.5c.69 0 1.25.56 1.25 1.25v.325C11.673 4.025 10.84 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clip-rule="evenodd"/>
          </svg>
          删除
        </button>
      </div>

      <!-- Breadcrumb -->
      <div class="breadcrumb">
        <span class="bread-parent">{{ workTitle }}</span>
        <span class="bread-sep">&rsaquo;</span>
        <span class="bread-current">{{ gp.name }}</span>
      </div>

      <!-- Card -->
      <div class="detail-card" :style="{ '--cat-color': 'var(--c-game)' }">
        <!-- Section: Status -->
        <div class="section">
          <h3 class="section-title">状态</h3>
          <div class="status-row">
            <button
              v-for="opt in statusOptions"
              :key="opt.key"
              class="st-opt"
              :class="{ on: gp.status === opt.key }"
              :style="gp.status === opt.key ? { background: statusBgMap[opt.key], color: '#fff' } : {}"
              @click="gp.status = opt.key"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <!-- Section: Progress type + stepper -->
        <div class="section">
          <h3 class="section-title">进度类型</h3>
          <div class="pt-options">
            <button
              v-for="pt in progressTypes"
              :key="pt.key"
              class="pt-opt"
              :class="{ on: (gp.progress_type || 'none') === pt.key }"
              @click="setProgressType(pt.key)"
              :title="pt.desc"
            >
              {{ pt.label }}
            </button>
          </div>

          <div v-if="(gp.progress_type || 'none') !== 'none'" class="progress-row">
            <button class="step-btn" @click="stepProgress(-1)" :disabled="stepping || !gp.progress_value">
              <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                <path fill-rule="evenodd" d="M4 10a.75.75 0 01.75-.75h10.5a.75.75 0 010 1.5H4.75A.75.75 0 014 10z" clip-rule="evenodd"/>
              </svg>
            </button>
            <input
              v-model.number="gp.progress_value"
              type="number"
              min="0"
              class="progress-inp"
              :placeholder="(gp.progress_type || 'none') === 'percent' ? '0' : '0'"
            />
            <button class="step-btn" @click="stepProgress(1)" :disabled="stepping || (gp.progress_type || 'none') === 'none'">
              <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z"/>
              </svg>
            </button>
            <span class="stepper-label">{{ progressLabel }}</span>
          </div>
        </div>

        <!-- Section: 游玩记录 -->
        <div class="section">
          <h3 class="section-title">游玩记录</h3>
          <div class="record-grid">
            <label class="rec-item">
              <span>开始时间</span>
              <input type="date" v-model="gp.start_date" />
            </label>
            <label class="rec-item">
              <span>完成时间</span>
              <input type="date" v-model="gp.finish_date" />
            </label>
            <label class="rec-item">
              <span>游玩时长（小时）</span>
              <input type="number" min="0" step="0.1" v-model="gp.playtime_hours" placeholder="0" />
            </label>
            <label class="rec-item rec-full">
              <span>来源</span>
              <input v-model="gp.source" placeholder="CurseForge / B站UP主 / Steam创意工坊 / 自己整合..." />
            </label>
          </div>
        </div>

        <!-- Section: 模组列表 -->
        <div class="section">
          <h3 class="section-title">模组列表</h3>
          <div class="mods-tags">
            <span v-for="mod in modsList" :key="mod" class="mod-tag">
              {{ mod }}
              <button class="mod-remove" @click="removeMod(mod)" title="移除">&times;</button>
            </span>
            <button v-if="!showModInput" class="add-mod-btn" @click="showModInput = true">+ 添加</button>
          </div>
          <div v-if="showModInput" class="mod-input-area">
            <textarea
              v-model="modInputText"
              placeholder="粘贴模组列表（每行一个）..."
              rows="4"
              class="mod-textarea"
            />
            <div class="mod-input-ft">
              <button class="mod-cancel" @click="showModInput = false; modInputText = ''">取消</button>
              <button class="mod-confirm" @click="addMods">确定</button>
            </div>
          </div>
        </div>

        <!-- Section: 附件 -->
        <div class="section">
          <h3 class="section-title">附件</h3>
          <div v-if="attachments.length" class="att-list">
            <div v-for="att in attachments" :key="att.id" class="att-item">
              <div class="att-info">
                <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16" class="att-icon">
                  <path d="M7 3.5A1.5 1.5 0 005.5 5v13a1.5 1.5 0 001.5 1.5h6a1.5 1.5 0 001.5-1.5V5A1.5 1.5 0 0013 3.5H7z"/>
                </svg>
                <span class="att-name">{{ att.file_name }}</span>
                <span class="att-size" v-if="att.file_size">({{ (att.file_size / 1024).toFixed(1) }} KB)</span>
              </div>
              <div class="att-actions">
                <button class="att-btn" @click="downloadAttachment(att.id)">下载</button>
                <button class="att-btn del" @click="deleteAttachment(att.id)">删除</button>
              </div>
            </div>
          </div>
          <div class="upload-row">
            <label class="upload-btn" :class="{ uploading }">
              <input type="file" class="file-inp" @change="uploadAttachment" :disabled="uploading" />
              {{ uploading ? '上传中...' : '+ 上传文件' }}
            </label>
          </div>
        </div>

        <!-- Section: 评分 -->
        <div class="section">
          <h3 class="section-title">评分</h3>
          <div class="rating-row">
            <input v-model.number="gp.rating" type="range" min="0" max="10" class="rating-slider" />
            <span class="rating-val">{{ gp.rating != null ? gp.rating : '—' }}/10</span>
          </div>
        </div>

        <!-- Section: 评价 -->
        <div class="section">
          <h3 class="section-title">评价</h3>
          <textarea v-model="gp.review" class="text-inp" rows="3" placeholder="写下你的评价..." />
        </div>

        <!-- Section: 笔记 -->
        <div class="section">
          <h3 class="section-title">笔记</h3>
          <textarea v-model="gp.notes" class="text-inp" rows="4" placeholder="游玩心得、备忘..." />
        </div>

        <!-- Save -->
        <button class="save-btn" @click="save" :disabled="saving">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>

    <div class="page-inner" v-else>
      <div class="empty">
        <p>配置不存在</p>
        <button class="back-btn" @click="router.back()">返回</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ===== Layout ===== */
.page { padding: 20px 16px; }
@media (max-width: 767px) { .page { padding-top: 0; } }
@media (min-width: 768px) { .page { padding: 24px 32px; } }
.page-inner { max-width: 600px; margin: 0 auto; }
.loading, .empty { text-align: center; padding: 80px 20px; color: var(--text-tertiary); }

/* Header */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
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
.act-btn.del:hover { color: var(--c-anime); }
.act-btn:disabled { opacity: 0.4; }

/* Breadcrumb */
.breadcrumb {
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--fs-sm);
}
.bread-parent { color: var(--text-tertiary); }
.bread-sep { color: var(--text-tertiary); opacity: 0.4; }
.bread-current { color: var(--text-primary); font-weight: 700; }

/* Card */
.detail-card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: 28px;
  box-shadow:
    0 0 0 1px var(--frame-outer-line),
    0 0 0 2px rgba(255,255,255,0.5),
    0 0 0 3px var(--cat-color, transparent),
    var(--shadow-md);
  position: relative;
}
@media (max-width: 767px) { .detail-card { padding: 20px; } }
@media (max-width: 480px) {
  .detail-card { padding: 16px; }
  .top-bar { flex-wrap: wrap; gap: 8px; }
  .back-btn, .act-btn { padding: 8px 12px; font-size: var(--fs-xs); }
  .st-opt { height: 28px; padding: 0 12px; font-size: 11px; }
  .pt-opt { height: 28px; padding: 0 12px; font-size: 11px; }
  .section { margin-bottom: 20px; }
  .att-item { flex-wrap: wrap; gap: 6px; }
  .att-info { min-width: 0; width: 100%; }
  .att-actions { margin-left: auto; }
  .mods-tags { gap: 4px; }
  .mod-tag { font-size: 10px; padding: 3px 8px; }
}

/* Sections */
.section { margin-bottom: 28px; }
.section:last-of-type { margin-bottom: 24px; }
.section-title {
  font-size: var(--fs-xs);
  font-weight: 700;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--color-border);
}

/* Status */
.status-row { display: flex; flex-wrap: wrap; gap: 6px; }
.st-opt {
  height: 32px;
  padding: 0 16px;
  border-radius: var(--radius-full);
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  background: var(--bg-primary);
  border: 1px solid var(--color-border);
  transition: all 0.15s;
}
.st-opt:hover { border-color: var(--text-tertiary); }
.st-opt:active { transform: none; }
.st-opt.on { border-color: transparent; }

/* Progress type */
.pt-options { display: flex; gap: 8px; margin-bottom: 14px; }
.pt-opt {
  height: 32px;
  padding: 0 16px;
  border-radius: var(--radius-md);
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  background: var(--bg-primary);
  border: 1px solid var(--color-border);
  transition: all 0.15s;
}
.pt-opt:hover { border-color: var(--text-tertiary); }
.pt-opt:active { transform: none; }
.pt-opt.on {
  background: var(--c-game);
  color: white;
  border-color: transparent;
}

/* Progress stepper */
.progress-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.step-btn {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--radius-md);
  background: var(--bg-primary);
  border: 1px solid var(--color-border);
  color: var(--text-secondary);
  transition: all 0.15s;
}
.step-btn:hover { border-color: var(--text-tertiary); color: var(--text-primary); }
.step-btn:disabled { opacity: 0.3; cursor: default; }
.progress-inp {
  width: 100px;
  text-align: center;
  font-size: var(--fs-xl);
  font-weight: 700;
  padding: 8px 12px;
  -moz-appearance: textfield;
}
.progress-inp::-webkit-outer-spin-button,
.progress-inp::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
.stepper-label {
  font-size: var(--fs-sm);
  font-weight: 700;
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
}

/* Play records */
.record-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
@media (max-width: 767px) {
  .record-grid { grid-template-columns: 1fr; gap: 10px; }
}
.rec-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}
.rec-item span {
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-tertiary);
}
.rec-item input {
  padding: 8px 12px;
  font-size: var(--fs-sm);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--bg-primary);
  width: 100%;
  min-width: 0;
  max-width: 100%;
}
.rec-item input:focus { border-color: var(--text-tertiary); background: var(--bg-surface); outline: none; }
.rec-item input[type="date"]::-webkit-calendar-picker-indicator {
  display: none;
}
@media (max-width: 480px) {
  .rec-item input { padding: 6px 8px; }
}
.rec-full { grid-column: 1 / -1; }

/* Mods list */
.mods-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}
.mod-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-xs);
  font-weight: 600;
  background: var(--c-game-bg);
  color: var(--c-game);
  border: 1px solid rgba(255, 122, 0, 0.15);
}
.mod-remove {
  font-size: 14px;
  line-height: 1;
  color: inherit;
  opacity: 0.5;
  transition: opacity 0.15s;
  padding: 0;
}
.mod-remove:hover { opacity: 1; }
.add-mod-btn {
  height: 28px;
  padding: 0 12px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--primary);
  background: var(--primary-light);
  border: 1px dashed var(--primary);
  transition: all 0.15s;
}
.add-mod-btn:hover { background: rgba(255, 107, 53, 0.14); }
.mod-input-area { margin-top: 10px; }
.mod-textarea {
  width: 100%;
  resize: vertical;
  min-height: 80px;
  font-size: var(--fs-sm);
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--bg-primary);
}
.mod-textarea:focus { border-color: var(--text-tertiary); background: var(--bg-surface); outline: none; }
.mod-input-ft { display: flex; justify-content: flex-end; gap: 6px; margin-top: 8px; }
.mod-cancel {
  height: 30px;
  padding: 0 14px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-tertiary);
}
.mod-cancel:hover { color: var(--text-primary); }
.mod-confirm {
  height: 30px;
  padding: 0 16px;
  border-radius: var(--radius-sm);
  background: var(--primary);
  color: white;
  font-size: var(--fs-xs);
  font-weight: 600;
}
.mod-confirm:hover { background: var(--primary-hover); }

/* Attachments */
.att-list { display: flex; flex-direction: column; gap: 4px; margin-bottom: 10px; }
.att-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  background: var(--bg-primary);
  border: 1px solid var(--color-border);
}
.att-info {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}
.att-icon { color: var(--text-tertiary); flex-shrink: 0; }
.att-name { font-size: var(--fs-xs); font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.att-size { font-size: 11px; color: var(--text-tertiary); white-space: nowrap; }
.att-actions { display: flex; gap: 4px; flex-shrink: 0; }
.att-btn {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  transition: all 0.1s;
}
.att-btn:hover { background: var(--bg-surface-hover); color: var(--text-primary); }
.att-btn.del:hover { color: var(--c-anime); }
.upload-row { margin-top: 2px; }
.upload-btn {
  display: inline-flex;
  align-items: center;
  height: 30px;
  padding: 0 14px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--primary);
  background: var(--primary-light);
  border: 1px dashed var(--primary);
  cursor: pointer;
  transition: all 0.15s;
}
.upload-btn:hover { background: rgba(255, 107, 53, 0.14); }
.upload-btn.uploading { opacity: 0.6; pointer-events: none; }
.file-inp { display: none; }

/* Rating */
.rating-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.rating-slider {
  flex: 1;
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
.rating-val { font-size: var(--fs-lg); font-weight: 700; color: var(--text-secondary); min-width: 48px; }

/* Text inputs */
.text-inp {
  width: 100%;
  resize: vertical;
  min-height: 72px;
  font-size: var(--fs-base);
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--bg-primary);
}
.text-inp:focus { border-color: var(--text-tertiary); background: var(--bg-surface); outline: none; }

/* Save */
@media (max-width: 480px) {
  .progress-row { gap: 8px; }
  .step-btn { width: 32px; height: 32px; }
  .progress-inp { width: 72px; font-size: var(--fs-lg); padding: 6px 8px; }
  .stepper-label { font-size: var(--fs-xs); }
  .save-btn { height: 44px; font-size: var(--fs-base); }
}
.save-btn {
  width: 100%;
  height: 42px;
  border-radius: var(--radius-md);
  background: var(--primary);
  color: white;
  font-size: var(--fs-base);
  font-weight: 700;
  transition: all 0.15s;
}
.save-btn:hover { background: var(--primary-hover); }
.save-btn:disabled { opacity: 0.5; cursor: default; }

/* 触屏：操作控件达到 44px 触控目标（Q3 决策） */
@media (pointer: coarse) {
  .st-opt, .pt-opt, .add-mod-btn, .mod-cancel, .mod-confirm, .upload-btn, .save-btn { min-height: 44px; }
  .step-btn { width: 44px; height: 44px; }
}
</style>
