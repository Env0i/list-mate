<script setup>
import { ref, computed, onMounted } from 'vue'
import { tagsApi, worksApi } from '../api/client'
import StateBlock from '../components/common/StateBlock.vue'
import SkeletonBlock from '../components/common/SkeletonBlock.vue'
import BaseModal from '../components/common/BaseModal.vue'
import { showToast } from '../utils/toast'

// 调色板只取 style.css 既有令牌（原型同款 7 色）；旧数据里的 hex 颜色仍可正常渲染
const PAL = [
  { token: 'var(--primary)', name: '能量橙' },
  { token: 'var(--c-anime)', name: '番剧红' },
  { token: 'var(--c-novel)', name: '小说蓝' },
  { token: 'var(--c-comic)', name: '漫画绿' },
  { token: 'var(--c-game)', name: '游戏橙' },
  { token: 'var(--s-paused)', name: '暂停黄' },
  { token: 'var(--s-wish)', name: '灰' },
]

const tags = ref([])
const works = ref([])
const loading = ref(true)
const error = ref(false)
const newName = ref('')
const newColor = ref(PAL[2].token) // 默认小说蓝（原型同款）
const formError = ref('')
const editingId = ref(null)
const editName = ref('')
const editColor = ref('')

// 删除确认
const delTarget = ref(null) // { tag, usage }

const usage = (id) => works.value.filter(w => (w.tag_ids || []).includes(id))
const usedWorks = computed(() => works.value.filter(w => (w.tag_ids || []).length).length)
const summary = computed(() => `${tags.value.length} 张贴纸 · 贴在 ${usedWorks.value} 部作品上`)
const coversOf = (id) => usage(id).slice(0, 6)
const coverUrl = (w) => worksApi.coverUrl(w.id)

onMounted(load)

async function load() {
  loading.value = true
  error.value = false
  try {
    const [tagsRes, worksRes] = await Promise.all([
      tagsApi.list(),
      worksApi.list({ page_size: 500 }),
    ])
    tags.value = tagsRes.data
    works.value = worksRes.data.items
  } catch (e) {
    console.error('Failed to load tags', e)
    error.value = true
  } finally {
    loading.value = false
  }
}

const dup = (n, except) => tags.value.some(t => t.name === n && t.id !== except)

