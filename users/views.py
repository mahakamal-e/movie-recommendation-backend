"""
views.py

Views for user management and authentication in the Django REST Framework project.

"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
#from ratelimit.decorators import ratelimit
from .serializers import RegisterSerializer, UserSerializer, EmailOrUsernameTokenObtainPairSerializer
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import update_session_auth_hash
from .serializers import ChangePasswordSerializer


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for registering a new user.

    Attributes:
        queryset: All User instances.
        permission_classes: Allow any user to access this endpoint.
        serializer_class: RegisterSerializer for validation and creation.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class MeView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve or update the authenticated user's profile.

    Permissions:
        Requires the user to be authenticated (IsAuthenticated).

    Restrictions:
        User cannot change 'username' or 'email' via partial update.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        """
        Return the currently authenticated user.
        """
        return self.request.user

    def partial_update(self, request, *args, **kwargs):
        """
        Allow partial update of the user's profile, except 'username' and 'email'.

        Returns:
            Response with error if username or email is included.
            Otherwise, performs standard partial update.
        """
        if "username" in request.data:
            return Response({"error": "You cannot change username."}, status=400)
        return super().partial_update(request, *args, **kwargs)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login endpoint.

    Features:
        - Allows login using either username or email.
        - Returns access and refresh tokens along with user details.
        - Optional rate limiting using django-ratelimit (currently commented out).
    """
    serializer_class = EmailOrUsernameTokenObtainPairSerializer

    #@ratelimit(key='ip', rate='5/m', method='POST', block=True)
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for obtaining JWT tokens.

        Returns:
            Response containing 'access' and 'refresh' tokens and user info.
        """
        return super().post(request, *args, **kwargs)


class ChangePasswordView(generics.UpdateAPIView):
    """
    
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['put']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": "Old password is incorrect."},
                            status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        update_session_auth_hash(request, user)

        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)

