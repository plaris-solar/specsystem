from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperUser(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsSuperUserOrReadOnly(BasePermission):
    """
    The request is authenticated as a superuser, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_superuser
        )


class IsStaffOrReadOnly(BasePermission):
    """
    The request is authenticated as a staff user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            (request.user.is_superuser or request.user.is_staff)
        )


class DataPermissions(BasePermission):
    """
    The request is authenticated as:
      Authenticated for POST (hold)
      Staff for DELETE (release from hold)
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and (
                (request.method == 'POST' and request.user.is_active) or
                (request.method == 'DELETE' and request.user.is_superuser) or
                (request.method == 'PUT' and request.user.is_superuser)
            )
        )


class DocPermissions(BasePermission):
    """
    The request is authenticated as:
      Authenticated for POST (hold)
      Staff for DELETE (release from hold)
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and (
                (request.method == 'POST' and request.user.is_superuser)
            )
        )
