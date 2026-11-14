from django_filters import rest_framework as filters

from advertisements.models import Advertisement


class AdvertisementFilter(filters.FilterSet):
    """Фильтры для объявлений."""

    created_at = filters.DateFromToRangeFilter()
    favorite = filters.BooleanFilter(method="filter_favorite")

    class Meta:
        model = Advertisement
        fields = ["creator", "status", "created_at"]

    def filter_favorite(self, queryset, name, value):
        """?favorite=true — только избранные текущего пользователя."""
        if not value:
            return queryset
        if not self.request.user.is_authenticated:
            return queryset.none()
        return queryset.filter(favorites__user=self.request.user)
