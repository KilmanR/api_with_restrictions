from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from advertisements.filters import AdvertisementFilter
from advertisements.models import Advertisement, AdvertisementStatusChoices, Favorite
from advertisements.permissions import IsAdmin, IsOwner, IsReadOnly
from advertisements.serializers import AdvertisementSerializer


class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filterset_class = AdvertisementFilter

    def get_queryset(self):
        """Админ видит всё; чужие черновики (DRAFT) — только автору."""
        user = self.request.user
        queryset = Advertisement.objects.all()
        if user.is_authenticated and user.is_superuser:
            return queryset
        if not user.is_authenticated:
            return queryset.exclude(status=AdvertisementStatusChoices.DRAFT)
        return queryset.filter(
            Q(status=AdvertisementStatusChoices.DRAFT, creator=user)
            | ~Q(status=AdvertisementStatusChoices.DRAFT)
        )

    def get_permissions(self):
        """Права по роли запросившего: админ → юзер → анон."""
        if self.action == "favorite":
            return [IsAuthenticated()]
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            return [IsAdmin()]
        if user.is_authenticated:
            return [IsOwner()]
        return [IsReadOnly()]

    @action(detail=True, methods=["post", "delete"], url_path="favorite")
    def favorite(self, request, pk=None):
        """Добавить объявление в избранное (POST) или убрать (DELETE)."""
        advertisement = self.get_object()
        if request.method == "POST":
            if advertisement.creator == request.user:
                return Response(
                    {"detail": "Нельзя добавить в избранное своё объявление."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Favorite.objects.get_or_create(
                user=request.user,
                advertisement=advertisement,
            )
            return Response(
                {"detail": "Добавлено в избранное."},
                status=status.HTTP_201_CREATED,
            )
        Favorite.objects.filter(
            user=request.user,
            advertisement=advertisement,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
