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
  username,
  email,
}) => {
  return api.post(
    '/auth/password-reset-request/',
    {
      username,
      email,
    },
  )
}

const confirmPasswordReset = ({
  username,
  email,
  code,
  newPassword,
}) => {
  return api.post(
    '/auth/password-reset-confirm/',
    {
      username,
      email,
      code,
      new_password: newPassword,
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