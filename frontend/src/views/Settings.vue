<script setup>
import { ref, onMounted } from 'vue'
import { exportApi } from '../api/client'
import { showToast } from '../utils/toast'
import { getThemeMode, resolveTheme, setThemeMode } from '../utils/theme'

// S5 新增设置页：数据管理（自统计页迁入）+ 外观主题 + 关于
const restoreInput = ref(null)
const restoring = ref(false)

function pickRestore() { restoreInput.value?.click() }

async function onRestoreFile(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  const ok = confirm(`将用「${file.name}」覆盖当前全部数据。
覆盖前当前数据会先自动备份到服务器 backups/ 目录。
确定还原？`)
  if (!ok) return
  restoring.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const { data } = await exportApi.restore(fd)
    showToast(data.message || '还原成功，请重启服务后刷新', 'success')
  } catch (err) {
    showToast(err.response?.data?.detail || '还原失败', 'error')
  } finally {
    restoring.value = false
  }
}

const themeOptions = [
  { key: 'system', label: '跟随系统' },
  { key: 'light', label: '白天' },
  { key: 'dark', label: '黑夜' },
]
const mode = ref('light')
const resolved = ref('light')

function syncTheme() {
  mode.value = getThemeMode()
  resolved.value = resolveTheme()
}

function pickTheme(key) {
  setThemeMode(key)
  syncTheme()
}

onMounted(syncTheme)

const version = typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : ''
</script>

<template>
  <div class="page">
    <div class="page-inner">
      <h1 class="page-title">设置</h1>
      <p class="subtitle">外观、数据与关于</p>

      <section class="set-card" aria-labelledby="set-appearance">
        <h2 id="set-appearance" class="set-h">外观</h2>
        <div class="theme-row" role="radiogroup" aria-label="主题">
          <button
            v-for="o in themeOptions"
            :key="o.key"
            type="button"
            role="radio"
            :aria-checked="mode === o.key"
            class="theme-opt"
            :class="{ on: mode === o.key }"
            @click="pickTheme(o.key)"
          >
            <svg v-if="o.key === 'system'" viewBox="0 0 20 20" width="16" height="16" aria-hidden="true">
              <defs><clipPath :id="'set-half'"><rect x="0" y="0" width="10" height="20"/></clipPath></defs>
              <circle cx="10" cy="10" r="7.5" fill="currentColor" opacity="0.25"/>
              <circle cx="10" cy="10" r="7.5" fill="currentColor" :clip-path="`url(#set-half)`"/>
            </svg>
            <svg v-else-if="o.key === 'dark'" viewBox="0 0 20 20" fill="currentColor" width="16" height="16" aria-hidden="true">
              <path d="M17.3 12.2A7.2 7.2 0 0 1 7.8 2.7a.6.6 0 0 0-.75-.75 8.3 8.3 0 1 0 11 11 .6.6 0 0 0-.75-.75z"/>
            </svg>
            <svg v-else viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" width="16" height="16" aria-hidden="true">
              <circle cx="10" cy="10" r="3.6"/>
              <path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.3 4.3l1.4 1.4M14.3 14.3l1.4 1.4M15.7 4.3l-1.4 1.4M5.7 14.3l-1.4 1.4"/>
            </svg>
            <span>{{ o.label }}</span>
          </button>
        </div>
        <p class="set-hint">当前生效：{{ resolved === 'dark' ? '黑夜' : '白天' }}</p>
      </section>

      <section class="set-card" aria-labelledby="set-data">
        <h2 id="set-data" class="set-h">数据管理</h2>
        <p class="set-desc">导出收藏为 JSON / CSV，或做数据库完整备份；备份含时间线、附件与封面，可直接还原。</p>
        <div class="data-row">
          <a :href="exportApi.jsonUrl()" class="data-btn" download>
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" aria-hidden="true">
              <path d="M10.75 2.75a.75.75 0 00-1.5 0v8.614L6.295 8.235a.75.75 0 10-1.09 1.03l4.25 4.5a.75.75 0 001.09 0l4.25-4.5a.75.75 0 00-1.09-1.03l-2.955 3.129V2.75z"/>
              <path d="M3.5 12.75a.75.75 0 00-1.5 0v2.5A2.75 2.75 0 004.75 18h10.5A2.75 2.75 0 0018 15.25v-2.5a.75.75 0 00-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5z"/>
            </svg>
            导出 JSON
          </a>
          <a :href="exportApi.csvUrl()" class="data-btn" download>
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" aria-hidden="true">
              <path d="M10.75 2.75a.75.75 0 00-1.5 0v8.614L6.295 8.235a.75.75 0 10-1.09 1.03l4.25 4.5a.75.75 0 001.09 0l4.25-4.5a.75.75 0 00-1.09-1.03l-2.955 3.129V2.75z"/>
              <path d="M3.5 12.75a.75.75 0 00-1.5 0v2.5A2.75 2.75 0 004.75 18h10.5A2.75 2.75 0 0018 15.25v-2.5a.75.75 0 00-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5z"/>
            </svg>
            导出 CSV
          </a>
          <a :href="exportApi.backupUrl()" class="data-btn" download title="下载数据库完整备份（含时间线/附件/封面，可直接还原）">
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" aria-hidden="true">
              <path d="M10 2a4 4 0 00-4 4v4.5a.75.75 0 001.5 0V6a2.5 2.5 0 015 0v4.5a.75.75 0 001.5 0V6a4 4 0 00-4-4z"/>
              <path d="M5.5 9.25a.75.75 0 011.5 0v2.25a3 3 0 006 0V9.25a.75.75 0 011.5 0v2.25a4.5 4.5 0 01-9 0V9.25z"/>
              <path d="M10 13.25a.75.75 0 01.75.75v2.19l.97-.97a.75.75 0 111.06 1.06l-2.25 2.25a.75.75 0 01-1.06 0l-2.25-2.25a.75.75 0 111.06-1.06l.97.97V14a.75.75 0 01.75-.75z"/>
            </svg>
            完整备份
          </a>
          <input
            ref="restoreInput"
            type="file"
            accept=".db,application/octet-stream"
            class="restore-input"
            @change="onRestoreFile"
          />
          <button
            type="button"
            class="data-btn"
            :disabled="restoring"
            title="从 .db 备份还原（覆盖当前数据，当前数据会先自动备份）"
            @click="pickRestore"
          >
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" aria-hidden="true">
              <path fill-rule="evenodd" d="M3.5 4.75A2.25 2.25 0 015.75 2.5h5.5a.75.75 0 01.53.22l4 4a.75.75 0 01.22.53v8.5a2.25 2.25 0 01-2.25 2.25h-8.5A2.25 2.25 0 013.5 15.75v-11zm6.75 3.75a.75.75 0 00-1.5 0v3.69l-.97-.97a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.06 0l2.25-2.25a.75.75 0 00-1.06-1.06l-.97.97V8.5z" clip-rule="evenodd"/>
            </svg>
            {{ restoring ? '还原中...' : '从备份还原' }}
          </button>
        </div>
      </section>

      <section class="set-card" aria-labelledby="set-about">
        <h2 id="set-about" class="set-h">关于</h2>
        <dl class="about-list">
          <div class="about-row">
            <dt>版本</dt>
            <dd class="mono">v{{ version || '—' }}</dd>
          </div>
          <div class="about-row">
            <dt>数据来源</dt>
            <dd>Bangumi API（只读同步，不会向远端写入你的任何数据）</dd>
          </div>
          <div class="about-row">
            <dt>数据存放</dt>
            <dd>全部收藏与记录保存在本地服务，不依赖云端</dd>
          </div>
        </dl>
      </section>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 20px 16px; }
