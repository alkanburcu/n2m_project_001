import api from '@/services/api'

const PHOTO_URL = '/photos/'
const ALBUM_URL = '/albums/'

const getAlbumsByUser = (userId) => {
  return api.get(ALBUM_URL, {
    params: {
      user: userId,
    },
  })
}

const getAlbumById = (id) => {
  return api.get(`${ALBUM_URL}${id}/`)
}

const createAlbum = (data) => {
  return api.post(ALBUM_URL, data)
}

const updateAlbum = (id, data) => {
  return api.patch(`${ALBUM_URL}${id}/`, data)
}

const deleteAlbum = (id) => {
  return api.delete(`${ALBUM_URL}${id}/`)
}

const getPhotosByAlbum = (albumId) => {
  return api.get(PHOTO_URL, {
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

  return api.post(PHOTO_URL, formData)
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
    `${PHOTO_URL}${id}/`,
    formData,
  )
}

const deletePhoto = (id) => {
  return api.delete(`${PHOTO_URL}${id}/`)
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