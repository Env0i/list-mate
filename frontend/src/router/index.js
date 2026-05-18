import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'work-list', component: () => import('../views/WorkList.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
