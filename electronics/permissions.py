from rest_framework import permissions


class IsActiveEmployee(permissions.BasePermission):
    """
    Разрешает доступ только активным сотрудникам.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_active
        )
