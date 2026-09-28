<script setup>
import { computed, ref } from 'vue'
import { STATUS_LABELS, STATUS_COLORS } from '../../constants/work'
import { showToast } from '../../utils/toast'
import ProgressBar from './ProgressBar.vue'
import BaseModal from '../common/BaseModal.vue'

// 游戏配置共用表单（交接 §1：新建与详情共用）。
// gp 就地绑定修改；脏状态由父级深度侦听；submit 校验通过后 emit('save')。
const props = defineProps({
  gp: { type: Object, required: true },
  isNew: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  dirty: { type: Boolean, default: false },
  cancelTo: { type: String, required: true },
})
const emit = defineEmits(['save'])

const statusOptions = Object.entries(STATUS_LABELS.game).map(([key, label]) => ({ key, label }))

const progressTypes = [
  { key: 'none', label: '不计进度', desc: '一次性剧情，只记状态' },
  { key: 'count', label: '通关次数', desc: '以撒、黑帝斯这类反复刷' },
  { key: 'percent', label: '完成百分比', desc: '整合包、收集度' },
]

const ptype = computed(() => props.gp.progress_type || 'none')

let typeTouched = false
function guessType(n) {
  return /二刷|周目|通关次数/.test(n) ? 'count' : /整合包|模组|mod/i.test(n) ? 'percent' : 'none'
}
function onNameInput() {
  if (props.isNew && !typeTouched) {
    props.gp.progress_type = guessType(props.gp.name || '')
    if (ptype.value === 'none') props.gp.progress_value = null
    else if (props.gp.progress_value == null) props.gp.progress_value = 0
  }
}
function setProgressType(pt) {
  typeTouched = true
  props.gp.progress_type = pt
  if (pt === 'none') props.gp.progress_value = null
  else if (props.gp.progress_value == null) props.gp.progress_value = 0
}

// 进度数值：本地修改（保存时统一提交）；percent 到 100 本地盖「通关」章（后端保存时同样兜底）
function setVal(v) {
  const max = ptype.value === 'percent' ? 100 : 9999
  props.gp.progress_value = Math.max(0, Math.min(max, Math.round(v || 0)))
  if (ptype.value === 'percent' && props.gp.progress_value === 100 && props.gp.status !== 'completed') {
    props.gp.status = 'completed'
  }
}
const decVal = () => setVal((props.gp.progress_value ?? 0) - (ptype.value === 'percent' ? 5 : 1))
const incVal = () => setVal((props.gp.progress_value ?? 0) + (ptype.value === 'percent' ? 5 : 1))
const onValInput = (e) => setVal(e.target.value === '' ? 0 : Number(e.target.value))

// 模组：chips + 粘贴批量添加 + 移除撤销（保存前的本地状态回滚）
const modsList = computed(() => {
  if (!props.gp.mods_list) return []
  return props.gp.mods_list.split('\n').filter(m => m.trim())
})
const showModModal = ref(false)
const modInputText = ref('')
const modCount = computed(() => modInputText.value.split('\n').map(s => s.trim()).filter(Boolean).length)
function openModModal() {
  modInputText.value = ''
  showModModal.value = true
}
function confirmMods() {
  const add = modInputText.value.split('\n').map(s => s.trim()).filter(s => s && !modsList.value.includes(s))
  props.gp.mods_list = [...modsList.value, ...add].join('\n')
  showModModal.value = false
}
function removeMod(mod) {
  props.gp.mods_list = modsList.value.filter(m => m !== mod).join('\n')
  // 撤销：把刚移除的模组放回末尾（保存前本地回滚）
  showToast(`已移除 ${mod}`, 'success', {
    action: {
      label: '撤销',
      handler: () => {
        props.gp.mods_list = [...modsList.value, mod].join('\n')
      },
    },
  })
}

// 校验：名称必填、完成时间不早于开始时间
const nameInvalid = ref(false)
const dateInvalid = ref(false)
function onSubmit() {
  nameInvalid.value = !props.gp.name?.trim()
  const s = props.gp.start_date
  const en = props.gp.finish_date
  dateInvalid.value = !!(s && en && en < s)
  if (nameInvalid.value || dateInvalid.value) return
  emit('save')
}
</script>

