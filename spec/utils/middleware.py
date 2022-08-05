from django.utils import timezone

class TimeStampMiddleware(object):
    """Middleware class add message timestamp to request
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not hasattr(request, '_req_dt'):
            dt = timezone.now()
            request._req_dt = dt
        return self.get_response(request)
