from django_auth_ldap.backend import LDAPBackend
from django.contrib.auth.models import User as DjangoUser
from rest_framework.exceptions import ValidationError

class User(DjangoUser):

    @staticmethod
    def lookup(username):
        user = DjangoUser.objects.filter(username=username).first()
        if not user:
            user = LDAPBackend().populate_user(username)
        if not user:
            raise ValidationError({"errorCode":"USER-M01", "error": f"User: {username} does not exist."})
        return user
