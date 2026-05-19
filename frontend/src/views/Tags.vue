<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { tagsApi } from '../api/client'

const router = useRouter()
const tags = ref([])
const loading = ref(true)
const newName = ref('')
const newColor = ref('#5bc0de')
const editingId = ref(null)
const editName = ref('')
const editColor = ref('')
const error = ref('')

const presetColors = [
  '#5bc0de', '#f43f5e', '#3b82f6', '#10b981', '#8b5cf6',
  '#f59e0b', '#ef4444', '#06b6d4', '#84cc16', '#ec4899',
  '#6366f1', '#14b8a6', '#f97316', '#a855f7', '#78716c',
]

onMounted(load)

async function load() {
  loading.value = true
  try {
    const { data } = await tagsApi.list()
    tags.value = data
  } catch (e) {
    console.error('Failed to load tags', e)
  } finally {
    loading.value = false
  }
}

async function create() {
  const name = newName.value.trim()
  if (!name) return
  error.value = ''
  try {
    await tagsApi.create({ name, color: newColor.value })
    newName.value = ''
    newColor.value = '#5bc0de'
    await load()
  } catch (e) {
    error.value = e.response?.status === 409 ? '标签已存在' : '创建失败'
  }
}

function startEdit(tag) {
  editingId.value = tag.id
  editName.value = tag.name
  editColor.value = tag.color
}

function cancelEdit() {
  editingId.value = null
  editName.value = ''
  editColor.value = ''
}

async function saveEdit() {
  const name = editName.value.trim()
  if (!name) return
  error.value = ''
  try {
    await tagsApi.update(editingId.value, { name, color: editColor.value })
    editingId.value = null
    await load()
  } catch (e) {
    error.value = e.response?.status === 409 ? '标签已存在' : '保存失败'
  }
}

async function remove(id) {
  if (!confirm('确定删除这个标签？所有作品上的该标签也会被移除。')) return
  try {
    await tagsApi.delete(id)
    await load()
  } catch (e) {
    console.error('Failed to delete tag', e)
  }
}
</script>

