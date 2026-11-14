from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement, AdvertisementStatusChoices


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
        )


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = (
            "id",
            "title",
            "description",
            "creator",
            "status",
            "created_at",
            "is_favorite",
        )

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def get_is_favorite(self, obj):
        """Добавил ли текущий пользователь объявление в избранное."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""
        user = self.context["request"].user
        new_status = data.get("status")
        if self.instance is None:
            new_status = new_status or AdvertisementStatusChoices.OPEN
        if new_status != AdvertisementStatusChoices.OPEN:
            return data
        open_ads = Advertisement.objects.filter(
            creator=user,
            status=AdvertisementStatusChoices.OPEN,
        )
        if self.instance is not None:
            open_ads = open_ads.exclude(pk=self.instance.pk)
        if open_ads.count() >= 10:
            raise serializers.ValidationError(
                "у пользователя не больше 10 открытых объявлений"
            )

        return data
