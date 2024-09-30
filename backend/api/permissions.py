from rest_framework import permissions


# class ReadOnly(permissions.BasePermission):

#     def has_permission(self, request, view):
#         if request.method not in permissions.SAFE_METHODS:
#             return request.user.is_authenticated
#         return True

#     def has_object_permission(self, request, view, obj):

#         if request.method not in permissions.SAFE_METHODS:
#             return (
#                 obj.author == request.user
#                 or request.user.is_admin
#                 or request.user.is_superuser
#             )
#         return True


class AuthenticatedOrReadOnlyRequest(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method not in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return True


class IsAuthorAdminOrReadOnlyObject(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.method not in permissions.SAFE_METHODS:
            return (
                obj.author == request.user
                or request.user.is_admin
                or request.user.is_superuser
            )
        return True


class RecipePermission(
    AuthenticatedOrReadOnlyRequest,
    IsAuthorAdminOrReadOnlyObject
):
    pass
