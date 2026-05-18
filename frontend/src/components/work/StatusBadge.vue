<script setup>
const props = defineProps({ status: String })
const map = { wish: '想看', watching: '在看', completed: '看完', paused: '暂停', dropped: '弃了' }
const colorMap = {
  wish: '#A39F98', watching: '#3366FF', completed: '#00B85A',
  paused: '#FFB800', dropped: '#FF4444',
}
</script>

<template>
  <span class="stamp" :style="{ background: colorMap[status] || '#A39F98' }">{{ map[status] || status }}</span>
</template>

<style scoped>
.stamp {
  display: inline-flex;
  align-items: center;
  height: 20px;
  padding: 0 7px;
  border-radius: 2px;
  font-size: 10px;
  font-weight: 800;
  color: white;
  letter-spacing: 0.8px;
  transform: rotate(2deg);
  box-shadow: 0 1px 4px rgba(0,0,0,0.12);
}
</style>
