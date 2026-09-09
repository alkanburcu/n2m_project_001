from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from authorization.services.assignments import (
    assign_default_role,
)
from companies.models import Company


User = get_user_model()


class CompanyAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user01",
            email="user01@test.com",
            password="Test123!",
        )

        assign_default_role(
            user=self.user,
        )

        self.company = Company.objects.create(
            name="N2Mobil",
            address="Ankara",
            city="Ankara",
            phone_number="03120000000",
            website="https://example.com",
        )

        self.client.force_authenticate(
            user=self.user,
        )

    def test_standard_user_can_list_companies(self):
        response = self.client.get(
            reverse("company-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_standard_user_can_search_companies(self):
        Company.objects.create(
            name="Example Company",
            city="Istanbul",
        )

        response = self.client.get(
            reverse("company-list"),
            {
                "search": "N2",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            response.data["results"][0]["name"],
            "N2Mobil",
        )

    def test_standard_user_can_create_company(self):
        response = self.client.post(
            reverse("company-list"),
            {
                "name": "New Company",
                "address": "Çankaya",
                "city": "Ankara",
                "phone_number": "03121111111",
                "website": "https://new-company.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Company.objects.filter(
                name="New Company",
            ).exists()
        )

    def test_company_list_is_paginated(self):
        Company.objects.create(
            name="Second Company",
            city="Istanbul",
        )

        response = self.client.get(
            reverse("company-list"),
            {
                "page_size": 1,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            2,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertIsNotNone(
            response.data["next"]
        )

    def test_standard_user_cannot_update_company(self):
        response = self.client.patch(
            reverse(
                "company-detail",
                args=[self.company.id],
            ),
            {
                "name": "Changed Company",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.company.refresh_from_db()

        self.assertEqual(
            self.company.name,
            "N2Mobil",
        )

    def test_standard_user_cannot_delete_company(self):
        response = self.client.delete(
            reverse(
                "company-detail",
                args=[self.company.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            Company.objects.filter(
                id=self.company.id,
            ).exists()
        )