async function create() {
  const name = newName.value.trim()
  formError.value = !name ? '名称不能为空' : dup(name) ? '已经有这张贴纸了' : ''
  if (formError.value) return
  try {
    await tagsApi.create({ name, color: newColor.value })
    newName.value = ''
    showToast(`贴上了「${name}」`)
    await load()
  } catch (e) {
    formError.value = e.response?.status === 409 ? '已经有这张贴纸了' : '创建失败'
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
  if (!name || dup(name, editingId.value)) return
  try {
    await tagsApi.update(editingId.value, { name, color: editColor.value })
    editingId.value = null
    showToast('贴纸已更新')
    await load()
  } catch (e) {
    showToast(e.response?.status === 409 ? '已经有这张贴纸了' : '保存失败', 'error')
  }
}

function askDelete(tag) {
  delTarget.value = { tag, usage: usage(tag.id) }
}

// 删除 + 5 秒撤销：撤销 = 重建标签（新 id）+ 批量回贴到原作品（§5 替换点）
async function doDelete() {
  const { tag, usage: hit } = delTarget.value
  delTarget.value = null
  // 快照：每部受影响作品删除前的完整 tag_ids
  const snapshot = hit.map(w => ({ id: w.id, tag_ids: [...(w.tag_ids || [])] }))
  try {
    await tagsApi.delete(tag.id)
    await load()
    showToast(`已删除「${tag.name}」`, 'success', {
      action: {
        label: '撤销',
        handler: async () => {
          try {
            const { data: created } = await tagsApi.create({ name: tag.name, color: tag.color })
            for (const s of snapshot) {
              const restored = s.tag_ids.map(id => (id === tag.id ? created.id : id))
              await worksApi.update(s.id, { tag_ids: restored })
            }
            showToast(`已恢复「${tag.name}」及其 ${snapshot.length} 处贴纸`)
            await load()
          } catch (e) {
            console.error('undo delete tag failed', e)
            showToast('没保存成功', 'error')
          }
        },
      },
    })
  } catch (e) {
    console.error('Failed to delete tag', e)
    showToast('删除失败', 'error')
  }
}
</script>

<template>
  <div class="page narrow">
    <!-- 页头 -->
    <div class="page-head">
      <div>
        <p class="eyebrow">Sticker Book</p>
        <h1 class="title">贴纸集</h1>
      </div>
      <p class="summary">{{ loading ? '' : summary }}</p>
    </div>

    <!-- 新建贴纸（读取未完成或失败时禁用，避免写入） -->
    <section class="panel new" aria-labelledby="newH">
      <form class="new-form" novalidate @submit.prevent="create">
        <h2 id="newH" class="new-title">新贴纸</h2>
        <div class="swatches" role="radiogroup" aria-label="贴纸颜色">
          <button
            v-for="p in PAL"
            :key="p.token"
            type="button"
            class="sw"
            role="radio"
            :aria-checked="newColor === p.token"
            :aria-label="p.name"
            :style="{ '--sw': p.token }"
            :disabled="loading || error"
            @click="newColor = p.token"
          />
        </div>
        <div class="field">
          <label class="sr-only" for="newN">标签名称</label>
          <input id="newN" v-model="newName" maxlength="12" placeholder="输入标签名称，如「异世界」" :disabled="loading || error">
          <span v-if="formError" class="err">{{ formError }}</span>
        </div>
        <button class="btn-primary" type="submit" :disabled="loading || error">贴上</button>
      </form>
    </section>

    <!-- 加载骨架 -->
    <div v-if="loading" class="stickers" aria-busy="true">
      <span class="sr-only">正在读取贴纸</span>
      <SkeletonBlock v-for="i in 6" :key="i" h="108px" w="100%" radius="var(--radius-md)" />
    </div>

    <!-- 错误态 -->
    <StateBlock
      v-else-if="error"
      kind="error"
      title="贴纸集没能打开"
      message="本地服务暂时没有响应，已有标签和作品上的贴纸都不会丢失。"
      @retry="load"
    />

    <!-- 标签列表 -->
    <section v-else aria-label="全部标签">
      <div v-if="tags.length" class="stickers">
        <article
          v-for="t in tags"
          :key="t.id"
          class="stk"
          :class="{ editing: editingId === t.id }"
          :style="{ '--tc': t.color }"
        >
          <div class="band" aria-hidden="true" />
          <!-- 编辑态 -->
          <form v-if="editingId === t.id" class="body edit-body" novalidate @submit.prevent="saveEdit">
            <div class="field grow">
              <label class="lbl" :for="`en-${t.id}`">名称</label>
              <input :id="`en-${t.id}`" v-model="editName" maxlength="12">
            </div>
            <div class="swatches" role="radiogroup" aria-label="颜色">
              <button
                v-for="p in PAL"
                :key="p.token"
                type="button"
                class="sw"
                role="radio"
                :aria-checked="editColor === p.token"
                :aria-label="p.name"
                :style="{ '--sw': p.token }"
                @click="editColor = p.token"
              />
            </div>
            <div class="edit-actions">
              <button class="btn-ghost sm" type="button" @click="cancelEdit">取消</button>
              <button class="btn-secondary sm" type="submit">保存</button>
            </div>
          </form>
          <!-- 展示态 -->
          <template v-else>
            <div class="body">
              <span class="nm">
                <span class="dot" aria-hidden="true" />
                <router-link :to="`/?tag=${t.id}`">{{ t.name }}</router-link>
              </span>
              <span class="cnt">{{ usage(t.id).length }} 部</span>
              <span class="ops">
                <button class="icon-btn" type="button" :aria-label="`编辑 ${t.name}`" @click="startEdit(t)">
                  <svg viewBox="0 0 20 20" fill="currentColor" width="13" height="13">
                    <path d="M2.695 14.763l-1.262 3.154a.5.5 0 00.65.65l3.155-1.262a4 4 0 001.343-.885L17.5 7.5a2.121 2.121 0 00-3-3L3.58 13.42a4 4 0 00-.885 1.343z"/>
                  </svg>
                </button>
                <button class="icon-btn" type="button" :aria-label="`删除 ${t.name}`" @click="askDelete(t)">
                  <svg viewBox="0 0 20 20" fill="currentColor" width="13" height="13">
                    <path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c-.84 0-1.673.025-2.5.075V3.75c0-.69.56-1.25 1.25-1.25h2.5c.69 0 1.25.56 1.25 1.25v.325C11.673 4.025 10.84 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clip-rule="evenodd"/>
                  </svg>
                </button>
              </span>
            </div>
            <div v-if="usage(t.id).length" class="covers">
              <img
                v-for="w in coversOf(t.id)"
                :key="w.id"
                :src="coverUrl(w)"
                :alt="w.title"
                :title="w.title"
                width="30"
                height="42"
                loading="lazy"
              >
              <span v-if="usage(t.id).length > 6" class="cnt more">+{{ usage(t.id).length - 6 }}</span>
            </div>
            <div v-else class="covers"><span class="cnt">还没贴在任何作品上</span></div>
          </template>
        </article>
      </div>

      <!-- 空态 -->
      <StateBlock
        v-else
        title="贴纸集还是空的"
        message="在上面挑个颜色、写个名字，贴出第一张。"
      />
    </section>

    <!-- 删除确认 -->
    <BaseModal
      :open="!!delTarget"
      size="sm"
      @close="delTarget = null"
    >
      <template #head><h2>撕掉这张贴纸？</h2></template>
      <p class="del-txt">
        <template v-if="delTarget && delTarget.usage.length">
          「{{ delTarget.tag.name }}」贴在 {{ delTarget.usage.length }} 部作品上，删除后这些作品会一起摘掉它。作品本身不受影响。
        </template>
        <template v-else-if="delTarget">「{{ delTarget.tag.name }}」还没用过，可以放心删除。</template>
      </p>
      <template #foot>
        <button class="btn-ghost" type="button" @click="delTarget = null">保留</button>
        <button class="btn-danger-solid" type="button" @click="doDelete">删除标签</button>
      </template>
    </BaseModal>
  </div>
</template>

<style scoped>
.page { padding: 20px 16px 64px; }
@media (min-width: 768px) { .page { padding: 24px 32px 64px; } }
.page.narrow { max-width: 1080px; margin: 0 auto; }

.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.eyebrow {
  font-family: var(--font-mono);
  font-size: var(--fs-xs);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-tertiary);
  margin-bottom: 2px;
}
.title { font-size: var(--fs-2xl); font-weight: 800; letter-spacing: -0.5px; }
.summary { font-size: var(--fs-sm); color: var(--text-secondary); }

