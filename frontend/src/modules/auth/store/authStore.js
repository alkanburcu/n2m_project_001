import {computed , ref} from 'vue'
import { defineStore } from 'pinia'
import authService from '../services/authService'
export const useAuthStore = defineStore ('auth', () => {
   const accessToken = ref(localStorage.getItem('access_token'))
   const refreshToken = ref(localStorage.getItem('refresh_token'))
   
   const isAuthenticated = computed(() => Boolean(accessToken.value))
   
   const login = async (credentials) => {
    const response = await authService.login(credentials)

    accessToken.value = response.data.access
    refreshToken.value = response.data.refresh

    localStorage.setItem('access_token', accessToken.value)
    localStorage.setItem('refresh_token', refreshToken.value)

    return response }

   const clearTokens = () => {
    accessToken.value = null
    refreshToken.value = null

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

   const logout = async () => {
    try {
      if (refreshToken.value) {
        await authService.logout(refreshToken.value)
      }
    } finally {
      clearTokens()
    }
  }

  return { accessToken, refreshToken, isAuthenticated, login, logout,}
})
