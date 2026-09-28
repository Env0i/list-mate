<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { worksApi, gameProfilesApi, attachmentsApi } from '../api/client'
import { STATUS_COLORS } from '../constants/work'
import { emptyToNull } from '../utils/payload'
import { showToast } from '../utils/toast'
import GameProfileForm from '../components/work/GameProfileForm.vue'
import StatusStamp from '../components/work/StatusStamp.vue'
import StateBlock from '../components/common/StateBlock.vue'
import SkeletonBlock from '../components/common/SkeletonBlock.vue'
import BaseModal from '../components/common/BaseModal.vue'

const route = useRoute()
const router = useRouter()

const gp = ref(null)
const work = ref(null)
const error = ref(false)
const loading = ref(true)
const saving = ref(false)
const dirty = ref(false)

const attachments = ref([])
const uploading = ref(false)
const dragOver = ref(false)

// 删除配置确认
const showDel = ref(false)
const deleting = ref(false)

const isGame = computed(() => (work.value?.category || 'game') === 'game')
const gpStatusSt = computed(() => gp.value?.status || 'wish')
const gpStatusColor = computed(() => STATUS_COLORS[gpStatusSt.value] || 'var(--s-wish)')
const siblings = computed(() => (work.value?.game_profiles || []).filter(x => x.id !== gp.value?.id))

// 脏状态：深度侦听表单对象；初始 load 的赋值不算修改
let suppressDirty = false
watch(gp, () => { if (!suppressDirty) dirty.value = true }, { deep: true })

async function load() {
  loading.value = true
  error.value = false
  suppressDirty = true
  try {
    const { data } = await gameProfilesApi.get(route.params.gpid)
    gp.value = data
    const workRes = await worksApi.get(data.work_id)
    work.value = workRes.data
    await loadAttachments()
  } catch (e) {
    console.error('Failed to load game profile', e)
    error.value = true
  } finally {
    loading.value = false
    // 深度 watcher 在下一次 flush 才触发，冲刷完再恢复脏标记
    nextTick(() => { suppressDirty = false })
  }
}
onMounted(load)
function beforeunload(e) {
  if (dirty.value) {
    e.preventDefault()
    e.returnValue = ''
  }
}
onMounted(() => window.addEventListener('beforeunload', beforeunload))
onBeforeUnmount(() => window.removeEventListener('beforeunload', beforeunload))

// —— 附件 ——
async function loadAttachments() {
  try {
    const { data } = await attachmentsApi.list(route.params.gpid)
    attachments.value = data
  } catch (e) {
    console.error('Failed to load attachments', e)
  }
}
async function uploadFiles(fileList) {
  const files = Array.from(fileList || [])
  if (!files.length) return
  uploading.value = true
  try {
    for (const f of files) {
      if (f.size > 20 * 1024 * 1024) {
        showToast(`${f.name} 超过 20 MB，未添加`, 'error')
        continue
      }
      await attachmentsApi.upload(route.params.gpid, f)
    }
    await loadAttachments()
    showToast('附件上传成功')
  } catch (e) {
    console.error('Upload failed', e)
    showToast('上传失败', 'error')
  } finally {
    uploading.value = false
  }
}
function onPick(e) {
  uploadFiles(e.target.files)
  e.target.value = ''
}
function onDrop(e) {
  dragOver.value = false
  uploadFiles(e.dataTransfer?.files)
}
function downloadAttachment(id) {
  window.open(attachmentsApi.downloadUrl(id), '_blank')
}
async function deleteAttachment(id) {
  try {
    await attachmentsApi.delete(id)
    attachments.value = attachments.value.filter(a => a.id !== id)
    showToast('附件已删除')
  } catch (e) {
    console.error('Delete failed', e)
    showToast('删除失败', 'error')
  }
}

// —— 保存 / 删除 ——
async function save() {
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
    await gameProfilesApi.update(route.params.gpid, body)
    dirty.value = false
    showToast('配置已保存')
  } catch (e) {
    console.error('Failed to save', e)
    showToast('保存失败', 'error')
  } finally {
    saving.value = false
  }
}

