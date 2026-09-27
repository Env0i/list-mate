// 主题状态管理：三态模式（跟随系统 / 白天 / 黑夜），localStorage 持久化，默认白天。
// 切换通过 documentElement[data-theme] 驱动 style.css 的变量覆盖；
// "跟随系统"下监听系统偏好变化实时应用。
const KEY = 'zace-theme'
const VALID = ['light', 'dark', 'system']
const media = window.matchMedia?.('(prefers-color-scheme: dark)')

function systemTheme() {
  return media?.matches ? 'dark' : 'light'
}

function storedMode() {
  const v = localStorage.getItem(KEY)
  return VALID.includes(v) ? v : null
}

// data-theme 的实际取值（system 展开为具体主题）
export function resolveTheme(mode) {
  const m = mode ?? storedMode() ?? 'light'
  return m === 'system' ? systemTheme() : m
}

export function getThemeMode() {
  return storedMode() ?? 'light'
}

export function applyTheme(mode) {
  document.documentElement.dataset.theme = resolveTheme(mode)
}

export function initTheme() {
  applyTheme(getThemeMode())
  // 跟随系统模式下，系统偏好变化实时生效
  media?.addEventListener?.('change', () => {
    if (getThemeMode() === 'system') applyTheme('system')
  })
}

export function setThemeMode(mode) {
  if (!VALID.includes(mode)) return
  localStorage.setItem(KEY, mode)
  applyTheme(mode)
}

// 桌面顶栏的快捷开关：在白天/黑夜间切换（显式选择，脱离"跟随系统"）
export function toggleTheme() {
  const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'
  setThemeMode(next)
  return next
}
