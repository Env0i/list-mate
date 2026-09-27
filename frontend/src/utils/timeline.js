// 时间线展示共享逻辑——Stats 操作记录与 WorkDetail 历史区块共用，避免两份漂移。
import { STATUS_LABELS_FLAT } from '../constants/work'

export const actionLabels = {
  created: '添加', status_change: '状态变更', rating_change: '评分变更',
  review_change: '评价变更', progress_update: '进度更新',
}

export const actionIcons = {
  created: '＋', status_change: '⇄', rating_change: '★', review_change: '✎', progress_update: '↑',
}

// 时间线 old/new 值在后端经 json.dumps 存储，API 返回的是 JSON 串（如 "\"watching\""、"{\"title\":...}"），
// 展示前先反序列化；非 JSON 串原样返回
function unjson(v) {
  if (typeof v !== 'string') return v
  try { return JSON.parse(v) } catch { return v }
}

export function formatValue(actionType, oldVal, newVal) {
  const o = unjson(oldVal)
  const n = unjson(newVal)
  if (actionType === 'status_change') {
    const os = o ? (STATUS_LABELS_FLAT[o] || o) : '无'
    const ns = n ? (STATUS_LABELS_FLAT[n] || n) : '无'
    return `${os} → ${ns}`
  }
  if (actionType === 'rating_change') {
    const os = o != null ? `${o}/10` : '未评分'
    const ns = n != null ? `${n}/10` : '未评分'
    return `${os} → ${ns}`
  }
  if (actionType === 'progress_update') {
    return `${o ?? '—'} → ${n ?? '—'}`
  }
  if (actionType === 'created') {
    if (n && typeof n === 'object' && n.title) return n.title
    return n != null ? String(n).slice(0, 60) : ''
  }
  return n != null ? String(n).slice(0, 60) : ''
}

// 后端时间为无时区 UTC 串，统一补 Z 解析
function dateOf(ts) {
  return new Date(/Z$|[+-]\d{2}:?\d{2}$/.test(ts) ? ts : ts + 'Z')
}

// 分组头标签：今天 / 昨天 / M月D日（跨年补年份）
export function dayLabel(ts) {
  const d = dateOf(ts)
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const that = new Date(d.getFullYear(), d.getMonth(), d.getDate())
  const diffDays = Math.round((today - that) / 86400000)
  if (diffDays === 0) return '今天'
  if (diffDays === 1) return '昨天'
  const y = d.getFullYear() === now.getFullYear() ? '' : `${d.getFullYear()}年`
  return `${y}${d.getMonth() + 1}月${d.getDate()}日`
}

export function timeAgo(ts) {
  const d = dateOf(ts)
  const now = new Date()
  const diff = now - d
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins}分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}天前`
  const months = Math.floor(days / 30)
  if (months < 12) return `${months}个月前`
  return `${Math.floor(months / 12)}年前`
}
