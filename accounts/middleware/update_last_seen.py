from django.utils.timezone import now
from accounts.models import UserProfile


class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            UserProfile.objects.filter(user=request.user).update(last_seen=now())
        response = self.get_response(request)
        return response
