import FeedPage from '../pages/FeedPage.vue'

const feedRoutes = [
  {
    path: 'feed',
    name: 'feed',
    component: FeedPage,
    meta: {
      requiresAuth: true,
    },
  },
]

export default feedRoutes