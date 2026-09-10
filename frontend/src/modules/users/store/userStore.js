import { ref } from 'vue'
import { defineStore } from 'pinia'

import userService from '../services/userService'

export const useUserStore = defineStore('users', () => {
  const users = ref([])
  const selectedUser = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  const fetchUsers = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await userService.getUsers()
      users.value = response.data
    } catch (err) {
      error.value = 'Users could not be loaded.'
      throw err
    } finally { isLoading.value = false}
  }

  const fetchUserById = async (id) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await userService.getUserById(id)
      selectedUser.value = response.data
    } catch (err) {
      error.value = 'User could not be loaded.'
      throw err
    } finally {isLoading.value = false}
  }

  const syncUser = (userData) => {
  if (!userData?.id) {
    return
  }

  if (
    selectedUser.value
    && String(selectedUser.value.id)
      === String(userData.id)
  ) {
    selectedUser.value = {
      ...selectedUser.value,
      ...userData,
    }
  }

  const userIndex =
    users.value.findIndex(
      (user) => {
        return (
          String(user.id)
          === String(userData.id)
        )
      },
    )

  if (userIndex !== -1) {
    users.value[userIndex] = {
      ...users.value[userIndex],
      ...userData,
    }
  }
}

  return {users,selectedUser,isLoading,error,fetchUsers, fetchUserById, syncUser,}
})