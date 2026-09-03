import api from '@/services/api'

const getTodosByUser = (userId) => {
  return api.get('/todos/', {
    params: {
      user: userId,
    },
  })
}

const getTodoById = (id) => {
  return api.get(`/todos/${id}/`)
}

const createTodo = (data) => {
  return api.post('/todos/', data)
}

const updateTodo = (id, data) => {
  return api.patch(`/todos/${id}/`, data)
}

const deleteTodo = (id) => {
  return api.delete(`/todos/${id}/`)
}

export default {
  getTodosByUser,
  getTodoById,
  createTodo,
  updateTodo,
  deleteTodo,
}