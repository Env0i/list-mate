import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'work-list', component: () => import('../views/WorkList.vue') },
  { path: '/works/:id', name: 'work-detail', component: () => import('../views/WorkDetail.vue') },
  { path: '/works/:id/edit', redirect: to => ({ path: `/works/${to.params.id}` }) },
  { path: '/search', name: 'search', component: () => import('../views/Search.vue') },
  { path: '/add', name: 'add', component: () => import('../views/Add.vue') },
  { path: '/stats', name: 'stats', component: () => import('../views/StatsPlaceholder.vue') },
  { path: '/tags', name: 'tags', component: () => import('../views/TagsPlaceholder.vue') },
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
