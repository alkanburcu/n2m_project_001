import {
  createRouter,
  createWebHistory,
} from 'vue-router'

import authRoutes from '@/modules/auth/routes/authRoutes'
import feedRoutes from '@/modules/posts/routes/feedRoutes'
import userRoutes from '@/modules/users/routes/userRoutes'

import { useAuthStore } from '@/modules/auth/store/authStore'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'

const router = createRouter({
  history: createWebHistory(
    import.meta.env.BASE_URL,
  ),

  routes: [
    {
      path: '/',
      redirect: {
        name: 'login',
      },
    },

    ...authRoutes,

    {
      path: '/',
      component: AuthenticatedLayout,

      children: [
        ...userRoutes,
        ...feedRoutes,
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  const accessToken =
    localStorage.getItem(
      'access_token',
    )

  if (
    to.meta.requiresAuth
    && !accessToken
  ) {
    return {
      name: 'login',
    }
  }

  if (!accessToken) {
    return true
  }

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

  if (to.name === 'login') {
    return {
      name: 'feed',
    }
  }

  if (
    to.meta.permission
    && !authStore.can(
      to.meta.permission,
    )
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