<script setup>
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'

// 模态底座：Teleport 到 body；Esc / 点击遮罩关闭、焦点圈定与还原；
// <768px 自动变底部抽屉。头部可用 #head 插槽整体替换（含关闭按钮）。
const props = defineProps({
  open: Boolean,
  title: { type: String, default: '' },
  size: { type: String, default: '' }, // '' | 'sm' | 'lg'
  accent: { type: String, default: '' }, // 顶部品类色条（CSS 颜色值），空则不渲染
})
const emit = defineEmits(['close'])

const panel = ref(null)
let lastFocused = null
let initialized = false

function focusables() {
  if (!panel.value) return []
  return Array.from(
    panel.value.querySelectorAll(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
  ).filter(el => el.offsetWidth > 0 || el.offsetHeight > 0 || el === document.activeElement)
}

function onKeydown(e) {
  if (e.key === 'Escape') {
    e.stopPropagation()
    emit('close')
    return
  }
  if (e.key !== 'Tab') return
  const list = focusables()
  if (!list.length) return
  const first = list[0]
  const last = list[list.length - 1]
  if (e.shiftKey && document.activeElement === first) {
    e.preventDefault()
    last.focus()
  } else if (!e.shiftKey && document.activeElement === last) {
    e.preventDefault()
    first.focus()
  }
}

function afterOpen() {
  document.addEventListener('keydown', onKeydown, true)
  document.body.style.overflow = 'hidden'
  nextTick(() => {
    const target = panel.value?.querySelector('[data-autofocus]') || panel.value
    target?.focus?.()
  })
}

function afterClose() {
  document.removeEventListener('keydown', onKeydown, true)
  document.body.style.overflow = ''
  if (lastFocused?.focus) lastFocused.focus()
  lastFocused = null
}

watch(() => props.open, v => {
  if (v) {
    if (!initialized) {
      initialized = true
      lastFocused = document.activeElement
    }
    afterOpen()
  } else if (initialized) {
    initialized = false
    afterClose()
  }
})

onBeforeUnmount(() => {
  if (initialized) {
    initialized = false
    afterClose()
  }
})
</script>

<template>
  <Teleport to="body">
    <Transition name="bmodal">
      <div v-if="open" class="scrim" @click.self="emit('close')">
        <div
          ref="panel"
          class="modal"
          :class="{ sm: size === 'sm', lg: size === 'lg' }"
          role="dialog"
          aria-modal="true"
          :aria-label="title || undefined"
          tabindex="-1"
        >
          <div v-if="accent" class="modal-accent" :style="{ background: accent }" aria-hidden="true" />
          <div v-if="$slots.head || title" class="modal-head">
            <slot name="head">
              <h2>{{ title }}</h2>
              <button class="modal-x" aria-label="关闭" @click="emit('close')">
                <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
                  <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"/>
                </svg>
              </button>
            </slot>
          </div>
          <div class="modal-body">
            <slot />
          </div>
          <div v-if="$slots.foot" class="modal-foot">
            <slot name="foot" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.scrim {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(10, 8, 6, 0.5);
  backdrop-filter: blur(3px);
  -webkit-backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
  overflow-y: auto;
}
.modal {
  width: min(640px, 100%);
  max-height: min(88vh, 900px);
  display: flex;
  flex-direction: column;
  background: var(--bg-elevated);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  position: relative;
}
.modal.sm { width: min(440px, 100%); }
.modal.lg { width: min(780px, 100%); }
.modal-accent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  z-index: 1;
}
.modal:focus { outline: none; }
.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
}
.modal-head h2 { font-size: var(--fs-lg); }
.modal-x {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  flex: none;
}
.modal-x:hover { background: var(--bg-surface-hover); color: var(--text-primary); }
.modal-body { padding: 20px; overflow-y: auto; }
.modal-foot {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 20px;
  border-top: 1px solid var(--color-border);
  flex-wrap: wrap;
}

@media (max-width: 767px) {
  .scrim { align-items: flex-end; padding: 0; }
  .modal {
    width: 100%;
    max-height: 92vh;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  }
  .modal-foot { padding-bottom: calc(12px + env(safe-area-inset-bottom)); }
}

/* 过渡：淡入 + 上浮；移动端从底部滑入 */
.bmodal-enter-active, .bmodal-leave-active { transition: opacity 0.18s ease; }
.bmodal-enter-active .modal, .bmodal-leave-active .modal { transition: transform 0.22s cubic-bezier(0.2, 0.8, 0.2, 1); }
.bmodal-enter-from, .bmodal-leave-to { opacity: 0; }
.bmodal-enter-from .modal, .bmodal-leave-to .modal { transform: translateY(24px) scale(0.98); }
@media (max-width: 767px) {
  .bmodal-enter-from .modal, .bmodal-leave-to .modal { transform: translateY(60px); }
}
@media (prefers-reduced-motion: reduce) {
  .bmodal-enter-active, .bmodal-leave-active,
  .bmodal-enter-active .modal, .bmodal-leave-active .modal { transition: none; }
}
</style>
