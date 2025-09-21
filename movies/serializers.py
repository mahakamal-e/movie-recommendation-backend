from rest_framework import serializers
from .models import Movie, UserFavorite


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"

# Serializer للـ response
class UserFavoriteSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserFavorite
        fields = ["id", "user", "movie"]


class UserFavoriteCreateSerializer(serializers.ModelSerializer):
    movie_id = serializers.IntegerField()  # حقل واحد للكتابة فقط

    class Meta:
        model = UserFavorite
        fields = ["movie_id"]
