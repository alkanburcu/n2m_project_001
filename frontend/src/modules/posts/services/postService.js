import api from '@/services/api'

const getPostsByUser = (userId) => {
  return api.get('/posts/', {
    params: {
      user: userId,
    },
  })
}

const getPostById = (id) => {
  return api.get(`/posts/${id}/`)
}

const getCommentsByPost = (postId) => {
  return api.get('/comments/', {
    params: {
      post: postId,
    },
  })
}

const createPost = (data) => {
  return api.post('/posts/', data)
}

const updatePost = (id, data) => {
  return api.patch(`/posts/${id}/`, data)
}

const deletePost = (id) => {
  return api.delete(`/posts/${id}/`)
}

export default {
  getPostsByUser,
  getPostById,
  getCommentsByPost,
  createPost,
  updatePost,
  deletePost,
}