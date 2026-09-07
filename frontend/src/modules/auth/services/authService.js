import api from '@/services/api'

const login = (credentials) => {
  return api.post(
    '/auth/login/',
    credentials,
  )
}

const me = () => {
  return api.get('/auth/me/')
}

const refreshToken = (refresh) => {
  return api.post(
    '/auth/refresh/',
    {
      refresh,
    },
  )
}

const logout = (refresh) => {
  return api.post(
    '/auth/logout/',
    {
      refresh,
    },
  )
}

const requestPasswordReset = ({
  email,
}) => {
  return api.post(
    '/auth/password-reset-request/',
    {
      email,
    },
  )
}

const confirmPasswordReset = ({
  uid,
  token,
  newPassword,
  newPasswordConfirm,
}) => {
  return api.post(
    '/auth/password-reset-confirm/',
    {
      uid,
      token,
      new_password: newPassword,
      new_password_confirm:
        newPasswordConfirm,
    },
  )
}

export default {
  login,
  me,
  refreshToken,
  logout,
  requestPasswordReset,
  confirmPasswordReset,
}