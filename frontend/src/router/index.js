import { createRouter, createWebHistory } from 'vue-router'

import authRoutes from '@/modules/auth/routes/authRoutes'
import userRoutes from '@/modules/users/routes/userRoutes'
import { useAuthStore } from '@/modules/auth/store/authStore'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),

  routes: [
    {
      path: '/',
      redirect: { name: 'login' },
    },

    ...authRoutes,

    {
      path: '/',
      component: AuthenticatedLayout,
      children: [
        ...userRoutes,
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  const accessToken = localStorage.getItem('access_token')

  // Login gerektiren sayfaya tokensız giriş.
  if (to.meta.requiresAuth && !accessToken) {
    return {
      name: 'login',
    }
  }

  // Giriş yapılmamışsa public route'larda devam et.
  if (!accessToken) {
    return true
  }

  // Token var ama sayfa refresh edildiği için Pinia user bilgisi yoksa
  // backend'den tekrar yükle.
  if (!authStore.user) {
    try {
      await authStore.fetchMe()
    } catch {
      await authStore.logout()

      return {
        name: 'login',
      }
    }
  }

  // Login sayfasına giriş yapmış kullanıcı gelirse
  // permissionına göre doğru yere gönder.
  if (to.name === 'login') {
    if (authStore.can('users.list')) {
      return {
        name: 'users',
      }
    }

    return {
      name: 'user-todos',
      params: {
        id: authStore.user.id,
      },
    }
  }

  // Route belirli bir permission gerektiriyorsa kontrol et.
  if (
    to.meta.permission &&
    !authStore.can(to.meta.permission)
  ) {
    return {
      name: 'user-todos',
      params: {
        id: authStore.user.id,
      },
    }
  }

  // Normal kullanıcı başka bir kullanıcının detail URL'sini
  // elle yazarsa kendi sayfasına geri gönder.
  if (
    to.meta.userScoped &&
    !authStore.can('users.list') &&
    String(to.params.id) !== String(authStore.user.id)
  ) {
    return {
      name: 'user-todos',
      params: {
        id: authStore.user.id,
      },
    }
  }

  return true
})

export default router