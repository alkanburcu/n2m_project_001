import { ref } from 'vue'
import { defineStore } from 'pinia'

import { useAuthStore } from '@/modules/auth/store/authStore'
import { useUserStore } from './userStore'
import profileService from '../services/profileService'


export const useProfileStore = defineStore(
  'profile',
  () => {
    const profile = ref(null)

    const isLoading = ref(false)
    const isSaving = ref(false)

    const error = ref(null)

    const syncUserState = (profileData) => {
      const authStore = useAuthStore()
      const userStore = useUserStore()

      authStore.syncProfile(
        profileData,
      )

      userStore.syncUser(
        profileData,
      )
    }

    const fetchProfile = async () => {
      isLoading.value = true
      error.value = null

      try {
        const response =
          await profileService.getProfile()

        profile.value =
          response.data

        syncUserState(
          response.data,
        )

        return profile.value
      } catch (err) {
        error.value =
          'Profile could not be loaded.'

        throw err
      } finally {
        isLoading.value = false
      }
    }

    const updateProfile = async (
      payload,
    ) => {
      isSaving.value = true
      error.value = null

      try {
        const response =
          await profileService.updateProfile(
            payload,
          )

        profile.value =
          response.data

        syncUserState(
          response.data,
        )

        return profile.value
      } catch (err) {
        error.value =
          'Profile could not be updated.'

        throw err
      } finally {
        isSaving.value = false
      }
    }

    const updateProfilePhoto = async (
      file,
    ) => {
      isSaving.value = true
      error.value = null

      try {
        const response =
          await profileService
            .updateProfilePhoto(
              file,
            )

        profile.value =
          response.data

        syncUserState(
          response.data,
        )

        return profile.value
      } catch (err) {
        error.value =
          'Profile photo could not be updated.'

        throw err
      } finally {
        isSaving.value = false
      }
    }

    return {
      profile,
      isLoading,
      isSaving,
      error,
      fetchProfile,
      updateProfile,
      updateProfilePhoto,
    }
  },
)