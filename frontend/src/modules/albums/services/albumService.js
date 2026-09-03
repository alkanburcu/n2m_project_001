import api from '@/services/api'

const getAlbumsByUser = (userId) => {
  return api.get('/albums/', {
    params: {
      user: userId,
    },
  })
}

const getAlbumById = (id) => {
  return api.get(`/albums/${id}/`)
}

const getPhotosByAlbum = (albumId) => {
  return api.get('/photos/', {
    params: {
      album: albumId,
    },
  })
}

const createAlbum = (data) => {
  return api.post('/albums/', data)
}

const updateAlbum = (id, data) => {
  return api.patch(`/albums/${id}/`, data)
}

const deleteAlbum = (id) => {
  return api.delete(`/albums/${id}/`)
}

export default {
  getAlbumsByUser,
  getAlbumById,
  getPhotosByAlbum,
  createAlbum,
  updateAlbum,
  deleteAlbum,
}