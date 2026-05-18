<script setup>
import TopBar from './components/layout/TopBar.vue'
import MobileNav from './components/layout/MobileNav.vue'
</script>

<template>
  <TopBar />
  <main class="main">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </main>
  <MobileNav />
</template>

<style scoped>
.main {
  margin-top: 0;
  min-height: 100vh;
  padding-bottom: var(--nav-height);
}

@media (min-width: 768px) {
  .main {
    margin-top: var(--topbar-height);
    padding-bottom: 0;
  }
}
</style>
