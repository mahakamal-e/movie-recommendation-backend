from django.urls import path
from .views import RegisterView, MeView, CustomTokenObtainPairView, ChangePasswordView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth_register"),
    path("auth/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/me/", MeView.as_view(), name="users_me"),
    path('me/change-password/', ChangePasswordView.as_view(), name='change_password'),
]
