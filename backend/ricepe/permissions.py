from rest_framework import permissions


class CurrentUserOrAdminOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):

        if request.method == "PATCH" or request.method == "DELETE":
            return (
                (request.user.is_authenticated and request.user == obj.author)
                or request.user.is_staff)
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated
