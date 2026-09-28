import { reactive } from 'vue'

const toasts = reactive([])
let id = 0

// options: { action: { label, handler }, duration }；带 action 的 toast（如撤销）默认停留 5 秒
export function showToast(message, type = 'success', options = {}) {
  const opts = typeof options === 'number' ? { duration: options } : options
  const duration = opts.duration ?? (opts.action ? 5000 : 2500)
  const toastId = ++id
  toasts.push({ id: toastId, message, type, action: opts.action || null })
  setTimeout(() => {
    const idx = toasts.findIndex(t => t.id === toastId)
    if (idx !== -1) toasts.splice(idx, 1)
  }, duration)
  return toastId
}

export function dismissToast(toastId) {
  const idx = toasts.findIndex(t => t.id === toastId)
  if (idx !== -1) toasts.splice(idx, 1)
}

export function useToast() {
  return { toasts, showToast, dismissToast }
}
