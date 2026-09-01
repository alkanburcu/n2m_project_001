from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from albums.models import Album, Photo


User = get_user_model()


class AlbumPhotoPermissionTests(APITestCase):
    def setUp(self):
        self.user01 = User.objects.create_user(
            username="user01",
            email="user01@test.com",
            password="Test123!",
        )

        self.user02 = User.objects.create_user(
            username="user02",
            email="user02@test.com",
            password="Test123!",
        )

        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="Admin123!",
        )

        self.album = Album.objects.create(
            user=self.user01,
            title="User01 Album",
        )

        self.photo = Photo.objects.create(
            album=self.album,
            title="User01 Photo",
            url="https://example.com/photo.jpg",
            thumbnail_url="https://example.com/thumb.jpg",
        )

    def test_user_only_sees_own_albums(self):
        Album.objects.create(
            user=self.user02,
            title="User02 Album",
        )

        self.client.force_authenticate(user=self.user01)

        response = self.client.get(reverse("album-list"))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)

        self.assertEqual(
            str(response.data[0]["id"]),
            str(self.album.id),
        )

    def test_user_can_create_own_album(self):
        self.client.force_authenticate(user=self.user01)

        response = self.client.post(
            reverse("album-list"),
            {
                "title": "New Album",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            str(response.data["user"]),
            str(self.user01.id),
        )

    def test_user_can_add_photo_to_own_album(self):
        self.client.force_authenticate(user=self.user01)

        response = self.client.post(
            reverse("photo-list"),
            {
                "album": str(self.album.id),
                "title": "New Photo",
                "url": "https://example.com/new-photo.jpg",
                "thumbnail_url": "https://example.com/new-thumb.jpg",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            str(response.data["album"]),
            str(self.album.id),
        )

    def test_user_cannot_add_photo_to_another_users_album(self):
        self.client.force_authenticate(user=self.user02)

        response = self.client.post(
            reverse("photo-list"),
            {
                "album": str(self.album.id),
                "title": "Unauthorized",
                "url": "https://example.com/hack.jpg",
                "thumbnail_url": "https://example.com/hack-thumb.jpg",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_owner_can_update_photo(self):
        self.client.force_authenticate(user=self.user01)

        response = self.client.patch(
            reverse(
                "photo-detail",
                args=[self.photo.id],
            ),
            {
                "title": "Updated Photo",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.photo.refresh_from_db()

        self.assertEqual(
            self.photo.title,
            "Updated Photo",
        )

    def test_other_user_cannot_update_photo(self):
        self.client.force_authenticate(user=self.user02)

        response = self.client.patch(
            reverse(
                "photo-detail",
                args=[self.photo.id],
            ),
            {
                "title": "Hacked",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.photo.refresh_from_db()

        self.assertEqual(
            self.photo.title,
            "User01 Photo",
        )

    def test_owner_can_delete_photo(self):
        self.client.force_authenticate(user=self.user01)

        response = self.client.delete(
            reverse(
                "photo-detail",
                args=[self.photo.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Photo.objects.filter(
                id=self.photo.id
            ).exists()
        )

    def test_owner_can_delete_album(self):
        album = Album.objects.create(
            user=self.user01,
            title="Delete Test",
        )

        self.client.force_authenticate(user=self.user01)

        response = self.client.delete(
            reverse(
                "album-detail",
                args=[album.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Album.objects.filter(
                id=album.id
            ).exists()
        )

    def test_other_user_cannot_delete_album(self):
        self.client.force_authenticate(user=self.user02)

        response = self.client.delete(
            reverse(
                "album-detail",
                args=[self.album.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            Album.objects.filter(
                id=self.album.id
            ).exists()
        )

    def test_superuser_can_see_all_albums(self):
        Album.objects.create(
            user=self.user02,
            title="User02 Album",
        )

        self.client.force_authenticate(user=self.superuser)

        response = self.client.get(
            reverse("album-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

    def test_user_cannot_move_photo_to_another_users_album(self):
        user02_album = Album.objects.create(user=self.user02,title="User02 Album",)

        self.client.force_authenticate(user=self.user01)

        response = self.client.patch(
            reverse(
                "photo-detail",
                args=[self.photo.id],
            ),
            {
                "album": str(user02_album.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.photo.refresh_from_db()

        self.assertEqual(self.photo.album_id,self.album.id,)


    def test_user_can_move_photo_to_another_own_album(self):
        second_album = Album.objects.create(
            user=self.user01,
            title="User01 Second Album",
        )

        self.client.force_authenticate(user=self.user01)

        response = self.client.patch(
            reverse(
                "photo-detail",
                args=[self.photo.id],
            ),
            {
                "album": str(second_album.id),
            },
            format="json",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)

        self.photo.refresh_from_db()

        self.assertEqual(self.photo.album_id,second_album.id,)