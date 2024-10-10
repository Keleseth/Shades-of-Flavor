from rest_framework import permissions


class AuthenticatedOrReadOnlyRequest(permissions.BasePermission):
    """Пермишен уровня запроса."""

    def has_permission(self, request, view):
        if (
            request.method not in permissions.SAFE_METHODS
            or request.path.endswith('/me/')
        ):
            return request.user.is_authenticated
        return True


class IsAuthorAdminOrReadOnlyObject(permissions.BasePermission):
    """Пермишен уровня объекта."""
    def has_object_permission(self, request, view, obj):

        if request.method not in permissions.SAFE_METHODS:
            return (
                obj.author == request.user
                or request.user.is_staff
                or request.user.is_superuser
            )
        return True

