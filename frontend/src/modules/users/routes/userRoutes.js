import albumRoutes from '@/modules/albums/routes/albumRoutes'
import postRoutes from '@/modules/posts/routes/postRoutes'
import todoRoutes from '@/modules/todos/routes/todoRoutes'

import UserDetailLayout from '../pages/UserDetailLayout.vue'
import UserListPage from '../pages/UserListPage.vue'
import ProfilePage from '../pages/ProfilePage.vue'

const userRoutes = [
  {
  path: '/profile',
  name: 'profile',
  component: ProfilePage,

  meta: {requiresAuth: true,},
  },

  {
    path: '/users/:id/edit',
    name: 'user-profile-edit',
    component: ProfilePage,

    meta: {
      requiresAuth: true,
      permission: 'users.update',
    },
  },

  {
    path: '/users',
    name: 'users',
    component: UserListPage,

    meta: {
      requiresAuth: true,
      permission: 'users.list',
    },
  },

  {
    path: '/users/:id',
    component: UserDetailLayout,

    meta: {
      requiresAuth: true,
    },

    children: [
      {
        path: '',

        redirect: (to) => ({
          name: 'user-posts',

          params: {
            id: to.params.id,
          },
        }),
      },

      ...todoRoutes,
      ...postRoutes,
      ...albumRoutes,
    ],
  },
]

export default userRoutes