<template>
  <div class="page">
    <div class="page-inner">
      <!-- Header -->
      <div class="top-bar">
        <div class="hd-left">
          <h1 class="title">
            <span class="title-stamp">🏷️</span>
            贴纸集
          </h1>
          <p class="subtitle">创建和管理标签，像收集贴纸一样为作品分类</p>
        </div>
        <div class="hd-back">
          <button class="back-btn" @click="router.push('/')">
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
              <path fill-rule="evenodd" d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z" clip-rule="evenodd"/>
            </svg>
            返回
          </button>
        </div>
      </div>

      <!-- Create sticker card -->
      <div class="create-card">
        <div class="create-bg" />
        <div class="create-inner">
          <div class="create-label">新贴纸</div>
          <div class="create-row">
            <div class="create-color-area">
              <div
                class="create-swatch-preview"
                :style="{ background: newColor }"
              />
              <div class="create-color-picker">
                <div
                  v-for="c in presetColors"
                  :key="c"
                  class="color-swatch"
                  :class="{ sel: newColor === c }"
                  :style="{ background: c }"
                  @click="newColor = c"
                />
                <label class="color-custom">
                  <input type="color" v-model="newColor" class="color-native" />
                  <svg viewBox="0 0 16 16" fill="currentColor" width="11" height="11">
                    <path d="M4 8h8M8 4v8" stroke="currentColor" stroke-width="1.5"/>
                  </svg>
                </label>
              </div>
            </div>
            <div class="create-input-area">
              <input
                v-model="newName"
                class="name-input"
                placeholder="输入标签名称..."
                maxlength="20"
                @keyup.enter="create"
              />
              <button class="create-btn" @click="create" :disabled="!newName.trim()">
                <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                  <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z"/>
                </svg>
                添加
              </button>
            </div>
          </div>
          <p v-if="error" class="err">{{ error }}</p>
        </div>
      </div>

      <!-- Tag list -->
      <div v-if="loading" class="loading">
        <div class="loading-dots">
          <span class="dot" v-for="i in 3" :key="i" :style="{ animationDelay: i * 0.15 + 's' }" />
        </div>
        <span class="loading-text">加载中...</span>
      </div>

      <div v-else-if="tags.length" class="tag-grid">
        <div
          v-for="t in tags"
          :key="t.id"
          class="tag-card"
          :style="{ '--tag-color': t.color }"
          :class="{ editing: editingId === t.id }"
        >
          <!-- Editing state -->
          <template v-if="editingId === t.id">
            <div class="edit-color-strip" :style="{ background: editColor }" />
            <div class="edit-body">
              <div class="edit-color-row">
                <div
                  v-for="c in presetColors"
                  :key="c"
                  class="color-swatch sm"
                  :class="{ sel: editColor === c }"
                  :style="{ background: c }"
                  @click="editColor = c"
                />
                <label class="color-custom sm">
                  <input type="color" v-model="editColor" class="color-native" />
                  <svg viewBox="0 0 16 16" fill="currentColor" width="10" height="10">
                    <path d="M4 8h8M8 4v8" stroke="currentColor" stroke-width="1.5"/>
                  </svg>
                </label>
              </div>
              <input v-model="editName" class="edit-input" maxlength="20" @keyup.enter="saveEdit" />
              <div class="edit-actions">
                <button class="act-save" @click="saveEdit">保存</button>
                <button class="act-cancel" @click="cancelEdit">取消</button>
              </div>
            </div>
          </template>

          <!-- Display state -->
          <template v-else>
            <div class="tag-stripe" :style="{ background: t.color }" />
            <div class="tag-body">
              <div class="tag-color-dot" :style="{ background: t.color }" />
              <span class="tag-name">{{ t.name }}</span>
              <div class="tag-actions">
                <button class="act-btn" @click="startEdit(t)" title="编辑">
                  <svg viewBox="0 0 20 20" fill="currentColor" width="13" height="13">
                    <path d="M2.695 14.763l-1.262 3.154a.5.5 0 00.65.65l3.155-1.262a4 4 0 001.343-.885L17.5 7.5a2.121 2.121 0 00-3-3L3.58 13.42a4 4 0 00-.885 1.343z"/>
                  </svg>
                </button>
                <button class="act-btn act-del" @click="remove(t.id)" title="删除">
                  <svg viewBox="0 0 20 20" fill="currentColor" width="13" height="13">
                    <path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c-.84 0-1.673.025-2.5.075V3.75c0-.69.56-1.25 1.25-1.25h2.5c.69 0 1.25.56 1.25 1.25v.325C11.673 4.025 10.84 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clip-rule="evenodd"/>
                  </svg>
                </button>
              </div>
            </div>
          </template>
        </div>
      </div>

      <div v-else class="empty">
        <div class="empty-icon">🏷️</div>
        <p>还没有标签</p>
        <span class="empty-hint">在上面创建一个吧</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 20px 16px;
  background: var(--bg-primary);
  min-height: calc(100vh - var(--topbar-height));
}
@media (max-width: 767px) { .page { padding-top: 0; } }
@media (min-width: 768px) { .page { padding: 24px 32px; } }
.page-inner { max-width: 720px; margin: 0 auto; }

/* Header */
.top-bar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
  gap: 16px;
}
.hd-left { min-width: 0; }
.title {
  font-size: var(--fs-2xl);
  font-weight: 800;
  letter-spacing: -0.5px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.title-stamp { font-size: 1.2em; }
.subtitle { font-size: var(--fs-sm); color: var(--text-tertiary); margin-top: 2px; }

.hd-back { flex-shrink: 0; }
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
.back-btn:hover {
  color: var(--text-primary);
  background: var(--bg-surface-hover);
}

/* Create card */
.create-card {
  position: relative;
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  margin-bottom: 20px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  transition: box-shadow 0.15s;
}
.create-card:hover { box-shadow: var(--shadow-md); }
.create-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,107,53,0.03) 0%, transparent 50%);
  pointer-events: none;
}
.create-inner {
  position: relative;
  padding: 18px 20px;
}
.create-label {
  font-size: var(--fs-xs);
  font-weight: 700;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}
.create-row {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  flex-wrap: wrap;
}
.create-color-area {
  display: flex;
  align-items: center;
  gap: 10px;
}
.create-swatch-preview {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
  border: 2px solid var(--color-border);
  transition: all 0.2s;
}
.create-color-picker {
  display: flex;
  gap: 4px;
  align-items: center;
  flex-wrap: wrap;
}
.create-input-area {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 200px;
}
.name-input {
  flex: 1;
  height: 38px;
  padding: 0 14px;
  font-size: var(--fs-sm);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--bg-primary);
  transition: all 0.15s;
  outline: none;
  min-width: 120px;
}
.name-input:focus {
  border-color: var(--text-tertiary);
  background: var(--bg-surface);
  box-shadow: 0 0 0 3px rgba(0,0,0,0.02);
}
.create-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 38px;
  padding: 0 18px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-sm);
  font-weight: 600;
  background: var(--primary);
  color: white;
  transition: all 0.15s;
  white-space: nowrap;
}
.create-btn:hover { background: var(--primary-hover); }
.create-btn:disabled { opacity: 0.4; cursor: default; }

