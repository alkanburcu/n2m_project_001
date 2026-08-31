import albumRoutes from '@/modules/albums/routes/albumRoutes'
import postRoutes from '@/modules/posts/routes/postRoutes'
import todoRoutes from '@/modules/todos/routes/todoRoutes'

import UserDetailLayout from '../pages/UserDetailLayout.vue'
import UserListPage from '../pages/UserListPage.vue'

const userRoutes = [
  {
    path: '/',
    name: 'users',
    component: UserListPage,
    meta: {requiresAuth: true,},
  },
  {
    path: '/users/:id',
    component: UserDetailLayout,
    meta: {requiresAuth: true,},
    children: [
      {
        path: '',
        redirect: (to) => ({
          name: 'user-todos',
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