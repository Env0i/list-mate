/**
 * 平台图标注册表
 *
 * 约定：SVG 文件放 frontend/src/assets/icons/{category}/{key}.svg
 * 如果文件不存在会静默降级为文字显示。
 */

const gamePlatforms = [
  { key: 'steam', label: 'Steam' },
  { key: 'epicgames', label: 'Epic' },
  { key: 'wegame', label: 'WeGame' },
  { key: 'playstation', label: 'PlayStation' },
  { key: 'xbox', label: 'Xbox' },
  { key: 'switch-fill', label: 'Switch' },
  { key: 'mobile', label: '手游' },
  { key: 'pc', label: 'PC' },
]

const animePlatforms = [
  { key: 'bilibili', label: 'Bilibili' },
  { key: 'netflix', label: 'Netflix' },
  { key: 'crunchyroll', label: 'Crunchyroll' },
  { key: 'tv', label: 'TV' },
  { key: 'movie', label: '剧场版' },
]

const novelPlatforms = [
  { key: '起点中文网', label: '起点中文网' },
  { key: '番茄小说', label: '番茄小说' },
]

const comicPlatforms = [
  { key: 'bilibili-comic', label: '哔哩哔哩漫画' },
  { key: 'dmzj', label: '动漫之家' },
  { key: 'kaobei', label: '拷贝漫画' },
]

const registry = {
  game: gamePlatforms,
  anime: animePlatforms,
  novel: novelPlatforms,
  comic: comicPlatforms,
}

export function getPlatforms(category) {
  return registry[category] || []
}

export function getPlatformLabel(category, key) {
  const list = registry[category] || []
  const found = list.find(p => p.key === key)
  return found ? found.label : key
}

export function getPlatformIconUrl(category, key) {
  // Vite 会在构建时处理这个路径模式
  return new URL(`../assets/icons/${category}/${key}.svg`, import.meta.url).href
}
