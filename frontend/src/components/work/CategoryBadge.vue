<script setup>
const props = defineProps({ category: String })
const map = { anime: '番剧', novel: '小说', comic: '漫画', game: '游戏' }
</script>

<template>
  <span class="badge" :class="'b-' + category">
    {{ map[category] || category }}
  </span>
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
}
.b-anime { background: var(--c-anime-bg); color: var(--c-anime); }
.b-novel { background: var(--c-novel-bg); color: var(--c-novel); }
.b-comic { background: var(--c-comic-bg); color: var(--c-comic); }
.b-game { background: var(--c-game-bg); color: var(--c-game); }
</style>
