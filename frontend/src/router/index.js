import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Records from '../views/Records.vue'
import AlertRules from '../views/AlertRules.vue'
import AlertLogs from '../views/AlertLogs.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/records',
    name: 'Records',
    component: Records
  },
  {
    path: '/alert-rules',
    name: 'AlertRules',
    component: AlertRules
  },
  {
    path: '/alert-logs',
    name: 'AlertLogs',
    component: AlertLogs
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
