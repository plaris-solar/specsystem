from django.contrib.auth.models import User as DjangoUser
from rest_framework.exceptions import ValidationError
from proj.util import MyLDAPBackend

class User(DjangoUser):

    @staticmethod
    def lookup(username):
        user = DjangoUser.objects.filter(username=username).first()
        if not user:
            user = MyLDAPBackend().populate_user(username)
        if not user:
            raise ValidationError({"errorCode":"USER-M01", "error": f"User: {username} does not exist."})
        if not user.is_active:
            raise ValidationError({"errorCode":"USER-M02", "error": f"User: {username} is not an active account."})
        return user
