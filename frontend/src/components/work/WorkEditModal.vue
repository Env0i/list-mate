<script setup>
import { worksApi } from '../../api/client'
import { STATUS_LABELS } from '../../constants/work'
import PlatformSelector from '../work/PlatformSelector.vue'
import BaseModal from '../common/BaseModal.vue'

// 编辑作品模态（收藏规格单）：四段表单按品类联动；表单对象由父级持有，保存时 emit('save')
defineProps({
  open: { type: Boolean, default: false },
  work: { type: Object, default: null },
  form: { type: Object, required: true },
  saving: { type: Boolean, default: false },
  allTags: { type: Array, default: () => [] },
  selectedTagIds: { type: Array, default: () => [] },
  tagLoading: { type: Boolean, default: false },
})
const emit = defineEmits(['close', 'save', 'toggle-tag'])

function toggleTag(tid) {
  emit('toggle-tag', tid)
}
</script>

<template>
  <BaseModal
    :open="open"
    size="lg"
    :accent="`var(--c-${work?.category || 'anime'})`"
    @close="emit('close')"
  >
    <template #head>
      <div class="modal-hd-left" :style="{ '--modal-accent': `var(--c-${work?.category || 'anime'})` }">
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
      <button class="modal-close" aria-label="关闭" @click="emit('close')">
        <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
          <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"/>
        </svg>
      </button>
    </template>

    <div class="modal-grid">
      <!-- 左列 -->
      <div class="modal-col">
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
                  <option v-for="(label, key) in STATUS_LABELS[work?.category]" :key="key" :value="key">{{ label }}</option>
                </select>
              </label>
              <label class="mf-label mf-xs" v-if="work?.category !== 'game'">
                <span>进度</span>
                <input v-model.number="form.progress_value" type="number" min="0" placeholder="0" />
              </label>
            </div>
          </div>
        </div>

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

      <!-- 右列 -->
      <div class="modal-col">
        <div class="modal-section">
          <h3 class="modal-section-title">标签</h3>
          <div v-if="tagLoading" class="tag-loading">加载标签中...</div>
          <div v-else-if="allTags.length" class="tag-chips">
            <button
              v-for="t in allTags"
              :key="t.id"
              type="button"
              class="tchip"
              :class="{ on: selectedTagIds.includes(t.id) }"
              :style="selectedTagIds.includes(t.id) ? { background: t.color, color: '#fff', borderColor: t.color } : { color: t.color, borderColor: t.color + '40' }"
              @click="toggleTag(t.id)"
            >{{ t.name }}</button>
          </div>
          <p v-else class="tag-none">暂无标签，前往 <router-link to="/tags" class="tag-link">标签管理</router-link> 创建</p>
        </div>

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

    <template #foot>
      <button class="modal-cancel" @click="emit('close')">取消</button>
      <button class="modal-save" @click="emit('save')" :disabled="saving">
        {{ saving ? '保存中...' : '保存修改' }}
      </button>
    </template>
  </BaseModal>
</template>

<style scoped>
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
.modal-col { display: flex; flex-direction: column; gap: 20px; }

.modal-section-title {
  font-size: 10px;
  font-weight: 700;
  color: var(--modal-accent, var(--text-tertiary));
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
.mf-label input:focus, .mf-label select:focus, .mf-label textarea:focus {
  border-color: var(--text-tertiary);
  background: var(--bg-surface);
  outline: none;
}
.mf-row { display: flex; gap: 10px; }
.mf-sm { flex: 1; }
.mf-xs { width: 100px; flex-shrink: 0; }

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
.free-toggle input:checked { background: var(--c-game); }
.free-toggle input:checked::after { transform: translateX(12px); }

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

.modal-cancel, .modal-save {
  height: 36px;
  padding: 0 20px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.modal-cancel {
  color: var(--text-secondary);
  background: var(--bg-primary);
  border: 1px solid var(--color-border);
}
.modal-cancel:hover {
  background: var(--bg-surface-hover);
  border-color: var(--text-tertiary);
  color: var(--text-primary);
}
.modal-save {
  padding: 0 28px;
  background: var(--primary);
  color: white;
  font-weight: 700;
  letter-spacing: 0.3px;
  box-shadow: 0 2px 8px rgba(255, 107, 53, 0.25);
}
.modal-save:hover:not(:disabled) {
  background: var(--primary-hover);
  box-shadow: 0 3px 12px rgba(255, 107, 53, 0.35);
}
.modal-save:disabled { opacity: 0.5; box-shadow: none; }

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
.tchip.on { font-weight: 700; }

@media (max-width: 480px) {
  .modal-cancel, .modal-save { flex: 1; }
}
</style>
