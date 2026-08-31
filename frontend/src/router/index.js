import { createRouter, createWebHistory } from 'vue-router'

import authRoutes from '@/modules/auth/routes/authRoutes'
import userRoutes from '@/modules/users/routes/userRoutes'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [...authRoutes, ...userRoutes, ],
})

router.beforeEach((to) => {
  const accessToken = localStorage.getItem('access_token')

  if (to.meta.requiresAuth && !accessToken) {
    return {name: 'login',}
  }

  if (to.name === 'login' && accessToken) {
    return {name: 'users',}
  }
})

export default router