/* 新建面板：虚线框表示可投放 */
.panel.new {
  border: 1.5px dashed var(--line, rgba(0,0,0,0.09));
  background: transparent;
  border-radius: var(--radius-md);
  padding: 16px;
  margin-bottom: 24px;
}
.new-form { display: flex; align-items: flex-start; gap: 12px; flex-wrap: wrap; }
.new-title { width: 100%; font-size: var(--fs-sm); font-weight: 700; margin-bottom: 8px; }
.swatches { display: flex; flex-wrap: wrap; gap: 6px; }
.sw {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--sw);
  box-shadow: inset 0 0 0 2px color-mix(in srgb, black 10%, transparent);
  position: relative;
  cursor: pointer;
}
.sw[aria-checked='true']::after {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  box-shadow: 0 0 0 2px var(--text-primary);
}
.field { display: flex; flex-direction: column; gap: 6px; flex: 1; min-width: 200px; }
.field input {
  height: 40px;
  padding: 0 14px;
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  border: 1px solid var(--color-border);
  color: var(--text-primary);
  font: inherit;
  font-size: var(--fs-sm);
}
.field input:focus { outline: none; border-color: var(--text-tertiary); }
.err { font-size: 11px; color: var(--s-dropped); font-weight: 600; }

.btn-primary {
  height: 40px;
  padding: 0 20px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 700;
  background: var(--primary);
  color: #fff;
  transition: background 0.15s;
}
.btn-primary:hover:not(:disabled) { background: var(--primary-hover); }
.btn-primary:disabled { opacity: 0.45; cursor: not-allowed; }

