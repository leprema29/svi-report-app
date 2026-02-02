import { createRouter, createWebHistory } from 'vue-router'
import ReportExtractor from '../views/ReportExtractor.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: ReportExtractor
    }
  ]
})

export default router