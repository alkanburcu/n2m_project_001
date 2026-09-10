import api from '@/services/api'

const USERS_ME = '/users/me/'

const getProfile = () => {
  return api.get(
    USERS_ME,
  )
}

const updateProfile = (payload) => {
  return api.patch(
    USERS_ME,
    payload,
  )
}

const updateProfilePhoto = (file) => {
  const formData = new FormData()

  formData.append(
    'profile_photo',
    file,
  )

  return api.patch(
    USERS_ME,
    formData,
  )
}

export default {
  getProfile,
  updateProfile,
  updateProfilePhoto,
}