async function del() {
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
      <div class="layout" aria-busy="true">
        <div>
          <span class="sr-only">正在读取游戏配置</span>
          <SkeletonBlock v-for="h in [180, 150, 130]" :key="h" :h="h + 'px'" w="100%" radius="var(--radius-lg)" class="skel-sec" />
        </div>
        <div class="side"><SkeletonBlock h="200px" w="100%" radius="var(--radius-lg)" /></div>
      </div>
    </template>

    <!-- 错误态 -->
    <StateBlock
      v-else-if="error"
      kind="error"
      title="这套配置没能打开"
      message="本地服务暂时没有响应。已保存的配置、模组和附件不会丢失，稍后重试即可。"
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

    <!-- 满载 -->
    <template v-else-if="gp">
      <nav class="crumb" aria-label="路径">
        <router-link to="/">收藏</router-link>
        <span class="sep" aria-hidden="true">/</span>
        <router-link :to="`/works/${route.params.id}`">{{ work?.title }}</router-link>
        <span class="sep" aria-hidden="true">/</span>
        <span aria-current="page">{{ gp.name }}</span>
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
          <p class="eyebrow">游戏配置 #{{ gp.id }}</p>
          <h1 class="gp-title">{{ gp.name }}</h1>
          <p class="gp-sub">
            {{ work?.title }} ·
            <span class="stamp-wrap" :style="{ '--sc': gpStatusColor }">
              <StatusStamp category="game" :status="gp.status" />
            </span>
          </p>
        </div>
        <div class="gp-act">
          <button class="danger-btn" @click="showDel = true">删除配置</button>
        </div>
      </header>

      <div class="layout">
        <GameProfileForm
          :gp="gp"
          :saving="saving"
          :dirty="dirty"
          :cancel-to="`/works/${route.params.id}`"
          @save="save"
        >
          <template #extra>
            <!-- 附件 -->
            <section class="panel sec">
              <div class="panel-title">附件</div>
              <ul class="files">
                <li v-for="att in attachments" :key="att.id">
                  <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" class="f-icon" aria-hidden="true">
                    <path d="M7 3.5A1.5 1.5 0 005.5 5v13a1.5 1.5 0 001.5 1.5h6a1.5 1.5 0 001.5-1.5V5A1.5 1.5 0 0013 3.5H7z"/>
                  </svg>
                  <span class="f-name">{{ att.file_name }}</span>
                  <span v-if="att.file_size" class="f-size mono">{{ (att.file_size / 1024).toFixed(1) }} KB</span>
                  <button class="f-btn" type="button" @click="downloadAttachment(att.id)">下载</button>
                  <button class="f-btn del" type="button" @click="deleteAttachment(att.id)">删除</button>
                </li>
              </ul>
              <label
                class="drop"
                :class="{ over: dragOver, uploading }"
                @dragover.prevent="dragOver = true"
                @dragleave="dragOver = false"
                @drop.prevent="onDrop"
              >
                {{ uploading ? '上传中...' : '拖入文件或点击上传（存档、配置、截图，单个 ≤ 20 MB）' }}
                <input type="file" multiple class="sr-only" @change="onPick" :disabled="uploading">
              </label>
            </section>
          </template>
        </GameProfileForm>

        <!-- 侧栏：同一游戏的其他配置 -->
        <aside class="side" aria-label="同一游戏的其他配置">
          <div class="panel others">
            <div class="panel-title">{{ work?.title }} 的配置</div>
            <router-link
              v-for="x in work?.game_profiles || []"
              :key="x.id"
              :to="`/works/${route.params.id}/game-profiles/${x.id}`"
              :aria-current="x.id === gp.id ? 'page' : undefined"
            >
              <span class="o-name">{{ x.name }}</span>
              <span class="o-stamp" :style="{ '--sc': STATUS_COLORS[x.status] || 'var(--s-wish)' }">
                <StatusStamp category="game" :status="x.status" />
              </span>
            </router-link>
            <router-link class="o-new" :to="`/works/${route.params.id}/game-profiles/new`">＋ 新增配置</router-link>
          </div>
        </aside>
      </div>

      <!-- 删除确认 -->
      <BaseModal :open="showDel" size="sm" @close="showDel = false">
        <template #head><h2>删除这套配置？</h2></template>
        <p class="del-txt">
          「{{ gp.name }}」的进度、模组列表、附件和笔记会一起删除，不影响同一游戏的其他配置。
        </p>
        <template #foot>
          <button class="ghost-btn" type="button" @click="showDel = false">保留</button>
          <button class="danger-solid-btn" type="button" :disabled="deleting" @click="del">
            {{ deleting ? '删除中...' : '删除配置' }}
          </button>
        </template>
      </BaseModal>
    </template>
  </div>
</template>

<style scoped>
.page { padding: 20px 16px 64px; }
@media (min-width: 768px) { .page { padding: 24px 32px 64px; } }
.page.narrow { max-width: 1080px; margin: 0 auto; }
.mono { font-family: var(--font-mono); }

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
  grid-template-columns: 72px minmax(0, 1fr) auto;
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
.gp-sub { color: var(--text-secondary); font-size: var(--fs-sm); display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.stamp-wrap :deep(.stamp) { animation: none; }
.danger-btn {
  height: 36px;
  padding: 0 14px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--s-dropped);
  background: var(--bg-surface);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--s-dropped) 40%, transparent);
}
.danger-btn:hover { background: color-mix(in srgb, var(--s-dropped) 10%, var(--bg-surface)); }

.layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 24px;
  align-items: start;
}
.side { position: sticky; top: calc(var(--topbar-height) + 16px); display: flex; flex-direction: column; gap: 12px; }
.panel {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm), inset 0 0 0 1px var(--color-border);
  padding: 16px;
}
.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--fs-sm);
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 0.04em;
  margin-bottom: 12px;
}
.panel-title::after { content: ''; flex: 1; height: 1px; background: var(--line, rgba(0,0,0,0.09)); }
.others a {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-sm);
  min-height: 40px;
  color: var(--text-primary);
}
.others a:hover { background: var(--bg-surface-hover); }
.others a[aria-current='page'] { background: var(--bg-input); font-weight: 700; }
.others .o-name { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.others .o-stamp :deep(.stamp) { animation: none; }
.o-new {
  margin-top: 4px;
  display: inline-flex;
  align-items: center;
  min-height: 40px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-secondary);
}
.o-new:hover { background: var(--bg-surface-hover); color: var(--text-primary); }

/* 附件（在表单 #extra 槽内，样式与表单面板一致） */
.panel.sec { margin-top: 16px; }
.files { list-style: none; display: flex; flex-direction: column; gap: 6px; padding: 0; margin: 0 0 10px; }
.files li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  background: var(--bg-input);
  font-size: var(--fs-sm);
}
.f-icon { color: var(--text-tertiary); flex: none; }
.f-name { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.f-size { font-size: 11px; color: var(--text-tertiary); flex: none; }
.f-btn {
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  flex: none;
}
.f-btn:hover { background: var(--bg-surface); color: var(--text-primary); }
.f-btn.del:hover { color: var(--s-dropped); }
.drop {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 56px;
  border: 1.5px dashed var(--line, rgba(0,0,0,0.09));
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s;
  text-align: center;
  padding: 8px;
}
.drop:hover, .drop.over {
  border-color: var(--c-game);
  color: var(--text-primary);
  background: color-mix(in srgb, var(--c-game) 6%, transparent);
}
.drop.uploading { opacity: 0.6; pointer-events: none; }

.ghost-btn {
  height: 40px;
  padding: 0 16px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-secondary);
}
.ghost-btn:hover { background: var(--bg-surface-hover); color: var(--text-primary); }
.del-txt { font-size: var(--fs-sm); color: var(--text-secondary); }
.danger-solid-btn {
  height: 40px;
  padding: 0 16px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  background: var(--s-dropped);
  color: #fff;
}
.danger-solid-btn:hover:not(:disabled) { background: color-mix(in srgb, var(--s-dropped) 85%, black); }
.danger-solid-btn:disabled { opacity: 0.5; }

.skel-sec { display: block; margin-bottom: 16px; }

@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
  .side { position: static; order: -1; }
}
@media (max-width: 767px) {
  .gp-head { grid-template-columns: 56px minmax(0, 1fr); }
  .gp-head .th { width: 56px; }
  .gp-act { grid-column: 1 / -1; }
}

/* 触屏：操作控件达到 44px 触控目标（Q3 决策；表单内部控件在 GameProfileForm 内处理） */
@media (pointer: coarse) {
  .danger-btn, .ghost-btn, .danger-solid-btn, .f-btn { min-height: 44px; }
  .others a, .o-new { min-height: 44px; }
}
</style>
