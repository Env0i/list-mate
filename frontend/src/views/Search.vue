<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { bangumiApi, worksApi } from '../api/client'
import { emptyToNull } from '../utils/payload'

const router = useRouter()

const q = ref('')
const activeType = ref('all')
const results = ref([])
const searching = ref(false)
const creating = ref(false)
const error = ref('')

// Prefill dialog state
const selected = ref(null)
const showDialog = ref(false)
const form = ref({})

const typeLabels = [
  { key: 'all', label: '全部' },
  { key: '1', label: '书籍' },
  { key: '2', label: '番剧' },
  { key: '3', label: '音乐' },
  { key: '4', label: '游戏' },
]

const typeToCategory = { 1: 'novel', 2: 'anime', 4: 'game', default: 'anime' }
const defaultProgressUnit = { anime: 'ep', novel: 'chapter', game: 'percent', comic: 'volume' }

async function search() {
  if (!q.value.trim()) return
  searching.value = true
  error.value = ''
  try {
    const type = activeType.value === 'all' ? undefined : activeType.value
    const { data } = await bangumiApi.search(q.value.trim(), type)
    results.value = data.results || data.items || []
  } catch (e) {
    error.value = '搜索失败，请重试'
    results.value = []
  } finally {
    searching.value = false
  }
}

function selectItem(item) {
  const cat = typeToCategory[item.type] || typeToCategory.default
  form.value = {
    title: item.name_cn || item.name || '',
    category: cat,
    sub_category: '',
    progress_unit: defaultProgressUnit[cat] || 'ep',
    total: null,
    bangumi_id: item.bangumi_id,
    cover_url: item.image_url || '',
    summary: item.summary || '',
  }
  selected.value = item
  showDialog.value = true
}

async function confirmCreate() {
  creating.value = true
  error.value = ''
  try {
    const { data } = await worksApi.create(emptyToNull(form.value, ['total']))
    showDialog.value = false
    router.push(`/works/${data.id}`)
  } catch (e) {
    error.value = e.response?.data?.detail || '创建失败'
  } finally {
    creating.value = false
  }
}

function closeDialog() {
  showDialog.value = false
  selected.value = null
}

function coverUrl(item) {
  return item.image_url || ''
}

function itemTitle(item) {
  return item.name_cn || item.name || '未知'
}

function itemId(item) {
  return item.bangumi_id
}
</script>

<template>
  <div class="page">
    <div class="page-inner">
      <!-- Header -->
      <div class="top-bar">
        <button class="back-btn" @click="router.push('/')">
          <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path fill-rule="evenodd" d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z" clip-rule="evenodd"/>
          </svg>
          返回
        </button>
      </div>

      <h1 class="page-title">搜索添加</h1>
      <p class="subtitle">通过 Bangumi 搜索自动填充作品信息</p>

      <!-- Search bar -->
      <div class="search-bar">
        <div class="search-w">
          <svg class="s-icon" viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path fill-rule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clip-rule="evenodd"/>
          </svg>
          <input
            v-model="q"
            class="s-inp"
            placeholder="搜索作品名..."
            @keyup.enter="search"
          />
        </div>
        <button class="search-btn" @click="search" :disabled="searching">
          {{ searching ? '搜索中...' : '搜索' }}
        </button>
      </div>

      <!-- Type filter -->
      <div class="type-row">
        <button
          v-for="t in typeLabels"
          :key="t.key"
          class="type-opt"
          :class="{ on: activeType === t.key }"
          @click="activeType = t.key"
        >
          {{ t.label }}
        </button>
      </div>

      <!-- Error -->
      <p v-if="error && !showDialog" class="err">{{ error }}</p>

      <!-- Results -->
      <div v-if="searching" class="loading">搜索中...</div>

      <div v-else-if="results.length" class="results">
        <div
          v-for="item in results"
          :key="itemId(item)"
          class="result-card"
          @click="selectItem(item)"
        >
          <div
            class="rc-cover"
            :style="{ backgroundImage: coverUrl(item) ? `url(${coverUrl(item)})` : 'none' }"
          >
            <div v-if="!coverUrl(item)" class="rc-placeholder">
              <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V4z"/>
              </svg>
            </div>
          </div>
          <span class="rc-title">{{ itemTitle(item) }}</span>
        </div>
      </div>

      <div v-else-if="q && !searching" class="empty">
        没有结果，试试别的关键词
      </div>
    </div>

    <!-- Confirmation dialog -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showDialog" class="modal-overlay" @click.self="closeDialog">
          <div class="modal-card" @click.stop>
            <div class="modal-hd">
              <h2>确认作品信息</h2>
              <button class="modal-close" @click="closeDialog">
                <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
                  <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"/>
                </svg>
              </button>
            </div>

            <div class="modal-body">
              <div class="modal-fields">
                <label class="mf-label">
                  <span>标题</span>
                  <input v-model="form.title" placeholder="作品名称" />
                </label>
                <div class="mf-row">
                  <label class="mf-label mf-sm">
                    <span>分类</span>
                    <select v-model="form.category">
                      <option value="anime">番剧</option>
                      <option value="novel">小说</option>
                      <option value="comic">漫画</option>
                      <option value="game">游戏</option>
                    </select>
                  </label>
                  <label class="mf-label mf-sm">
                    <span>子分类</span>
                    <input v-model="form.sub_category" placeholder="如：单机、欧美剧" />
                  </label>
                </div>
                <div class="mf-row" v-if="form.category !== 'game'">
                  <label class="mf-label mf-xs">
                    <span>总量</span>
                    <input v-model.number="form.total" type="number" min="0" placeholder="0" />
                  </label>
                </div>
                <label class="mf-label" v-if="form.cover_url">
                  <span>封面</span>
                  <div class="cover-preview">
                    <img :src="form.cover_url" alt="" class="cover-preview-img" />
                    <span class="cover-preview-txt">{{ form.cover_url }}</span>
                  </div>
                </label>
                <label class="mf-label">
                  <span>简介</span>
                  <textarea v-model="form.summary" rows="3" placeholder="作品简介..." />
                </label>
              </div>
            </div>

            <p v-if="error" class="modal-err">{{ error }}</p>

            <div class="modal-ft">
              <button class="modal-cancel" @click="closeDialog">取消</button>
              <button class="modal-save" @click="confirmCreate" :disabled="creating">
                {{ creating ? '创建中...' : '添加到收藏' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
/* Layout */
.page { padding: 20px 16px; }
@media (max-width: 767px) { .page { padding-top: 0; } }
@media (min-width: 768px) { .page { padding: 24px 32px; } }
.page-inner { max-width: 800px; margin: 0 auto; }

.top-bar { margin-bottom: 16px; }
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

.page-title { font-size: var(--fs-2xl); font-weight: 800; margin-bottom: 4px; }
.subtitle { font-size: var(--fs-sm); color: var(--text-tertiary); margin-bottom: 20px; }

/* Search */
.search-bar { display: flex; gap: 8px; margin-bottom: 14px; }
.search-w { flex: 1; position: relative; }
.s-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-tertiary); pointer-events: none; }
.s-inp {
  height: 40px;
  padding-left: 36px;
  padding-right: 12px;
  border-radius: var(--radius-md);
  font-size: var(--fs-base);
  background: var(--bg-surface);
  border: 1px solid var(--color-border);
}
.s-inp:focus { border-color: var(--text-tertiary); background: white; }
.search-btn {
  height: 40px;
  padding: 0 24px;
  border-radius: var(--radius-md);
  background: var(--primary);
  color: white;
  font-size: var(--fs-sm);
  font-weight: 700;
  transition: all 0.15s;
  flex-shrink: 0;
}
.search-btn:hover { background: var(--primary-hover); }
.search-btn:disabled { opacity: 0.6; }

