import LoginPage from '../pages/LoginPage.vue'
import ForgotPasswordPage from '../pages/ForgotPasswordPage.vue'

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
]

export default authRoutes