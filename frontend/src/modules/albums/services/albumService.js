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

const createAlbum = (data) => {
  return api.post('/albums/', data)
}

const updateAlbum = (id, data) => {
  return api.patch(`/albums/${id}/`, data)
}

const deleteAlbum = (id) => {
  return api.delete(`/albums/${id}/`)
}

const getPhotosByAlbum = (albumId) => {
  return api.get('/photos/', {
    params: {
      album: albumId,
    },
  })
}

const createPhoto = (data) => {
  const formData = new FormData()

  formData.append('album', data.album)
  formData.append('title', data.title)
  formData.append('image', data.image)

  return api.post('/photos/', formData)
}

const updatePhoto = (id, data) => {
  const formData = new FormData()

  if (data.title !== undefined) {
    formData.append('title', data.title)
  }

  if (data.image) {
    formData.append('image', data.image)
  }

  return api.patch(
    `/photos/${id}/`,
    formData,
  )
}

const deletePhoto = (id) => {
  return api.delete(`/photos/${id}/`)
}

export default {
  getAlbumsByUser,
  getAlbumById,
  createAlbum,
  updateAlbum,
  deleteAlbum,

  getPhotosByAlbum,
  createPhoto,
  updatePhoto,
  deletePhoto,
}