/* 贴纸卡 */
.stickers {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}
.stk {
  position: relative;
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  box-shadow: var(--shadow-sm), inset 0 0 0 1px var(--color-border);
  overflow: hidden;
  transition: transform 0.2s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.2s;
}
.stk:hover { transform: rotate(-0.6deg) translateY(-2px); box-shadow: var(--shadow-md), inset 0 0 0 1px var(--color-border); }
.band { height: 10px; background: var(--tc); }
.body { display: flex; align-items: center; gap: 12px; padding: 12px 12px 12px 16px; }
.nm { flex: 1; min-width: 0; font-weight: 700; display: flex; align-items: center; gap: 8px; }
.nm .dot { width: 12px; height: 12px; border-radius: 50%; background: var(--tc); flex: none; }
.nm a { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.nm a:hover { text-decoration: underline; }
.cnt { font-size: 11px; color: var(--text-tertiary); font-family: var(--font-mono); flex: none; }
.ops { display: flex; gap: 2px; opacity: 0; transition: opacity 0.15s; }
.stk:hover .ops, .stk:focus-within .ops { opacity: 1; }
@media (hover: none) { .ops { opacity: 1; } }
.icon-btn {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  transition: background 0.15s;
}
.icon-btn:hover { background: var(--bg-surface-hover); color: var(--text-primary); }
.covers { display: flex; gap: 4px; padding: 0 16px 12px; align-items: center; }
.covers img { width: 30px; height: 42px; object-fit: cover; border-radius: 3px; background: var(--bg-input); }
.covers .more { align-self: center; }

/* 编辑态 */
.edit-body { flex-wrap: wrap; }
.edit-body .grow { min-width: 100%; }
.lbl { font-size: var(--fs-xs); font-weight: 600; color: var(--text-secondary); }
.edit-actions { display: flex; gap: 6px; margin-left: auto; }
.btn-ghost, .btn-secondary {
  height: 32px;
  padding: 0 12px;
  border-radius: var(--radius-md);
  font-size: var(--fs-xs);
  font-weight: 600;
}
.btn-ghost { color: var(--text-secondary); }
.btn-ghost:hover { background: var(--bg-surface-hover); color: var(--text-primary); }
.btn-secondary { background: var(--bg-surface); color: var(--text-primary); box-shadow: inset 0 0 0 1px var(--line, rgba(0,0,0,0.09)); }
.btn-secondary:hover { background: var(--bg-surface-hover); }

/* 删除确认 */
.del-txt { font-size: var(--fs-sm); color: var(--text-secondary); }
.btn-danger-solid {
  height: 40px;
  padding: 0 16px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  background: var(--s-dropped);
  color: #fff;
}
.btn-danger-solid:hover { background: color-mix(in srgb, var(--s-dropped) 85%, black); }

/* 触屏 */
@media (pointer: coarse) {
  .sw { width: 40px; height: 40px; }
  .icon-btn { width: 44px; height: 44px; }
  .btn-ghost, .btn-secondary { min-height: 44px; }
}
@media (prefers-reduced-motion: reduce) {
  .stk { transition: none; }
}
</style>