/* Color swatches */
.color-swatch {
  width: 22px; height: 22px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.15s;
  flex-shrink: 0;
}
.color-swatch.sm { width: 18px; height: 18px; }
.color-swatch:hover { transform: scale(1.15); }
.color-swatch.sel {
  border-color: var(--text-primary);
  box-shadow: 0 0 0 2px var(--bg-surface);
  transform: scale(1.15);
}
.color-custom {
  width: 22px; height: 22px;
  border-radius: 50%;
  background: var(--bg-input);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: var(--text-tertiary);
  flex-shrink: 0; transition: all 0.15s;
}
.color-custom.sm { width: 18px; height: 18px; }
.color-custom:hover { color: var(--text-primary); }
.color-native { position: absolute; opacity: 0; width: 0; height: 0; }

.err { font-size: var(--fs-xs); color: #ef4444; margin-top: 10px; }

/* Loading */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--text-tertiary);
  gap: 12px;
}
.loading-dots { display: flex; gap: 6px; }
.dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--text-tertiary);
  animation: bounce-dot 1s ease-in-out infinite;
}
@keyframes bounce-dot {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}
.loading-text { font-size: var(--fs-sm); }

/* Tag grid */
.tag-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Tag card */
.tag-card {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: all 0.2s;
  border: 1px solid var(--color-border);
}
.tag-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.06), 0 0 0 1px var(--tag-color);
  transform: translateY(-1px);
}
.tag-card.editing {
  border-color: var(--tag-color);
  box-shadow: 0 0 0 1px var(--tag-color), var(--shadow-sm);
}

/* Tag card — display state */
.tag-stripe {
  height: 4px;
  width: 100%;
  flex-shrink: 0;
}
.tag-body {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
}
.tag-color-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: 0 0 0 3px var(--bg-surface), 0 0 0 4px var(--tag-color);
}
.tag-name {
  flex: 1;
  font-size: var(--fs-base);
  font-weight: 600;
  color: var(--text-primary);
}
.tag-actions {
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.15s;
}
.tag-card:hover .tag-actions { opacity: 1; }
.act-btn {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--text-tertiary);
  transition: all 0.15s;
}
.act-btn:hover { background: var(--bg-surface-hover); color: var(--primary); }
.act-del:hover { color: #ef4444; }

/* Tag card — editing state */
.edit-color-strip {
  height: 4px;
  width: 100%;
}
.edit-body {
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.edit-color-row {
  display: flex;
  gap: 4px;
  align-items: center;
  flex-wrap: wrap;
}
.edit-input {
  height: 36px;
  padding: 0 12px;
  font-size: var(--fs-sm);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--bg-primary);
  outline: none;
  transition: all 0.15s;
}
.edit-input:focus { border-color: var(--tag-color, var(--text-tertiary)); background: var(--bg-surface); }

.edit-actions { display: flex; gap: 6px; }
.act-save, .act-cancel {
  height: 30px; padding: 0 14px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-xs); font-weight: 600;
  transition: all 0.15s;
}
.act-save { background: var(--primary); color: white; }
.act-save:hover { background: var(--primary-hover); }
.act-cancel { color: var(--text-tertiary); background: var(--bg-input); }
.act-cancel:hover { background: var(--bg-surface-hover); color: var(--text-primary); }

/* Empty state */
.empty {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-tertiary);
}
.empty-icon { font-size: 2.5rem; margin-bottom: 12px; }
.empty p { font-size: var(--fs-base); font-weight: 600; margin-bottom: 4px; }
.empty-hint { font-size: var(--fs-sm); color: var(--text-tertiary); }

/* Mobile adjustments */
@media (max-width: 480px) {
  .create-inner { padding: 14px 16px; }
  .create-row { flex-direction: column; gap: 10px; }
  .create-color-area { width: 100%; }
  .create-input-area { width: 100%; }
  .tag-body { padding: 12px 14px; }
  .tag-actions { opacity: 1; }
}
</style>
