<script setup>
import TopBar from './components/layout/TopBar.vue'
import MobileNav from './components/layout/MobileNav.vue'
import AppFooter from './components/layout/AppFooter.vue'
import { useToast, dismissToast } from './utils/toast'
const { toasts } = useToast()
</script>

<template>
  <TopBar />
  <main class="main">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    <AppFooter />
  </main>
  <MobileNav />

  <!-- Toast notifications -->
  <div class="toast-container">
    <transition-group name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="toast"
        :class="t.type"
      >
        <span>{{ t.message }}</span>
        <button v-if="t.action" class="toast-action" @click="t.action.handler(); dismissToast(t.id)">
          {{ t.action.label }}
        </button>
      </div>
    </transition-group>
  </div>
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

/* ===== Toast notifications ===== */
.toast-container {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
  max-width: 90vw;
}
@media (min-width: 768px) {
  .toast-container { top: 80px; }
}

.toast {
  padding: 10px 20px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  text-align: center;
  white-space: nowrap;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.12);
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 90vw;
}
.toast > span {
  overflow: hidden;
  text-overflow: ellipsis;
}
.toast-action {
  color: inherit;
  font-weight: 800;
  text-decoration: underline;
  text-underline-offset: 3px;
  min-height: 28px;
  flex: none;
}
.toast.success {
  background: rgba(0, 184, 90, 0.92);
  color: white;
}
.toast.error {
  background: rgba(244, 67, 54, 0.92);
  color: white;
}
.toast.info {
  background: rgba(51, 102, 255, 0.92);
  color: white;
}

/* Toast animation */
.toast-enter-active {
  transition: all 0.25s cubic-bezier(.34,1.56,.64,1);
}
.toast-leave-active {
  transition: all 0.2s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(-12px) scale(0.92);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.96);
}
</style>
