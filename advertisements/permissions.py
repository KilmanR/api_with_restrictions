from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdmin(BasePermission):
    """Админ — полный доступ: что угодно с любым объявлением."""

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True


class IsOwner(BasePermission):
    """Обычный юзер: правит и удаляет только свои объявления."""

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.creator == request.user


class IsReadOnly(BasePermission):
    """Аноним — только просмотр."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
