<script setup>
import { ref, onMounted } from 'vue'
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
      <div class="top-bar">
        <button class="back-btn" @click="router.push('/')">
          <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path fill-rule="evenodd" d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z" clip-rule="evenodd"/>
          </svg>
          返回
        </button>
      </div>
      <h1 class="page-title">自定义标签</h1>
      <p class="subtitle">创建和管理标签，为作品打上标签以便分类筛选</p>

      <!-- Create form -->
      <div class="create-card">
        <div class="create-row">
          <input
            v-model="newName"
            class="name-input"
            placeholder="新标签名称..."
            maxlength="20"
            @keyup.enter="create"
          />
          <div class="color-picker">
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
              <svg viewBox="0 0 16 16" fill="currentColor" width="12" height="12">
                <path d="M4 8h8M8 4v8" stroke="currentColor" stroke-width="1.5"/>
              </svg>
            </label>
          </div>
          <button class="create-btn" @click="create" :disabled="!newName.trim()">
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
              <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z"/>
            </svg>
            添加
          </button>
        </div>
        <p v-if="error" class="err">{{ error }}</p>
      </div>

      <!-- Tag list -->
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="tags.length" class="tag-list">
        <div v-for="t in tags" :key="t.id" class="tag-row">
          <template v-if="editingId === t.id">
            <input v-model="editName" class="name-input sm" maxlength="20" @keyup.enter="saveEdit" />
            <div class="color-picker sm">
              <div
                v-for="c in presetColors"
                :key="c"
                class="color-swatch sm"
                :class="{ sel: editColor === c }"
                :style="{ background: c }"
                @click="editColor = c"
              />
            </div>
            <div class="edit-actions">
              <button class="act-save" @click="saveEdit">保存</button>
              <button class="act-cancel" @click="cancelEdit">取消</button>
            </div>
          </template>
          <template v-else>
            <span class="tag-dot" :style="{ background: t.color }" />
            <span class="tag-name">{{ t.name }}</span>
            <div class="tag-actions">
              <button class="act-edit" @click="startEdit(t)" title="编辑">
                <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                  <path d="M2.695 14.763l-1.262 3.154a.5.5 0 00.65.65l3.155-1.262a4 4 0 001.343-.885L17.5 7.5a2.121 2.121 0 00-3-3L3.58 13.42a4 4 0 00-.885 1.343z"/>
                </svg>
              </button>
              <button class="act-del" @click="remove(t.id)" title="删除">
                <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                  <path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c-.84 0-1.673.025-2.5.075V3.75c0-.69.56-1.25 1.25-1.25h2.5c.69 0 1.25.56 1.25 1.25v.325C11.673 4.025 10.84 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clip-rule="evenodd"/>
                </svg>
              </button>
            </div>
          </template>
        </div>
      </div>
      <div v-else class="empty">
        <p>暂无标签，创建一个吧</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 20px 16px; }
@media (min-width: 768px) { .page { padding: 24px 32px; } }
.page-inner { max-width: 600px; margin: 0 auto; }
.top-bar { margin-bottom: 16px; }
.back-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 16px; border-radius: var(--radius-md);
  font-size: var(--fs-sm); font-weight: 600; color: var(--text-tertiary);
  transition: all 0.15s;
}
.back-btn:hover { color: var(--text-primary); background: var(--bg-surface-hover); }
.page-title { font-size: var(--fs-2xl); font-weight: 800; margin-bottom: 4px; }
.subtitle { font-size: var(--fs-sm); color: var(--text-tertiary); margin-bottom: 24px; }

/* Create card */
.create-card {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  padding: 16px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 16px;
}
.create-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.name-input {
  flex: 1; min-width: 140px;
  height: 36px; padding: 0 12px;
  font-size: var(--fs-sm); border-radius: var(--radius-sm);
  border: 1px solid var(--color-border); background: var(--bg-primary);
  transition: border-color 0.15s;
}
.name-input:focus { border-color: var(--text-tertiary); outline: none; background: var(--bg-surface); }
.name-input.sm { flex: none; width: 160px; height: 30px; font-size: var(--fs-xs); }

.color-picker { display: flex; gap: 4px; align-items: center; flex-wrap: wrap; }
.color-picker.sm { gap: 2px; }
.color-swatch {
  width: 20px; height: 20px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.15s;
  flex-shrink: 0;
}
.color-swatch.sm { width: 16px; height: 16px; }
.color-swatch:hover { transform: scale(1.2); }
.color-swatch.sel { border-color: var(--text-primary); box-shadow: 0 0 0 2px var(--bg-surface); transform: scale(1.2); }
.color-custom {
  width: 20px; height: 20px;
  border-radius: 50%;
  background: var(--bg-input);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  color: var(--text-tertiary);
  flex-shrink: 0;
}
.color-custom:hover { color: var(--text-primary); }
.color-native { position: absolute; opacity: 0; width: 0; height: 0; }

.create-btn {
  display: inline-flex; align-items: center; gap: 4px;
  height: 36px; padding: 0 16px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm); font-weight: 600;
  background: var(--primary); color: white;
  transition: all 0.15s;
}
.create-btn:hover { background: var(--primary-hover); }
.create-btn:disabled { opacity: 0.4; cursor: default; }
.err { font-size: var(--fs-xs); color: #ef4444; margin-top: 8px; }

/* Tag list */
.loading { text-align: center; padding: 60px 20px; color: var(--text-tertiary); }
.tag-list { display: flex; flex-direction: column; gap: 6px; }
.tag-row {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px;
  background: var(--bg-surface);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
  transition: all 0.15s;
}
.tag-row:hover { box-shadow: var(--shadow-md); }
.tag-dot {
  width: 12px; height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}
.tag-name { flex: 1; font-size: var(--fs-base); font-weight: 600; color: var(--text-primary); }
.tag-actions { display: flex; gap: 2px; }
.act-edit, .act-del {
  width: 30px; height: 30px;
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--text-tertiary);
  transition: all 0.15s;
}
.act-edit:hover { background: var(--bg-surface-hover); color: var(--primary); }
.act-del:hover { background: var(--bg-surface-hover); color: #ef4444; }

.edit-actions { display: flex; gap: 4px; }
.act-save, .act-cancel {
  height: 28px; padding: 0 10px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-xs); font-weight: 600;
  transition: all 0.15s;
}
.act-save { background: var(--primary); color: white; }
.act-save:hover { background: var(--primary-hover); }
.act-cancel { color: var(--text-tertiary); }
.act-cancel:hover { background: var(--bg-surface-hover); color: var(--text-primary); }

.empty { text-align: center; padding: 60px 20px; color: var(--text-tertiary); font-size: var(--fs-sm); }
</style>
