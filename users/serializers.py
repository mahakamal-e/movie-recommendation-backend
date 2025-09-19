"""
Serializers for user management and authentication.

Includes:
- User registration with password validation
- User detail serialization
- Custom JWT authentication serializer supporting login via username or email
"""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Validates password and password confirmation,
    ensures username defaults to email prefix if not provided,
    and creates a new user with hashed password.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
        )

    def validate(self, attrs):
        """Ensure password and confirmation match."""
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Passwords don't match"}
            )
        return attrs

    def create(self, validated_data):
        """
        Create a new user instance.

        - Remove password2 (not needed in DB)
        - Set username from email prefix if not provided
        - Hash the password before saving
        """
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        username = (
            validated_data.get("username")
            or validated_data.get("email").split("@")[0]
        )

        user = User(**validated_data)
        if not user.username:
            user.username = username

        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for returning basic user information
    without exposing password fields.
    """

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer.

    Allows authentication using either username or email
    in the 'username' field of the login request.
    """

    def validate(self, attrs):
        """
        Validate login credentials.

        - Try authenticating by username
        - If not found, try authenticating by email
        - Return JWT tokens and serialized user data if successful
        """
        raw_username = attrs.get(self.username_field)
        password = attrs.get("password")
        user = None

        # Try to authenticate by username
        try:
            user = User.objects.get(username__iexact=raw_username)
            if not user.check_password(password):
                user = None
        except User.DoesNotExist:
            user = None

        # If not found by username, try by email
        if user is None:
            try:
                user = User.objects.get(email__iexact=raw_username)
                if not user.check_password(password):
                    user = None
            except User.DoesNotExist:
                user = None

        if user is None:
            raise serializers.ValidationError(
                "No user found with given credentials"
            )

        # Build JWT tokens
        token = super().get_token(user)
        return {
            "refresh": str(token),
            "access": str(token.access_token),
            "user": UserSerializer(user).data,
        }
