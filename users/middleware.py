from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class JWTAuthMiddleware:
    """
    Allows open endpoints without JWT.
    Checks JWT on protected endpoints.
    Returns clear errors if token is missing or invalid.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.open_paths = [
            "/api/auth/register",
            "/api/auth/token",
            "/api/auth/token/refresh",
            "/api/docs",
        ]

    def __call__(self, request):
        # Allow open endpoints without authentication
        if any(request.path.startswith(p) for p in self.open_paths):
            return self.get_response(request)

        # Try to authenticate JWT for protected endpoints
        auth = JWTAuthentication()
        try:
            user_auth_tuple = auth.authenticate(request)
            if user_auth_tuple is None:
                # No token provided
                return JsonResponse({"error": "Token missing"}, status=401)
            request.user, _ = user_auth_tuple
        except AuthenticationFailed:
            # Token invalid
            return JsonResponse({"error": "Invalid token"}, status=401)

        return self.get_response(request)
