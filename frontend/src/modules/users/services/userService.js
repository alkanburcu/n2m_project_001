import api from '@/services/api'

const getUsers = () => {
  return api.get('/users/')
}

const getUserById = (id) => {
  return api.get(`/users/${id}/`)
}

const createUser = (data) => {
  return api.post(
    '/users/',
    data,
  )
}

export default {
  getUsers,
  getUserById,
  createUser,
}