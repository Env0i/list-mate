// 主题状态管理：localStorage 持久化，未设置时跟随系统 prefers-color-scheme。
// 切换通过 documentElement[data-theme] 驱动 style.css 的变量覆盖。
const KEY = 'zace-theme'

export function resolveInitialTheme() {
  const stored = localStorage.getItem(KEY)
  if (stored === 'dark' || stored === 'light') return stored
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function applyTheme(theme) {
  document.documentElement.dataset.theme = theme
}

export function initTheme() {
  applyTheme(resolveInitialTheme())
}

export function currentTheme() {
  return document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light'
}

export function setTheme(theme) {
  localStorage.setItem(KEY, theme)
  applyTheme(theme)
}

export function toggleTheme() {
  const next = currentTheme() === 'dark' ? 'light' : 'dark'
  setTheme(next)
  return next
}