@media (max-width: 767px) { .page { padding-top: 0; } }
@media (min-width: 768px) { .page { padding: 24px 32px; } }
.page-inner { max-width: 640px; margin: 0 auto; }

.page-title { font-size: var(--fs-2xl); font-weight: 800; margin-bottom: 4px; }
.subtitle { font-size: var(--fs-sm); color: var(--text-tertiary); margin-bottom: 24px; }

.set-card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: 22px 24px;
  margin-bottom: 16px;
  box-shadow:
    0 0 0 1px var(--frame-outer-line),
    0 0 0 2px rgba(255,255,255,0.5),
    var(--shadow-md);
}
@media (max-width: 767px) { .set-card { padding: 18px 16px; } }

.set-h {
  font-size: var(--fs-xs);
  font-weight: 700;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 14px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--color-border);
}

/* 主题三选 */
.theme-row { display: flex; gap: 8px; flex-wrap: wrap; }
.theme-opt {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  height: 36px;
  padding: 0 16px;
  border-radius: var(--radius-full);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-tertiary);
  background: var(--bg-primary);
  border: 1px solid var(--color-border);
  transition: all 0.15s;
}
.theme-opt:hover { border-color: var(--text-tertiary); }
.theme-opt.on {
  background: var(--primary);
  color: white;
  border-color: transparent;
}
.set-hint { margin-top: 10px; font-size: var(--fs-xs); color: var(--text-tertiary); }

/* 数据管理 */
.set-desc { font-size: var(--fs-sm); color: var(--text-secondary); margin-bottom: 14px; line-height: 1.6; }
.data-row { display: flex; gap: 8px; flex-wrap: wrap; }
.data-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 36px;
  padding: 0 14px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-primary);
  border: 1px solid var(--color-border);
  transition: all 0.15s;
}
.data-btn:hover {
  color: var(--text-primary);
  border-color: var(--text-tertiary);
  box-shadow: var(--shadow-sm);
}
.data-btn:disabled { opacity: 0.5; cursor: default; }
.restore-input { display: none; }

/* 关于 */
.about-list { display: flex; flex-direction: column; gap: 8px; }
.about-row { display: flex; gap: 16px; }
.about-row dt {
  flex: none;
  width: 72px;
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-tertiary);
}
.about-row dd { font-size: var(--fs-sm); color: var(--text-primary); line-height: 1.6; }
.mono { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }

/* 触屏 44px（Q3 决策） */
@media (pointer: coarse) {
  .theme-opt, .data-btn { min-height: 44px; }
}
</style>
