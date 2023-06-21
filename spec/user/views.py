import jwt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utils.dev_utils import formatError, IsSuperUser
from user.authentication import token_expire_handler
from user.serializers import TokenSerializer
from proj.util import MyLDAPBackend
from django.views import View
from django.conf import settings


class CustomLoginView(LoginView):
    def get(self, request, *args, **kwargs):
        jwt_token = request.GET.get('jwt_token')
        print("In CustomLoginView get method")

        # As there's no signature validation, it's okay to not provide a key.
        decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})

        first_name = decoded_token.get('name', '')
        last_name = ''
        upn = decoded_token.get('upn', '')

        print(f"TOKEN Value in Login View: {jwt_token}")
        print(f"Decoded TOKEN Value: {decoded_token}")
        print(f"Decoded First Name: {first_name}")
        print(f"Decoded Email: {upn}")

        if upn:
            try:
                user, created = User.objects.get_or_create(
                    username=upn,
                    defaults={'first_name': first_name, 'last_name': last_name, 'email': upn}
                )
                if created:
                    print(f"New user created: {user}")
                else:
                    print(f"User found in database: {user}")

                auth.login(request, user)
                return HttpResponseRedirect('/ui-spec/')
            except User.DoesNotExist:
                return HttpResponseRedirect(settings.AUTH_URL_LOGIN)
        else:
            return HttpResponseRedirect(settings.AUTH_URL_LOGIN)

        return super().get(request, *args, **kwargs)


class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        # Log the user out.
        logout(request)

        # Return a success response.
        return JsonResponse({'status': 'success'})


class UserToken(APIView):
    """
    get:
    See a list of current tokens and their expiration

    post:
    Generate a new token for the authenticated user and return it.

    delete:
    Invalidate token for authenticated user
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            tokens = Token.objects.raw("""
                            select t.*
                            from authtoken_token t
                            inner join auth_user u
                            on t.user_id = u.id
                            order by u.username""")
            serializer = TokenSerializer(tokens, many=True)
            return Response(serializer.data)
        except BaseException as be:  # pragma: no cover
            formatError(be, "TOKEN-001")


class AdminToken(APIView):
    """
    post:
    Generate a new token for the specified user and return it.

    delete:
    Invalidate token for specified user
    """
    permission_classes = [IsSuperUser]

    def post(self, request, username, format=None):
        try:
            user = MyLDAPBackend().populate_user(username)
            if user is None:
                raise ValidationError(
                    {"errorCode": "TOKEN-004", "error": f"Specified user: {username} does not exist."})

            token, _ = Token.objects.get_or_create(user=user)
            _, token = token_expire_handler(token)

            return Response({"Authorization": token.key})
        except BaseException as be:  # pragma: no cover
            formatError(be, "TOKEN-005")

    def delete(self, request, username, format=None):
        try:
            user = User.objects.filter(username=username).first()
            if user is None:
                raise ValidationError(
                    {"errorCode": "TOKEN-006", "error": f"Specified user: {username} does not exist."})
            token = Token.objects.filter(user=user).first()
            if token is not None:
                token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except BaseException as be:  # pragma: no cover
            formatError(be, "TOKEN-007")


class GetUser(APIView):
    """
    Return user info.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            token = Token.objects.filter(user=request.user).first()
            ret = {
                "user": request.user.username,
                "is_admin": request.user.is_superuser,
                "is_readAll": request.user.is_superuser,
            }
            return Response(ret)
        except BaseException as be:  # pragma: no cover
            formatError(be, "TOKEN-008")


@login_required
def auth_status(request):
    return JsonResponse({
        'is_authenticated': request.user.is_authenticated,
        'username': request.user.username,
        'isAdmin': request.user.is_superuser,
        'is_admin': request.user.is_superuser,
    })