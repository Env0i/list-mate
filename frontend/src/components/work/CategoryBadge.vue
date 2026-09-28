<script setup>
import { computed } from 'vue'

// 品类徽章：品类实底 + --cc-on 文字（style.css 按 data-cat 定义，唯一能全品类过 4.5:1 的搭配）
const props = defineProps({ category: String })
const map = { anime: '番剧', novel: '小说', comic: '漫画', game: '游戏' }
const known = computed(() => !!map[props.category])
</script>

<template>
  <span v-if="known" class="badge" :data-cat="category">{{ map[category] }}</span>
  <span v-else class="badge badge-unknown">{{ category }}</span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  height: 20px;
  padding: 0 8px;
  border-radius: var(--radius-sm);
  font-size: 10px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: 0.3px;
  color: var(--cc-on, var(--text-primary));
  background: var(--cc, var(--text-tertiary));
}
.badge[data-cat='anime'] { background: var(--c-anime); }
.badge[data-cat='novel'] { background: var(--c-novel); }
.badge[data-cat='comic'] { background: var(--c-comic); }
.badge[data-cat='game'] { background: var(--c-game); }
.badge-unknown { color: var(--text-primary); }
</style>