<template>
  <form novalidate @submit.prevent="onSubmit">
    <!-- 基础 -->
    <section class="panel">
      <div class="panel-title">基础</div>
      <div class="fields">
        <div class="field full" :class="{ invalid: nameInvalid }">
          <label for="gName">配置名称</label>
          <input id="gName" v-model="gp.name" maxlength="40" placeholder="如：二周目 · 智力法师 / 奇幻大修整合包" @input="onNameInput">
          <span class="err">给这套配置起个名字</span>
          <span class="hint">名称含「周目 / 二刷」会默认按次数计，含「整合包 / 模组」按百分比计</span>
        </div>
        <div class="field full">
          <span class="lbl" id="stL">状态</span>
          <div class="status-pick" role="radiogroup" aria-labelledby="stL">
            <button
              v-for="opt in statusOptions"
              :key="opt.key"
              type="button"
              role="radio"
              :aria-checked="gp.status === opt.key"
              :style="{ '--sc': STATUS_COLORS[opt.key] }"
              @click="gp.status = opt.key"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- 进度方式 -->
    <section class="panel sec">
      <div class="panel-title">进度方式</div>
      <div class="ptype" role="radiogroup" aria-label="进度方式">
        <label v-for="pt in progressTypes" :key="pt.key" :class="{ checked: ptype === pt.key }">
          <input type="radio" name="ptype" :value="pt.key" :checked="ptype === pt.key" @change="setProgressType(pt.key)">
          <span class="check" aria-hidden="true">✓</span>
          <b>{{ pt.label }}</b>
          <span class="desc">{{ pt.desc }}</span>
        </label>
      </div>
      <div v-if="ptype !== 'none'" class="val-box">
        <div class="stepper">
          <button type="button" aria-label="减少" @click="decVal">−</button>
          <input
            :value="gp.progress_value ?? 0"
            type="number"
            min="0"
            :max="ptype === 'percent' ? 100 : 9999"
            :aria-label="ptype === 'percent' ? '完成百分比' : '通关次数'"
            @change="onValInput"
          >
          <button type="button" aria-label="增加" @click="incVal">+</button>
        </div>
        <span class="unit mono">{{ ptype === 'percent' ? '%' : '次通关' }}</span>
        <ProgressBar
          v-if="ptype === 'percent'"
          size="lg"
          :current="gp.progress_value ?? 0"
          :total="100"
          category="game"
          label="完成百分比"
          class="val-exp"
        />
      </div>
      <p v-if="ptype === 'percent'" class="hint">到 100% 会自动盖「通关」章，可以再手动改回。</p>
      <p v-else-if="ptype === 'none'" class="hint">这套配置只记录状态，不显示数字进度。</p>
    </section>

    <!-- 游玩记录 -->
    <section class="panel sec">
      <div class="panel-title">游玩记录</div>
      <div class="fields">
        <div class="field" :class="{ invalid: dateInvalid }">
          <label for="gStart">开始时间</label>
          <input id="gStart" v-model="gp.start_date" type="date">
        </div>
        <div class="field" :class="{ invalid: dateInvalid }">
          <label for="gEnd">完成时间</label>
          <input id="gEnd" v-model="gp.finish_date" type="date">
          <span class="err">完成时间不能早于开始时间</span>
        </div>
        <div class="field">
          <label for="gHours">游玩时长（小时）</label>
          <input id="gHours" v-model="gp.playtime_hours" type="number" min="0" step="0.5" placeholder="0">
        </div>
        <div class="field">
          <label for="gSrc">来源</label>
          <input id="gSrc" v-model="gp.source" list="gpSrcList" placeholder="CurseForge / B 站 UP 主 / 自己整合">
          <datalist id="gpSrcList">
            <option value="本体"></option>
            <option value="CurseForge"></option>
            <option value="Nexus Mods"></option>
            <option value="B 站 UP 主"></option>
            <option value="自己整合"></option>
          </datalist>
        </div>
      </div>
    </section>

    <!-- 模组列表 -->
    <section class="panel sec">
      <div class="panel-title">模组列表 · <span class="mono">{{ modsList.length }}</span></div>
      <div class="mods">
        <template v-if="modsList.length">
          <span v-for="mod in modsList" :key="mod" class="mod">
            {{ mod }}
            <button type="button" :aria-label="`移除 ${mod}`" @click="removeMod(mod)">×</button>
          </span>
        </template>
        <p v-else class="hint">还没有模组。纯本体可以不填。</p>
      </div>
      <button type="button" class="mod-add" @click="openModModal">＋ 粘贴添加</button>
    </section>

    <!-- 评分评价 -->
    <section class="panel sec">
      <div class="panel-title">评分评价</div>
      <div class="fields">
        <div class="field full">
          <label for="gRate">评分 <b class="mono">{{ gp.rating ?? '未评' }}</b></label>
          <input id="gRate" v-model.number="gp.rating" type="range" min="0" max="10">
        </div>
        <div class="field full">
          <label for="gReview">评价</label>
          <textarea id="gReview" v-model="gp.review" rows="3" placeholder="写下你的评价..."></textarea>
        </div>
        <div class="field full">
          <label for="gNotes">笔记 / 心得</label>
          <textarea id="gNotes" v-model="gp.notes" rows="4" placeholder="配装、路线、踩过的坑…"></textarea>
        </div>
      </div>
    </section>

    <!-- 详情页附加区块（附件等，仅已有配置） -->
    <slot name="extra" />

    <!-- 常驻保存条 -->
    <div class="savebar">
      <span class="st" :class="{ dirty }" aria-live="polite">
        {{ isNew ? '尚未保存' : (dirty ? '有未保存的修改' : '所有修改已保存') }}
      </span>
      <router-link class="cancel-link" :to="cancelTo">{{ isNew ? '取消' : '返回作品' }}</router-link>
      <button class="save-btn" type="submit" :disabled="saving || (!isNew && !dirty)">
        {{ saving ? '保存中...' : (isNew ? '创建配置' : '保存') }}
      </button>
    </div>

    <!-- 粘贴批量添加模组 -->
    <BaseModal :open="showModModal" title="批量添加模组" size="sm" @close="showModModal = false">
      <div class="field full">
        <label for="modTxt">每行一个模组名，粘贴后自动拆分</label>
        <textarea id="modTxt" v-model="modInputText" rows="7" placeholder="例如：&#10;Seamless Co-op&#10;Item and Enemy Randomizer"></textarea>
        <span class="hint">将添加 {{ modCount }} 个</span>
      </div>
      <template #foot>
        <button class="cancel-link as-btn" type="button" @click="showModModal = false">取消</button>
        <button class="save-btn slim" type="button" :disabled="!modCount" @click="confirmMods">添加</button>
      </template>
    </BaseModal>
  </form>
