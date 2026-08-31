import { createRouter, createWebHistory } from 'vue-router'
import authRoutes from '@/modules/auth/routes/authRoutes'
import UserListPage from '@/modules/users/pages/UserListPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [ ...authRoutes, {path: '/', name: 'users', component: UserListPage, meta: { requiresAuth: true},}],
})

router.beforeEach((to)=> { const access_token = localStorage.getItem('access_token')
   if (to.meta.requiresAuth && !access_token) {
    return {name: 'login',}
  }

  if (to.name === 'login' && access_token) {
    return { name: 'users',}
  }
})


export default router
