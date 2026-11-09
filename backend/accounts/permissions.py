from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminRole(BasePermission):
    message = "Bu işlem yalnızca yöneticiler içindir."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsAdminOrReadOnly(BasePermission):
    """Herkes okuyabilir; yalnızca yöneticiler yazabilir."""

    message = "Bu içeriği yalnızca yöneticiler düzenleyebilir."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsAdminRole().has_permission(request, view)
