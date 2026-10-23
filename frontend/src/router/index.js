import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'work-list', component: () => import('../views/WorkList.vue') },
  { path: '/works/:id', name: 'work-detail', component: () => import('../views/WorkDetail.vue') },
  { path: '/works/:id/edit', redirect: to => ({ path: `/works/${to.params.id}` }) },
  // S5 添加页合并：旧搜索页与添加页统一为 /add?tab=…，深链保持可用
  { path: '/search', redirect: to => ({ path: '/add', query: { tab: 'search', q: to.query.q } }) },
  { path: '/add', name: 'add', component: () => import('../views/Add.vue') },
  { path: '/settings', name: 'settings', component: () => import('../views/Settings.vue') },
  { path: '/stats', name: 'stats', component: () => import('../views/Stats.vue') },
  { path: '/tags', name: 'tags', component: () => import('../views/Tags.vue') },
  {
    path: '/works/:id/game-profiles/new',
    name: 'game-profile-new',
    component: () => import('../views/GameProfileNew.vue'),
  },
  {
    path: '/works/:id/game-profiles/:gpid',
    name: 'game-profile-detail',
    component: () => import('../views/GameProfileDetail.vue'),
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
