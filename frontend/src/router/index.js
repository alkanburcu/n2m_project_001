import { createRouter, createWebHistory } from 'vue-router'
import authRoutes from '@/modules/auth/routes/authRoutes'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [ ...authRoutes, ],
})

export default router
