<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { getThemeMode, resolveTheme, setThemeMode } from '../../utils/theme'

defineProps({ floating: { type: Boolean, default: false } })

const mode = ref('light')
const resolved = ref('light')
const open = ref(false)
const wrap = ref(null)

const options = [
  { key: 'system', label: '跟随系统' },
  { key: 'light', label: '白天' },
  { key: 'dark', label: '黑夜' },
]

function sync() {
  mode.value = getThemeMode()
  resolved.value = resolveTheme()
}

function pick(key) {
  setThemeMode(key)
  sync()
}

function onDocClick(e) {
  if (open.value && wrap.value && !wrap.value.contains(e.target)) open.value = false
}

onMounted(() => {
  sync()
  document.addEventListener('click', onDocClick)
})
onBeforeUnmount(() => document.removeEventListener('click', onDocClick))
</script>

<template>
  <div ref="wrap" class="tt-wrap" :class="{ floating }">
    <!-- 系统模式用半填充圆表达 -->
    <button class="tt-btn" title="主题" @click.stop="open = !open">
      <svg v-if="mode === 'system'" viewBox="0 0 20 20" width="16" height="16">
        <defs><clipPath id="tt-half"><rect x="0" y="0" width="10" height="20"/></clipPath></defs>
        <circle cx="10" cy="10" r="7.5" fill="currentColor" opacity="0.25"/>
        <circle cx="10" cy="10" r="7.5" fill="currentColor" clip-path="url(#tt-half)"/>
      </svg>
      <svg v-else-if="resolved === 'dark'" viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
        <path d="M17.3 12.2A7.2 7.2 0 0 1 7.8 2.7a.6.6 0 0 0-.75-.75 8.3 8.3 0 1 0 11 11 .6.6 0 0 0-.75-.75z"/>
      </svg>
      <svg v-else viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" width="16" height="16">
        <circle cx="10" cy="10" r="3.6"/>
        <path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.3 4.3l1.4 1.4M14.3 14.3l1.4 1.4M15.7 4.3l-1.4 1.4M5.7 14.3l-1.4 1.4"/>
      </svg>
    </button>

    <div v-if="open" class="tt-pop">
      <button
        v-for="o in options"
        :key="o.key"
        class="tt-opt"
        :class="{ on: mode === o.key }"
        @click.stop="pick(o.key); open = false"
      >
        <span>{{ o.label }}</span>
        <span v-if="mode === o.key" class="tt-check">✓</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.tt-wrap { position: relative; }
.tt-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-md);
  color: var(--text-tertiary);
  transition: all 0.15s;
}
.tt-btn:hover { color: var(--text-secondary); background: var(--bg-surface-hover); }

/* 弹出选项层 */
.tt-pop {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  z-index: 96;
  min-width: 132px;
  padding: 4px;
  background: var(--bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
}
.tt-opt {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-sm);
  color: var(--text-primary);
  transition: background 0.12s;
}
.tt-opt:hover { background: var(--bg-surface-hover); }
.tt-opt.on { color: var(--primary); font-weight: 700; }
.tt-check { font-size: var(--fs-xs); }

/* 移动端：固定悬浮在页面右上角（桌面由 TopBar 承载，隐藏悬浮体） */
.tt-wrap.floating {
  position: fixed;
  top: 8px;
  right: 10px;
  z-index: 95;
}
.tt-wrap.floating .tt-btn {
  background: var(--bg-surface);
  box-shadow: var(--shadow-md), 0 0 0 1px var(--frame-outer-line);
}
.tt-wrap.floating .tt-btn:hover { background: var(--bg-surface-hover); }
@media (min-width: 768px) { .tt-wrap.floating { display: none; } }
</style>
