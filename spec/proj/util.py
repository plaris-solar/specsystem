import os
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

# Custom LDAP code to Consider any user in OU=DisableUsers to be inactive
from django_auth_ldap.backend import LDAPBackend

class MyLDAPBackend(LDAPBackend):
    """ A custom LDAP authenticate_ldap_user  backend """
    def __set_is_flags(self, user):
        # Users in any disabled OU are not active
        user.is_active = True
        if 'disabled' in str(user.ldap_user.dn):
            user.is_active = False

        # Users in SPEC-Admin-<env> are admins
        user.is_staff = False
        user.is_superuser = False
        if 'memberOf' in user.ldap_user.attrs:
            for mo in user.ldap_user.attrs['memberOf']:
                if f"CN=SPEC-ReadAll-{os.environ['AD_SUFFIX']}".lower() in str(mo).lower():
                    user.is_staff = True
                if f"CN=SPEC-Admin-{os.environ['AD_SUFFIX']}".lower() in str(mo).lower():
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