"""
views.py

Views for user management and authentication in the Django REST Framework project.

"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
#from ratelimit.decorators import ratelimit
from .serializers import RegisterSerializer, UserSerializer, EmailOrUsernameTokenObtainPairSerializer, ChangePasswordSerializer
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import update_session_auth_hash

# -------------------------
# Register
# -------------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    @swagger_auto_schema(tags=["Authentication"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# -------------------------
# Current User (Me)
# -------------------------
class MeView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(tags=["Users"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Users"])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Users"])
    def patch(self, request, *args, **kwargs):
        if "username" in request.data:
            return Response({"error": "You cannot change username."}, status=400)
        return super().partial_update(request, *args, **kwargs)


# -------------------------
# JWT Login
# -------------------------
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailOrUsernameTokenObtainPairSerializer

    @swagger_auto_schema(tags=["Authentication"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# -------------------------
# Change Password
# -------------------------
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['put']

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(tags=["Users"])
    def put(self, request, *args, **kwargs):
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
