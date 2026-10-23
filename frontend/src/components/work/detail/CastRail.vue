<script setup>
import { onMounted, ref } from 'vue'
import { bangumiApi } from '../../../api/client'

// 主要角色：竖版海报不裁切 + 同图虚化底（评审 R1）；声优取第一个
const props = defineProps({
  bangumiId: { type: Number, required: true },
})

const characters = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await bangumiApi.characters(props.bangumiId)
    characters.value = data.data || []
  } catch (e) {
    console.error('Failed to load characters', e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div v-if="loading" class="rail-skel" aria-hidden="true">
    <span v-for="i in 8" :key="i" class="skel-card" />
  </div>
  <div v-else-if="characters.length" class="rail" role="list">
    <figure v-for="c in characters" :key="c.id" class="cast" role="listitem">
      <div class="ph">
        <img
          v-if="c.image_url"
          :src="bangumiApi.imageUrl(c.image_url)"
          :alt="c.name"
          loading="lazy"
        >
        <span v-else class="no-img" aria-hidden="true">?</span>
      </div>
      <figcaption>
        <p class="nm">{{ c.name }}</p>
        <p class="cv" v-if="c.actors?.length">{{ c.actors[0].name }}</p>
        <p class="rel">{{ c.relation }}</p>
      </figcaption>
    </figure>
  </div>
</template>

<style scoped>
.rail-skel { display: flex; gap: 10px; overflow: hidden; }
.skel-card { flex: none; width: 92px; height: 150px; border-radius: 8px; background: linear-gradient(90deg, var(--bg-input) 25%, var(--bg-surface-hover) 50%, var(--bg-input) 75%); background-size: 200% 100%; animation: skel 1.3s ease-in-out infinite; }
@keyframes skel { to { background-position: -200% 0; } }

.rail {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 2px 2px 10px;
  scroll-snap-type: x proximity;
  mask-image: linear-gradient(90deg, #000 92%, transparent);
  -webkit-mask-image: linear-gradient(90deg, #000 92%, transparent);
}
.cast { margin: 0; flex: none; width: 92px; scroll-snap-align: start; }
.ph {
  position: relative;
  aspect-ratio: 3 / 4.4;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-input);
}
.ph img { width: 100%; height: 100%; object-fit: cover; object-position: top; display: block; }
.no-img { position: absolute; inset: 0; display: grid; place-items: center; color: var(--text-tertiary); }
figcaption p { margin: 0; }
.nm { font-size: var(--fs-xs); font-weight: 700; margin-top: 6px !important; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cv { font-size: 10px; color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rel { font-size: 10px; color: var(--text-tertiary); }
@media (prefers-reduced-motion: reduce) {
  .skel-card { animation: none; }
}
</style>