</template>

<style scoped>
.panel {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm), inset 0 0 0 1px var(--color-border);
  padding: 20px;
}
.sec { margin-top: 16px; }
.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--fs-sm);
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 0.04em;
  margin-bottom: 16px;
}
.panel-title::after { content: ''; flex: 1; height: 1px; background: var(--line, rgba(0,0,0,0.09)); }
.mono { font-family: var(--font-mono); }

.fields { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
@media (max-width: 600px) { .fields { grid-template-columns: 1fr; } }
.field { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.field.full { grid-column: 1 / -1; }
.field > label, .field > .lbl { font-size: var(--fs-xs); font-weight: 600; color: var(--text-secondary); }
.field input, .field textarea {
  width: 100%;
  padding: 9px 14px;
  border-radius: var(--radius-md);
  background: var(--bg-input);
  border: 0;
  color: var(--text-primary);
  font: inherit;
  font-size: var(--fs-sm);
}
.field input:focus, .field textarea:focus { outline: none; background: var(--bg-surface); box-shadow: inset 0 0 0 1.5px var(--text-secondary); }
.field textarea { resize: vertical; line-height: 1.6; }
.field .hint { font-size: 11px; color: var(--text-tertiary); }
.field .err { font-size: 11px; color: var(--s-dropped); font-weight: 600; display: none; }
.field.invalid .err { display: block; }
.field.invalid input { box-shadow: inset 0 0 0 1.5px var(--s-dropped); }

/* 状态选择 */
.status-pick { display: flex; flex-wrap: wrap; gap: 8px; }
.status-pick button {
  height: 36px;
  padding: 0 14px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 700;
  color: var(--text-secondary);
  box-shadow: inset 0 0 0 1px var(--line, rgba(0,0,0,0.09));
  background: var(--bg-surface);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.status-pick button::before { content: ''; width: 8px; height: 8px; border-radius: 50%; background: var(--sc); }
.status-pick button:hover { background: var(--bg-surface-hover); color: var(--text-primary); }
.status-pick button[aria-checked='true'] {
  color: var(--text-primary);
  background: color-mix(in srgb, var(--sc) 12%, var(--bg-surface));
  box-shadow: inset 0 0 0 2px var(--sc);
}

/* 进度方式卡片单选 */
.ptype { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.ptype label {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  box-shadow: inset 0 0 0 1px var(--line, rgba(0,0,0,0.09));
  cursor: pointer;
  background: var(--bg-surface);
}
.ptype label:hover { background: var(--bg-surface-hover); }
.ptype input { position: absolute; opacity: 0; }
.ptype label.checked {
  box-shadow: inset 0 0 0 2px var(--c-game);
  background: color-mix(in srgb, var(--c-game) 8%, var(--bg-surface));
}
.ptype label:has(input:focus-visible) { outline: 2px solid var(--s-watching); outline-offset: 2px; }
.ptype .check {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: none;
  place-items: center;
  background: var(--c-game);
  color: #fff;
  font-size: 11px;
  font-weight: 800;
}
.ptype label.checked .check { display: grid; }
.ptype b { font-size: var(--fs-sm); padding-right: 20px; }
.ptype .desc { font-size: 11px; color: var(--text-secondary); }

/* 进度数值 */
.val-box { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; margin-top: 16px; }
.stepper { display: inline-flex; align-items: center; gap: 2px; background: var(--bg-input); border-radius: var(--radius-md); padding: 3px; }
.stepper button { width: 36px; height: 36px; border-radius: 8px; display: grid; place-items: center; font-size: 18px; font-weight: 600; }
.stepper button:hover:not(:disabled) { background: var(--bg-surface); }
.stepper input { width: 64px; height: 36px; text-align: center; border: 0; background: transparent; font: inherit; font-family: var(--font-mono); font-weight: 700; color: var(--text-primary); }
.stepper input:focus { outline: none; background: var(--bg-surface); border-radius: 8px; }
.unit { font-size: var(--fs-sm); color: var(--text-secondary); }
.val-exp { flex: 1; min-width: 160px; }

/* 模组 */
.mods { display: flex; flex-wrap: wrap; gap: 6px; }
.mod {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 30px;
  padding: 0 4px 0 10px;
  border-radius: var(--radius-sm);
  background: var(--bg-input);
  font-size: var(--fs-xs);
  font-weight: 600;
}
.mod button { width: 24px; height: 24px; display: grid; place-items: center; border-radius: 4px; color: var(--text-secondary); }
.mod button:hover { background: var(--bg-surface); color: var(--text-primary); }
.mod-add {
  margin-top: 12px;
  height: 32px;
  padding: 0 12px;
  border-radius: var(--radius-md);
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-surface);
  box-shadow: inset 0 0 0 1px var(--line, rgba(0,0,0,0.09));
}
.mod-add:hover { background: var(--bg-surface-hover); color: var(--text-primary); }

/* 保存条 */
.savebar {
  position: sticky;
  bottom: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 12px 0;
  margin-top: 16px;
  background: var(--bg-primary);
  border-top: 1px solid var(--line, rgba(0,0,0,0.09));
}
.savebar .st { margin-right: auto; font-size: var(--fs-xs); color: var(--text-secondary); }
.savebar .st.dirty { color: var(--text-primary); font-weight: 600; }
.cancel-link {
  display: inline-flex;
  align-items: center;
  height: 40px;
  padding: 0 14px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-secondary);
}
.cancel-link:hover { background: var(--bg-surface-hover); color: var(--text-primary); }
.cancel-link.as-btn { height: 40px; }
.save-btn {
  height: 40px;
  padding: 0 22px;
  border-radius: var(--radius-md);
  background: var(--primary);
  color: #fff;
  font-size: var(--fs-sm);
  font-weight: 700;
  transition: background 0.15s;
}
.save-btn:hover:not(:disabled) { background: var(--primary-hover); }
.save-btn:disabled { opacity: 0.5; cursor: default; }
.save-btn.slim { height: 40px; padding: 0 16px; }

@media (max-width: 767px) {
  .savebar { bottom: calc(var(--nav-height) + env(safe-area-inset-bottom)); }
  .ptype { grid-template-columns: 1fr; }
}

/* 触屏：操作控件达到 44px 触控目标（Q3 决策） */
@media (pointer: coarse) {
  .status-pick button, .stepper button, .stepper input, .mod-add, .cancel-link, .save-btn { min-height: 44px; }
}
@media (prefers-reduced-motion: reduce) {
  .ptype label, .status-pick button { transition: none; }
}
</style>
