from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserSerializer, EmailOrUsernameTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from drf_yasg.utils import swagger_auto_schema


class RegisterView(generics.CreateAPIView):
    """
    API endpoint to register a new user.

    - Uses RegisterSerializer for validation and creation.
    - Accessible to all users (no authentication required).
    """

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class MeView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve or update the authenticated user's profile.

    - Requires authentication (IsAuthenticated).
    - Uses UserSerializer for representation and update.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        """
        Returns the currently authenticated user instance.
        """
        return self.request.user


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login endpoint.

    - Allows authentication using either username or email + password.
    - Uses EmailOrUsernameTokenObtainPairSerializer to generate tokens.
    - Returns access and refresh tokens along with user details.
    """

    serializer_class = EmailOrUsernameTokenObtainPairSerializer
