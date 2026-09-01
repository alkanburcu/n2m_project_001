from rest_framework.routers import DefaultRouter

from .views import AlbumViewSet, PhotoViewSet


router = DefaultRouter()

router.register("albums",AlbumViewSet,basename="album",)

router.register("photos",PhotoViewSet, basename="photo",)

urlpatterns = router.urls