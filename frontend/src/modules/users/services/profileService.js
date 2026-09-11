import api from '@/services/api'

const getProfileUrl = (userId = null) => {
  if (userId) {
    return `/users/${userId}/`
  }

  return '/users/me/'
}

const getProfile = (userId = null) => {
  return api.get(
    getProfileUrl(userId),
  )
}

const updateProfile = (
  payload,
  userId = null,
) => {
  return api.patch(
    getProfileUrl(userId),
    payload,
  )
}

const updateProfilePhoto = (
  file,
  userId = null,
) => {
  const formData = new FormData()

  formData.append(
    'profile_photo',
    file,
  )

  return api.patch(
    getProfileUrl(userId),
    formData,
  )
}

export default {
  getProfile,
  updateProfile,
  updateProfilePhoto,
}