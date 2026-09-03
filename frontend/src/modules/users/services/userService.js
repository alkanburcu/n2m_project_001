import api from '@/services/api'

const getUsers = () => { return api.get('/users/') }

const getUserById = (id) => {return api.get(`/users/${id}/`)}

export default {getUsers,getUserById,}