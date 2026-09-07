import ForgotPasswordPage from '../pages/ForgotPasswordPage.vue'
import LoginPage from '../pages/LoginPage.vue'
import ResetPasswordPage from '../pages/ResetPasswordPage.vue'

const authRoutes = [
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: ForgotPasswordPage,
  },
  {
    path: '/reset-password/:uid/:token',
    name: 'reset-password',
    component: ResetPasswordPage,
  },
]

export default authRoutes