import {computed , ref} from 'vue'
import { defineStore } from 'pinia'
import authService from '../services/authService'
export const useAuthStore = defineStore ('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))
   
  const isAuthenticated = computed(() => Boolean(accessToken.value))
  const user = ref(null)
  const isSuperuser = computed(() => Boolean(user.value?.is_superuser))
  const can = (permissionKey) => {return Boolean(user.value?.permissions?.[permissionKey])}


  const login = async (credentials) => {
  const response = await authService.login(credentials)

  accessToken.value = response.data.access
  refreshToken.value = response.data.refresh

  localStorage.setItem('access_token', accessToken.value)
  localStorage.setItem('refresh_token', refreshToken.value)

  await fetchMe()

  return user.value
}

  const clearAuth = () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

const logout = async () => {
  try {
    if (refreshToken.value) {
      await authService.logout(refreshToken.value)
    }
  } finally {
    clearAuth()
  }
}

const fetchMe = async () => {
  const response = await authService.me()

  user.value = response.data

  return user.value
}
 

return { accessToken, refreshToken, isAuthenticated, isSuperuser, user, can, login, logout, fetchMe }
})


