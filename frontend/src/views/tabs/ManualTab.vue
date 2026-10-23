<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { worksApi } from '../../api/client'
import { showToast } from '../../utils/toast'
import { emptyToNull } from '../../utils/payload'
import { STATUS_LABELS } from '../../constants/work'
import PlatformSelector from '../../components/work/PlatformSelector.vue'

// 手动录入 Tab：原独立手动添加页的表单，页头由添加页壳承担
const router = useRouter()
const form = ref({
  title: '',
  category: 'anime',
  sub_category: '',
  progress_unit: 'ep',
  status: '',
  total: null,
  summary: '',
  start_date: '',
  finish_date: '',
  platform: '',
  priority: null,
  external_links: '',
  purchase_platform: '',
  purchase_date: '',
  purchase_price: null,
  playtime_hours: null,
  replay_count: null,
  is_free: false,
  rating: null,
  review: '',
})

const saving = ref(false)
const error = ref('')

const categories = [
  { key: 'anime', label: '番剧', unit: 'ep' },
  { key: 'novel', label: '小说', unit: 'chapter' },
  { key: 'comic', label: '漫画', unit: 'volume' },
  { key: 'game', label: '游戏', unit: 'percent' },
]

const statusLabels = STATUS_LABELS

const unitLabels = { ep: '集', chapter: '章', volume: '卷', percent: '%' }

watch(() => form.value.category, (cat) => {
  const c = categories.find(c => c.key === cat)
  if (c) form.value.progress_unit = c.unit
})

