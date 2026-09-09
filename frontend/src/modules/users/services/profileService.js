import api from '@/services/api'
const USERS_ME = '/users/me/'

const getProfile = () => {
    return api.get(USERS_ME)
}

const updateProfile = (payload) => {
    return api.patch(
        'USER_ME',
        payload,
    )
}

const updateProfilePhoto = (file) => {
    const formData = new FormData()

    FormData.append(
        'profile_photo',
        file,
    )

    return api.patch(
        'USER_ME',
        formData,
    )
}

export default{
    getProfile,
    updateProfile,
    updateProfilePhoto,
}