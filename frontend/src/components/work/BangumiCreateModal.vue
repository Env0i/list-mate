<script setup>
import { ref, watch, computed } from 'vue'
import { bangumiApi, worksApi } from '../../api/client'
import { emptyToNull } from '../../utils/payload'

// 搜索/发现共用的「确认作品信息」入库模态：单列紧凑，封面走本地图床代理
const props = defineProps({
  open: { type: Boolean, default: false },
  item: { type: Object, default: null },
})
const emit = defineEmits(['close', 'created'])

const form = ref({})
const creating = ref(false)
const error = ref('')

const typeToCategory = { 1: 'novel', 2: 'anime', 4: 'game', default: 'anime' }
const defaultProgressUnit = { anime: 'ep', novel: 'chapter', game: 'percent', comic: 'volume' }

watch(() => [props.open, props.item], ([open, item]) => {
  if (!open || !item) return
  error.value = ''
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
  // 动画自动回填总集数（Bangumi 的 total_episodes 单位与 ep 一致；
  // 漫画按卷、小说按章，话数不能混用，保持手填）。失败静默，不影响手动填写。
  if (item.type === 2) {
    bangumiApi.get(item.bangumi_id).then(({ data }) => {
      if (props.item === item && data.total_episodes && form.value.total == null) {
        form.value.total = data.total_episodes
      }
    }).catch(() => {})
  }
}, { immediate: true })

const coverSrc = computed(() => (form.value.cover_url ? bangumiApi.imageUrl(form.value.cover_url) : ''))

async function confirmCreate() {
  creating.value = true
  error.value = ''
  try {
    const { data } = await worksApi.create(emptyToNull(form.value, ['total']))
    emit('created', data)
  } catch (e) {
    error.value = e.response?.data?.detail || '创建失败'
  } finally {
    creating.value = false
  }
}

function close() {
  if (creating.value) return
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <Transition name="bmodal">
      <div v-if="open" class="bmodal-overlay" @click.self="close">
        <div class="bmodal-card" role="dialog" aria-modal="true" aria-label="确认作品信息" @click.stop>
          <div class="bmodal-hd">
            <h2>确认作品信息</h2>
            <button class="bmodal-close" aria-label="关闭" @click="close">
              <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
                <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"/>
              </svg>
            </button>
          </div>

          <div class="bmodal-body">
            <div class="bmodal-fields">
              <label class="bf-label">
                <span>标题</span>
                <input v-model="form.title" placeholder="作品名称" />
              </label>
              <div class="bf-row">
                <label class="bf-label bf-sm">
                  <span>分类</span>
                  <select v-model="form.category">
                    <option value="anime">番剧</option>
                    <option value="novel">小说</option>
                    <option value="comic">漫画</option>
                    <option value="game">游戏</option>
                  </select>
                </label>
                <label class="bf-label bf-sm">
                  <span>子分类</span>
                  <input v-model="form.sub_category" placeholder="如：单机、欧美剧" />
                </label>
              </div>
              <div class="bf-row" v-if="form.category !== 'game'">
                <label class="bf-label bf-xs">
                  <span>总量</span>
                  <input v-model.number="form.total" type="number" min="0" placeholder="0" />
                </label>
              </div>
              <label class="bf-label" v-if="form.cover_url">
                <span>封面</span>
                <div class="cover-preview">
                  <img :src="coverSrc" alt="" class="cover-preview-img" />
                  <span class="cover-preview-txt">已通过本地图床代理获取</span>
                </div>
              </label>
              <label class="bf-label">
                <span>简介</span>
                <textarea v-model="form.summary" rows="3" placeholder="作品简介..." />
              </label>
            </div>
          </div>

          <p v-if="error" class="bmodal-err">{{ error }}</p>

          <div class="bmodal-ft">
            <button class="bmodal-cancel" @click="close">取消</button>
            <button class="bmodal-save" @click="confirmCreate" :disabled="creating">
              {{ creating ? '创建中...' : '添加到收藏' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.bmodal-overlay {
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
.bmodal-card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 520px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}
.bmodal-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 0;
}
.bmodal-hd h2 { font-size: var(--fs-xl); font-weight: 800; }
.bmodal-close {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--radius-full);
  color: var(--text-tertiary);
  transition: all 0.15s;
}
.bmodal-close:hover { background: var(--bg-surface-hover); color: var(--text-primary); }
.bmodal-body { padding: 16px 24px 4px; }
.bmodal-fields { display: flex; flex-direction: column; gap: 10px; }
.bf-label { display: flex; flex-direction: column; gap: 4px; }
.bf-label span { font-size: var(--fs-xs); font-weight: 600; color: var(--text-tertiary); }
.bf-label input, .bf-label select, .bf-label textarea {
  padding: 8px 12px;
  font-size: var(--fs-sm);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--bg-primary);
}
.bf-label input:focus, .bf-label select:focus, .bf-label textarea:focus {
  border-color: var(--text-tertiary);
  background: var(--bg-surface);
  outline: none;
}
.bf-row { display: flex; gap: 10px; }
.bf-sm { flex: 1; }
.bf-xs { width: 100px; flex-shrink: 0; }

.cover-preview { display: flex; align-items: center; gap: 10px; }
.cover-preview-img { width: 48px; height: 64px; border-radius: var(--radius-sm); object-fit: cover; background: var(--bg-input); }
.cover-preview-txt { font-size: 11px; color: var(--text-tertiary); flex: 1; }

.bmodal-err { color: var(--c-anime); font-size: var(--fs-sm); padding: 0 24px 8px; }
.bmodal-ft {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px 24px 24px;
}
.bmodal-cancel {
  height: 36px;
  padding: 0 20px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-tertiary);
  transition: all 0.15s;
}
.bmodal-cancel:hover { color: var(--text-primary); background: var(--bg-surface-hover); }
.bmodal-save {
  height: 36px;
  padding: 0 24px;
  border-radius: var(--radius-md);
  background: var(--primary);
  color: white;
  font-size: var(--fs-sm);
  font-weight: 700;
  transition: all 0.15s;
}
.bmodal-save:hover { background: var(--primary-hover); }
.bmodal-save:disabled { opacity: 0.5; }

.bmodal-enter-active, .bmodal-leave-active { transition: opacity 0.2s ease; }
.bmodal-enter-active .bmodal-card, .bmodal-leave-active .bmodal-card { transition: transform 0.2s cubic-bezier(.2,0,0,1); }
.bmodal-enter-from, .bmodal-leave-to { opacity: 0; }
.bmodal-enter-from .bmodal-card { transform: scale(0.95) translateY(10px); }
.bmodal-leave-to .bmodal-card { transform: scale(0.95) translateY(10px); }

/* 触屏：操作控件达到 44px 触控目标（Q3 决策） */
@media (pointer: coarse) {
  .bmodal-cancel, .bmodal-save { min-height: 44px; }
  .bmodal-close { width: 44px; height: 44px; }
}
</style>
