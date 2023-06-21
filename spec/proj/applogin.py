from django.shortcuts import redirect
from django.conf import settings

class CustomAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if hasattr(view_func, 'view_class'):
            # Class-based views
            view_class = view_func.view_class
            if view_class.__name__ == 'CustomLoginView':
                print("Excluding CustomLoginView from auth check")
                return None
        else:
            # Function-based views (or other callable objects)
            if view_func.__name__ == 'CustomLoginView':
                print("Excluding CustomLoginView from auth check")
                return None

        authenticated = request.user.is_authenticated
        print(f"User authenticated status: {authenticated}")

        if not authenticated:
            print("Redirecting to external login service")
            login_url = settings.AUTH_URL_LOGIN
            return redirect(login_url)