/* Type filter */
.type-row { display: flex; gap: 4px; margin-bottom: 20px; }
.type-opt {
  height: 28px;
  padding: 0 12px;
  border-radius: var(--radius-full);
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  transition: all 0.15s;
}
.type-opt:hover { color: var(--text-secondary); }
.type-opt.on {
  background: var(--bg-surface);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}

.err { color: var(--c-anime); font-size: var(--fs-sm); margin-bottom: 12px; }
.loading { text-align: center; padding: 60px 20px; color: var(--text-tertiary); }

/* Results grid */
.results {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
@media (min-width: 640px) { .results { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 900px) { .results { grid-template-columns: repeat(4, 1fr); } }

.result-card {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: var(--shadow-sm);
}
.result-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.rc-cover {
  aspect-ratio: 3 / 4;
  background: var(--bg-input);
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
}
.rc-placeholder { color: var(--text-tertiary); opacity: 0.2; }
.rc-title {
  display: block;
  padding: 10px 12px;
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.empty { text-align: center; padding: 60px 20px; color: var(--text-tertiary); }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.3);
  backdrop-filter: blur(4px);
  padding: 16px;
}
.modal-card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 520px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}
.modal-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 0;
}
.modal-hd h2 { font-size: var(--fs-xl); font-weight: 800; }
.modal-close {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--radius-full);
  color: var(--text-tertiary);
  transition: all 0.15s;
}
.modal-close:hover { background: var(--bg-surface-hover); color: var(--text-primary); }
.modal-body { padding: 16px 24px 4px; }
.modal-fields { display: flex; flex-direction: column; gap: 10px; }
.mf-label { display: flex; flex-direction: column; gap: 4px; }
.mf-label span { font-size: var(--fs-xs); font-weight: 600; color: var(--text-tertiary); }
.mf-label input, .mf-label select, .mf-label textarea {
  padding: 8px 12px;
  font-size: var(--fs-sm);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--bg-primary);
}
.mf-label input:focus, .mf-label select:focus, .mf-label textarea:focus {
  border-color: var(--text-tertiary);
  background: var(--bg-surface);
  outline: none;
}
.mf-row { display: flex; gap: 10px; }
.mf-sm { flex: 1; }
.mf-xs { width: 100px; flex-shrink: 0; }

.cover-preview { display: flex; align-items: center; gap: 10px; }
.cover-preview-img { width: 48px; height: 64px; border-radius: var(--radius-sm); object-fit: cover; background: var(--bg-input); }
.cover-preview-txt { font-size: 11px; color: var(--text-tertiary); word-break: break-all; flex: 1; }

.modal-err { color: var(--c-anime); font-size: var(--fs-sm); padding: 0 24px 8px; }
.modal-ft {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px 24px 24px;
}
.modal-cancel {
  height: 36px;
  padding: 0 20px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-tertiary);
  transition: all 0.15s;
}
.modal-cancel:hover { color: var(--text-primary); background: var(--bg-surface-hover); }
.modal-save {
  height: 36px;
  padding: 0 24px;
  border-radius: var(--radius-md);
  background: var(--primary);
  color: white;
  font-size: var(--fs-sm);
  font-weight: 700;
  transition: all 0.15s;
}
.modal-save:hover { background: var(--primary-hover); }
.modal-save:disabled { opacity: 0.5; }

.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-active .modal-card, .modal-leave-active .modal-card { transition: transform 0.2s cubic-bezier(.2,0,0,1); }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-card { transform: scale(0.95) translateY(10px); }
.modal-leave-to .modal-card { transform: scale(0.95) translateY(10px); }
</style>
