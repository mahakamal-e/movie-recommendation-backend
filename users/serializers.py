from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.

    Includes:
    - Password validation
    - Password confirmation (password2)
    - Automatically sets username from email if not provided
    """

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
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
        """
        Ensure that password and password2 match.

        Raises:
            serializers.ValidationError: If passwords do not match.
        """
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs

    def create(self, validated_data):
        """
        Create and return a new user instance.

        - Removes password2 from validated_data
        - Sets username from email prefix if username is not provided
        - Uses create_user() to automatically hash the password
        """
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        username = validated_data.get("username") or validated_data.get("email").split("@")[0]

        user = User.objects.create_user(
            username=username,
            email=validated_data.get("email"),
            password=password,
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for returning basic user information.

    Does not expose password or sensitive fields.
    """

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['username']
        

class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer for obtaining token using either
    username or email for authentication.
    """

    def validate(self, attrs):
        """
        Validate user credentials and return JWT tokens.

        Args:
            attrs (dict): Contains 'username' and 'password'.

        Raises:
            serializers.ValidationError: If no user matches the credentials.

        Returns:
            dict: Contains 'refresh' token, 'access' token, and serialized user data.
        """
        raw_username = attrs.get(self.username_field)
        password = attrs.get("password")

        try:
            user = User.objects.get(Q(username__iexact=raw_username) | Q(email__iexact=raw_username))
            if not user.check_password(password):
                user = None
        except User.DoesNotExist:
            user = None

        if user is None:
            raise serializers.ValidationError("No user found with given credentials")

        token = super().get_token(user)
        return {
            "refresh": str(token),
            "access": str(token.access_token),
            "user": UserSerializer(user).data,
        }
        
    
class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for handling user password change.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs