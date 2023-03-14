import os
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperUser(BasePermission):

    def has_permission(self, request, view):
        return True


class IsSuperUserOrReadOnly(BasePermission):
    """
    The request is authenticated as a superuser, or is a read-only request.
    """

    def has_permission(self, request, view):
        return True

# class IsStaffOrReadOnly(BasePermission):
#     """
#     The request is authenticated as a staff user, or is a read-only request.
#     """

#     def has_permission(self, request, view):
#         return bool(
#             request.method in SAFE_METHODS or
#             request.user and
#             (request.user.is_superuser or request.user.is_staff)
#         )

# Custom LDAP code to Consider any user in OU=DisableUsers to be inactive
from django_auth_ldap.backend import LDAPBackend

class MyLDAPBackend(LDAPBackend):
    """ A custom LDAP authenticate_ldap_user  backend """
    def __set_is_flags(self, user):
        if not user: # pragma nocover
            return None
        # Users in any disabled OU are not active
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

    def authenticate_ldap_user (self, username, password):
        """ Overrides LDAPBackend.authenticate_ldap_user  to add custom logic """
        user = LDAPBackend().authenticate_ldap_user (username, password)
        return self.__set_is_flags(user)

    def populate_user(self, username):
        """ Overrides LDAPBackend.authenticate_ldap_user  to add custom logic """
        user = LDAPBackend().populate_user (username)
        return self.__set_is_flags(user)