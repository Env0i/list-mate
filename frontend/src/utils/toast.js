import { reactive } from 'vue'

const toasts = reactive([])
let id = 0

export function showToast(message, type = 'success', duration = 2500) {
  const toastId = ++id
  toasts.push({ id: toastId, message, type })
  setTimeout(() => {
    const idx = toasts.findIndex(t => t.id === toastId)
    if (idx !== -1) toasts.splice(idx, 1)
  }, duration)
  return toastId
}

export function useToast() {
  return { toasts, showToast }
}
