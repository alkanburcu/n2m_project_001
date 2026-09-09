from authorization.permissions import HasAppPermission
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet

from .models import Company
from .pagination import CompanyPagination
from .serializers import CompanySerializer


class CompanyViewSet(ModelViewSet):
    queryset = Company.objects.filter(
        is_active=True,
    )

    serializer_class = CompanySerializer
    permission_classes = [HasAppPermission]
    pagination_class = CompanyPagination

    permission_map = {
        "list": "companies.list",
        "retrieve": "companies.view",
        "create": "companies.create",
        "update": "companies.update",
        "partial_update": "companies.update",
        "destroy": "companies.delete",
    }

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = (
        "name",
        "city",
    )

    ordering_fields = (
        "name",
        "city",
        "created_at",
    )

    ordering = ("name",)