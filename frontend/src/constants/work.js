// 作品品类与状态的展示常量——全局唯一定义，视图从这里引用。
// 颜色一律引用 style.css 的设计令牌（--c-* / --s-*），此处不写死色值。
export const CATEGORIES = [
  { key: 'anime', label: '番剧', unit: 'ep', unitLabel: '集' },
  { key: 'novel', label: '小说', unit: 'chapter', unitLabel: '章' },
  { key: 'comic', label: '漫画', unit: 'volume', unitLabel: '卷' },
  { key: 'game', label: '游戏', unit: 'percent', unitLabel: '%' },
]

export const CATEGORY_LABELS = { anime: '番剧', novel: '小说', comic: '漫画', game: '游戏' }

const MEDIA_STATUS = { wish: '想看', watching: '在看', completed: '看完', paused: '暂停', dropped: '弃了' }

// 按品类索引的状态标签（卡片/详情/添加页用）
export const STATUS_LABELS = {
  anime: MEDIA_STATUS,
  novel: MEDIA_STATUS,
  comic: MEDIA_STATUS,
  game: { wish: '想玩', playing: '在玩', completed: '通关', dropped: '弃坑', wait_buy: '等购买', wait_sale: '等折扣' },
}

// 扁平版（统计页/时间线等不区分品类的场景用）
export const STATUS_LABELS_FLAT = {
  ...MEDIA_STATUS,
  playing: '在玩', wait_buy: '等购买', wait_sale: '等折扣',
}

// 状态色（inline style 场景用；游戏复用影视近似色，wait_sale 为游戏专属）
export const STATUS_COLORS = {
  wish: 'var(--s-wish)',
  watching: 'var(--s-watching)',
  playing: 'var(--s-watching)',
  completed: 'var(--s-completed)',
  paused: 'var(--s-paused)',
  dropped: 'var(--s-dropped)',
  wait_buy: 'var(--s-paused)',
  wait_sale: 'var(--s-wait-sale)',
}

// 品类渐变（封面兜底 / EXP 条），颜色来自 --c-* / --c-*-light 令牌
export function categoryGradient(cat, deg = 135) {
  return `linear-gradient(${deg}deg, var(--c-${cat}), var(--c-${cat}-light))`
}
