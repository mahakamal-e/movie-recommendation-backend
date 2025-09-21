from rest_framework import serializers
from .models import Movie, UserFavorite


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"

class UserFavoriteSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = UserFavorite
        fields = ["id", "user", "movie", "movie_id"]
