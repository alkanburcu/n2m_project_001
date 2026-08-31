import AlbumListPage from '../pages/AlbumListPage.vue'
import AlbumPhotosPage from '../pages/AlbumPhotosPage.vue'

const albumRoutes = [
  {
    path: 'albums',
    name: 'user-albums',
    component: AlbumListPage,
  },
  {
    path: 'albums/:albumId',
    name: 'album-photos',
    component: AlbumPhotosPage,
  },
]

export default albumRoutes