async function submit() {
  if (!form.value.title.trim()) {
    error.value = '请输入作品名称'
    return
  }
  saving.value = true
  error.value = ''
  try {
    const payload = emptyToNull(form.value, [
      'status', 'total', 'priority', 'purchase_price',
      'playtime_hours', 'replay_count', 'rating',
      'start_date', 'finish_date', 'purchase_date',
    ])
    const { data } = await worksApi.create(payload)
    showToast('作品已添加')
    router.push(`/works/${data.id}`)
  } catch (e) {
    error.value = e.response?.data?.detail || '创建失败'
    showToast('创建失败', 'error')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="add-card">
    <!-- Section 1: 基本信息 -->
    <div class="section">
      <h3 class="section-title">基本信息</h3>
      <div class="fields">
        <label class="field">
          <span>标题</span>
          <input v-model="form.title" placeholder="作品名称" />
        </label>
        <div class="f-row">
          <label class="field f-sm">
            <span>分类</span>
            <select v-model="form.category">
              <option v-for="c in categories" :key="c.key" :value="c.key">{{ c.label }}</option>
            </select>
          </label>
          <label class="field f-sm">
            <span>子分类</span>
            <input v-model="form.sub_category" placeholder="如：单机、欧美剧" />
          </label>
        </div>
        <div class="f-row" v-if="form.category !== 'game'">
          <label class="field f-xs">
            <span>总量（{{ unitLabels[form.progress_unit] || '' }}）</span>
            <input v-model.number="form.total" type="number" min="0" placeholder="0" />
          </label>
        </div>
        <label class="field">
          <span>状态</span>
          <div class="status-row">
            <button
              v-for="(label, key) in statusLabels[form.category]"
              :key="key"
              type="button"
              class="st-opt"
              :class="{ on: form.status === key }"
              :aria-pressed="form.status === key"
              @click="form.status = form.status === key ? '' : key"
            >
              {{ label }}
            </button>
          </div>
        </label>
        <label class="field">
          <span>简介</span>
          <textarea v-model="form.summary" rows="3" placeholder="作品简介..." />
        </label>
      </div>
    </div>

    <!-- Section 2: 追踪信息 -->
    <div class="section">
      <h3 class="section-title">追踪信息</h3>
      <div class="fields">
        <div class="f-row">
          <label class="field f-sm">
            <span>开始时间</span>
            <input v-model="form.start_date" type="date" />
          </label>
          <label class="field f-sm">
            <span>完成时间</span>
            <input v-model="form.finish_date" type="date" />
          </label>
        </div>
        <div class="f-row">
          <label class="field f-sm">
            <span>平台</span>
            <PlatformSelector :category="form.category" v-model="form.platform" />
          </label>
          <label class="field f-xs">
            <span>优先度 (0-5)</span>
            <input v-model.number="form.priority" type="number" min="0" max="5" placeholder="0-5" />
          </label>
        </div>
        <label class="field">
          <span>外部链接</span>
          <input v-model="form.external_links" placeholder='{"steam":"https://..."}' />
        </label>
      </div>
    </div>

    <!-- Section 3: 游戏专属 -->
    <div class="section" v-if="form.category === 'game'">
      <h3 class="section-title">游戏专属</h3>
      <div class="fields">
        <label class="field toggle-field">
          <span class="toggle-row">
            <span>免费获取</span>
            <input type="checkbox" v-model="form.is_free" class="toggle" />
          </span>
          <span class="toggle-hint">免费游戏或平台赠送，不记录价格</span>
        </label>

        <div class="f-row" v-if="!form.is_free">
          <label class="field f-sm">
            <span>购买价格</span>
            <input v-model.number="form.purchase_price" type="number" min="0" step="0.01" placeholder="0" />
          </label>
          <label class="field f-sm">
            <span>购买时间</span>
            <input v-model="form.purchase_date" type="date" />
          </label>
        </div>
        <div class="f-row">
          <label class="field f-sm">
            <span>游戏时长（小时）</span>
            <input v-model.number="form.playtime_hours" type="number" min="0" step="0.1" placeholder="0" />
          </label>
          <label class="field f-sm">
            <span>重刷次数</span>
            <input v-model.number="form.replay_count" type="number" min="0" placeholder="0" />
          </label>
        </div>
      </div>
    </div>

    <!-- Section 4: 评分评价 -->
    <div class="section">
      <h3 class="section-title">评分评价</h3>
      <div class="fields">
        <label class="field">
          <span>评分 {{ form.rating != null ? form.rating + '/10' : '—' }}</span>
          <input v-model.number="form.rating" type="range" min="0" max="10" class="rating-slider" />
        </label>
        <label class="field">
          <span>评价</span>
          <textarea v-model="form.review" rows="3" placeholder="写下你的评价..." />
        </label>
      </div>
    </div>

    <p v-if="error" class="err" role="alert">{{ error }}</p>

    <button class="save-btn" @click="submit" :disabled="saving">
      {{ saving ? '创建中...' : '添加到收藏' }}
    </button>
  </div>
</template>

<style scoped>
/* Card */
.add-card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: 28px;
  box-shadow:
    0 0 0 1px var(--frame-outer-line),
    0 0 0 2px rgba(255,255,255,0.5),
    var(--shadow-md);
}
@media (max-width: 767px) { .add-card { padding: 20px; } }

.section { margin-bottom: 24px; }
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

.fields { display: flex; flex-direction: column; gap: 10px; }
.field { display: flex; flex-direction: column; gap: 4px; }
.field span { font-size: var(--fs-xs); font-weight: 600; color: var(--text-tertiary); }
.field input, .field select, .field textarea {
  padding: 8px 12px;
  font-size: var(--fs-sm);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--bg-primary);
}
.field input:focus, .field select:focus, .field textarea:focus {
  border-color: var(--text-tertiary);
  background: var(--bg-surface);
  outline: none;
}
.f-row { display: flex; gap: 10px; }
.f-sm { flex: 1; }
.f-xs { width: 120px; flex-shrink: 0; }

/* Status inline */
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
.st-opt.on {
  background: var(--primary);
  color: white;
  border-color: transparent;
}

/* Rating */
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

/* Toggle */
.toggle-field { gap: 0; }
.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-secondary);
}
.toggle {
  width: 40px;
  height: 22px;
  appearance: none;
  border-radius: 11px;
  background: var(--color-border);
  cursor: pointer;
  position: relative;
  transition: background 0.2s;
}
.toggle::after {
  content: '';
  position: absolute;
  top: 2px; left: 2px;
  width: 18px; height: 18px;
  border-radius: 50%;
  background: white;
  transition: transform 0.2s;
}
.toggle:checked { background: var(--primary); }
.toggle:checked::after { transform: translateX(18px); }
.toggle-hint { font-size: 11px; color: var(--text-tertiary); margin-top: 2px; }

.err { color: var(--c-anime); font-size: var(--fs-sm); margin-bottom: 12px; }

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

/* 触屏：状态选项与开关达到 44px 触控目标（Q3 决策） */
@media (pointer: coarse) {
  .st-opt, .save-btn { min-height: 44px; }
  .toggle { width: 52px; height: 30px; border-radius: 15px; }
  .toggle::after { width: 26px; height: 26px; top: 2px; left: 2px; }
  .toggle:checked::after { transform: translateX(22px); }
}
</style>
